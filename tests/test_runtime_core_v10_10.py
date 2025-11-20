# FILE: tests/test_runtime_core_v10_10.py

"""
Core Runtime Tests for Agentic Workflow v10_10
==============================================

Covers:
    • L1 Planning
    • L2 Execution (with mocked LLM)
    • L3 DAG Orchestration + Self-Correction
    • L4 State Adapter
    • L5 Safety Gate
    • Routing + Prompt Registry
    • Agentic Layer Purity tests (no cross-layer violations)
    • Determinism and Regression Guards
"""

import pytest
from unittest.mock import patch

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    WorkflowPlanBundle,
    ExecutionContext,
)
from routing import RoutingPolicy, classify_complexity
from registry import build_default_prompt_registry
from runtime_utils import SandboxConfig
from cognitive_agents import (
    StrategyLLMAgent,
    DraftingGuild,
    SemanticQAAgent,
    ConstitutionalSafetyAgent,
)
from l1 import build_workflow_plan_bundle
from l2 import execute_workflow_plans
from l3 import run_dag
from l4 import apply_state_patch
from l5 import safety_gate
from self_correction import evaluate_all_surfaces, aggregate_correction_signals


# -------------------------------------------------------------------------
# FIXTURES
# -------------------------------------------------------------------------

@pytest.fixture
def job():
    return JobInput(
        title="Senior AI Engineer",
        role_type="engineering",
        seniority="senior",
        posting_text="Looking for an AI engineer with leadership and Python experience.",
        requirements=["AI", "Leadership", "Python"],
    )


@pytest.fixture
def resume():
    return ResumeInput(
        name="Alice Example",
        summary="Experienced AI engineer working on ML systems.",
        experience_sections=[
            {"impact_summary": "Built production ML models."},
            {"impact_summary": "Led a team of 4 engineers."},
        ],
        skills=["Python", "ML", "Leadership"],
    )


@pytest.fixture
def config():
    return WorkflowConfig()


@pytest.fixture
def routing_policy():
    return RoutingPolicy()


@pytest.fixture
def prompt_registry():
    return build_default_prompt_registry()


@pytest.fixture
def sandbox():
    return SandboxConfig()


@pytest.fixture
def ctx(job, resume, config, routing_policy, sandbox, prompt_registry):
    return ExecutionContext(
        job=job,
        resume=resume,
        config=config,
        routing_policy=routing_policy,
        sandbox_config=sandbox,
        prompt_registry=prompt_registry,
        cache_manager=None,
        meta_profile_snapshot=None,
    )


# -------------------------------------------------------------------------
# MOCK LLM BEHAVIOR
# -------------------------------------------------------------------------

MOCK_LLM_RESPONSES = {
    "strategy_generate_branch": "Mock strategy branch text for testing.",
    "strategy_select_branch": "0",
    "drafting_structure": '[{"title": "Summary", "outline": "Key achievements"}]',
    "drafting_narrative": "This is a drafted narrative.",
    "drafting_compliance": "Looks compliant.",
    "qa_semantic_check": '{"passed": true, "reason": "OK", "severity": 1}',
    "safety_check": '{"category": "none", "blocking": false, "reason": "Safe"}',
}


def mock_invoke_model(model, prompt, sandbox, temperature=0.2, max_tokens=1024):
    for key in MOCK_LLM_RESPONSES:
        if key in prompt:
            return MOCK_LLM_RESPONSES[key]
    return "Default mock LLM output."


# -------------------------------------------------------------------------
# TESTS
# -------------------------------------------------------------------------


def test_l1_builds_valid_plans(job, resume, config, routing_policy, prompt_registry):
    plans = build_workflow_plan_bundle(
        job=job,
        resume=resume,
        config=config,
        meta_profile=None,
        routing_policy=routing_policy,
        prompt_registry=prompt_registry,
    )
    assert isinstance(plans, WorkflowPlanBundle)
    assert plans.strategy.steps
    assert plans.drafting.sections


@patch("runtime_utils.invoke_model", side_effect=mock_invoke_model)
def test_l2_execute_with_mock_llm(mock_llm, ctx):
    plans = build_workflow_plan_bundle(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=None,
        routing_policy=ctx.routing_policy,
        prompt_registry=ctx.prompt_registry,
    )
    result = execute_workflow_plans(plans, ctx)
    assert result.strategy.branches
    assert result.drafting.sections
    assert all(sec.text for sec in result.drafting.sections)


@patch("runtime_utils.invoke_model", side_effect=mock_invoke_model)
def test_l3_dag_orchestration(mock_llm, ctx):
    plans = build_workflow_plan_bundle(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=None,
        routing_policy=ctx.routing_policy,
        prompt_registry=ctx.prompt_registry,
    )
    dag = run_dag(ctx, plans, max_retries=2)
    assert dag.l2_results.strategy
    assert dag.l2_results.drafting
    assert dag.final_state_patch["strategy_text"]


def test_l4_state_patch_deterministic(ctx):
    # Create minimal fake L2 results for determinism test
    from models import (
        StrategyResult, StrategyBranch,
        RAGResult, Evidence,
        DraftingResult, DraftSectionResult,
        QAResult, QACheckResult,
        SafetyResult, SafetyFinding,
        L2ResultBundle
    )

    strategy = StrategyResult(
        branches=[StrategyBranch(id="b1", text="Example branch")],
        chosen_branch_id="b1",
    )
    rag = RAGResult(evidence=[Evidence(text="x", score=0.5, source="job")])
    drafting = DraftingResult(sections=[
        DraftSectionResult(title="Summary", outline="", text="Draft", compliance_notes="")
    ], mode="balanced")
    qa = QAResult(checks=[QACheckResult(id="c1", passed=True, reason="ok", severity=1)])
    safety = SafetyResult(findings=[SafetyFinding(id="s1", category="none", blocking=False, reason="ok")])

    l2 = L2ResultBundle(strategy=strategy, rag=rag, drafting=drafting, qa=qa, safety=safety)
    patch1 = apply_state_patch(l2, [], ctx, safety_passed=True)
    patch2 = apply_state_patch(l2, [], ctx, safety_passed=True)

    assert patch1 == patch2


def test_l5_safety_gate_basic():
    from models import SafetyResult, SafetyFinding
    result = SafetyResult(findings=[SafetyFinding(id="a", category="none", blocking=False, reason="ok")])
    assert safety_gate(result) is True


def test_self_correction_surfaces_basic():
    from models import (
        StrategyResult, StrategyBranch,
        RAGResult, Evidence,
        DraftingResult, DraftSectionResult,
        QAResult, QACheckResult,
        SafetyResult, SafetyFinding,
    )

    strategy = StrategyResult(branches=[StrategyBranch(id="b1", text="some strategy text that is long")],
                              chosen_branch_id="b1")
    rag = RAGResult(evidence=[Evidence(text="x", score=0.5, source="job")])
    drafting = DraftingResult(sections=[
        DraftSectionResult(title="s", outline="", text="some text", compliance_notes="")
    ], mode="balanced")
    qa = QAResult(checks=[QACheckResult(id="c1", passed=True, reason="ok", severity=1)])
    safety = SafetyResult(findings=[SafetyFinding(id="s1", category="none", blocking=False, reason="ok")])

    signals = evaluate_all_surfaces(
        strategy=strategy, rag=rag, drafting=drafting, qa=qa, safety=safety
    )
    assert all(sig.severity == 0 for sig in signals)

    best = aggregate_correction_signals(signals)
    assert best is None


# -------------------------------------------------------------------------
# ARCHITECTURE PURITY TESTS
# -------------------------------------------------------------------------

def test_architecture_layer_purity():
    """
    Ensures no forbidden cross-layer imports.
    L3 must not import cognitive agents.
    L4 must not call LLM.
    L5 must be deterministic.
    """
    import inspect
    import l3, l4, l5

    # L3 must not import cognitive_agents
    l3_src = inspect.getsource(l3)
    assert "cognitive_agents" not in l3_src

    # L4 must not call invoke_model
    l4_src = inspect.getsource(l4)
    assert "invoke_model" not in l4_src

    # L5 must not call invoke_model
    l5_src = inspect.getsource(l5)
    assert "invoke_model" not in l5_src
