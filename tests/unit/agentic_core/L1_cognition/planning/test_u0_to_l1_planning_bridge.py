"""Tests for the U0 ValidatedRequest -> L1 v6 ParsedRequestInput bridge."""

from __future__ import annotations

import pytest

from agentic_core.L1_cognition.bridges.u0_to_l1_planning import (
    rejected_request_to_parsed_request_input,
    validated_request_to_parsed_request_input,
)
from agentic_core.L1_cognition.planning import (
    L1ContractViolation,
    ParsedRequestInput,
    run_l1_planning,
)


def _make_validated_request(**overrides):
    """Build a minimal valid :class:`ValidatedRequest` for tests.

    We construct via the dataclass constructor with sane defaults; any
    field can be overridden via kwargs.
    """
    from agentic_core.L0_routing.intake.envelope import (
        AttachmentManifestShell,
        ModalityManifest,
    )
    from agentic_core.L0_routing.intake.validated_request import ValidatedRequest
    from agentic_core.L0_routing.intake.verdicts import (
        AuthVerdict,
        IdempotencyStatus,
        NormalizationVerdict,
        PrincipalType,
        QuotaVerdict,
        SchemaVerdict,
        SourceClass,
    )

    defaults = dict(
        request_id="req-bridge-001",
        session_id="sess-bridge-001",
        trace_root="trace-bridge-001",
        ingress_time_unix=0.0,
        received_at_iso="2026-04-26T00:00:00Z",
        source_channel="api",
        source_class=SourceClass.USER,
        tenant_bind="tenant-x",
        workspace_bind=None,
        principal_type=PrincipalType.USER,
        principal_id="user-x",
        auth_verdict=AuthVerdict.AUTHENTICATED,
        caller_scope_baseline="user:standard",
        region_scope_baseline=None,
        baseline_entitlements=(),
        quota_verdict=QuotaVerdict.ALLOWED,
        quota_bucket="default",
        rate_window_state="ok",
        dedupe_status="not_duplicate",
        idempotency_status=IdempotencyStatus.NEW,
        abuse_precheck_status="ok",
        retry_after_seconds=None,
        schema_verdict=SchemaVerdict.VALID,
        envelope_version="v1",
        request_shape_class="chat_text",
        modality_manifest=ModalityManifest(),
        field_validation_report=(),
        normalization_verdict=NormalizationVerdict.NORMALIZED,
        normalized_payload="Summarize the README and cite the version line.",
        normalized_payload_ref="payload-ref-x",
        raw_payload_ref="raw-ref-x",
        raw_payload_hash="raw-hash-x",
        normalized_payload_hash="norm-hash-x",
        normalization_report=(),
        suspicious_field_markers=(),
        attachment_manifest=AttachmentManifestShell(),
        upstream_traceparent=None,
        locale=None,
        timezone=None,
        client_version=None,
        platform=None,
        batch_id=None,
        job_id=None,
        alert_id=None,
        webhook_delivery_id=None,
        ingress_reason_codes=(),
        intake_manifest_hash="manifest-hash-x",
        normalized_request_hash="norm-hash-x",
        ingress_replay_seed_ref="replay-seed-x",
        correlation_receipt_ref="corr-receipt-x",
    )
    defaults.update(overrides)
    return ValidatedRequest(**defaults)


def test_bridge_returns_parsed_request_input():
    vr = _make_validated_request()
    pi = validated_request_to_parsed_request_input(vr)
    assert isinstance(pi, ParsedRequestInput)
    assert pi.request_id == vr.request_id
    assert pi.session_id == vr.session_id
    assert pi.trace_root == vr.trace_root
    assert pi.caller_scope_baseline == vr.caller_scope_baseline
    assert pi.normalized_user_payload == vr.normalized_payload
    assert pi.policy_hash_observed == vr.intake_manifest_hash
    assert pi.instruction_hash_observed == vr.correlation_receipt_ref
    assert pi.source_envelope_id == vr.ingress_replay_seed_ref
    assert pi.validated_request is vr


def test_bridge_pipes_into_run_l1_planning_end_to_end():
    """Full integration: ValidatedRequest -> ParsedRequestInput -> L1PlanContract."""
    vr = _make_validated_request()
    pi = validated_request_to_parsed_request_input(vr)
    packet = run_l1_planning(pi)
    assert packet.l1_plan_contract.layer == "L1_REASONING_PLAN_GENERATION"
    assert packet.l1_plan_contract.identity["request_id"] == vr.request_id
    assert packet.l1_plan_contract.identity["trace_root"] == vr.trace_root


def test_validated_request_itself_rejects_non_l1_authorisation():
    """Defense-in-depth: ValidatedRequest's own __post_init__ enforces the
    invariant before our bridge ever sees the slip. We document that here so
    a future change loosening the upstream check is caught by this test.
    """
    with pytest.raises(ValueError, match="permitted_next_layer"):
        _make_validated_request(permitted_next_layer="L0")


def test_bridge_rejects_downstream_authority_grant():
    """Cannot construct a ValidatedRequest with downstream_authority != none.

    ValidatedRequest's own `__post_init__` enforces the invariant; this test
    confirms our defense-in-depth check is consistent with U0's contract.
    """
    with pytest.raises(ValueError):
        _make_validated_request(downstream_authority="something")


def test_rejected_request_bridge_requires_summary():
    with pytest.raises(L1ContractViolation):
        rejected_request_to_parsed_request_input(
            None,
            request_id="r",
            session_id="s",
            trace_root="t",
            caller_scope_baseline="b",
        )


def test_rejected_request_bridge_builds_input():
    pi = rejected_request_to_parsed_request_input(
        rejected_summary={"reason": "schema_invalid", "code": "SCHEMA_FAIL"},
        request_id="req-rej-1",
        session_id="sess-rej-1",
        trace_root="trace-rej-1",
        caller_scope_baseline="user:standard",
    )
    assert isinstance(pi, ParsedRequestInput)
    assert pi.validated_request is None
    assert pi.rejected_request_summary["reason"] == "schema_invalid"
