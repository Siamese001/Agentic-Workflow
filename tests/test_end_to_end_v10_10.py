# FILE: tests/test_end_to_end_v10_10.py

"""
End-to-End + Regression + Integration Tests for Agentic Workflow v10_10
======================================================================

This suite covers:
    • Full L1 → L2 → L3 → L4 → L5 execution
    • Multi-scenario deterministic tests (mocked LLM)
    • Regression tests via golden state patches
    • Prompt registry + routing + self-correction integration
    • Agentic purity tests across layers

All LLM calls are mocked for CI-safe deterministic execution.
"""

import pytest
from unittest.mock import patch
import json

from core.models.models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    ExecutionContext,
    RetrievalConfig,
)
from core.routing import RoutingPolicy
from registry import build_default_prompt_registry
from runtime_utils import SandboxConfig
from core.l1 import build_workflow_plan_bundle
from core.l3 import run_dag
from core.l5 import safety_gate


# -------------------------------------------------------------------------
# MOCK LLM OUTPUT (deterministic)
# -------------------------------------------------------------------------

MOCK_LLM_OUTPUTS = {
    "strategy_generate_branch": "Strategy branch text: improve resume alignment.",
    "strategy_select_branch": "0",
    "drafting_structure": '[{"title": "Summary", "outline": "Key summary bullet points"}]',
    "drafting_narrative": "A strong, concise summary aligned with requirements.",
    "drafting_compliance": "Compliant and professional.",
    "qa_semantic_check": '{"passed": true, "reason": "OK", "severity": 1}',
    "safety_check": '{"category": "none", "blocking": false, "reason": "Safe"}',
}


def mock_llm(model, prompt, sandbox, temperature=0.2, max_tokens=1024):
    for k, v in MOCK_LLM_OUTPUTS.items():
        if k in prompt:
            return v
    return "Default Mock Output"


# -------------------------------------------------------------------------
# GOLDEN PATCH FIXTURE (Regression Baseline)
# -------------------------------------------------------------------------

GOLDEN_PATCH = {
    "strategy_text": "Strategy branch text: improve resume alignment.",
    "rag_evidence": [],
    "drafted_sections": [
        {
            "title": "Summary",
            "outline": "Key summary bullet points",
            "text": "A strong, concise summary aligned with requirements.",
            "compliance_notes": "Compliant and professional.",
        }
    ],
    "qa_findings": [
        {"id": "jd_alignment", "passed": True, "reason": "OK", "severity": 1}
    ],
    "safety_findings": [
        {"id": "pii_detection", "category": "none", "blocking": False, "reason": "Safe"}
    ],
    "correction_signals": [],
    "safety_passed": True,
}


# -------------------------------------------------------------------------
# BASE FIXTURE
# -------------------------------------------------------------------------

@pytest.fixture
def ctx():
    job = JobInput(
        title="Director of AI",
        role_type="leadership",
        seniority="director",
        posting_text="Seeking a Director of AI to lead strategic initiatives.",
        requirements=["AI", "Leadership", "Strategy"],
    )

    resume = ResumeInput(
        name="Alice Applicant",
        summary="AI engineer with experience in strategy and leadership.",
        experience_sections=[
            {"impact_summary": "Led teams at large scale."},
            {"impact_summary": "Architected AI platforms."},
        ],
        skills=["Leadership", "AI", "ML"],
    )

    config = WorkflowConfig()
    routing = RoutingPolicy()
    sandbox = SandboxConfig()
    prompt_registry = build_default_prompt_registry()
    retrieval = RetrievalConfig()

    return ExecutionContext(
        job=job,
        resume=resume,
        config=config,
        prompt_registry=prompt_registry,
        cache_manager=None,
        workflow_id="test-workflow",
        profile_name="default",
        retrieval=retrieval,
        routing_policy=routing,
        sandbox_config=sandbox,
        meta_profile_snapshot=None,
        meta_profile=None,
        cost_snapshot=None,
    )


# -------------------------------------------------------------------------
# END-TO-END SCENARIO TESTS
# -------------------------------------------------------------------------

@patch("runtime_utils.invoke_model", side_effect=mock_llm)
def test_e2e_full_pipeline(mocked_llm, ctx):
    plans = build_workflow_plan_bundle(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=None,
        routing_policy=ctx.routing_policy,
        prompt_registry=ctx.prompt_registry,
    )
    dag_result = run_dag(ctx, plans)

    assert dag_result.l2_results.strategy
    assert dag_result.final_state_patch
    assert dag_result.safety_passed in (True, False)

    patch = dag_result.final_state_patch

    for key in GOLDEN_PATCH:
        assert key in patch


@patch("runtime_utils.invoke_model", side_effect=mock_llm)
def test_e2e_safety_flow(mocked_llm, ctx):
    plans = build_workflow_plan_bundle(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=None,
        routing_policy=ctx.routing_policy,
        prompt_registry=ctx.prompt_registry,
    )
    dag = run_dag(ctx, plans)

    assert isinstance(dag.safety_passed, bool)
    assert safety_gate(dag.l2_results.safety) == dag.safety_passed


@patch("runtime_utils.invoke_model", side_effect=mock_llm)
def test_e2e_correction_loop(mocked_llm, ctx):
    plans = build_workflow_plan_bundle(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=None,
        routing_policy=ctx.routing_policy,
        prompt_registry=ctx.prompt_registry,
    )
    dag = run_dag(ctx, plans)

    assert dag.corrected is False
    assert len([s for s in dag.corrections if s.severity > 0]) == 0


# -------------------------------------------------------------------------
# REGRESSION TESTS (Golden State)
# -------------------------------------------------------------------------

@patch("runtime_utils.invoke_model", side_effect=mock_llm)
def test_regression_state_patch_against_golden(mock_llm, ctx):
    plans = build_workflow_plan_bundle(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=None,
        routing_policy=ctx.routing_policy,
        prompt_registry=ctx.prompt_registry,
    )
    dag = run_dag(ctx, plans)
    patch = dag.final_state_patch

    assert set(patch.keys()) == set(GOLDEN_PATCH.keys())


# -------------------------------------------------------------------------
# INTEGRATION TESTS
# -------------------------------------------------------------------------

def test_prompt_registry_integrity(ctx):
    reg = ctx.prompt_registry
    required_ids = [
        "strategy_generate_branch",
        "strategy_select_branch",
        "drafting_structure",
        "drafting_narrative",
        "drafting_compliance",
        "qa_semantic_check",
        "safety_check",
    ]
    for pid in required_ids:
        assert reg.get_prompt(pid)


def test_routing_policy_integrity(ctx):
    rp = ctx.routing_policy
    assert rp.select_model("drafting_narrative", None, None)
    assert rp.select_model("qa_semantic_check", None, None)
    assert rp.strategy_branches_for(complexity=ctx.config.drafting_depth or 1)


# -------------------------------------------------------------------------
# CRITICAL AGENTIC ARCHITECTURE TESTS
# -------------------------------------------------------------------------

def test_agentic_layer_purity_l3_has_no_llm_calls():
    import inspect, l3
    assert "invoke_model" not in inspect.getsource(l3)


def test_agentic_layer_purity_l4_is_pure(ctx):
    import inspect, l4
    src = inspect.getsource(l4)
    assert "invoke_model" not in src
    assert "StrategyLLMAgent" not in src
    assert "DraftingGuild" not in src


def test_agentic_layer_purity_l5_deterministic():
    import inspect, l5
    src = inspect.getsource(l5)
    assert "invoke_model" not in src
    assert "llm" not in src.lower()


# -------------------------------------------------------------------------
# E2E MULTI-SCENARIO TESTS
# -------------------------------------------------------------------------

SCENARIOS = [
    {
        "name": "strategy_heavy",
        "job": JobInput(
            title="Chief AI Strategist",
            role_type="ai",
            seniority="chief",
            posting_text="Lead AI strategy and innovation.",
            requirements=["AI", "Strategy", "Leadership"],
        ),
        "resume": ResumeInput(
            name="Bob",
            summary="AI strategist with 10 years experience.",
            experience_sections=[{"impact_summary": "Led AI vision."}],
        ),
    },
    {
        "name": "rag_heavy",
        "job": JobInput(
            title="Data Analyst",
            role_type="data",
            seniority="mid",
            posting_text="Analyze data and build dashboards.",
            requirements=["SQL", "Analytics"],
        ),
        "resume": ResumeInput(
            name="Sara",
            summary="Data analyst with visualization experience.",
            experience_sections=[{"impact_summary": "Built dashboards."}],
        ),
    },
]


@patch("runtime_utils.invoke_model", side_effect=mock_llm)
@pytest.mark.parametrize("scenario", SCENARIOS)
def test_multi_scenario_e2e(mock_llm, scenario):
    config = WorkflowConfig()
    routing = RoutingPolicy()
    prompt_registry = build_default_prompt_registry()
    sandbox = SandboxConfig()

    ctx = ExecutionContext(
        job=scenario["job"],
        resume=scenario["resume"],
        config=config,
        routing_policy=routing,
        sandbox_config=sandbox,
        prompt_registry=prompt_registry,
        cache_manager=None,
        meta_profile_snapshot=None,
    )

    plans = build_workflow_plan_bundle(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=None,
        routing_policy=ctx.routing_policy,
        prompt_registry=ctx.prompt_registry,
    )

    dag = run_dag(ctx, plans)
    assert dag.l2_results.strategy
    assert dag.final_state_patch
    assert isinstance(dag.safety_passed, bool)
