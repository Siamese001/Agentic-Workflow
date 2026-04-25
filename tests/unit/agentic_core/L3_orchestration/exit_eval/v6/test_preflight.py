"""Tests for v6 §5.0 + §5.1 preflight."""

from __future__ import annotations

from agentic_core.L3_orchestration.exit_eval.v6 import (
    ExitReviewPacket,
    SourceType,
    classify_source,
    normalize_to_packet,
    validate_required_receipts,
)
from agentic_core.L3_orchestration.exit_eval.v6.preflight import bind_run_identity

from tests.unit.agentic_core.L3_orchestration.exit_eval.v6._fixtures import base_receipts


# ---- 5.1 N1 source classification ----


def test_source_explicit_l2_sealed() -> None:
    assert classify_source({"source_type": "L2_SEALED_ARTIFACT"}) is SourceType.L2_SEALED_ARTIFACT


def test_source_inferred_workflow() -> None:
    assert classify_source({"workflow_package": {"steps": []}}) is SourceType.L3_WORKFLOW_PACKAGE


def test_source_inferred_cache_exact() -> None:
    assert classify_source({"cache_hit_kind": "exact"}) is SourceType.RET_CACHE_EXACT


def test_source_inferred_hitl() -> None:
    assert classify_source({"hitl_recleared": True}) is SourceType.HITL_RECLEARED_PACKET


def test_source_invalid_raises() -> None:
    import pytest

    with pytest.raises(ValueError, match="unknown source_type"):
        classify_source({"source_type": "BOGUS"})


# ---- 5.0 immediate-fail validation ----


def test_clean_receipts_pass_validation() -> None:
    failures = validate_required_receipts(base_receipts())
    assert failures == []


def test_missing_policy_hash_fails() -> None:
    rec = base_receipts(policy_hash="")
    failures = validate_required_receipts(rec)
    codes = [f.reason_code for f in failures]
    assert "POLICY_HASH_MISSING" in codes


def test_missing_replay_key_fails() -> None:
    rec = base_receipts(replay_key="")
    codes = [f.reason_code for f in validate_required_receipts(rec)]
    assert "REPLAY_KEY_MISSING" in codes


def test_missing_route_contract_fails() -> None:
    rec = base_receipts(route_contract={})
    codes = [f.reason_code for f in validate_required_receipts(rec)]
    assert "ROUTE_CONTRACT_MISSING" in codes


def test_missing_terminal_class_fails() -> None:
    rec = base_receipts(terminal_class="")
    codes = [f.reason_code for f in validate_required_receipts(rec)]
    assert "TERMINAL_CLASS_MISSING" in codes


def test_action_terminal_requires_sandbox() -> None:
    rec = base_receipts(terminal_class="with_state_diff", sandbox_envelope={})
    codes = [f.reason_code for f in validate_required_receipts(rec)]
    assert "SANDBOX_SCOPE_MISSING" in codes


def test_action_terminal_requires_capability_token() -> None:
    rec = base_receipts(terminal_class="with_state_diff", capability_token={})
    codes = [f.reason_code for f in validate_required_receipts(rec)]
    assert "CAPABILITY_TOKEN_MISSING" in codes


def test_grounding_required_needs_evidence_contract() -> None:
    rec = base_receipts(grounding_required=True, final_evidence_contract={})
    codes = [f.reason_code for f in validate_required_receipts(rec)]
    assert "EVIDENCE_CONTRACT_MISSING" in codes


def test_answer_only_no_capability_token_required() -> None:
    rec = base_receipts(capability_token={})
    rec["exec_trace"] = {"tool_calls": [], "model_calls": [], "replay_receipts_present": True}
    codes = [f.reason_code for f in validate_required_receipts(rec)]
    assert "CAPABILITY_TOKEN_MISSING" not in codes


# ---- 5.1 N3 identity binding ----


def test_identity_binding_clean() -> None:
    assert bind_run_identity(base_receipts()) == []


def test_identity_binding_missing_run_id() -> None:
    rec = base_receipts(run_id="")
    codes = [f.reason_code for f in bind_run_identity(rec)]
    assert "IDENTITY_BINDING_INCOMPLETE" in codes


def test_hidden_reroute_detected() -> None:
    rec = base_receipts(route_id="R5", route_contract={**base_receipts()["route_contract"], "route_id": "R3"})
    codes = [f.reason_code for f in bind_run_identity(rec)]
    assert "HIDDEN_REROUTE_DETECTED" in codes


def test_policy_hash_mismatch_detected() -> None:
    rec = base_receipts(
        policy_hash="pol::v1", route_contract={**base_receipts()["route_contract"], "policy_hash": "pol::v2"}
    )
    codes = [f.reason_code for f in bind_run_identity(rec)]
    assert "POLICY_HASH_MISMATCH" in codes


# ---- 5.1 N2 normalization ----


def test_normalize_preserves_lineage() -> None:
    rec = base_receipts(source_type="L3_WORKFLOW_PACKAGE")
    packet = normalize_to_packet(rec)
    assert isinstance(packet, ExitReviewPacket)
    assert packet.source_type is SourceType.L3_WORKFLOW_PACKAGE
    assert packet.request_id == "req-1"
    assert packet.replay_key == "rk-1"


def test_normalize_attaches_live_signals() -> None:
    rec = base_receipts(
        bus_d_signals=["DENY_HINT"],
        replay_guard_violations=["RGV_001"],
        anomaly_flags=["ANOMALY_X"],
    )
    packet = normalize_to_packet(rec)
    assert packet.bus_d_signals == ["DENY_HINT"]
    assert packet.replay_guard_violations == ["RGV_001"]
    assert packet.anomaly_flags == ["ANOMALY_X"]
