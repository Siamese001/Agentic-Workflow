"""Tests for L2 entry-pipeline normalization (doc 04.1).

Covers the four 04.1 §PHASE 4 acceptance tests plus per-rule rejections.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.entry.packet_normalizer import (
    NormalizationResult,
    normalize_to_request,
)
from agentic_core.L2_execution.types.l2_execution_request import (
    DurableWriteAuthority,
    EntryRejectionReason,
    ExecutionAuthorityContext,
    HumanInputScope,
    IssuerSurface,
    L2BoundaryAssertion,
    L2ExecutionRequest,
    SourcePacketType,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


def _good_authority(issuer: IssuerSurface = IssuerSurface.L0) -> ExecutionAuthorityContext:
    return ExecutionAuthorityContext(
        authority_context_id="auth-1",
        issuer_surface=issuer,
        issuer_receipt_ref="iss-receipt-1",
        route_authority_ref="route-auth-1",
        capability_scope="cap.read",
        sandbox_scope="sbx.tmp",
        tenant_scope="tenant-a",
        acl_scope="acl.read",
        provider_lane="anthropic.lane.a",
        filesystem_scope="/tmp/sandbox",
        network_scope="none",
        credential_scope="none",
    )


def _good_packet() -> dict:
    return {
        "request_id": "req-1",
        "run_id": "run-1",
        "trace_root": "trace-1",
        "route_id": "route-1",
        "route_contract_ref": "rc-1",
        "execution_form": "SINGLE_STEP",
        "source_packet_type": SourcePacketType.L0_SINGLE_STEP,
        "signed_packet_ref": "sig-1",
        "task_spec_ref": "task-1",
        "capability_token_ref": "cap-tok-1",
        "sandbox_envelope_ref": "sbx-env-1",
        "side_effect_class": "READ",
        "policy_hash": "pol-1",
        "blueprint_hash": "bp-1",
        "replay_key": "rk-1",
        "snapshot_manifest_ref": "sm-1",
        "expected_output_contract": "answer.text.v1",
        "max_attempts": 1,
        "max_repair_count": 1,
        "timeout_ms": 5_000,
        "cost_budget": 0.05,
        "issuer_signature_hmac": "abc123",
        "telemetry_keys": ("trace_root", "request_id"),
    }


# ---------------------------------------------------------------------------
# Acceptance tests from 04.1 §PHASE 4
# ---------------------------------------------------------------------------


def test_unsigned_packet_rejected_before_e1() -> None:
    raw = _good_packet()
    raw["issuer_signature_hmac"] = ""
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert isinstance(res, NormalizationResult)
    assert res.rejection is not None
    assert res.request is None
    assert res.rejection.reason is EntryRejectionReason.UNSIGNED_PACKET


def test_l3_step_without_route_contract_rejected() -> None:
    raw = _good_packet()
    raw["source_packet_type"] = SourcePacketType.L3_CURRENT_STEP
    raw["route_contract_ref"] = ""  # missing parent route
    res = normalize_to_request(
        raw_packet=raw, authority_context=_good_authority(IssuerSurface.L3)
    )
    assert res.rejection is not None
    # Either MISSING_REQUIRED_REF (caught earlier) or NO_ROUTE_CONTRACT_REF
    assert res.rejection.reason in (
        EntryRejectionReason.MISSING_REQUIRED_REF,
        EntryRejectionReason.NO_ROUTE_CONTRACT_REF,
    )


def test_ptc_marker_does_not_execute_during_entry() -> None:
    """A PTC-marked packet that's well-formed normalizes — but does NOT run.

    The entry surface MUST never invoke the PTC sandbox; it only stamps the
    request with `is_ptc_execution=True` and the requirement-validated refs.
    """
    raw = _good_packet()
    raw["is_ptc_execution"] = True
    raw["ptc_execution_profile_ref"] = "ptc-profile-1"
    raw["script_digest"] = "sha256:abc"
    raw["sandbox_profile_ref"] = "sbx-profile-1"

    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.ok
    assert res.request is not None
    # Smoking gun: the request contains the PTC refs but the result is a
    # *request*, not a sandbox receipt.
    assert res.request.is_ptc_execution is True
    assert res.request.ptc_execution_profile_ref == "ptc-profile-1"
    assert res.request.script_digest == "sha256:abc"
    assert res.request.sandbox_profile_ref == "sbx-profile-1"
    # No execution-side artifact is emitted by entry.
    assert not hasattr(res, "ptc_sandbox_receipt")


def test_direct_write_authority_flag_rejected() -> None:
    # We can't construct an authority with NONE then override; the type
    # system enforces it. So we make a stub class instead.
    class _BadAuth(ExecutionAuthorityContext):
        pass

    bad = ExecutionAuthorityContext(
        authority_context_id="bad-auth",
        issuer_surface=IssuerSurface.L0,
        issuer_receipt_ref="iss-1",
        route_authority_ref="r-1",
        capability_scope="c",
        sandbox_scope="s",
        tenant_scope="t",
        acl_scope="a",
        provider_lane="p",
        filesystem_scope="f",
        network_scope="n",
        credential_scope="cr",
    )
    # Replace the field via dataclasses.replace to a synthetic 'WRITE' value.
    # We construct a fake enum-like via subclassing isn't trivial; instead
    # we use dataclasses.replace to swap the .durable_write_authority — the
    # type system still allows assignment because frozen=True only blocks
    # attribute set after __init__.
    import dataclasses

    class _FakeAuthority(str):
        value = "WRITE"

    forced = dataclasses.replace(bad, durable_write_authority=_FakeAuthority("WRITE"))  # type: ignore[arg-type]
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=forced)
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.GRANTS_DURABLE_WRITE


def test_route_change_request_rejected() -> None:
    raw = _good_packet()
    raw["declared_intent"] = "reroute"
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.ASKS_L2_TO_RETRIEVE_OR_ROUTE


def test_human_review_text_cannot_become_authority() -> None:
    bad_auth = ExecutionAuthorityContext(
        authority_context_id="auth-2",
        issuer_surface=IssuerSurface.L0,
        issuer_receipt_ref=(
            "Approved by human reviewer on 2026-01-01 because the request "
            "looked fine and the customer was nice"
        ),
        route_authority_ref="r-1",
        capability_scope="c",
        sandbox_scope="s",
        tenant_scope="t",
        acl_scope="a",
        provider_lane="p",
        filesystem_scope="f",
        network_scope="n",
        credential_scope="cr",
    )
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=bad_auth)
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.HUMAN_TEXT_IN_AUTHORITY


def test_entry_receipt_preserves_route_plan_prompt_evidence_step_refs() -> None:
    raw = _good_packet()
    raw["prompt_envelope_ref"] = "pe-1"
    raw["final_evidence_contract_ref"] = "fec-1"
    raw["l3_step_contract_ref"] = "step-1"
    raw["grounded"] = True

    res = normalize_to_request(
        raw_packet=raw, authority_context=_good_authority(IssuerSurface.L3)
    )
    assert res.ok
    req = res.request
    assert req is not None
    assert req.prompt_envelope_ref == "pe-1"
    assert req.final_evidence_contract_ref == "fec-1"
    assert req.l3_step_contract_ref == "step-1"
    assert req.route_contract_ref == "rc-1"
    assert req.task_spec_ref == "task-1"


# ---------------------------------------------------------------------------
# Per-rule rejections (04.1 §PHASE 3 FAILURE MODES)
# ---------------------------------------------------------------------------


def test_missing_route_contract_ref_rejected() -> None:
    raw = _good_packet()
    raw["route_contract_ref"] = ""
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.rejection is not None
    # Caught by required-field loop OR by explicit no_route_contract_ref check.
    assert res.rejection.reason in (
        EntryRejectionReason.MISSING_REQUIRED_REF,
        EntryRejectionReason.NO_ROUTE_CONTRACT_REF,
    )


def test_route_digest_mismatch_rejected() -> None:
    raw = _good_packet()
    raw["route_digest"] = "digest-A"
    res = normalize_to_request(
        raw_packet=raw,
        authority_context=_good_authority(),
        expected_route_digest="digest-B",
    )
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.ROUTE_DIGEST_MISMATCH


def test_route_digest_match_passes() -> None:
    raw = _good_packet()
    raw["route_digest"] = "digest-X"
    res = normalize_to_request(
        raw_packet=raw,
        authority_context=_good_authority(),
        expected_route_digest="digest-X",
    )
    assert res.ok


def test_grounded_route_missing_evidence_contract_rejected() -> None:
    raw = _good_packet()
    raw["grounded"] = True
    # Intentionally omit prompt_envelope_ref + final_evidence_contract_ref.
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.GROUNDED_MISSING_EVIDENCE_CONTRACT


def test_model_execution_missing_prompt_envelope_rejected() -> None:
    raw = _good_packet()
    raw["is_model_execution"] = True
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.MODEL_EXECUTION_MISSING_PROMPT_ENVELOPE


def test_ptc_missing_script_digest_rejected() -> None:
    raw = _good_packet()
    raw["is_ptc_execution"] = True
    raw["ptc_execution_profile_ref"] = "ptc-profile-1"
    # script_digest intentionally missing
    raw["sandbox_profile_ref"] = "sbx-profile-1"
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.PTC_MISSING_DIGEST_OR_PROFILE


def test_boundary_violation_short_circuits() -> None:
    raw = _good_packet()
    bad_boundary = L2BoundaryAssertion(no_direct_l4_write_asserted=False)
    res = normalize_to_request(
        raw_packet=raw,
        authority_context=_good_authority(),
        boundary_assertion=bad_boundary,
    )
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.BOUNDARY_VIOLATION
    assert "no_direct_l4_write_asserted" in res.rejection.boundary_violations


def test_non_governed_issuer_rejected() -> None:
    # Construct an issuer that isn't L0/L3 by force.
    class _Issuer(str):
        pass

    bad_iss_value = _Issuer("L99")
    bad = ExecutionAuthorityContext(
        authority_context_id="auth-bad",
        issuer_surface=bad_iss_value,  # type: ignore[arg-type]
        issuer_receipt_ref="iss-1",
        route_authority_ref="r-1",
        capability_scope="c",
        sandbox_scope="s",
        tenant_scope="t",
        acl_scope="a",
        provider_lane="p",
        filesystem_scope="f",
        network_scope="n",
        credential_scope="cr",
    )
    res = normalize_to_request(raw_packet=_good_packet(), authority_context=bad)
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.NON_GOVERNED_ISSUER


# ---------------------------------------------------------------------------
# Happy path — full end-to-end normalization
# ---------------------------------------------------------------------------


def test_well_formed_packet_normalizes_to_request() -> None:
    raw = _good_packet()
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.ok
    assert res.rejection is None
    assert isinstance(res.request, L2ExecutionRequest)
    assert res.request.source_packet_type is SourcePacketType.L0_SINGLE_STEP
    assert res.request.is_governed_channel()
    assert res.request.boundary_assertion.all_clean()
    assert res.request.authority_context.human_input_scope is HumanInputScope.DATA_ONLY
    assert res.request.authority_context.durable_write_authority is DurableWriteAuthority.NONE


def test_replay_resume_source_packet_type_accepted() -> None:
    raw = _good_packet()
    raw["source_packet_type"] = SourcePacketType.REPLAY_RESUME
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.ok
    assert res.request is not None
    assert res.request.source_packet_type is SourcePacketType.REPLAY_RESUME


def test_unknown_source_packet_type_rejected() -> None:
    raw = _good_packet()
    raw["source_packet_type"] = "L7_FANTASY"
    res = normalize_to_request(raw_packet=raw, authority_context=_good_authority())
    assert res.rejection is not None
    assert res.rejection.reason is EntryRejectionReason.MISSING_REQUIRED_REF
    assert res.rejection.failed_field == "source_packet_type"
