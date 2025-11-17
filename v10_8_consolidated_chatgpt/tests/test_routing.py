"""Grouped routing tests."""
import pytest

from routing import build_client_for_route, configure_for_routing
from l3_orchestration import GraphOrchestrator
from routing import RoutingCriteria, decide_route


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
import pytest

from routing import RoutingCriteria, decide_route


def test_high_complexity_routes_to_gpt4o():
    decision = decide_route(RoutingCriteria(task_type="analysis", complexity="high"))
    assert decision.model == "gpt-4o"
    assert decision.endpoint == "default"


def test_strict_risk_routes_to_gpt4o():
    decision = decide_route(RoutingCriteria(task_type="analysis", risk_level="strict"))
    assert decision.model == "gpt-4o"
    assert decision.endpoint == "default"


def test_low_latency_routes_to_fast_endpoint():
    decision = decide_route(RoutingCriteria(task_type="analysis", latency_target_ms=500))
    assert decision.model == "gpt-4o-mini"
    assert decision.endpoint == "fast"


def test_default_case_rationale_deterministic():
    decision = decide_route(RoutingCriteria(task_type="analysis"))
    assert decision.rationale == "Default routing for normal tasks."
import pytest

from routing import configure_for_routing
from routing import (
    get_routing_metadata,
    get_routing_model_name,
    get_routing_plan,
)


def test_get_routing_plan_returns_routing_metadata():
    plan = {"routing": {"complexity": "simple", "path": "alpha"}}

    routing_plan = get_routing_plan(plan)

    assert routing_plan == {"complexity": "simple", "path": "alpha"}


def test_get_routing_model_name_returns_deterministic_value():
    plan = {"routing": {"complexity": "advanced", "selected_model": "gpt-4o-mini"}}

    model_name = get_routing_model_name(plan)

    assert model_name == "gpt-4o-mini"


def test_get_routing_metadata_is_read_only():
    plan = {"routing": {"complexity": "standard", "priority": 1}}

    metadata = get_routing_metadata(plan)
    metadata["priority"] = 2

    assert plan["routing"]["priority"] == 1
    assert metadata["priority"] == 2


def test_configure_for_routing_constructs_deterministic_client_config():
    route = {"complexity": "expert", "model": "gpt-4o-mini", "endpoint": "fast"}

    config = configure_for_routing(route)

    assert config == {
        "model": "gpt-4o-mini",
        "model_name": "gpt-4o-mini",
        "endpoint": "fast",
        "route": route,
    }
import pytest

from routing import ModelClient, build_client_for_route


def test_build_client_for_route_returns_model_client():
    route = {"route_name": "test"}
    client = build_client_for_route(route)
    assert isinstance(client, ModelClient)


def test_complete_returns_expected_keys():
    client = ModelClient()
    prompt = "Hello world"
    config = {"model": "test-model", "endpoint": "local"}

    result = client.complete(prompt, config)

    assert set(result.keys()) == {"completion", "model"}


def test_complete_is_deterministic():
    client = ModelClient()
    prompt = "Consistent prompt"
    config = {"model": "deterministic", "endpoint": "offline"}

    first_result = client.complete(prompt, config)
    second_result = client.complete(prompt, config)

    assert first_result == second_result
