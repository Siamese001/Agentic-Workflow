# FILE: 10_10/l1.py
"""
Unified L1 Planning Layer (v10_10)
==================================

This is the v10_10 refactor of the v10_9 L1 planners.

In v10_10:

    • L1 produces ONLY plans.
    • NO LLM calls occur at L1.
    • NO cross-layer work (no execution, no RAG, no QA, no safety).
    • NO meta-learning logic.
    • NO profile objects (FramingProfile, ContextProfile, etc.)
    • NO PlanObject.
    • NO multi-mode entrypoint.

L1 produces a SINGLE object:
    WorkflowPlanBundle

Which contains:
    • StrategyPlan
    • RAGPlan
    • DraftingPlan
    • QAPlan
    • SafetyPlan
    • RoutingHint

This is the only output L2/L3 will consume.

The job_text and resume_text come from:
    job.posting_text
    resume.summary / experience
"""

from __future__ import annotations

from typing import List

from models import (
    JobInput,
    ResumeInput,
    WorkflowConfig,
    RoutingHint,
    StrategyPlan,
    StrategyStep,
    RAGPlan,
    RAGQueryHint,
    DraftingPlan,
    DraftSectionPlan,
    QAPlan,
    QACheck,
    SafetyPlan,
    SafetyCheck,
    WorkflowPlanBundle,
)
from routing import classify_complexity
from meta_profile import MetaProfileSnapshot


# =============================================================================
# Helper: extract plain text from job + resume
# =============================================================================

def _extract_resume_text(resume: ResumeInput) -> str:
    """
    Combine summary + experience sections into a plain text block.
    Used for complexity estimation.
    """
    parts: List[str] = []
    if resume.summary:
        parts.append(resume.summary)

    for sec in resume.experience_sections:
        # Sec is dict-like; pull common keys if present.
        for k in ("impact_summary", "description", "details", "summary"):
            if k in sec:
                parts.append(str(sec[k]))

    return "\n".join(parts)


# =============================================================================
# L1 Planning
# =============================================================================

def build_workflow_plan_bundle(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    meta_profile: MetaProfileSnapshot | None,
    routing_policy,
    prompt_registry,
) -> WorkflowPlanBundle:
    """
    Main planning function for v10_10.

    Steps:
        1. Estimate complexity using classify_complexity()
        2. Build RoutingHint
        3. Build StrategyPlan
        4. Build RAGPlan
        5. Build DraftingPlan
        6. Build QAPlan
        7. Build SafetyPlan
        8. Return WorkflowPlanBundle
    """

    # Extract job/resume text for complexity estimation
    job_text = job.posting_text
    resume_text = _extract_resume_text(resume)

    complexity = classify_complexity(
        job=job, resume=resume, config=config, meta_profile=meta_profile
    )

    # ---------------------------------------------------------------------
    # Routing hint for downstream layers
    # ---------------------------------------------------------------------
    routing_hint = RoutingHint(
        complexity=complexity,
        cost_budget=config.cost_budget,
        latency_slo_ms=config.latency_slo_ms,
        safety_sensitivity=config.safety_sensitivity,
        drafting_depth=config.drafting_depth,
    )

    # ---------------------------------------------------------------------
    # Strategy Plan
    # ---------------------------------------------------------------------
    strategy_steps = [
        StrategyStep(id="analyze_role", order=1, description="Analyze job role and seniority."),
        StrategyStep(id="map_resume", order=2, description="Identify strongest experience alignment."),
        StrategyStep(id="outline_strategy", order=3, description="Define high-level positioning strategy."),
    ]

    strategy_plan = StrategyPlan(
        complexity=complexity,
        routing_hint=routing_hint,
        steps=strategy_steps,
    )

    # ---------------------------------------------------------------------
    # RAG Plan
    # ---------------------------------------------------------------------
    rag_hints = [
        RAGQueryHint(
            id="job_core",
            description="Extract core job requirements.",
            focus="job",
            max_chunks=config.rag_max_job_chunks,
            importance=1.0,
        ),
        RAGQueryHint(
            id="resume_alignment",
            description="Extract resume achievements relevant to job alignment.",
            focus="resume",
            max_chunks=config.rag_max_resume_chunks,
            importance=1.0,
        ),
    ]

    if config.rag_require_hybrid:
        rag_hints.append(
            RAGQueryHint(
                id="hybrid_context",
                description="Retrieve hybrid JD+resume alignment signals.",
                focus="hybrid",
                max_chunks=config.rag_max_hybrid_chunks,
                importance=0.8,
            )
        )

    rag_plan = RAGPlan(
        hints=rag_hints,
        allow_hyde=config.rag_allow_hyde,
        require_hybrid=config.rag_require_hybrid,
    )

    # ---------------------------------------------------------------------
    # Drafting Plan
    # ---------------------------------------------------------------------
    # Minimal draft structure; L2 fills all content.
    draft_sections = [
        DraftSectionPlan(id="header", title="Header", required=True, max_tokens=256, priority=1.0),
        DraftSectionPlan(id="summary", title="Summary", required=True, max_tokens=512, priority=1.0),
        DraftSectionPlan(id="experience", title="Experience", required=True, max_tokens=1024, priority=1.0),
        DraftSectionPlan(id="skills", title="Skills", required=True, max_tokens=512, priority=0.8),
    ]

    # Optional projects section for technical roles
    if "engineer" in job.title.lower() or "data" in job.title.lower():
        draft_sections.append(
            DraftSectionPlan(id="projects", title="Projects", required=False, max_tokens=768, priority=0.6)
        )

    drafting_plan = DraftingPlan(
        mode="balanced",
        sections=draft_sections,
        target_tone=config.target_tone,
        target_length_tokens=config.target_total_tokens,
    )

    # ---------------------------------------------------------------------
    # QA Plan
    # ---------------------------------------------------------------------
    qa_checks = [
        QACheck(id="jd_alignment", description="Check resume alignment with job description.", category="alignment"),
        QACheck(id="keyword_coverage", description="Check key term coverage.", category="coverage"),
        QACheck(id="resume_consistency", description="Ensure factual consistency across drafted sections.", category="consistency"),
    ]

    if complexity.value in ("medium", "high"):
        qa_checks.append(
            QACheck(
                id="rag_alignment",
                description="Ensure RAG evidence matches drafted content.",
                category="rag",
                severity=2,
            )
        )

    qa_plan = QAPlan(checks=qa_checks)

    # ---------------------------------------------------------------------
    # Safety Plan
    # ---------------------------------------------------------------------
    safety_checks = [
        SafetyCheck(
            id="pii_detection",
            description="Check for presence of PII.",
            category="pii",
            severity=2,
        ),
        SafetyCheck(
            id="policy_violations",
            description="Check for disallowed or harmful content.",
            category="policy",
            severity=2,
        ),
        SafetyCheck(
            id="professionalism",
            description="Ensure output meets professional tone.",
            category="professionalism",
            severity=1,
        ),
    ]

    safety_plan = SafetyPlan(checks=safety_checks)

    # ---------------------------------------------------------------------
    # Bundle all plans
    # ---------------------------------------------------------------------
    return WorkflowPlanBundle(
        strategy=strategy_plan,
        rag=rag_plan,
        drafting=drafting_plan,
        qa=qa_plan,
        safety=safety_plan,
        routing_hint=routing_hint,
    )
