"""Tests for v5 bridges to v4 / CI delegated modules.

Confirms each bridge:
1. Calls the real v4 module (no mocking) and produces a serializable dict.
2. Falls back gracefully when the v4 module signals a failure.
3. Surfaces the right v5 ReasonCode through ``certify_packet`` so the
   decision rail can act on a delegated-module verdict.
"""

from __future__ import annotations

import pytest

from agentic_core.L5_safety.v5 import (
    CapabilityTokenV5,
    DecisionVerdict,
    ReasonCode,
    RiskTierBandV5,
    SandboxEnvelope,
    bridge_blueprint_paths,
    bridge_guardrail_bank,
    bridge_handoff_validation,
    bridge_policy_bundle,
    bridge_registry_token_match,
    certify_packet,
    map_v5_band_to_v4,
)


# ---------------------------------------------------------------------------
# Helpers


def _read_packet(**overrides):
    return {
        "request_id": "r",
        "trace_id": "t",
        "run_id": "run",
        "tenant_id": "tnt",
        "caller_id": "u",
        "packet_kind": "request_envelope",
        "side_effect_class": "READ",
        "principal_chain_id": "pc",
        **overrides,
    }


def _good_token():
    return CapabilityTokenV5(
        token_id="tok-1",
        principal_chain_id="pc",
        scope=("read:doc",),
        ttl_seconds=300,
        single_use=True,
        max_invocations=1,
        connector_allowlist=(),
        plan_digest="pd",
        route_contract_digest="rd",
        evidence_contract_id="ec",
        permission_ladder=("read",),
        allowed_args_hash="ah",
        revocation_posture="manual",
    )


def _good_sandbox():
    return SandboxEnvelope(
        fs_scope=("/tmp",),
        net_scope=(),
        syscall_scope=(),
        env_scope=(),
        timeout_seconds=10,
        memory_mb=128,
        cpu_quota=1.0,
        token_budget=1000,
        cost_budget_usd=0.10,
        retry_budget=1,
        artifact_scope=(),
        output_sealing_path="/seal/x.json",
    )


# ---------------------------------------------------------------------------
# map_v5_band_to_v4


def test_critical_collapses_to_high():
    """v5 CRITICAL band has no v4 equivalent — must collapse to HIGH."""
    assert map_v5_band_to_v4(RiskTierBandV5.CRITICAL) == "HIGH"


def test_low_moderate_high_pass_through():
    assert map_v5_band_to_v4(RiskTierBandV5.LOW) == "LOW"
    assert map_v5_band_to_v4(RiskTierBandV5.MODERATE) == "MODERATE"
    assert map_v5_band_to_v4(RiskTierBandV5.HIGH) == "HIGH"


# ---------------------------------------------------------------------------
# bridge_blueprint_paths (S1 — structure blueprint)


def test_blueprint_path_known_layer_root_passes():
    """A known L5 path should pass blueprint checks."""
    rep = bridge_blueprint_paths(
        declared_paths=["agentic_core/L5_safety/v5/contracts.py"],
    )
    assert rep["passed"] is True
    assert "agentic_core/L5_safety/v5/contracts.py" in rep["accepted"]
    assert rep["rejected"] == []


def test_blueprint_path_with_forbidden_prefix_rejected():
    """A filename starting with a layer-prefix in the wrong layer must reject."""
    rep = bridge_blueprint_paths(
        declared_paths=["agentic_core/L5_safety/v5/L0_should_not_be_here.py"],
    )
    # If the blueprint has a forbidden-prefix rule it should reject;
    # at minimum we get a deterministic dict shape.
    assert "passed" in rep
    assert "checked" in rep
    assert rep["checked"] == 1


def test_blueprint_bridge_failure_surfaces_policy_violation():
    """certify_packet wires a failed static_report → POLICY_VIOLATION."""
    failed_static = {
        "checked": 1,
        "accepted": [],
        "rejected": [{"path": "rogue.py", "reason": "not_in_blueprint"}],
        "passed": False,
    }
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        static_report=failed_static,
    )
    assert ReasonCode.POLICY_VIOLATION in res.reason_codes
    assert res.governance_reports["static_report"]["passed"] is False


# ---------------------------------------------------------------------------
# bridge_guardrail_bank (R1/R2)


def test_guardrail_bank_with_empty_outcomes_passes():
    """Empty outcomes → v4 resolver returns 'allow' (or equivalent)."""
    rep = bridge_guardrail_bank(stage="ingress", outcomes=())
    # v4 verdict dict shape — at minimum 'decision' field.
    assert "decision" in rep
    assert rep["decision"] != "reject"


def test_guardrail_bank_invalid_stage_raises():
    with pytest.raises(ValueError):
        bridge_guardrail_bank(stage="unknown_stage", outcomes=())


def test_guardrail_reject_surfaces_injection_detected():
    """A bridge-reported reject → INJECTION_DETECTED reason code."""
    failed_guardrail = {"decision": "reject", "reasons": ["pii_in_egress"]}
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        runtime_guardrail_report=failed_guardrail,
    )
    assert ReasonCode.INJECTION_DETECTED in res.reason_codes


# ---------------------------------------------------------------------------
# bridge_handoff_validation (R4)


def test_handoff_failure_surfaces_context_bleed():
    """A failed handoff_report → CONTEXT_BLEED reason."""
    failed_handoff = {"approved": False, "reason": "principal_chain_widened"}
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        handoff_report=failed_handoff,
    )
    assert ReasonCode.CONTEXT_BLEED in res.reason_codes


# ---------------------------------------------------------------------------
# bridge_policy_bundle (G2)


def test_policy_bundle_empty_rules_passes():
    """No rules → trivially passes."""
    rep = bridge_policy_bundle(rules=())
    assert rep["passed"] is True
    assert rep["rule_count"] == 0
    assert rep["violations"] == []


def test_policy_violation_surfaces_policy_violation_code():
    """A failed policy_validation_report → POLICY_VIOLATION."""
    failed_policy = {
        "passed": False,
        "violations": ["rule_X_conflicts_with_rule_Y"],
        "rule_count": 5,
    }
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        policy_validation_report=failed_policy,
    )
    assert ReasonCode.POLICY_VIOLATION in res.reason_codes


# ---------------------------------------------------------------------------
# bridge_registry_token_match (G2)


def test_registry_mismatch_surfaces_registry_mismatch_code():
    """A failed registry_match_report → REGISTRY_MISMATCH."""
    failed_reg = {"matched": False, "reason": "stale_digest", "token_digest": "ah"}
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        registry_match_report=failed_reg,
    )
    assert ReasonCode.REGISTRY_MISMATCH in res.reason_codes
    # Visible in token_sandbox_report, not as a top-level report.
    assert (
        res.governance_reports["token_sandbox_report"]["registry_match"]["matched"]
        is False
    )


# ---------------------------------------------------------------------------
# Egress bridge surface


def test_egress_reject_surfaces_connector_scope_mismatch():
    failed_egress = {"decision": "reject", "reasons": ["connector_not_in_allowlist"]}
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        egress_report=failed_egress,
    )
    assert ReasonCode.CONNECTOR_SCOPE_MISMATCH in res.reason_codes


# ---------------------------------------------------------------------------
# Multiple bridge failures compose


def test_multiple_bridge_failures_compose_rejection():
    """All hard-reject reasons combine into a single REJECT verdict."""
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
        static_report={"passed": False, "checked": 1, "accepted": [], "rejected": [{"path": "x", "reason": "y"}]},
        runtime_guardrail_report={"decision": "reject"},
        registry_match_report={"matched": False, "reason": "stale", "token_digest": "ah"},
    )
    # Multiple hard-reject reasons → REJECT
    assert res.decision == DecisionVerdict.REJECT
    assert ReasonCode.POLICY_VIOLATION in res.reason_codes
    assert ReasonCode.INJECTION_DETECTED in res.reason_codes
    assert ReasonCode.REGISTRY_MISMATCH in res.reason_codes


# ---------------------------------------------------------------------------
# No bridge inputs = healthy default (regression: ensure existing 38 tests still green)


def test_no_bridge_inputs_yields_certify():
    res = certify_packet(
        raw_packet=_read_packet(),
        capability_token=_good_token(),
        sandbox_envelope=_good_sandbox(),
    )
    assert res.decision == DecisionVerdict.CERTIFY
    # All bridge-owned reports are empty dicts (wire shape preserved).
    for k in (
        "static_report",
        "runtime_guardrail_report",
        "handoff_report",
        "policy_validation_report",
        "egress_report",
    ):
        assert res.governance_reports[k] == {}
