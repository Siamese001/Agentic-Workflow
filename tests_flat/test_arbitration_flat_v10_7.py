# AUTO-GENERATED FLAT TEST FILE
# Sources:
#   - tests/core/test_arbitration_engine_v10_7.py
#   - tests/integration/test_arbitration_graph_wiring.py
# ------------------------------------------------------------------
# ----- BEGIN: tests/core/test_arbitration_engine_v10_7.py -----
import copy
from types import SimpleNamespace

import pytest

from agent_orchestration_v10_7 import _attach_arbitration_report
from core_v10_7.config import ConfigSection
from core_v10_7.models import ArbitrationReport
from core_v10_7.services import ArbitrationEngine, MetricsCollector


BASE_STAGES = {
    "strategy_post_plan": {"enabled": True, "allow_revision": True},
    "prompt_rag_join": {"enabled": True, "allow_revision": False},
    "draft_post_assembly": {"enabled": True, "allow_revision": True},
    "bullets_post_selection": {"enabled": True, "allow_revision": True},
    "qa_post_validation": {"enabled": True, "allow_revision": True},
}


def make_config(*, enabled: bool = True, stage_overrides: dict | None = None):
    cfg = {
        "enabled": enabled,
        "default_mode": "observe_only",
        "max_revision_loops_per_stage": 1,
        "stages": copy.deepcopy(BASE_STAGES),
    }
    if stage_overrides:
        for stage, overrides in stage_overrides.items():
            current = cfg["stages"].get(stage, {})
            merged = {**current, **overrides}
            cfg["stages"][stage] = merged
    return SimpleNamespace(arbitration_config=ConfigSection(cfg))


@pytest.mark.asyncio
async def test_arbitration_disabled_returns_accept():
    engine = ArbitrationEngine(config=make_config(enabled=False), metrics=MetricsCollector())
    state = {"strategy": {"strategy_plan": {"focus_areas": ["impact"], "tone": "bold"}}}

    report = await engine.run_check("strategy_post_plan", state)

    assert report.decision == "ACCEPT"
    assert any("disabled" in reason.lower() for reason in report.reasons)
    assert report.suggested_route == "ACCEPT"


@pytest.mark.asyncio
async def test_strategy_success_sets_accept_route():
    engine = ArbitrationEngine(config=make_config(), metrics=MetricsCollector())
    state = {"strategy": {"strategy_plan": {"focus_areas": ["impact"], "tone": "bold"}}}

    report = await engine.run_check("strategy_post_plan", state)

    assert report.decision == "ACCEPT"
    assert report.suggested_route == "ACCEPT"


@pytest.mark.asyncio
async def test_strategy_missing_fields_requests_revise():
    engine = ArbitrationEngine(config=make_config(), metrics=MetricsCollector())
    state = {"strategy": {"strategy_plan": {"focus_areas": [], "tone": ""}}}

    report = await engine.run_check("strategy_post_plan", state)

    assert report.decision == "REQUEST_REVISE"
    assert report.suggested_route == "REPLAN_STRATEGY"


@pytest.mark.asyncio
async def test_draft_empty_requests_revise():
    engine = ArbitrationEngine(config=make_config(), metrics=MetricsCollector())
    state = {"draft": {"sections": {}}}

    report = await engine.run_check("draft_post_assembly", state)

    assert report.decision == "REQUEST_REVISE"
    assert report.suggested_route == "RETRY_DRAFTING"


@pytest.mark.asyncio
async def test_qa_failed_requests_revise():
    engine = ArbitrationEngine(config=make_config(), metrics=MetricsCollector())
    state = {"qa": {"qa_passed": False}}

    report = await engine.run_check("qa_post_validation", state)

    assert report.decision == "REQUEST_REVISE"
    assert report.suggested_route == "RETRY_QA"


@pytest.mark.asyncio
async def test_prompt_rag_warn_sets_retry_route():
    engine = ArbitrationEngine(config=make_config(), metrics=MetricsCollector())
    state = {"rag": {"results": []}}

    report = await engine.run_check("prompt_rag_join", state)

    assert report.decision == "WARN"
    assert report.suggested_route == "RETRY_RAG"


@pytest.mark.asyncio
async def test_bullets_empty_requests_retry_route():
    engine = ArbitrationEngine(config=make_config(), metrics=MetricsCollector())
    state = {"bullets": {"critiqued_bullets": []}}

    report = await engine.run_check("bullets_post_selection", state)

    assert report.decision == "REQUEST_REVISE"
    assert report.suggested_route == "RETRY_BULLETS"


def test_arbitration_attachment_helper():
    state: dict = {}
    report = ArbitrationReport(
        stage="qa_post_validation",
        decision="ACCEPT",
        reasons=["ok"],
        confidence=1.0,
    )

    _attach_arbitration_report(state, "qa_post_validation", report)

    assert "qa_post_validation" in state["arbitration"]
    assert state["arbitration"]["qa_post_validation"]["decision"] == "ACCEPT"
# ----- END: tests/core/test_arbitration_engine_v10_7.py -----
# ----- BEGIN: tests/integration/test_arbitration_graph_wiring.py -----
from types import SimpleNamespace

from agent_orchestration_v10_7 import get_graph_app
from core_v10_7.models import ArbitrationReport


class DummyArbitrationEngine:
    async def run_check(self, stage: str, state: dict) -> ArbitrationReport:  # pragma: no cover - trivial stub
        return ArbitrationReport(stage=stage, decision="ACCEPT", reasons=["stub"], confidence=1.0)


class DummyWorkflowContext:
    def __init__(self) -> None:
        agent_stacks = SimpleNamespace(
            enable_hil_stack=False,
            max_local_retries=1,
            enable_prompt_injection_detection=False,
        )
        performance_config = SimpleNamespace(workflow_node_timeout_seconds=1)
        self.config = SimpleNamespace(agent_stacks=agent_stacks, performance_config=performance_config)
        self.arbitration_engine = DummyArbitrationEngine()
        self.wrap_mcp_nodes = True

    def reset_mcp_clients(self) -> None:  # pragma: no cover - stubbed
        self.wrap_mcp_nodes = False


def test_graph_app_contains_arbitration_nodes():
    context = DummyWorkflowContext()
    workflow = get_graph_app(checkpointer=None, workflow_context=context, enable_hil=False)

    node_names = set(workflow.nodes.keys())
    expected = {
        "run_arbitration_after_strategy",
        "run_arbitration_after_join",
        "run_arbitration_after_bullets",
        "run_arbitration_after_drafting",
        "run_arbitration_after_qa",
    }

    assert expected.issubset(node_names)
# ----- END: tests/integration/test_arbitration_graph_wiring.py -----
# ----- BEGIN: tests/routing/test_arbitration_driven_routing_v10_7.py -----
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
    decision = "ACCEPT" if route in {"", "ACCEPT"} else "REQUEST_REVISE"
    arbitration = {stage: {"suggested_route": route, "decision": decision}}
    return {"arbitration": arbitration}


def _wrap_state(node_name: str, state: dict) -> dict:
    return node_success(node_name, copy.deepcopy(state))


def test_check_bullets_retry_respects_arbitration_route():
    context = _make_context(max_local_retries=1)
    state = _make_arbitration_state("bullets_post_selection", "RETRY_BULLETS")
    result = _wrap_state("run_arbitration_after_bullets", state)

    assert check_bullets_passed(result, context) == "retry_bullets"
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
# ----- END: tests/routing/test_arbitration_driven_routing_v10_7.py -----
