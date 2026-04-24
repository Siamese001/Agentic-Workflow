"""Integration tests for the §5 orchestrator and flywheel promoter."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from agentic_core.L5_safety.eval_spine import exit_decision
from agentic_core.L5_safety.eval_spine.budget_envelope import BudgetEnvelope
from agentic_core.L5_safety.eval_spine.exit_eval import (
    ExitEvalPolicy,
    SealedArtifact,
    evaluate_exit,
)
from agentic_core.L5_safety.eval_spine.kill_switch import KillSwitchStore
from agentic_core.L6_observability import flywheel_promoter


@pytest.fixture
def generous_env() -> BudgetEnvelope:
    return BudgetEnvelope(
        tokens_max=10_000,
        latency_ms_max=60_000,
        tool_calls_max=32,
        cost_usd_max=5.0,
    )


class TestEvaluateExit:
    def test_happy_path_allows_finish(self, generous_env):
        art = SealedArtifact(
            request_id="r1",
            trace_id="t1",
            answer_text="The agent returned 42.",
            latency_ms=100,
            tokens_consumed=50,
            predicted_tool_calls=[{"tool": "calc", "args_hash": "h"}],
        )
        policy = ExitEvalPolicy(policy_snapshot="sha-1")
        result = evaluate_exit(art, generous_env, policy)
        assert result.exit_decision.disposition == "allow_finish"
        assert result.exit_decision.quality.verdict == "pass"
        assert result.escalation_packet is None
        assert result.exit_decision.safety.policy_halt is False

    def test_safety_violation_routes_escalate(self, generous_env):
        art = SealedArtifact(
            request_id="r2", trace_id="t2", answer_text=".", latency_ms=1, tokens_consumed=1
        )
        policy = ExitEvalPolicy(
            policy_snapshot="sha-1", policy_hits=("pii_leak",)
        )
        result = evaluate_exit(art, generous_env, policy)
        assert result.exit_decision.disposition == "escalate_hitl"
        assert result.exit_decision.safety.policy_violation is True
        assert result.escalation_packet is not None
        assert result.escalation_packet.hitl_class == "safety"

    def test_budget_breach_routes_escalate(self):
        art = SealedArtifact(
            request_id="r3",
            trace_id="t3",
            answer_text=".",
            latency_ms=10_000,
            tokens_consumed=2_000,
        )
        tight = BudgetEnvelope(
            tokens_max=100, latency_ms_max=1000, tool_calls_max=1, cost_usd_max=0.1
        )
        policy = ExitEvalPolicy(policy_snapshot="sha-1")
        result = evaluate_exit(art, tight, policy)
        assert result.exit_decision.budget.budget_fit is False
        assert result.exit_decision.disposition == "escalate_hitl"
        assert result.exit_decision.reason_code == "grader.budget_breach"

    def test_budget_breach_with_deny_policy(self):
        art = SealedArtifact(
            request_id="r3a",
            trace_id="t3a",
            answer_text=".",
            latency_ms=10_000,
            tokens_consumed=2_000,
        )
        tight = BudgetEnvelope(
            tokens_max=100, latency_ms_max=1000, tool_calls_max=1, cost_usd_max=0.1
        )
        policy = ExitEvalPolicy(
            policy_snapshot="sha-1", budget_deny_reroute_on_breach=True
        )
        result = evaluate_exit(art, tight, policy)
        assert result.exit_decision.disposition == "deny_reroute"

    def test_kill_switch_hit_denies(self, generous_env):
        store = KillSwitchStore()
        store.activate(scope="tenant:acme", reason="abuse", operator="ops")
        art = SealedArtifact(
            request_id="r4",
            trace_id="t4",
            tenant="acme",
            latency_ms=10,
            tokens_consumed=10,
        )
        policy = ExitEvalPolicy(policy_snapshot="sha-1")
        result = evaluate_exit(art, generous_env, policy, kill_switch_store=store)
        assert result.exit_decision.safety.policy_halt is True
        assert result.exit_decision.disposition == "deny_reroute"
        assert result.exit_decision.reason_code == "grader.policy_halt"
        assert result.exit_decision.safety.severity_band == "critical"

    def test_trajectory_metrics_populated_with_reference(self, generous_env):
        ref = [
            {"tool": "search", "args_hash": "h1"},
            {"tool": "summarize", "args_hash": "h2"},
        ]
        art = SealedArtifact(
            request_id="r5",
            trace_id="t5",
            predicted_tool_calls=ref,
            latency_ms=10,
            tokens_consumed=10,
        )
        policy = ExitEvalPolicy(
            policy_snapshot="sha-1", reference_trajectory=ref
        )
        result = evaluate_exit(art, generous_env, policy)
        traj = result.exit_decision.trajectory
        assert traj.exact_match == 1
        assert traj.in_order_match == 1
        assert traj.any_order_match == 1
        assert traj.precision == 1.0
        assert traj.recall == 1.0

    def test_output_contract_unresolved_denies(self, generous_env):
        art = SealedArtifact(
            request_id="r6", trace_id="t6", answer_text="x", latency_ms=10, tokens_consumed=10
        )
        policy = ExitEvalPolicy(
            policy_snapshot="sha-1", output_contract_ref="definitely_not_registered"
        )
        result = evaluate_exit(art, generous_env, policy)
        assert result.exit_decision.output_contract.required_form_satisfied is False
        assert result.exit_decision.disposition == "deny_reroute"

    def test_instruction_violation_denies(self, generous_env):
        art = SealedArtifact(
            request_id="r7", trace_id="t7", answer_text=".", latency_ms=1, tokens_consumed=1
        )
        policy = ExitEvalPolicy(
            policy_snapshot="sha-1",
            instruction_violations=("ignored_tone", "missed_section"),
        )
        result = evaluate_exit(art, generous_env, policy)
        assert result.exit_decision.safety.instruction_violation is True
        assert result.exit_decision.disposition == "deny_reroute"

    def test_all_results_schema_valid(self, generous_env):
        art = SealedArtifact(
            request_id="r8",
            trace_id="t8",
            answer_text="ok",
            latency_ms=1,
            tokens_consumed=1,
        )
        policy = ExitEvalPolicy(policy_snapshot="sha-1")
        result = evaluate_exit(art, generous_env, policy)
        errors = exit_decision.validate_dict(result.exit_decision.to_dict())
        assert errors == [], errors


class TestFlywheelPromoter:
    def _event(self, **decision_overrides) -> dict:
        decision = {
            "disposition": "allow_finish",
            "reason_code": "grader.ok",
            "quality": {"verdict": "pass"},
            "safety": {"policy_violation": False},
            "trajectory": {"exact_match": 1},
        }
        decision.update(decision_overrides)
        return {
            "event_id": "ev-1",
            "trace_id": "t1",
            "request_id": "r1",
            "exit_decision": decision,
            "replication": {"is_replicate": False},
        }

    def test_clean_event_is_not_a_candidate(self):
        assert flywheel_promoter.analyze(self._event()) is None

    def test_escalation_is_candidate(self):
        event = self._event(disposition="escalate_hitl")
        record = flywheel_promoter.analyze(event)
        assert record is not None
        assert "escalation" in record.candidate_reasons

    def test_safety_violation_routes_to_safety_dataset(self):
        event = self._event(
            disposition="escalate_hitl",
            safety={"policy_violation": True},
        )
        record = flywheel_promoter.analyze(event)
        assert record is not None
        assert record.target_dataset.endswith("safety")

    def test_trajectory_regression_routes_to_trajectory(self):
        event = self._event(trajectory={"exact_match": 0})
        record = flywheel_promoter.analyze(event)
        assert record is not None
        assert record.target_dataset.endswith("trajectory")

    def test_non_determinism_hotspot(self):
        event = self._event()
        event["replication"] = {"is_replicate": True, "pass_rate_0_1": 0.5}
        record = flywheel_promoter.analyze(event)
        assert record is not None
        assert "non_determinism_hotspot" in record.candidate_reasons

    def test_stage_to_disk(self, tmp_path: Path):
        event = self._event(disposition="escalate_hitl")
        record = flywheel_promoter.promote_candidate(
            event, triage_root=tmp_path, stage_to_disk=True
        )
        assert record is not None
        written = list(tmp_path.glob("*.json"))
        assert len(written) == 1
        payload = json.loads(written[0].read_text(encoding="utf-8"))
        assert payload["event_id"] == "ev-1"
