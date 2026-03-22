import os
from unittest.mock import Mock, patch

import pytest

from agentic_core.L5_safety.reasoning.RedSentinelAgent import RedSentinelAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("test_red_sentinel_agent_agents", "p4obs", "metric_1")
_emit_emits_metric_event("test_red_sentinel_agent_agents", "p4obs", "metric_2")
_emit_emits_metric_event("test_red_sentinel_agent_agents", "p4obs", "metric_3")
_emit_emits_metric_event("test_red_sentinel_agent_agents", "p4obs", "metric_4")
_emit_emits_metric_event("test_red_sentinel_agent_agents", "p4obs", "metric_5")
_emit_emits_metric_event("test_red_sentinel_agent_agents", "p4obs", "metric_6")
_emit_records_incident_event("test_red_sentinel_agent_agents", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_red_sentinel_agent_agents", "p4obs", "anomaly")
_emit_writes_observability_log("test_red_sentinel_agent_agents", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_red_sentinel_agent_agents", "p4obs", "mon_state")
_emit_triggers_alert("test_red_sentinel_agent_agents", "p4obs", "alert")
_emit_links_incident_trace("test_red_sentinel_agent_agents", "p4obs", "trace_link")
_emit_captures_pattern("test_red_sentinel_agent_agents", "p3lm", "pattern")
_emit_records_learning_event("test_red_sentinel_agent_agents", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_red_sentinel_agent_agents", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_red_sentinel_agent_agents", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_red_sentinel_agent_agents", "p3lm", "routing")
_emit_improves_agent_policy("test_red_sentinel_agent_agents", "p3lm", "policy")
_emit_stores_learning_state("test_red_sentinel_agent_agents", "p3lm", "state")
_emit_records_execution_trace("test_red_sentinel_agent_agents", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_red_sentinel_agent_agents", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_red_sentinel_agent_agents", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_red_sentinel_agent_agents", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_red_sentinel_agent_agents", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_red_sentinel_agent_agents", "env_read", "p2_env_1")
_emit_reads_environ("test_red_sentinel_agent_agents", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_red_sentinel_agent_agents", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_red_sentinel_agent_agents", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "test_red_sentinel_agent_agents")
_emit_applies_guardrail("p0", "test_red_sentinel_agent_agents", "p0_governance")
_emit_reads_policy_state("p0", "test_red_sentinel_agent_agents", "policy_binding")
_emit_snapshots_state("p0", "test_red_sentinel_agent_agents", "state_snapshot")
_emit_pulls_context("p1", "test_red_sentinel_agent_agents", "context_pull")
_emit_pulls_context("p1", "test_red_sentinel_agent_agents", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_red_sentinel_agent_agents", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_red_sentinel_agent_agents", "uwg_term_secondary")
_emit_writes_through("p1", "test_red_sentinel_agent_agents", "write_through")
_emit_writes_through("p1", "test_red_sentinel_agent_agents", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_red_sentinel_agent_agents", "safety_validation")
_emit_invokes_eval("p1", "test_red_sentinel_agent_agents", "eval_call")
_emit_proposal_commits_routing("p1", "test_red_sentinel_agent_agents", "routing_commit")
_emit_escalates_to_human("p1", "test_red_sentinel_agent_agents", "human_escalation")
_emit_routes_through("p1", "test_red_sentinel_agent_agents", "route_through")
_emit_checks_agent_registry("p1", "test_red_sentinel_agent_agents", "agent_registry")
_emit_validates_agent_capability("p1", "test_red_sentinel_agent_agents", "capability")
_emit_dispatches_execution_plan("p1", "test_red_sentinel_agent_agents", "exec_plan")
_emit_agent_executes_agent("p1", "test_red_sentinel_agent_agents", "sub_agent")
_emit_routes_to_agent("p1", "test_red_sentinel_agent_agents", "target_agent")
_emit_verifies_policy("p1", "test_red_sentinel_agent_agents", "policy_check")
_emit_observes_runtime_state("p1", "test_red_sentinel_agent_agents", "runtime_state")
_emit_verifies_boundary("p1", "test_red_sentinel_agent_agents", "boundary_check")
_emit_transcripts_response("p1", "test_red_sentinel_agent_agents", "transcript")
_emit_hard_fails_untranscripted("p1", "test_red_sentinel_agent_agents")
_emit_gated_by_confidence("p1", "test_red_sentinel_agent_agents", "confidence_gate")
emit_replay_key("p0", "test_red_sentinel_agent_agents")
emit_determinism_digest("p0", "test_red_sentinel_agent_agents")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_red_sentinel_agent_agents", "execution_auth")
_emit_validates_capability("p2", "test_red_sentinel_agent_agents", "capability_check")
_emit_routes_to_capability("p2", "test_red_sentinel_agent_agents", "capability_route")
_emit_writes_via_uwg("p2", "test_red_sentinel_agent_agents", "uwg_write")
_emit_blocks_direct_write("p2", "test_red_sentinel_agent_agents", "direct_write_block")
_emit_records_tool_invocation("p2", "test_red_sentinel_agent_agents", "tool_invocation")
_emit_captures_execution_output("p2", "test_red_sentinel_agent_agents", "exec_output")
_emit_dispatches_agent("p3", "test_red_sentinel_agent_agents", "agent_dispatch")
_emit_coordinates_agents("p3", "test_red_sentinel_agent_agents", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_red_sentinel_agent_agents", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_red_sentinel_agent_agents", "healing_outcome")
_emit_escalates_failure("p3", "test_red_sentinel_agent_agents", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_red_sentinel_agent_agents", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_red_sentinel_agent_agents", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_red_sentinel_agent_agents", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_red_sentinel_agent_agents", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_red_sentinel_agent_agents", "eval_metric")
_emit_stores_embedding("p4", "test_red_sentinel_agent_agents", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_red_sentinel_agent_agents", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_red_sentinel_agent_agents", "exec_snapshot_link")


@pytest.fixture
def agent():
    return RedSentinelAgent()


@pytest.fixture
def agent_with_client():
    return RedSentinelAgent(llm_client=Mock())


def test_instantiation(agent):
    """Smoke test: agent instantiates without error."""
    assert agent is not None
    assert hasattr(agent, "fuzz_function")
    assert hasattr(agent, "enabled")
    assert hasattr(agent, "audit_path")


def test_initialization_defaults(agent):
    """Default state: llm_client None, enabled False, audit_path correct."""
    assert agent.llm_client is None
    assert agent.enabled is False
    assert agent.audit_path.name == "fuzz_results.json"
    assert {"observability", "audit"}.issubset(set(agent.audit_path.parts))


def test_llm_client_stored(agent_with_client):
    """llm_client kwarg is stored on the instance."""
    assert agent_with_client.llm_client is not None


@patch.dict(os.environ, {"ENABLE_FUZZ": "true"})
def test_initialization_enabled():
    """ENABLE_FUZZ=true → enabled is True."""
    assert RedSentinelAgent().enabled is True


@patch.dict(os.environ, {"ENABLE_FUZZ": "false"})
def test_initialization_disabled():
    """ENABLE_FUZZ=false → enabled is False."""
    assert RedSentinelAgent().enabled is False


@patch.dict(os.environ, {"ENABLE_FUZZ": "yes"})
def test_environment_only_true_enables():
    """Only the literal 'true' enables fuzzing — 'yes' must not."""
    assert RedSentinelAgent().enabled is False


def test_get_default_hostile_inputs_returns_list(agent):
    """_get_default_hostile_inputs returns a non-empty list of dicts."""
    defaults = agent._get_default_hostile_inputs()
    assert isinstance(defaults, list)
    assert len(defaults) > 0
    for item in defaults:
        assert isinstance(item, dict)
        assert "type" in item
        assert "value" in item
