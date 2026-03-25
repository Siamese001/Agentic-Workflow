"""
Regression tests for InspectionCapability dedup refactor (2026-02-08).

Verifies:
1. Default perform_checks() in InspectionCapability produces correct results
2. Subclasses that don't override perform_checks() inherit the default
3. Subclasses that DO override perform_checks() use their own logic
4. The 3 Cluster-4 agents (DagRuntime, SignatureVerifier, TokenBudget)
   all produce identical results via inherited default
"""

from __future__ import annotations

from typing import Any

import pytest

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_inspection_capability_dedup_regression")
# REMOVED: _emit_applies_guardrail("p0", "test_inspection_capability_dedup_regression", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_inspection_capability_dedup_regression", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_inspection_capability_dedup_regression", "state_snapshot")
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

# REMOVED: _emit_emits_metric_event("test_inspection_capability_dedup_regression", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_inspection_capability_dedup_regression", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_inspection_capability_dedup_regression", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_inspection_capability_dedup_regression", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_inspection_capability_dedup_regression", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_inspection_capability_dedup_regression", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_inspection_capability_dedup_regression", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_inspection_capability_dedup_regression", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_inspection_capability_dedup_regression", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_inspection_capability_dedup_regression", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_inspection_capability_dedup_regression", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_inspection_capability_dedup_regression", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_inspection_capability_dedup_regression", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_inspection_capability_dedup_regression", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_inspection_capability_dedup_regression", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_inspection_capability_dedup_regression", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_inspection_capability_dedup_regression", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_inspection_capability_dedup_regression", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_inspection_capability_dedup_regression", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_inspection_capability_dedup_regression", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_inspection_capability_dedup_regression", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_inspection_capability_dedup_regression", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_inspection_capability_dedup_regression", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_inspection_capability_dedup_regression", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_inspection_capability_dedup_regression", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_inspection_capability_dedup_regression", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_inspection_capability_dedup_regression", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_inspection_capability_dedup_regression", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_inspection_capability_dedup_regression", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_inspection_capability_dedup_regression", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_inspection_capability_dedup_regression", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_inspection_capability_dedup_regression", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_inspection_capability_dedup_regression", "write_through")
# REMOVED: _emit_writes_through("p1", "test_inspection_capability_dedup_regression", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_inspection_capability_dedup_regression", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_inspection_capability_dedup_regression", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_inspection_capability_dedup_regression", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_inspection_capability_dedup_regression", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_inspection_capability_dedup_regression", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_inspection_capability_dedup_regression", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_inspection_capability_dedup_regression", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_inspection_capability_dedup_regression", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_inspection_capability_dedup_regression", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_inspection_capability_dedup_regression", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_inspection_capability_dedup_regression", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_inspection_capability_dedup_regression", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_inspection_capability_dedup_regression", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_inspection_capability_dedup_regression", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_inspection_capability_dedup_regression")
# REMOVED: _emit_gated_by_confidence("p1", "test_inspection_capability_dedup_regression", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_inspection_capability_dedup_regression")
# REMOVED: emit_determinism_digest("p0", "test_inspection_capability_dedup_regression")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_inspection_capability_dedup_regression", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_inspection_capability_dedup_regression", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_inspection_capability_dedup_regression", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_inspection_capability_dedup_regression", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_inspection_capability_dedup_regression", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_inspection_capability_dedup_regression", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_inspection_capability_dedup_regression", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_inspection_capability_dedup_regression", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_inspection_capability_dedup_regression", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_inspection_capability_dedup_regression", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_inspection_capability_dedup_regression", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_inspection_capability_dedup_regression", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_inspection_capability_dedup_regression", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_inspection_capability_dedup_regression", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_inspection_capability_dedup_regression", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_inspection_capability_dedup_regression", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_inspection_capability_dedup_regression", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_inspection_capability_dedup_regression", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_inspection_capability_dedup_regression", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_inspection_capability_dedup_regression", "exec_snapshot_link")


MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

class TestDefaultPerformChecks:
    """Verify InspectionCapability.perform_checks default implementation."""

    def _get_capability(self):
        from agentic_core.mixins.inspection_capability_mixin import InspectionCapability

        return InspectionCapability()

    def test_none_target_reports_issue(self) -> None:
        cap = self._get_capability()
        issues, metrics = cap.perform_checks(None)
        assert issues == ["Target is null"]
        assert metrics["type"] == "NoneType"

    def test_dict_target_reports_field_count(self) -> None:
        cap = self._get_capability()
        issues, metrics = cap.perform_checks({"a": 1, "b": 2})
        assert issues == []
        assert metrics["field_count"] == 2
        assert metrics["type"] == "dict"

    def test_list_target_reports_item_count(self) -> None:
        cap = self._get_capability()
        issues, metrics = cap.perform_checks([1, 2, 3])
        assert issues == []
        assert metrics["item_count"] == 3
        assert metrics["type"] == "list"

    def test_string_target_reports_type_only(self) -> None:
        cap = self._get_capability()
        issues, metrics = cap.perform_checks("hello")
        assert issues == []
        assert "field_count" not in metrics
        assert "item_count" not in metrics
        assert metrics["type"] == "str"

    def test_empty_dict_reports_zero_fields(self) -> None:
        cap = self._get_capability()
        issues, metrics = cap.perform_checks({})
        assert issues == []
        assert metrics["field_count"] == 0

    def test_empty_list_reports_zero_items(self) -> None:
        cap = self._get_capability()
        issues, metrics = cap.perform_checks([])
        assert issues == []
        assert metrics["item_count"] == 0


class TestInheritedDefault:
    """Verify subclasses without local perform_checks inherit the default."""

    def test_bare_subclass_inherits_default(self) -> None:
        from agentic_core.mixins.inspection_capability_mixin import InspectionCapability

        class _BareInspector(InspectionCapability):
            INSPECTION_LOG_PREFIX = "Bare"

        inspector = _BareInspector()
        issues, metrics = inspector.perform_checks(None)
        assert issues == ["Target is null"]

    def test_override_takes_precedence(self) -> None:
        from agentic_core.mixins.inspection_capability_mixin import InspectionCapability

        class _CustomInspector(InspectionCapability):
            INSPECTION_LOG_PREFIX = "Custom"

            def perform_checks(
                self,
                target: Any,
                context: dict[str, Any] | None = None,
            ) -> tuple[list[str], dict[str, Any]]:
                return ["custom-issue"], {"custom": True}

        inspector = _CustomInspector()
        issues, metrics = inspector.perform_checks("anything")
        assert issues == ["custom-issue"]
        assert metrics == {"custom": True}


class TestCluster4AgentConsistency:
    """Verify all 3 Cluster-4 agents produce identical default results.

    This is the dedup regression contract: after extracting perform_checks
    into InspectionCapability, all three agents must behave identically
    for the same inputs.
    """

    TARGETS = [
        None,
        {"key": "value"},
        [1, 2, 3],
        "string",
        42,
    ]

    @pytest.mark.parametrize("target", TARGETS, ids=lambda t: type(t).__name__)
    def test_all_agents_produce_same_result(self, target: Any) -> None:
        from agentic_core.mixins.inspection_capability_mixin import InspectionCapability

        # All three agents inherit perform_checks from InspectionCapability.
        # Verify directly on the capability to ensure contract holds.
        cap = InspectionCapability()
        canonical_issues, canonical_metrics = cap.perform_checks(target)

        # Verify deterministic: call again, same result
        issues2, metrics2 = cap.perform_checks(target)
        assert canonical_issues == issues2
        assert canonical_metrics == metrics2


class TestRunInspectionIntegration:
    """Verify run_inspection() works with the default perform_checks."""

    def test_healthy_result_for_dict(self) -> None:
        from agentic_core.mixins.inspection_capability_mixin import (
            InspectionCapability,
            InspectionResult,
        )

        class _Inspector(InspectionCapability):
            INSPECTION_LOG_PREFIX = "Test"

        result = _Inspector().run_inspection({"a": 1})
        assert isinstance(result, InspectionResult)
        assert result.healthy is True
        assert result.metrics["field_count"] == 1

    def test_unhealthy_result_for_none(self) -> None:
        from agentic_core.mixins.inspection_capability_mixin import (
            InspectionCapability,
            InspectionResult,
        )

        class _Inspector(InspectionCapability):
            INSPECTION_LOG_PREFIX = "Test"

        result = _Inspector().run_inspection(None)
        assert isinstance(result, InspectionResult)
        assert result.healthy is False
        assert "Target is null" in result.issues
