import pytest

from routing_policy import RoutingCriteria, decide_route


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
