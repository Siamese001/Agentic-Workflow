"""Tests for the eval_spine enforcement bridge (plan `-d5e8b3` §Q4).

Covers:
- Env-flag gating (EVAL_SPINE_ENFORCE).
- Disposition translation (eval_spine string -> ExitDisposition enum).
- Upgrade-only semantics (never loosens).
- policy_halt forces ESCALATE_TO_HITL.
- Integration with ExitControlGate.evaluate_sealed.
"""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.types.sealed_l2_artifact import (
    SealedL2Artifact,
    ValidationCounters,
)
from agentic_core.L5_safety.eval_spine import enforcement_bridge, shadow_observer
from agentic_core.L5_safety.eval_spine.exit_decision import (
    BudgetReport,
    ExitDecision,
    FinalResponseMetrics,
    OutputContractReport,
    QualityVerdict,
    SafetyFlags,
    TrajectoryMetrics,
)
from agentic_core.L5_safety.types.exit_disposition_types import ExitDisposition


@pytest.fixture(autouse=True)
def _clear_enforce_flag(monkeypatch):
    monkeypatch.delenv("EVAL_SPINE_ENFORCE", raising=False)
    monkeypatch.delenv("EVAL_SPINE_SHADOW", raising=False)


def _make_decision(
    *,
    disposition: str = "allow_finish",
    policy_halt: bool = False,
    reason_code: str = "grader.ok",
) -> ExitDecision:
    return ExitDecision(
        request_id="r",
        trace_id="t",
        emitted_at_utc="2026-04-23T00:00:00Z",
        disposition=disposition,  # type: ignore[arg-type]
        reason_code=reason_code,
        final_response=FinalResponseMetrics(),
        trajectory=TrajectoryMetrics(failure=False, latency_ms=1, tool_call_count=0),
        safety=SafetyFlags(policy_halt=policy_halt),
        budget=BudgetReport(budget_fit=True),
        quality=QualityVerdict(verdict="pass"),
        output_contract=OutputContractReport(required_form_satisfied=True),
        policy_snapshot="sha-x",
    )


class TestIsEnforceEnabled:
    def test_unset(self):
        assert enforcement_bridge.is_enforce_enabled() is False

    @pytest.mark.parametrize("value", ["1", "true", "yes", "on", "TRUE"])
    def test_truthy(self, monkeypatch, value):
        monkeypatch.setenv("EVAL_SPINE_ENFORCE", value)
        assert enforcement_bridge.is_enforce_enabled() is True

    @pytest.mark.parametrize("value", ["0", "false", "no", "off", ""])
    def test_falsy(self, monkeypatch, value):
        monkeypatch.setenv("EVAL_SPINE_ENFORCE", value)
        assert enforcement_bridge.is_enforce_enabled() is False


class TestTranslation:
    @pytest.mark.parametrize(
        "eval_spine_str,expected",
        [
            ("allow_finish", ExitDisposition.ALLOW_RESPONSE),
            ("commit_request", ExitDisposition.COMMIT_TO_UWG),
            ("deny_reroute", ExitDisposition.DENY_RETURN),
            ("escalate_hitl", ExitDisposition.ESCALATE_TO_HITL),
        ],
    )
    def test_known_values(self, eval_spine_str, expected):
        assert enforcement_bridge.eval_spine_to_legacy(eval_spine_str) == expected

    def test_unknown_returns_none(self):
        assert enforcement_bridge.eval_spine_to_legacy("garbage") is None


class TestMergeDisposition:
    def test_no_upgrade_when_both_allow(self):
        decision = _make_decision(disposition="allow_finish")
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.ALLOW_RESPONSE, decision)
        assert final == ExitDisposition.ALLOW_RESPONSE
        assert reason is None

    def test_upgrade_allow_to_deny(self):
        decision = _make_decision(disposition="deny_reroute", reason_code="grader.quality_fail")
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.ALLOW_RESPONSE, decision)
        assert final == ExitDisposition.DENY_RETURN
        assert reason is not None
        assert "deny_reroute" in reason

    def test_upgrade_allow_to_escalate(self):
        decision = _make_decision(disposition="escalate_hitl", reason_code="grader.safety_violation")
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.ALLOW_RESPONSE, decision)
        assert final == ExitDisposition.ESCALATE_TO_HITL
        assert reason is not None

    def test_upgrade_deny_to_escalate(self):
        decision = _make_decision(disposition="escalate_hitl")
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.DENY_RETURN, decision)
        assert final == ExitDisposition.ESCALATE_TO_HITL
        assert reason is not None

    def test_never_downgrade_escalate_to_allow(self):
        decision = _make_decision(disposition="allow_finish")
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.ESCALATE_TO_HITL, decision)
        assert final == ExitDisposition.ESCALATE_TO_HITL
        assert reason is None

    def test_never_downgrade_deny_to_allow(self):
        decision = _make_decision(disposition="allow_finish")
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.DENY_RETURN, decision)
        assert final == ExitDisposition.DENY_RETURN
        assert reason is None

    def test_policy_halt_forces_escalate(self):
        decision = _make_decision(
            disposition="allow_finish", policy_halt=True, reason_code="grader.policy_halt"
        )
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.ALLOW_RESPONSE, decision)
        assert final == ExitDisposition.ESCALATE_TO_HITL
        assert reason is not None
        assert "policy_halt" in reason

    def test_policy_halt_noop_when_already_escalate(self):
        decision = _make_decision(disposition="escalate_hitl", policy_halt=True)
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.ESCALATE_TO_HITL, decision)
        assert final == ExitDisposition.ESCALATE_TO_HITL
        assert reason is None

    def test_unknown_disposition_keeps_legacy(self):
        decision = _make_decision(disposition="garbage")
        final, reason = enforcement_bridge.merge_disposition(ExitDisposition.ALLOW_RESPONSE, decision)
        assert final == ExitDisposition.ALLOW_RESPONSE
        assert reason is None


class TestExitControlGateEnforceIntegration:
    """Full-stack: flag on + sealed artifact -> ExitControlGate disposition."""

    def _gate(self):
        from agentic_core.L5_safety.enforcement.exit_control_gate import (
            ExitControlGate,
        )

        return ExitControlGate(policy_hash="sha-enforce-test")

    def _artifact(self, trace_id: str = "enforce-trace") -> SealedL2Artifact:
        return SealedL2Artifact(
            artifact_id="enforce-1",
            trace_id=trace_id,
            validation_counters=ValidationCounters(),
        )

    def test_flag_off_no_change(self, monkeypatch):
        # Sanity: no flag, disposition is whatever legacy produces.
        result = self._gate().evaluate_sealed(self._artifact())
        assert isinstance(result.disposition, ExitDisposition)
        legacy_off = result.disposition

        # With flag off, we should reproduce exactly the same disposition.
        result2 = self._gate().evaluate_sealed(self._artifact("same-artifact-2"))
        assert result2.disposition == legacy_off

    def test_flag_on_never_loosens(self, monkeypatch):
        # Compare disposition with and without the flag; flag may upgrade
        # (stricter) but must never loosen.
        off_result = self._gate().evaluate_sealed(self._artifact("compare-off"))
        monkeypatch.setenv("EVAL_SPINE_ENFORCE", "1")
        on_result = self._gate().evaluate_sealed(self._artifact("compare-on"))
        # Rank: ESCALATE(3) > DENY(2) > ALLOW/COMMIT(0). Flag-on rank must be >=.
        rank = {
            ExitDisposition.ALLOW_RESPONSE: 0,
            ExitDisposition.COMMIT_TO_UWG: 0,
            ExitDisposition.DENY_RETURN: 2,
            ExitDisposition.ESCALATE_TO_HITL: 3,
        }
        assert rank[on_result.disposition] >= rank[off_result.disposition]

    def test_flag_on_does_not_leak_shadow_writes(self, monkeypatch, tmp_path):
        # Enforce flag alone must not write shadow artifacts (distinct flag).
        monkeypatch.setenv("EVAL_SPINE_ENFORCE", "1")
        monkeypatch.setattr(shadow_observer, "_DEFAULT_OUTPUT_ROOT", tmp_path)
        self._gate().evaluate_sealed(self._artifact("no-shadow"))
        assert list(tmp_path.iterdir()) == []
