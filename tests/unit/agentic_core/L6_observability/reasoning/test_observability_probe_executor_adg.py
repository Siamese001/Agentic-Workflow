"""ADG-driven tests for agentic_core/L6_observability/reasoning/observability_probe_executor.py — fan_in=2.

Contract tests: ObservabilityProbeExecutorAgent init, probe dispatch, execute.
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_observability_probe_executor_adg")
_emit_applies_guardrail("p0", "test_observability_probe_executor_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_observability_probe_executor_adg", "policy_binding")
_emit_snapshots_state("p0", "test_observability_probe_executor_adg", "state_snapshot")
emit_replay_key("p0", "test_observability_probe_executor_adg")
emit_determinism_digest("p0", "test_observability_probe_executor_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_observability_probe_executor_adg", "execution_auth")
_emit_validates_capability("p2", "test_observability_probe_executor_adg", "capability_check")
_emit_routes_to_capability("p2", "test_observability_probe_executor_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_observability_probe_executor_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_observability_probe_executor_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_observability_probe_executor_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_observability_probe_executor_adg", "exec_output")
_emit_dispatches_agent("p3", "test_observability_probe_executor_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_observability_probe_executor_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_observability_probe_executor_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_observability_probe_executor_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_observability_probe_executor_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_observability_probe_executor_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_observability_probe_executor_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_observability_probe_executor_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_observability_probe_executor_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_observability_probe_executor_adg", "eval_metric")
_emit_stores_embedding("p4", "test_observability_probe_executor_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_observability_probe_executor_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_observability_probe_executor_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.L6_observability.reasoning.observability_probe_executor import (
    ObservabilityProbeExecutorAgent,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("test_observability_probe_executor_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_observability_probe_executor_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_observability_probe_executor_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_observability_probe_executor_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_observability_probe_executor_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_observability_probe_executor_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_observability_probe_executor_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_observability_probe_executor_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_observability_probe_executor_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_observability_probe_executor_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_observability_probe_executor_adg", "p4obs", "alert")
_emit_links_incident_trace("test_observability_probe_executor_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_observability_probe_executor_adg", "p3lm", "pattern")
_emit_records_learning_event("test_observability_probe_executor_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_observability_probe_executor_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_observability_probe_executor_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_observability_probe_executor_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_observability_probe_executor_adg", "p3lm", "policy")
_emit_stores_learning_state("test_observability_probe_executor_adg", "p3lm", "state")
_emit_records_execution_trace("test_observability_probe_executor_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_observability_probe_executor_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_observability_probe_executor_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_observability_probe_executor_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_observability_probe_executor_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_observability_probe_executor_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_observability_probe_executor_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_observability_probe_executor_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_observability_probe_executor_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_observability_probe_executor_adg", "context_pull")
_emit_pulls_context("p1", "test_observability_probe_executor_adg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_observability_probe_executor_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_observability_probe_executor_adg", "uwg_term_2")
_emit_writes_through("p1", "test_observability_probe_executor_adg", "write_through")
_emit_writes_through("p1", "test_observability_probe_executor_adg", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_observability_probe_executor_adg", "safety_validation")
_emit_invokes_eval("p1", "test_observability_probe_executor_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_observability_probe_executor_adg", "routing_commit")


class TestObservabilityProbeExecutorAgentInit:
    def test_creates_with_defaults(self):
        agent = ObservabilityProbeExecutorAgent()
        assert agent is not None

    def test_probe_type_default_generic(self):
        agent = ObservabilityProbeExecutorAgent()
        assert agent.probe_type == "generic"

    def test_probe_type_custom(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
        assert agent.probe_type == "cost_tracker"

    def test_results_start_empty(self):
        agent = ObservabilityProbeExecutorAgent()
        assert agent._results == {}

    def test_project_root_is_path(self):
        from pathlib import Path
        agent = ObservabilityProbeExecutorAgent()
        assert isinstance(agent.project_root, Path)


class TestObservabilityProbeExecutorAgentExecute:
    def test_execute_generic_returns_dict(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="generic")
        result = agent.execute()
        assert isinstance(result, dict)

    def test_execute_cost_tracker(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
        result = agent.execute({"cost_metrics": {"tokens": 100}})
        assert result.get("probe") == "cost_tracker"

    def test_execute_coordinator(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="coordinator")
        result = agent.execute()
        assert result.get("probe") == "coordinator"

    def test_execute_strategic(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="strategic")
        result = agent.execute()
        assert result.get("probe") == "strategic"

    def test_execute_deadlock(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="deadlock")
        result = agent.execute()
        assert result.get("probe") == "deadlock"

    def test_execute_debate(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="debate")
        result = agent.execute()
        assert result.get("probe") == "debate"

    def test_execute_runtime_telemetry(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="runtime_telemetry")
        result = agent.execute()
        assert result.get("probe") == "runtime_telemetry"

    def test_execute_with_context(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="cost_tracker")
        result = agent.execute({"cost_metrics": {"tokens": 500}})
        assert result["metrics"].get("tokens") == 500

    def test_execute_unknown_probe_returns_empty(self):
        agent = ObservabilityProbeExecutorAgent(probe_type="unknown_xyz")
        result = agent.execute()
        assert isinstance(result, dict)
