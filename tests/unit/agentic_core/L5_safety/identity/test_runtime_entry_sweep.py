"""Tests for runtime_entry_sweep.py — Wave 38 module 1."""

from __future__ import annotations

import pytest

from agentic_core.interfaces.principal_chain_types import PermissionLadderRung
from agentic_core.L2_execution.types.capability_token_v4_types import (
    CapabilityTokenV4Artifact,
)
from agentic_core.L5_safety.identity.guardrail_adapter import (
    ChokepointV4Result,
)
from agentic_core.L5_safety.identity.guardrail_bank import GuardrailOutcome
from agentic_core.L5_safety.identity.pre_l5_sweep import (
    PreL5SweepResult,
)
from agentic_core.L5_safety.identity.principal_verifier import VerificationStatus
from agentic_core.L5_safety.identity.runtime_entry_sweep import (
    RuntimeLaneDecisionWithSweep,
    RuntimeLaneRejected,
    evaluate_runtime_lane_with_sweep,
)
from agentic_core.L5_safety.identity.runtime_rails import (
    AgentRegistryRecord,
    HandoffValidationResult,
    RiskTierDecision,
)


def _make_token() -> CapabilityTokenV4Artifact:
    """Minimal token for testing - use simple mock objects."""
    from agentic_core.L0_routing.types.determinism_types import (
        SemanticClockSnapshot,
    )

    # Create a minimal mock token - use type() to avoid complex constructor
    token = type("obj", (object,), {
        "artifact_type": "CAPABILITY_TOKEN_V4",
        "semantic_clock": SemanticClockSnapshot(tick=0),
        "v4_trace_id": "v4-trace-1",
        "v3_artifact": type("obj", (object,), {})(),
        "principal_chain": type("obj", (object,), {
            "invoking_user": "user-1",
            "delegation_depth": 0,
        })(),
        "risk_tier_band": "LOW",
        "permission_ladder_entry": "read",
        "ttl_seconds": 3600,
        "single_use": False,
        "expires_at_semantic_clock": "tick-999999",
        "connector_allowlist": (),
        "tool_allowlist": (),
        "plan_digest": "plan-digest-1",
        "grant_mode": "permanent",
        "standards_fingerprint": type("obj", (object,), {})(),
    })()
    return token


def _make_sweep_result(
    *,
    verification_status: VerificationStatus = VerificationStatus.PASS,
    registry_match: bool = True,
    data_authority_all_match: bool = True,
) -> PreL5SweepResult:
    """Minimal sweep result for testing."""
    # Create a proper mock verification object with required attributes and methods
    def mock_to_dict(self):
        return {
            "status": verification_status.value if hasattr(verification_status, "value") else str(verification_status),
            "is_pass": verification_status == VerificationStatus.PASS,
            "needs_step_up": False,
            "failures": () if verification_status == VerificationStatus.PASS else ("verification_failed",),
        }
    
    verification = type("obj", (object,), {
        "status": verification_status,
        "is_pass": verification_status == VerificationStatus.PASS,
        "needs_step_up": False,
        "failures": () if verification_status == VerificationStatus.PASS else ("verification_failed",),
        "to_dict": mock_to_dict,
    })()
    return PreL5SweepResult(
        verification=verification,
        registry_match=registry_match,
        registry_reason="ok" if registry_match else "drift",
        data_authority_all_match=data_authority_all_match,
    )


def _make_risk_tier_result() -> RiskTierDecision:
    """Minimal risk tier result for testing."""
    from agentic_core.L5_safety.identity.runtime_rails import (
        RiskEscalationReason,
    )

    return RiskTierDecision(
        token_band="LOW",
        runtime_band="LOW",
        escalation_reason=RiskEscalationReason.NONE,
        requires_hitl=False,
        log_verbosity=1,
    )


def _make_chokepoint_result(final_action: str = "allow") -> ChokepointV4Result:
    """Minimal chokepoint result for testing."""
    from agentic_core.L5_safety.identity.guardrail_bank import (
        EgressInspectionResult,
        GuardrailBankVerdict,
    )
    from typing import Literal

    # Type-safe final_action
    action: Literal["allow", "remediate", "reject"] = final_action  # type: ignore

    # Minimal verdict objects - egress inspection requires stage='egress'
    egress_verdict = GuardrailBankVerdict(
        stage="egress",
        verdict=action,
        ordered_outcomes=(),
        digest="digest-1",
    )
    egress_inspection = EgressInspectionResult(
        bank_verdict=egress_verdict,
        guard_model_outcome=None,
        final_action=action,
    )

    return ChokepointV4Result(
        ingress_verdict=egress_verdict,  # Use same verdict for simplicity
        egress_inspection=egress_inspection,
        final_action=action,
    )


def _make_handoff_result(allow: bool = True) -> HandoffValidationResult:
    """Minimal handoff result for testing."""
    return HandoffValidationResult(
        allow=allow,
        failures=() if allow else ("blocked",),
        target_agent_id="agent-1",
        effective_scopes=(),
    )


class TestRuntimeLaneDecisionWithSweep:
    """Tests for RuntimeLaneDecisionWithSweep dataclass."""

    def test_construction(self):
        """Dataclass constructs with all required fields."""
        sweep = _make_sweep_result()
        risk_tier = _make_risk_tier_result()
        chokepoint = _make_chokepoint_result()

        decision = RuntimeLaneDecisionWithSweep(
            sweep=sweep,
            risk_tier=risk_tier,
            chokepoint=chokepoint,
            handoff=None,
            final_action="allow",
        )

        assert decision.sweep is sweep
        assert decision.risk_tier is risk_tier
        assert decision.chokepoint is chokepoint
        assert decision.handoff is None
        assert decision.final_action == "allow"

    def test_to_dict_with_handoff(self):
        """Serialization includes handoff when present."""
        sweep = _make_sweep_result()
        risk_tier = _make_risk_tier_result()
        chokepoint = _make_chokepoint_result()
        handoff = _make_handoff_result()

        decision = RuntimeLaneDecisionWithSweep(
            sweep=sweep,
            risk_tier=risk_tier,
            chokepoint=chokepoint,
            handoff=handoff,
            final_action="allow",
        )

        d = decision.to_dict()
        assert d["final_action"] == "allow"
        assert d["sweep"] is not None
        assert d["risk_tier"] is not None
        assert d["chokepoint"] is not None
        assert d["handoff"] is not None

    def test_to_dict_without_handoff(self):
        """Serialization omits handoff when None."""
        sweep = _make_sweep_result()
        risk_tier = _make_risk_tier_result()
        chokepoint = _make_chokepoint_result()

        decision = RuntimeLaneDecisionWithSweep(
            sweep=sweep,
            risk_tier=risk_tier,
            chokepoint=chokepoint,
            handoff=None,
            final_action="allow",
        )

        d = decision.to_dict()
        assert d["handoff"] is None


class TestRuntimeLaneRejected:
    """Tests for RuntimeLaneRejected exception."""

    def test_construction(self):
        """Exception constructs with decision."""
        sweep = _make_sweep_result()
        risk_tier = _make_risk_tier_result()
        chokepoint = _make_chokepoint_result()

        decision = RuntimeLaneDecisionWithSweep(
            sweep=sweep,
            risk_tier=risk_tier,
            chokepoint=chokepoint,
            handoff=None,
            final_action="reject",
        )

        exc = RuntimeLaneRejected(decision)

        assert exc.decision is decision
        assert "RuntimeLaneRejected" in str(exc)
        assert "reject" in str(exc)


class TestEvaluateRuntimeLaneWithSweep:
    """Tests for evaluate_runtime_lane_with_sweep function."""

    def test_import_clean(self):
        """Module imports without errors."""
        from agentic_core.L5_safety.identity import runtime_entry_sweep

        assert runtime_entry_sweep is not None

    def test_all_exports_present(self):
        """__all__ exports the expected symbols."""
        from agentic_core.L5_safety.identity.runtime_entry_sweep import __all__

        assert set(__all__) == {
            "RuntimeLaneDecisionWithSweep",
            "RuntimeLaneRejected",
            "evaluate_runtime_lane_with_sweep",
        }

    def test_minimal_allow_path(self, monkeypatch):
        """Happy path: all checks pass, final_action=allow."""
        token = _make_token()

        # Mock the four dependent functions
        def mock_sweep(**kwargs):
            return _make_sweep_result(
                verification_status=VerificationStatus.PASS,
                registry_match=True,
                data_authority_all_match=True,
            )

        def mock_risk_tier(**kwargs):
            return _make_risk_tier_result()

        def mock_chokepoint(**kwargs):
            return _make_chokepoint_result(final_action="allow")

        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_pre_l5_sweep",
            mock_sweep,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.select_runtime_band",
            mock_risk_tier,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_chokepoint_v4",
            mock_chokepoint,
        )

        decision = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="read",
        )

        assert decision.final_action == "allow"
        assert decision.handoff is None

    def test_verification_fail_triggers_reject(self, monkeypatch):
        """Verification status FAIL causes final_action=reject."""
        token = _make_token()

        def mock_sweep(**kwargs):
            return _make_sweep_result(
                verification_status=VerificationStatus.FAIL,
                registry_match=True,
                data_authority_all_match=True,
            )

        def mock_risk_tier(**kwargs):
            return _make_risk_tier_result()

        def mock_chokepoint(**kwargs):
            return _make_chokepoint_result(final_action="allow")

        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_pre_l5_sweep",
            mock_sweep,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.select_runtime_band",
            mock_risk_tier,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_chokepoint_v4",
            mock_chokepoint,
        )

        decision = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="read",
        )

        assert decision.final_action == "reject"

    def test_registry_drift_triggers_step_up(self, monkeypatch):
        """Registry drift causes final_action=step_up."""
        token = _make_token()

        def mock_sweep(**kwargs):
            return _make_sweep_result(
                verification_status=VerificationStatus.PASS,
                registry_match=False,
                data_authority_all_match=True,
            )

        def mock_risk_tier(**kwargs):
            return _make_risk_tier_result()

        def mock_chokepoint(**kwargs):
            return _make_chokepoint_result(final_action="allow")

        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_pre_l5_sweep",
            mock_sweep,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.select_runtime_band",
            mock_risk_tier,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_chokepoint_v4",
            mock_chokepoint,
        )

        decision = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="read",
        )

        assert decision.final_action == "step_up"

    def test_data_authority_drift_triggers_step_up(self, monkeypatch):
        """Data-authority drift causes final_action=step_up."""
        token = _make_token()

        def mock_sweep(**kwargs):
            return _make_sweep_result(
                verification_status=VerificationStatus.PASS,
                registry_match=True,
                data_authority_all_match=False,
            )

        def mock_risk_tier(**kwargs):
            return _make_risk_tier_result()

        def mock_chokepoint(**kwargs):
            return _make_chokepoint_result(final_action="allow")

        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_pre_l5_sweep",
            mock_sweep,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.select_runtime_band",
            mock_risk_tier,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_chokepoint_v4",
            mock_chokepoint,
        )

        decision = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="read",
        )

        assert decision.final_action == "step_up"

    def test_chokepoint_reject_triggers_reject(self, monkeypatch):
        """Chokepoint reject causes final_action=reject."""
        token = _make_token()

        def mock_sweep(**kwargs):
            return _make_sweep_result(
                verification_status=VerificationStatus.PASS,
                registry_match=True,
                data_authority_all_match=True,
            )

        def mock_risk_tier(**kwargs):
            return _make_risk_tier_result()

        def mock_chokepoint(**kwargs):
            return _make_chokepoint_result(final_action="reject")

        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_pre_l5_sweep",
            mock_sweep,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.select_runtime_band",
            mock_risk_tier,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_chokepoint_v4",
            mock_chokepoint,
        )

        decision = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="read",
        )

        assert decision.final_action == "reject"

    def test_handoff_block_triggers_reject(self, monkeypatch):
        """Handoff block causes final_action=reject."""
        token = _make_token()
        handoff_target = AgentRegistryRecord(
            agent_id="agent-1",
            allowed_scope_ceiling=("default",),
        )

        def mock_sweep(**kwargs):
            return _make_sweep_result(
                verification_status=VerificationStatus.PASS,
                registry_match=True,
                data_authority_all_match=True,
            )

        def mock_risk_tier(**kwargs):
            return _make_risk_tier_result()

        def mock_chokepoint(**kwargs):
            return _make_chokepoint_result(final_action="allow")

        def mock_handoff(**kwargs):
            return _make_handoff_result(allow=False)

        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_pre_l5_sweep",
            mock_sweep,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.select_runtime_band",
            mock_risk_tier,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_chokepoint_v4",
            mock_chokepoint,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.validate_handoff",
            mock_handoff,
        )

        decision = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="read",
            handoff_target=handoff_target,
        )

        assert decision.final_action == "reject"
        assert decision.handoff is not None

    def test_most_restrictive_wins(self, monkeypatch):
        """When multiple checks fail, most restrictive action wins."""
        token = _make_token()

        def mock_sweep(**kwargs):
            return _make_sweep_result(
                verification_status=VerificationStatus.FAIL,  # reject
                registry_match=False,  # step_up
                data_authority_all_match=False,  # step_up
            )

        def mock_risk_tier(**kwargs):
            return _make_risk_tier_result()

        def mock_chokepoint(**kwargs):
            return _make_chokepoint_result(final_action="remediate")  # remediate

        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_pre_l5_sweep",
            mock_sweep,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.select_runtime_band",
            mock_risk_tier,
        )
        monkeypatch.setattr(
            "agentic_core.L5_safety.identity.runtime_entry_sweep.run_chokepoint_v4",
            mock_chokepoint,
        )

        decision = evaluate_runtime_lane_with_sweep(
            token=token,
            action_required_rung="read",
        )

        # reject (3) > step_up (2) > remediate (1) > allow (0)
        assert decision.final_action == "reject"
