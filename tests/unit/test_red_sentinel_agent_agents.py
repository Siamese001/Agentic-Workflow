import os
from unittest.mock import Mock, patch

import pytest

from agentic_core.L5_safety.reasoning.RedSentinelAgent import RedSentinelAgent
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

_emit_records_execution_trace("p0", "evidence", "test_red_sentinel_agent_agents")
_emit_applies_guardrail("p0", "test_red_sentinel_agent_agents", "p0_governance")
_emit_reads_policy_state("p0", "test_red_sentinel_agent_agents", "policy_binding")
_emit_snapshots_state("p0", "test_red_sentinel_agent_agents", "state_snapshot")
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
