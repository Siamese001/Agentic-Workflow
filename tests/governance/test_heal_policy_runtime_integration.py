"""
Governance test: Heal policy runtime integration contract.

Proves that decide_reasoning_tier() is invoked inside standard_heal wrapper
and the decision is logged, without changing execution behavior.

Phase 3 acceptance test.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from unittest.mock import patch

import pytest

from agentic_core.L5_safety.types.heal_policy_types import (
    HealEscalationDecision,
    ReasoningTier,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_authorize_and_execute("p2", "test_heal_policy_runtime_integration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_heal_policy_runtime_integration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_heal_policy_runtime_integration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_heal_policy_runtime_integration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_heal_policy_runtime_integration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_heal_policy_runtime_integration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_heal_policy_runtime_integration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_heal_policy_runtime_integration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_heal_policy_runtime_integration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_heal_policy_runtime_integration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_heal_policy_runtime_integration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_heal_policy_runtime_integration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_heal_policy_runtime_integration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_heal_policy_runtime_integration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_heal_policy_runtime_integration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_heal_policy_runtime_integration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_heal_policy_runtime_integration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_heal_policy_runtime_integration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_heal_policy_runtime_integration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_heal_policy_runtime_integration", "exec_snapshot_link")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
)
from agentic_core.utils.decorators_compat_util import standard_heal

# REMOVED: _emit_emits_metric_event("test_heal_policy_runtime_integration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_heal_policy_runtime_integration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_heal_policy_runtime_integration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_heal_policy_runtime_integration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_heal_policy_runtime_integration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_heal_policy_runtime_integration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_heal_policy_runtime_integration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_heal_policy_runtime_integration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_heal_policy_runtime_integration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_heal_policy_runtime_integration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_heal_policy_runtime_integration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_heal_policy_runtime_integration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_heal_policy_runtime_integration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_heal_policy_runtime_integration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_heal_policy_runtime_integration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_heal_policy_runtime_integration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_heal_policy_runtime_integration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_heal_policy_runtime_integration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_heal_policy_runtime_integration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_heal_policy_runtime_integration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_heal_policy_runtime_integration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_heal_policy_runtime_integration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_heal_policy_runtime_integration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_heal_policy_runtime_integration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_heal_policy_runtime_integration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_heal_policy_runtime_integration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_heal_policy_runtime_integration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_heal_policy_runtime_integration", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_heal_policy_runtime_integration")
# REMOVED: _emit_applies_guardrail("p0", "test_heal_policy_runtime_integration", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_heal_policy_runtime_integration", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_heal_policy_runtime_integration", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_heal_policy_runtime_integration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_heal_policy_runtime_integration", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_heal_policy_runtime_integration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_heal_policy_runtime_integration", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_heal_policy_runtime_integration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_heal_policy_runtime_integration", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_heal_policy_runtime_integration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_heal_policy_runtime_integration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_heal_policy_runtime_integration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_heal_policy_runtime_integration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_heal_policy_runtime_integration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_heal_policy_runtime_integration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_heal_policy_runtime_integration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_heal_policy_runtime_integration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_heal_policy_runtime_integration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_heal_policy_runtime_integration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_heal_policy_runtime_integration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_heal_policy_runtime_integration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_heal_policy_runtime_integration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_heal_policy_runtime_integration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_heal_policy_runtime_integration")
# REMOVED: _emit_gated_by_confidence("p1", "test_heal_policy_runtime_integration", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_heal_policy_runtime_integration")
# REMOVED: emit_determinism_digest("p0", "test_heal_policy_runtime_integration")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

pytestmark = pytest.mark.governance


@dataclass
class DummyHealer:
    """Minimal healer class for testing standard_heal decorator."""

    name: str = "DummyHealer"

    @standard_heal
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        _call_path: set[str] | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Minimal heal_repository that returns a simple dict."""
        return {
            "violations_found": 2,
            "violations_fixed": 1,
            "status": "PASS",
        }


class TestHealPolicyRuntimeIntegration:
    """Prove policy decision is computed and logged without behavior change."""

    def test_decide_reasoning_tier_is_invoked(self) -> None:
        """Assert decide_reasoning_tier() is called exactly once per wrapper invocation."""
        mock_decision = HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Test rationale",
            threshold_used="TEST",
        )

        with patch(
            "agentic_core.utils.decorators_util.decide_heal_escalation",
            return_value=mock_decision,
        ) as mock_decide:
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

            mock_decide.assert_called_once()

    def test_policy_decision_is_logged(self) -> None:
        """Assert Logger.debug receives the policy decision log line."""
        mock_decision = HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Test rationale",
            threshold_used="TEST",
        )

        captured_messages: list[str] = []

        def capture_debug(msg: str, *args: Any, **kwargs: Any) -> None:
            captured_messages.append(msg)

        with (
            patch(
                "agentic_core.utils.decorators_util.decide_heal_escalation",
                return_value=mock_decision,
            ),
            patch(
                "agentic_core.utils.decorators_util.Logger.debug",
                side_effect=capture_debug,
            ),
        ):
            healer = DummyHealer()
            healer.heal_repository(dry_run=True)

        policy_logs = [m for m in captured_messages if "[heal_policy]" in m]
        assert len(policy_logs) == 1, f"Expected exactly one policy log, got: {policy_logs}"
        assert "tier=LOW" in policy_logs[0]
        assert "threshold=TEST" in policy_logs[0]

    def test_output_unchanged_by_policy_integration(self) -> None:
        """Assert returned normalized dict matches baseline behavior."""
        mock_decision = HealEscalationDecision(
            proceed=True,
            tier=ReasoningTier.LOW,
            rationale="Test rationale",
            threshold_used="TEST",
        )

        with patch(
            "agentic_core.utils.decorators_util.decide_heal_escalation",
            return_value=mock_decision,
        ):
            healer = DummyHealer()
            result = healer.heal_repository(dry_run=True)

        assert isinstance(result, dict)
        assert "status" in result
        assert "violations_found" in result
        assert "violations_fixed" in result
        assert result["violations_found"] == 2
        assert result["violations_fixed"] == 1
        assert result["status"] == "PASS"
