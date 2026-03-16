import os
from unittest.mock import Mock, patch

import pytest

from agentic_core.L5_safety.reasoning.RedSentinelAgent import RedSentinelAgent
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
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
