# FILE: l1.py
"""
Unified L1 Planning Layer (v10_10)

Responsibilities (WHAT to do, not HOW):
    - Interpret high-level inputs (job, resume, config).
    - Classify task complexity and routing hints.
    - Produce typed plans for:
        • Strategy (overall workflow plan)
        • RAG (retrieval & evidence fusion)
        • Drafting (resume sections + tone)
        • QA (semantic QA checks)
        • Safety (safety review plan)
    - Remain 100% deterministic and side-effect free.

Non-Responsibilities (must NOT do):
    - No LLM calls.
    - No tool invocation (retrievers, HTTP, DB).
    - No state mutation (beyond constructing plan objects).
    - No logging side-effects (leave to observability).

L2 (cognitive_agents + l2.py) is responsible for executing these plans
and invoking models/tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    ComplexityLevel,
    StrategyPlan,
    StrategyStep,
    RAGPlan,
    RAGQueryHint,
    DraftingPlan,
    DraftSectionPlan,
    DraftingMode,
    QAPlan,
    QACheck,
    SafetyPlan,
    SafetyCheck,
    WorkflowPlanBundle,
    RoutingHint,
)
from meta_profile import MetaProfileSnapshot
from routing import RoutingPolicy, classify_complexity
from registry import PromptRegistry  # logical dependency, used for future extensions


# ============================================================================
# L1 Context
# ============================================================================


@dataclass(frozen=True)
class L1Context:
    """
    Immutable planning context for L1.

    Contains only:
        - raw inputs (job, resume, config)
        - a snapshot of meta-profile
        - routing policy
        - prompt registry descriptor (not used deeply in v10_10 L1, but kept for evolution)
    """

    job: JobInput
    resume: ResumeInput
    config: WorkflowConfig
    meta_profile: Optional[MetaProfileSnapshot]
    routing_policy: RoutingPolicy
    prompt_registry: PromptRegistry


# ============================================================================
# Internal Planning Helpers
# ============================================================================


def _estimate_complexity(ctx: L1Context) -> ComplexityLevel:
    """
    Estimate ComplexityLevel via routing.classify_complexity.

    This signal drives:
        - ToT depth (StrategyLLMAgent)
        - RAG depth
        - Drafting density
        - QA strictness
        - Safety depth
    """
    return classify_complexity(
        job=ctx.job,
        resume=ctx.resume,
        config=ctx.config,
        meta_profile=ctx.meta_profile,
    )


def _derive_routing_hint(ctx: L1Context, complexity: ComplexityLevel) -> RoutingHint:
    """
    Build the RoutingHint L2 and routing.py will use to pick models/policies.
    """
    return RoutingHint(
        complexity=complexity,
        cost_budget=ctx.config.cost_budget,
        latency_slo_ms=ctx.config.latency_slo_ms,
        safety_sensitivity=ctx.config.safety_sensitivity,
        drafting_depth=ctx.config.drafting_depth,
    )


def _build_strategy_steps(ctx: L1Context, complexity: ComplexityLevel) -> List[StrategyStep]:
    """
    Build a deterministic skeleton of strategy steps.

    L2 StrategyLLMAgent will use this skeleton to:
        - explore branches (ToT)
        - choose a final strategy narrative.
    """
    steps: List[StrategyStep] = []

    steps.append(
        StrategyStep(
            id="analyze_requirements",
            order=10,
            description="Analyze job posting and map requirements to candidate strengths.",
            must_complete=True,
            can_parallelize=False,
        )
    )

    steps.append(
        StrategyStep(
            id="plan_rag",
            order=20,
            description="Plan evidence retrieval from resume and any external RAG corpus.",
            must_complete=True,
            can_parallelize=True,
        )
    )

    steps.append(
        StrategyStep(
            id="plan_drafting",
            order=30,
            description="Decide sections, emphasis, and tone for the tailored resume.",
            must_complete=True,
            can_parallelize=False,
        )
    )

    steps.append(
        StrategyStep(
            id="plan_qa",
            order=40,
            description="Plan semantic QA passes for claims, tone, structure, and alignment.",
            must_complete=True,
            can_parallelize=True,
        )
    )

    steps.append(
        StrategyStep(
            id="plan_safety",
            order=50,
            description="Plan safety and constitutional review (PII, risky content, professionalism).",
            must_complete=True,
            can_parallelize=False,
        )
    )

    if complexity in (ComplexityLevel.MEDIUM, ComplexityLevel.HIGH):
        steps.append(
            StrategyStep(
                id="explore_alternative_strategies",
                order=15,
                description=(
                    "Enumerate alternative positioning strategies (technical-heavy, leadership-heavy, "
                    "risk-averse) for Tree-of-Thought exploration."
                ),
                must_complete=False,
                can_parallelize=True,
            )
        )

    return sorted(steps, key=lambda s: s.order)


def _build_rag_plan(ctx: L1Context, complexity: ComplexityLevel) -> RAGPlan:
    """
    Construct a RAGPlan with multiple query hints.

    L2 will convert these hints into concrete retrieval calls.
    """
    hints: List[RAGQueryHint] = []

    hints.append(
        RAGQueryHint(
            id="job_requirements",
            description="Retrieve evidence relevant to explicit job requirements.",
            focus="job",
            max_chunks=ctx.config.rag_max_job_chunks,
            importance=0.9,
        )
    )

    hints.append(
        RAGQueryHint(
            id="candidate_strengths",
            description="Retrieve evidence showing the candidate's strongest achievements.",
            focus="resume",
            max_chunks=ctx.config.rag_max_resume_chunks,
            importance=0.8,
        )
    )

    if complexity == ComplexityLevel.HIGH:
        hints.append(
            RAGQueryHint(
                id="edge_case_requirements",
                description="Retrieve evidence for ambiguous or edge-case requirements.",
                focus="hybrid",
                max_chunks=ctx.config.rag_max_hybrid_chunks,
                importance=0.7,
            )
        )

    return RAGPlan(
        hints=hints,
        allow_hyde=ctx.config.rag_allow_hyde,
        require_hybrid=ctx.config.rag_require_hybrid,
    )


def _infer_drafting_mode(ctx: L1Context, complexity: ComplexityLevel) -> DraftingMode:
    """
    Decide which DraftingMode to use based on job/resume characteristics.
    """
    if ctx.job.seniority in ("VP", "SVP", "C-level"):
        return DraftingMode.HYBRID_EXEC_SUMMARY

    if ctx.job.role_type in ("Engineer", "Analyst", "IC") and complexity == ComplexityLevel.LOW:
        return DraftingMode.BULLET_HEAVY

    if ctx.job.role_type in ("Product", "Strategy") and complexity != ComplexityLevel.LOW:
        return DraftingMode.MIXED_NARRATIVE

    return DraftingMode.BALANCED


def _build_drafting_plan(ctx: L1Context, complexity: ComplexityLevel) -> DraftingPlan:
    """
    Build a high-level DraftingPlan: sections, tone, and target length.

    L2 DraftingGuild will fill in content.
    """
    mode = _infer_drafting_mode(ctx, complexity)
    max_tokens = ctx.config.section_max_tokens

    sections: List[DraftSectionPlan] = []

    sections.append(
        DraftSectionPlan(
            id="header",
            title="Header",
            required=True,
            max_tokens=max_tokens.get("header", 256),
            priority=1.0,
        )
    )

    sections.append(
        DraftSectionPlan(
            id="summary",
            title="Executive Summary",
            required=mode in (DraftingMode.HYBRID_EXEC_SUMMARY, DraftingMode.MIXED_NARRATIVE),
            max_tokens=max_tokens.get("summary", 512),
            priority=0.9,
        )
    )

    sections.append(
        DraftSectionPlan(
            id="experience",
            title="Experience",
            required=True,
            max_tokens=max_tokens.get("experience", 1024),
            priority=1.0,
        )
    )

    sections.append(
        DraftSectionPlan(
            id="skills",
            title="Skills",
            required=True,
            max_tokens=max_tokens.get("skills", 512),
            priority=0.8,
        )
    )

    sections.append(
        DraftSectionPlan(
            id="projects",
            title="Projects",
            required=False,
            max_tokens=max_tokens.get("projects", 768),
            priority=0.6,
        )
    )

    return DraftingPlan(
        mode=mode,
        sections=sections,
        target_tone=ctx.config.target_tone,
        target_length_tokens=ctx.config.target_total_tokens,
    )


def _build_qa_plan(ctx: L1Context, complexity: ComplexityLevel) -> QAPlan:
    """
    Build a QAPlan describing semantic QA checks to run in L2.
    """
    checks: List[QACheck] = []

    checks.append(
        QACheck(
            id="claims_supported",
            description="Verify that major claims in the draft are supported by evidence.",
            category="claims",
            severity=3,
        )
    )

    checks.append(
        QACheck(
            id="tone_alignment",
            description="Check that tone matches target seniority, culture, and role type.",
            category="tone",
            severity=2,
        )
    )

    checks.append(
        QACheck(
            id="structure_integrity",
            description="Ensure sections are complete, ordered logically, and not redundant.",
            category="structure",
            severity=2,
        )
    )

    if complexity in (ComplexityLevel.MEDIUM, ComplexityLevel.HIGH):
        checks.append(
            QACheck(
                id="requirements_coverage",
                description="Ensure each explicit job requirement is addressed in the draft.",
                category="alignment",
                severity=3,
            )
        )

    return QAPlan(checks=checks)


def _build_safety_plan(ctx: L1Context) -> SafetyPlan:
    """
    Build a SafetyPlan describing what safety checks must be run in L2/L5.
    """
    checks: List[SafetyCheck] = []

    checks.append(
        SafetyCheck(
            id="pii_leakage",
            description="Detect accidental PII or sensitive identifiers.",
            category="pii",
            severity=3,
        )
    )

    checks.append(
        SafetyCheck(
            id="policy_risky_content",
            description="Detect disallowed or risky content (hate, violence, etc.).",
            category="policy",
            severity=3,
        )
    )

    checks.append(
        SafetyCheck(
            id="professionalism",
            description="Flag overly informal or unprofessional language.",
            category="professionalism",
            severity=1,
        )
    )

    return SafetyPlan(
        checks=checks,
        enforce_block_on_severe=True,
    )


# ============================================================================
# Public L1 API
# ============================================================================


def build_workflow_plan_bundle(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    meta_profile: Optional[MetaProfileSnapshot],
    routing_policy: RoutingPolicy,
    prompt_registry: PromptRegistry,
) -> WorkflowPlanBundle:
    """
    Main L1 entrypoint.

    Given raw inputs + configuration, emit a fully-typed WorkflowPlanBundle
    that L2–L5 can execute:

        - StrategyPlan
        - RAGPlan
        - DraftingPlan
        - QAPlan
        - SafetyPlan
        - RoutingHint (for model selection)

    This function MUST remain deterministic and side-effect free.
    """
    ctx = L1Context(
        job=job,
        resume=resume,
        config=config,
        meta_profile=meta_profile,
        routing_policy=routing_policy,
        prompt_registry=prompt_registry,
    )

    complexity = _estimate_complexity(ctx)
    routing_hint = _derive_routing_hint(ctx, complexity)

    strategy_plan = StrategyPlan(
        complexity=complexity,
        routing_hint=routing_hint,
        steps=_build_strategy_steps(ctx, complexity),
    )
    rag_plan = _build_rag_plan(ctx, complexity)
    drafting_plan = _build_drafting_plan(ctx, complexity)
    qa_plan = _build_qa_plan(ctx, complexity)
    safety_plan = _build_safety_plan(ctx)

    return WorkflowPlanBundle(
        strategy=strategy_plan,
        rag=rag_plan,
        drafting=drafting_plan,
        qa=qa_plan,
        safety=safety_plan,
        routing_hint=routing_hint,
    )
