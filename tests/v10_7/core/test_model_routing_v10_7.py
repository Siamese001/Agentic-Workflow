import pytest

from core_v10_7 import BaseAgent, canonical_model_name


class DummyRoutingAgent(BaseAgent):
    pass


@pytest.fixture
def agent(workflow_context):
    workflow_context.workflow_id = "wf-routing"
    return DummyRoutingAgent(workflow_context)


def test_complexity_routing_selects_simple_model_on_simple(agent):
    agent.context.complexity = "simple"
    client = agent.get_model_client("strategy_model")
    expected = canonical_model_name(agent.config.model_config.strategy_model_simple.model_name)
    assert client.model_name == expected


def test_complexity_routing_selects_complex_model_on_complex(agent):
    agent.context.complexity = "complex"
    client = agent.get_model_client("strategy_model")
    expected = canonical_model_name(agent.config.model_config.strategy_model_complex.model_name)
    assert client.model_name == expected


def test_latency_based_fallback_switch_to_simple(agent):
    agent.context.complexity = "complex"
    agent.config.performance_config.max_complex_model_latency_ms = 1
    agent.metrics.record(
        agent_name=agent.__class__.__name__,
        task_name="strategy_model_complex",
        duration_ms=500,
        success=True,
    )

    client = agent.get_model_client("strategy_model")
    expected = canonical_model_name(agent.config.model_config.strategy_model_simple.model_name)
    assert client.model_name == expected
    assert any(m["task_name"] == "latency_fallback" for m in agent.metrics.metrics)


def test_missing_model_config_reverts_to_base_key(agent):
    agent.context.complexity = "complex"
    client = agent.get_model_client("qa_model")
    expected = canonical_model_name(agent.config.model_config.qa_model.model_name)
    assert client.model_name == expected
