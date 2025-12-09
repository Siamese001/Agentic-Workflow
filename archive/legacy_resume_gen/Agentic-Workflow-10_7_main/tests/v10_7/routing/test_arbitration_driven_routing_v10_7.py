import copy
from types import SimpleNamespace

import pytest

from agent_orchestration_v10_7 import (
    _get_robustness_stack,
    check_bullets_passed,
    check_qa_passed,
    node_success,
)


def _make_context(max_local_retries: int = 1):
    agent_stacks = SimpleNamespace(max_local_retries=max_local_retries)
    performance = SimpleNamespace(node_retry_backoff_seconds=0.0, node_retry_max_backoff_seconds=0.0)
    config = SimpleNamespace(agent_stacks=agent_stacks, performance_config=performance)
    return SimpleNamespace(config=config)


def _make_arbitration_state(stage: str, route: str | None) -> dict:
    arbitration = {stage: {"suggested_route": route, "decision": "ACCEPT" if route in {"", "ACCEPT"} else "REQUEST_REVISE"}}
    return {"arbitration": arbitration}


def _wrap_state(node_name: str, state: dict) -> dict:
    # node_success clones the payload, so we deepcopy for predictable assertions
    return node_success(node_name, copy.deepcopy(state))


def test_check_bullets_retry_respects_arbitration_route():
    context = _make_context(max_local_retries=1)
    state = _make_arbitration_state("bullets_post_selection", "RETRY_BULLETS")
    result = _wrap_state("run_arbitration_after_bullets", state)

    assert check_bullets_passed(result, context) == "retry_bullets"
    # Retry budget exhausted on second invocation
    assert check_bullets_passed(result, context) == "global_replanner"


def test_check_bullets_accept_route_resets_robustness():
    context = _make_context()
    robustness = _get_robustness_stack(context)
    robustness.should_retry("bullets_quality", "seed_failure")

    state = _make_arbitration_state("bullets_post_selection", "ACCEPT")
    result = _wrap_state("run_arbitration_after_bullets", state)

    assert check_bullets_passed(result, context) == "bullets_passed"
    assert "bullets_quality" not in robustness._failure_counts


def test_check_bullets_fallback_without_report():
    context = _make_context()
    state = {
        "bullets": {
            "critiqued_bullets": [
                {"critique": {"score": 8}},
                {"critique": {"score": 9}},
            ]
        }
    }
    result = _wrap_state("run_arbitration_after_bullets", state)

    assert check_bullets_passed(result, context) == "bullets_passed"


def test_check_bullets_fallback_handles_missing_critiques():
    context = _make_context()
    state = {"bullets": {"critiqued_bullets": []}}
    result = _wrap_state("run_arbitration_after_bullets", state)

    assert check_bullets_passed(result, context) == "global_replanner"


def test_check_qa_retry_respects_arbitration_route():
    context = _make_context(max_local_retries=1)
    state = _make_arbitration_state("qa_post_validation", "RETRY_QA")
    result = _wrap_state("run_arbitration_after_qa", state)

    assert check_qa_passed(result, context) == "retry_drafting"
    assert check_qa_passed(result, context) == "global_replanner"


def test_check_qa_accept_route_resets_robustness():
    context = _make_context()
    robustness = _get_robustness_stack(context)
    robustness.should_retry("qa_validation", "seed_failure")

    state = _make_arbitration_state("qa_post_validation", "ACCEPT")
    result = _wrap_state("run_arbitration_after_qa", state)

    assert check_qa_passed(result, context) == "qa_passed"
    assert "qa_validation" not in robustness._failure_counts


def test_check_qa_global_replan_route_short_circuits():
    context = _make_context()
    state = _make_arbitration_state("qa_post_validation", "GLOBAL_REPLAN")
    result = _wrap_state("run_arbitration_after_qa", state)

    assert check_qa_passed(result, context) == "global_replanner"


def test_check_qa_fallback_retries_without_report():
    context = _make_context(max_local_retries=1)
    state = {"qa": {"qa_passed": False}}
    result = _wrap_state("run_arbitration_after_qa", state)

    assert check_qa_passed(result, context) == "retry_drafting"
    assert check_qa_passed(result, context) == "global_replanner"
