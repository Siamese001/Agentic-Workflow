import pytest

from client_strategy import configure_for_routing
from routing_views import (
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
