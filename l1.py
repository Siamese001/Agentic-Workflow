# FILE: 10_10/l1.py
"""
Unified L1 Planning Layer (v10_10 · Phase 3)
===========================================

Responsibilities (L1 only):

    • Interpret workflow inputs (job, resume, workflow config).
    • Look up the active execution profile (G1–G3) using the meta-profile.
    • Choose complexity and reasoning mode hints for downstream layers.
    • Construct typed plans:

        – StrategyPlan
        – RAGPlan
        – DraftingPlan
        – QAPlan
        – SafetyPlan
        – RoutingHint

    • Bundle the above into a WorkflowPlanBundle for L2/L3/L4/L5.

Strict layer constraints:

    • NO LLM calls.
    • NO retrieval / ranking.
    • NO DAG orchestration.
    • NO state mutation or safety enforcement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from models import (
    ComplexityLevel,
    DraftingMode,
    ReasoningMode,
    JobInput,
    ResumeInput,
    WorkflowConfig,
    ExecutionProfile,
    RoutingHint,
    StrategyStep,
    StrategyPlan,
    RAGQueryHint,
    RAGPlan,
    DraftSectionPlan,
    DraftingPlan,
    QACheck,
    QAPlan,
    SafetyCheck,
    SafetyPlan,
    WorkflowPlanBundle,
)
from config_profiles_v10_10 import ExecutionProfileSpec, get_profile
from meta_profile import MetaProfileSnapshot


# =============================================================================
# Helpers: text extraction
# =============================================================================


def _normalize_text(value: Optional[str]) -> str:
    if not value:
        return ""
    return str(value).strip()


def _extract_job_text(job: JobInput) -> str:
    """
    Aggregate job fields into a single planning surface.
    """
    parts: List[str] = []
    parts.append(_normalize_text(job.title))
    parts.append(_normalize_text(job.role_type))
    parts.append(_normalize_text(job.seniority))
    parts.append(_normalize_text(job.posting_text))
    if job.requirements:
        parts.append(" ".join(str(r) for r in job.requirements))
    return "\n".join(p for p in parts if p)


def _extract_resume_text(resume: ResumeInput) -> str:
    """
    Aggregate resume fields into a single planning surface.
    """
    parts: List[str] = []
    parts.append(_normalize_text(resume.summary))

    for section in resume.experience_sections or []:
        for key in ("impact_summary", "summary", "description", "details"):
            if key in section and section[key]:
                parts.append(str(section[key]))

    if resume.skills:
        parts.append(" ".join(str(s) for s in resume.skills))

    if resume.projects:
        for proj in resume.projects:
            if isinstance(proj, dict):
                parts.append(str(proj.get("summary") or proj.get("description") or ""))
            else:
                parts.append(str(proj))

    return "\n".join(p for p in parts if p)


# =============================================================================
# Helpers: meta-profile mapping
# =============================================================================


def _map_meta_profile_to_routing_hint(meta_profile: Optional[MetaProfileSnapshot]) -> Dict[str, Any]:
    """
    Convert MetaProfileSnapshot into a simple dict used as RoutingHint.metadata.
    """
    if meta_profile is None:
        return {}

    return {
        "active_profile_id": meta_profile.active_profile_id,
        "prefers_anthropic": meta_profile.prefers_anthropic,
        "prefers_openai": meta_profile.prefers_openai,
        "prefers_fast_models": meta_profile.prefers_fast_models,
        "reasoning_mode_hint": meta_profile.reasoning_mode_hint,
        "qa_failure_rate_last_10": meta_profile.qa_failure_rate_last_10,
        "correction_rate_last_10": meta_profile.correction_rate_last_10,
        "extra_qa_passes": meta_profile.extra_qa_passes,
        "reinforce_strictness": meta_profile.reinforce_strictness,
        "elevated_caution": meta_profile.elevated_caution,
        "hil_preferred": meta_profile.hil_preferred,
    }


# =============================================================================
# Helpers: complexity and reasoning mode
# =============================================================================


def _classify_complexity(
    job_text: str,
    resume_text: str,
    profile_spec: ExecutionProfileSpec,
    meta_profile: Optional[MetaProfileSnapshot],
) -> ComplexityLevel:
    """
    Map the combined text + profile + meta-profile signals into LOW/MEDIUM/HIGH.
    """
    total_tokens = len(job_text.split()) + len(resume_text.split())

    if total_tokens < 800:
        level: ComplexityLevel = ComplexityLevel.LOW
    elif total_tokens < 2500:
        level = ComplexityLevel.MEDIUM
    else:
        level = ComplexityLevel.HIGH

    if meta_profile is not None:
        if meta_profile.qa_failure_rate_last_10 > 0.4:
            if level is ComplexityLevel.LOW:
                level = ComplexityLevel.MEDIUM
            elif level is ComplexityLevel.MEDIUM:
                level = ComplexityLevel.HIGH

    return level


def _choose_reasoning_mode(
    profile_spec: ExecutionProfileSpec,
    meta_profile: Optional[MetaProfileSnapshot],
) -> ReasoningMode:
    """
    Choose the reasoning mode for this workflow.
    """
    mode = profile_spec.reasoning_mode

    if meta_profile is not None:
        hint = (meta_profile.reasoning_mode_hint or "").lower()
        if hint == "tot":
            mode = ReasoningMode.TOT
        elif hint == "react":
            mode = ReasoningMode.REACT

    return mode


def _to_execution_profile(spec: ExecutionProfileSpec) -> ExecutionProfile:
    """
    Map an ExecutionProfileSpec (config) into the simpler ExecutionProfile
    model used at L1 planning time.
    """
    return ExecutionProfile(
        name=spec.id,
        description=spec.description,
        retrieval=spec.retrieval,
        metadata={
            "safety_tier": spec.safety_tier.value,
            "model_tier": spec.model_tier.value,
            "max_cost_usd": spec.max_cost_usd,
            "max_latency_ms": spec.max_latency_ms,
            "qa_council_size": spec.qa_council_size,
            "enable_correction_loop": spec.enable_correction_loop,
            "max_corrections": spec.max_corrections,
            "rag_allow_hyde": spec.rag_allow_hyde,
            "hyde_model_tier": spec.hyde_model_tier,
            "routing_telemetry_mode": spec.routing_telemetry_mode,
        },
    )


# =============================================================================
# Builders: StrategyPlan, RAGPlan, DraftingPlan, QAPlan, SafetyPlan
# =============================================================================


def _build_strategy_plan(
    job: JobInput,
    resume: ResumeInput,
    complexity: ComplexityLevel,
) -> StrategyPlan:
    """
    Build a simple, interpretable strategy plan.
    """
    steps: List[StrategyStep] = []
    order = 1

    steps.append(
        StrategyStep(
            id="clarify_objective",
            order=order,
            description="Clarify the target role, seniority, and core value proposition.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="analyze_job",
            order=order,
            description="Analyze the job posting to extract key requirements and signals.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="analyze_resume",
            order=order,
            description="Analyze the resume to extract strengths, gaps, and transferrable skills.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="draft_core_sections",
            order=order,
            description="Draft core sections (Summary, Experience, Skills) tailored to the job.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="refine_and_polish",
            order=order,
            description="Refine phrasing, quantify impact, and ensure coherence across sections.",
        )
    )

    return StrategyPlan(
        steps=steps,
        complexity=complexity,
    )


def _build_rag_plan(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    profile_spec: ExecutionProfileSpec,
    complexity: ComplexityLevel,
) -> RAGPlan:
    """
    Build a RAGPlan describing which retrieval surfaces to use.
    """
    max_hits = profile_spec.retrieval.max_hits

    job_chunks = min(config.rag_max_job_chunks, max_hits)
    resume_chunks = min(config.rag_max_resume_chunks, max_hits)
    hybrid_chunks = min(config.rag_max_hybrid_chunks, max_hits)

    hints: List[RAGQueryHint] = [
        RAGQueryHint(
            id="job_core",
            description="Extract core job requirements and responsibilities.",
            focus="job",
            max_chunks=job_chunks,
            importance=1.0,
        ),
        RAGQueryHint(
            id="resume_core",
            description="Extract core resume experience and impact statements.",
            focus="resume",
            max_chunks=resume_chunks,
            importance=1.0,
        ),
        RAGQueryHint(
            id="hybrid_overlap",
            description="Retrieve hybrid signals to align resume content tightly with the job.",
            focus="hybrid",
            max_chunks=hybrid_chunks,
            importance=1.1 if complexity is ComplexityLevel.HIGH else 1.0,
        ),
    ]

    allow_hyde = config.rag_allow_hyde
    require_hybrid = getattr(config, "rag_require_hybrid", False) or profile_spec.retrieval.strategy == "hybrid"

    return RAGPlan(hints=hints, allow_hyde=allow_hyde, require_hybrid=require_hybrid)


def _select_drafting_mode(
    job: JobInput,
    resume: ResumeInput,
    complexity: ComplexityLevel,
) -> DraftingMode:
    """
    Choose drafting mode (e.g., bullet-heavy vs narrative).
    """
    seniority = (job.seniority or "").lower()
    if any(k in seniority for k in ("director", "vp", "chief", "head")):
        return DraftingMode.NARRATIVE

    if complexity is ComplexityLevel.LOW:
        return DraftingMode.BULLET_HEAVY

    return DraftingMode.BALANCED


def _build_drafting_plan(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    complexity: ComplexityLevel,
) -> DraftingPlan:
    """
    Build a DraftingPlan describing which sections to generate.
    """
    sections: List[DraftSectionPlan] = []

    sections.append(
        DraftSectionPlan(
            id="summary",
            title="Summary",
            required=True,
            max_tokens=256,
            priority=1.0,
        )
    )

    sections.append(
        DraftSectionPlan(
            id="experience",
            title="Experience",
            required=True,
            max_tokens=1024,
            priority=1.0,
        )
    )

    sections.append(
        DraftSectionPlan(
            id="skills",
            title="Skills",
            required=False,
            max_tokens=256,
            priority=0.8,
        )
    )

    seniority = (job.seniority or "").lower()
    if any(k in seniority for k in ("director", "vp", "chief", "head")):
        sections.append(
            DraftSectionPlan(
                id="leadership",
                title="Leadership Highlights",
                required=False,
                max_tokens=768,
                priority=0.6,
            )
        )

    drafting_mode = _select_drafting_mode(job, resume, complexity)

    return DraftingPlan(
        sections=sections,
        mode=drafting_mode,
        target_tone=config.target_tone,
    )


def _build_qa_plan(
    profile_spec: ExecutionProfileSpec,
    meta_profile: Optional[MetaProfileSnapshot],
    complexity: ComplexityLevel,
) -> QAPlan:
    """
    Build a QAPlan describing which checks to run.
    """
    depth = profile_spec.qa_depth
    checks: List[QACheck] = []

    checks.append(
        QACheck(
            id="alignment_to_job",
            description="Check that the resume content aligns with job requirements.",
            severity="high",
        )
    )
    checks.append(
        QACheck(
            id="hallucinations",
            description="Check for claims not supported by candidate history.",
            severity="high",
        )
    )
    checks.append(
        QACheck(
            id="clarity",
            description="Check for clarity and readability issues.",
            severity="medium",
        )
    )

    if depth in ("medium", "deep") or complexity is ComplexityLevel.MEDIUM:
        checks.append(
            QACheck(
                id="impact_quantification",
                description="Check for quantified impact where feasible.",
                severity="medium",
            )
        )

    if depth == "deep" or complexity is ComplexityLevel.HIGH:
        checks.append(
            QACheck(
                id="consistency",
                description="Check for consistency across sections and dates.",
                severity="medium",
            )
        )

    if meta_profile is not None and meta_profile.extra_qa_passes:
        checks.append(
            QACheck(
                id="extra_pass",
                description="Extra QA pass requested by meta-profile.",
                severity="low",
            )
        )

    return QAPlan(checks=checks)


def _build_safety_plan(
    profile_spec: ExecutionProfileSpec,
    meta_profile: Optional[MetaProfileSnapshot],
) -> SafetyPlan:
    """
    Build a SafetyPlan describing which safety / policy checks to run.
    """
    checks: List[SafetyCheck] = []

    checks.append(
        SafetyCheck(
            id="privacy",
            description="Check for privacy violations or sensitive PII.",
            severity="high",
        )
    )
    checks.append(
        SafetyCheck(
            id="fairness",
            description="Check for fairness / bias issues.",
            severity="medium",
        )
    )

    if profile_spec.safety_tier in ("strict", "debug"):
        checks.append(
            SafetyCheck(
                id="debug_policy",
                description="Extra debug/policy checks for strict tiers.",
                severity="low",
            )
        )

    if meta_profile is not None and meta_profile.elevated_caution:
        checks.append(
            SafetyCheck(
                id="elevated_caution",
                description="Meta-profile requested elevated safety caution.",
                severity="high",
            )
        )

    return SafetyPlan(checks=checks)


# =============================================================================
# Public API: build_workflow_plan_bundle
# =============================================================================


def build_workflow_plan_bundle(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    meta_profile: Optional[MetaProfileSnapshot] = None,
) -> WorkflowPlanBundle:
    """
    Top-level L1 entrypoint.
    """
    profile_spec: ExecutionProfileSpec = get_profile(config.profile_id)
    execution_profile: ExecutionProfile = _to_execution_profile(profile_spec)

    job_text = _extract_job_text(job)
    resume_text = _extract_resume_text(resume)

    complexity = _classify_complexity(
        job_text=job_text,
        resume_text=resume_text,
        profile_spec=profile_spec,
        meta_profile=meta_profile,
    )
    reasoning_mode = _choose_reasoning_mode(profile_spec, meta_profile)

    strategy_plan = _build_strategy_plan(job, resume, complexity)
    rag_plan = _build_rag_plan(job, resume, config, profile_spec, complexity)
    drafting_plan = _build_drafting_plan(job, resume, config, complexity)
    qa_plan = _build_qa_plan(profile_spec, meta_profile, complexity)
    safety_plan = _build_safety_plan(profile_spec, meta_profile)

    routing_hint = RoutingHint(
        complexity=complexity,
        reasoning_mode=reasoning_mode,
        execution_profile=execution_profile,
        meta=_map_meta_profile_to_routing_hint(meta_profile),
    )

    return WorkflowPlanBundle(
        strategy=strategy_plan,
        rag=rag_plan,
        drafting=drafting_plan,
        qa=qa_plan,
        safety=safety_plan,
        routing_hint=routing_hint,
    )
