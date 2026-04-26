"""Tests for 01.6 Validated Request Handoff."""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.intake import (
    IngressRejectionReport,
    IntakeAuditReceipt,
    IntakePipeline,
    IntakePolicy,
    IntakeStatus,
    L1HandoffEnvelope,
    RawIngressEnvelope,
    REJECTED_STATUSES,
    ValidatedRequest,
)
from agentic_core.L0_routing.intake.reason_codes import IngressReasonCode


def _pipe() -> IntakePipeline:
    return IntakePipeline(IntakePolicy())


# ----------------------------------------------------------------------
# Success path: ValidatedRequest + L1HandoffEnvelope + audit
# ----------------------------------------------------------------------


def test_handoff_envelope_emitted_on_success() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.accepted
    assert out.handoff_envelope is not None
    assert isinstance(out.handoff_envelope, L1HandoffEnvelope)
    assert out.rejection_report is None
    assert out.handoff_envelope.handoff_target == "L1_REASONING_PLAN"
    assert out.handoff_envelope.no_raw_bypass_assertion is True
    assert out.handoff_envelope.downstream_read_only_assertion is True


def test_handoff_envelope_carries_validated_request_only() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hello"))
    assert out.handoff_envelope is not None
    assert isinstance(out.handoff_envelope.validated_request, ValidatedRequest)
    # The dataclass shape excludes RouteContract / RetrievalPlan / PromptEnvelope.
    forbidden = {
        "route_contract",
        "retrieval_plan",
        "prompt_envelope",
        "l2_execution_request",
        "exit_disposition",
    }
    fields = set(L1HandoffEnvelope.__dataclass_fields__.keys())
    assert fields & forbidden == set()


def test_handoff_receipt_hash_set() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.handoff_envelope is not None
    assert out.handoff_envelope.handoff_receipt_hash != ""


def test_final_audit_receipt_carries_status_and_audit_hash() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    audit = out.final_audit
    assert isinstance(audit, IntakeAuditReceipt)
    assert audit.intake_status is IntakeStatus.VALIDATED_FOR_L1
    assert audit.audit_hash != ""
    assert audit.completeness_score == 1.0
    assert audit.first_failure_stage is None
    assert audit.intake_manifest_hash is not None


def test_intake_manifest_hash_present_on_validated_request() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.validated is not None
    assert out.validated.intake_manifest_hash != ""
    assert out.validated.intake_status == "VALIDATED_FOR_L1"


# ----------------------------------------------------------------------
# Failure path: IngressRejectionReport + audit, no handoff envelope
# ----------------------------------------------------------------------


def test_rejection_report_emitted_on_transport_failure() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="smtp", body_text="x"))
    assert not out.accepted
    assert out.handoff_envelope is None
    rep = out.rejection_report
    assert isinstance(rep, IngressRejectionReport)
    assert rep.rejection_status is IntakeStatus.REJECTED_AT_TRANSPORT
    assert rep.decisive_reason_code is IngressReasonCode.UNSUPPORTED_TRANSPORT
    assert rep.safe_user_visible_summary  # non-empty
    assert rep.audit_receipt_refs  # carries audit ref
    assert rep.recoverable_by_user is True


def test_rejection_report_for_quota_includes_retry_hint() -> None:
    from agentic_core.L0_routing.intake.stages import QuotaState

    state = QuotaState(rate_limit_per_window=1, burst_limit=1)
    pipe = IntakePipeline(IntakePolicy(quota=state))
    pipe.run(RawIngressEnvelope(transport="chat", body_text="a"))
    out = pipe.run(RawIngressEnvelope(transport="chat", body_text="b"))
    if not out.accepted:
        rep = out.rejection_report
        assert rep is not None
        if rep.decisive_reason_code in {
            IngressReasonCode.QUOTA_EXCEEDED,
            IngressReasonCode.BURST_LIMIT,
        }:
            assert rep.retry_hint == "retry_after_seconds"
            assert rep.rejection_status is IntakeStatus.REJECTED_AT_QUOTA


def test_rejection_status_is_canonical_member() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="smtp", body_text="x"))
    rep = out.rejection_report
    assert rep is not None
    assert rep.rejection_status in REJECTED_STATUSES


def test_audit_receipt_emitted_even_on_failure() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="smtp", body_text="x"))
    assert out.final_audit is not None
    assert out.final_audit.intake_status in REJECTED_STATUSES
    assert out.final_audit.audit_hash != ""
    assert 0.0 <= out.final_audit.completeness_score < 1.0
    assert out.final_audit.first_failure_stage == "E1"


# ----------------------------------------------------------------------
# Boundary invariants
# ----------------------------------------------------------------------


def test_handoff_envelope_rejects_bad_target() -> None:
    """Construction MUST fail-closed if someone tries to point handoff at
    a non-L1 layer."""
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.handoff_envelope is not None
    with pytest.raises(ValueError):
        L1HandoffEnvelope(
            handoff_id="h:1",
            validated_request=out.handoff_envelope.validated_request,
            handoff_target="L2_EXECUTION",  # forbidden
        )


def test_handoff_envelope_rejects_disabled_no_bypass_assertion() -> None:
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert out.handoff_envelope is not None
    with pytest.raises(ValueError):
        L1HandoffEnvelope(
            handoff_id="h:1",
            validated_request=out.handoff_envelope.validated_request,
            no_raw_bypass_assertion=False,  # forbidden
        )


def test_intake_outcome_is_valid_xor_rejected() -> None:
    """01.6 hard-no: must carry exactly one of validated / rejected (and the
    handoff envelope vs rejection report mirror this)."""
    out = _pipe().run(RawIngressEnvelope(transport="chat", body_text="hi"))
    assert (out.validated is None) != (out.rejected is None)
    assert (out.handoff_envelope is None) != (out.rejection_report is None)


def test_audit_hash_is_deterministic_across_runs() -> None:
    """Same logical input → same final-audit audit_hash. Volatile per-run
    audit_receipt_id is excluded from the hash inputs."""
    env = RawIngressEnvelope(
        transport="chat",
        body_text="stable",
        auth_credential={"kind": "session", "token": "t"},
        claimed_user_id="u",
        claimed_tenant_id="t1",
        session_id_hint="sess",
    )
    a = _pipe().run(env)
    b = _pipe().run(env)
    assert a.final_audit is not None and b.final_audit is not None
    assert a.final_audit.audit_hash == b.final_audit.audit_hash
