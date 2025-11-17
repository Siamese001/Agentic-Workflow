import pytest

from client_strategy import build_client_for_route, configure_for_routing
from l3_graph_orchestrator import GraphOrchestrator
from routing_policy import RoutingCriteria, decide_route


def test_decide_route_is_deterministic_and_metadata_rich():
    criteria = RoutingCriteria(
        task_type="analysis",
        complexity="medium",
        latency_target_ms=1500,
        risk_level="normal",
    )

    first_decision = decide_route(criteria)
    second_decision = decide_route(criteria)

    assert first_decision == second_decision
    assert first_decision.model == "gpt-4o-mini"
    assert first_decision.endpoint in {"default", "fast"}


def test_decide_route_falls_back_when_unavailable():
    criteria = RoutingCriteria(
        task_type="analysis",
        complexity="high",
        latency_target_ms=500,
        model_available=False,
    )

    decision = decide_route(criteria)

    assert decision.model == "gpt-4o-mini"
    assert decision.endpoint == "fast"


def test_client_complete_uses_invoke_model_metadata():
    route = {"model": "gpt-4o-mini", "endpoint": "fast"}
    client = build_client_for_route(route)
    config = configure_for_routing(route)
    prompt = "This prompt will be echoed deterministically by the model."

    result = client.complete(prompt, config)

    assert result["model"] == "gpt-4o-mini"
    assert result["completion"] == prompt[:30]


def test_graph_orchestrator_includes_selected_model():
    orchestrator = GraphOrchestrator()

    result = orchestrator.orchestrate()

    selected_model = result.plan["routing"].get("selected_model")
    assert selected_model == "gpt-4o-mini"
