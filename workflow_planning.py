"""L1 - Planning Layer

This module provides high-level workflow planning functions that analyze
job and resume inputs to produce execution plans.

Layer: L1 (Planning/Cognition)
Responsibilities:
- Analyze job and resume complexity
- Generate workflow plans (strategy, RAG, drafting, QA, safety)
- Determine execution profiles
- Produce pure, stateless plans

Non-responsibilities:
- Execution (L2)
- Orchestration (L3)
- State management (L4)
- Policy enforcement (L5)
"""

# FILE: workflow_planning.py

from __future__ import annotations

from typing import Any, Dict, List, Optional

from core.models.models import (
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
    PromptMeta,
    ProfileInferenceResult,
    SeniorityClassifierResult,
    SkillClusterResult,
    DomainClassifierResult,
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
        parts.append(" ".join(job.requirements))

    if job.tags:
        parts.append(" ".join(job.tags))

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
            parts.append(_normalize_text(proj.get("summary")))
            parts.append(_normalize_text(proj.get("details")))

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
        # Phase-1 profile inference view (read-only routing hint metadata)
        "seniority_label": meta_profile.seniority_label,
        "domain_label": meta_profile.domain_label,
        "skill_cluster_labels": list(meta_profile.skill_cluster_labels),
    }


def _build_prompt_meta(
    profile_spec: ExecutionProfileSpec,
    meta_profile: Optional[MetaProfileSnapshot],
) -> PromptMeta:
    """Build L1 prompt-planning metadata from profile + meta-profile.

    This helper is intentionally pure and limited to assembling a PromptMeta
    structure. It does not render prompts, call tools, or touch state.
    """

    sections: List[Dict[str, Any]] = []

    # High-level conceptual sections broadly aligned with Strategy/RAG/Drafting/QA/Safety.
    sections.append({"id": "strategy", "role": "planner", "order": 0})
    sections.append({"id": "rag", "role": "retriever", "order": 1})
    sections.append({"id": "drafting", "role": "drafter", "order": 2})
    sections.append({"id": "qa", "role": "qa", "order": 3})
    sections.append({"id": "safety", "role": "safety", "order": 4})

    injection_types: List[str] = [
        "job_posting",
        "candidate_resume",
        "rag_evidence",
        "profile_inference",
        "safety_policies",
    ]

    taxonomy: Dict[str, Any] = {
        "profile_id": profile_spec.id,
        "safety_tier": getattr(profile_spec.safety_tier, "value", profile_spec.safety_tier),
        "model_tier": getattr(profile_spec.model_tier, "value", profile_spec.model_tier),
    }

    meta_bias: Dict[str, Any] = {}
    if meta_profile is not None:
        meta_bias = {
            "reasoning_mode_hint": meta_profile.reasoning_mode_hint,
            "elevated_caution": meta_profile.elevated_caution,
            "extra_qa_passes": meta_profile.extra_qa_passes,
            "prefers_fast_models": meta_profile.prefers_fast_models,
        }

    return PromptMeta(
        sections=sections,
        injection_types=injection_types,
        taxonomy=taxonomy,
        meta_bias=meta_bias,
    )


# =============================================================================
# Helpers: profile inference (restored from v10_9 semantics)
# =============================================================================


def _infer_seniority(job_text: str, resume_text: str) -> str:
    """Very small heuristic seniority inference (v10_9-compatible).

    This mirrors the v10_9 behavior where seniority was derived from
    combined job + resume text using simple keyword families.
    """

    combined = f"{job_text} {resume_text}".lower()

    senior_terms = {
        "executive": ["chief", "cxo", "svp", "evp", "executive"],
        "director": ["director", "head of", "senior director"],
        "manager": ["manager", "lead", "team lead"],
        "senior_ic": ["senior", "staff", "principal"],
        "junior": ["junior", "entry-level", "associate"],
    }

    for label, terms in senior_terms.items():
        if any(t in combined for t in terms):
            return label

    return "mid"


def _infer_domains(job_text: str, resume_text: str) -> List[str]:
    """Heuristic domain tagging from job/resume content (v10_9-compatible)."""

    text = f"{job_text} {resume_text}".lower()
    domains: List[str] = []

    if any(k in text for k in ["insurance", "actuary", "actuarial"]):
        domains.append("insurance")
    if any(k in text for k in ["bank", "credit", "loan", "trading", "broker"]):
        domains.append("financial_services")
    if any(k in text for k in ["llm", "large language model", "rag"]):
        domains.append("foundation_models")
    if any(k in text for k in ["ml", "machine learning", "deep learning"]):
        domains.append("machine_learning")
    if any(k in text for k in ["cloud", "aws", "azure", "gcp"]):
        domains.append("cloud")
    if any(k in text for k in ["data platform", "databricks", "snowflake"]):
        domains.append("data_platform")

    return sorted(set(domains))


def _infer_skill_clusters(job_text: str, resume_text: str) -> List[str]:
    """Rough skill clustering based on keyword families (v10_9-compatible)."""

    text = f"{job_text} {resume_text}".lower()
    clusters: List[str] = []

    if any(k in text for k in ["python", "pandas", "numpy"]):
        clusters.append("python_data")
    if any(k in text for k in ["pytorch", "tensorflow", "keras"]):
        clusters.append("deep_learning")
    if any(k in text for k in ["aws", "azure", "gcp"]):
        clusters.append("cloud_infra")
    if any(k in text for k in ["stakeholder", "executive", "c-suite"]):
        clusters.append("executive_communication")
    if any(k in text for k in ["roadmap", "strategy", "vision"]):
        clusters.append("strategy_product")

    return sorted(set(clusters))


def _run_profile_inference(
    job_text: str,
    resume_text: str,
    complexity: ComplexityLevel,
) -> ProfileInferenceResult:
    """Unified profile inference wrapper for L1.

    Returns a ProfileInferenceResult containing seniority/domain/skills
    plus the already-estimated ComplexityLevel. This is intentionally
    deterministic and mirrors the v10_9 heuristic behavior.
    """

    seniority_label = _infer_seniority(job_text, resume_text)
    domains = _infer_domains(job_text, resume_text)
    skill_clusters = _infer_skill_clusters(job_text, resume_text)

    seniority = SeniorityClassifierResult(label=seniority_label)

    domain = None
    if domains:
        domain = DomainClassifierResult(
            labels=domains,
            primary_label=domains[0],
        )

    skills = None
    if skill_clusters:
        skills = SkillClusterResult(
            labels=skill_clusters,
            primary_label=skill_clusters[0],
        )

    return ProfileInferenceResult(
        seniority=seniority,
        domain=domain,
        skills=skills,
        complexity=complexity,
    )


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

    # Meta-profile can bump complexity if we see elevated caution / frequent corrections.
    if meta_profile is not None:
        if meta_profile.elevated_caution or meta_profile.correction_rate_last_10 > 0.3:
            # Do not downshift, only upshift.
            if level is ComplexityLevel.LOW:
                level = ComplexityLevel.MEDIUM
            elif level is ComplexityLevel.MEDIUM:
                level = ComplexityLevel.HIGH

    # Execution profile may override to enforce a minimum complexity tier.
    if profile_spec.min_complexity is not None:
        if level.value < profile_spec.min_complexity.value:
            level = profile_spec.min_complexity

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
        if hint == "cot":
            mode = ReasoningMode.CHAIN_OF_THOUGHT
        elif hint == "tot":
            mode = ReasoningMode.TOT
        elif hint == "react":
            mode = ReasoningMode.REACT

    return mode


def _to_execution_profile(spec: ExecutionProfileSpec) -> ExecutionProfile:
    """
    Map an ExecutionProfileSpec (config) into the simpler ExecutionProfile
    model used at L1 planning time.

    This object (ExecutionProfile) is what gets carried inside RoutingHint,
    and is the primary top-level knob carrier for Phase-3 features like:
        • HYDE (rag_allow_hyde)
        • RRF strategy
        • QA council size
        • Correction loop configuration
        • Telemetry routing mode
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
# Strategy Plan
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
            description="Analyze the resume to identify strengths, gaps, and leverage points.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="alignment_plan",
            order=order,
            description="Plan how to align resume content and emphasis with job requirements.",
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


# =============================================================================
# RAG Plan
# =============================================================================


def _build_rag_plan(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    profile_spec: ExecutionProfileSpec,
    complexity: ComplexityLevel,
) -> RAGPlan:
    """
    Build a RAGPlan describing which retrieval surfaces to use.

    Phase-3 invariants:
        • HYDE is controlled by config/profile flags (rag_allow_hyde).
        • Hybrid vs non-hybrid is determined by RetrievalConfig.strategy.
        • Hints describe job / resume / hybrid focus surfaces.
        • strategy_hint links to the configured retrieval strategy, which
          downstream retrieval/ranking can use.
    """
    max_hits = profile_spec.retrieval.max_hits

    job_chunks = min(config.rag_max_job_chunks, max_hits)
    resume_chunks = min(config.rag_max_resume_chunks, max_hits)
    hybrid_chunks = min(config.rag_max_hybrid_chunks, max_hits)

    hints: List[RAGQueryHint] = [
        RAGQueryHint(
            id="job_core",
            description="Extract core job requirements and key phrases.",
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
    require_hybrid = (
        getattr(config, "rag_require_hybrid", False)
        or profile_spec.retrieval.strategy == "hybrid"
    )

    return RAGPlan(
        hints=hints,
        allow_hyde=allow_hyde,
        require_hybrid=require_hybrid,
        strategy_hint=profile_spec.retrieval.strategy,
    )


# =============================================================================
# Drafting Plan
# =============================================================================


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
            max_tokens=config.drafting_experience_max_tokens,
            priority=1.0,
        )
    )

    sections.append(
        DraftSectionPlan(
            id="skills",
            title="Skills",
            required=True,
            max_tokens=256,
            priority=0.8,
        )
    )

    if complexity is ComplexityLevel.HIGH:
        sections.append(
            DraftSectionPlan(
                id="projects",
                title="Projects",
                required=False,
                max_tokens=512,
                priority=0.7,
            )
        )

    mode = _select_drafting_mode(job, resume, complexity)

    return DraftingPlan(
        sections=sections,
        mode=mode,
    )


# =============================================================================
# QA Plan
# =============================================================================


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

    try:
        depth_value = int(getattr(depth, "value", depth))
    except (TypeError, ValueError):
        depth_value = 1

    if depth_value >= 2:
        checks.append(
            QACheck(
                id="tone_appropriateness",
                description="Check that tone and style are appropriate for the target role.",
                severity="medium",
            )
        )

    if depth_value >= 3:
        checks.append(
            QACheck(
                id="consistency",
                description="Check for internal consistency across sections and roles.",
                severity="medium",
            )
        )

    # Meta-profile can request extra QA passes.
    if meta_profile is not None and meta_profile.extra_qa_passes > 0:
        checks.append(
            QACheck(
                id="extra_pass_meta_profile",
                description="Extra QA pass requested due to recent failures.",
                severity="medium",
            )
        )

    return QAPlan(checks=checks, depth=depth)


# =============================================================================
# Safety Plan
# =============================================================================


def _build_safety_plan(
    profile_spec: ExecutionProfileSpec,
    meta_profile: Optional[MetaProfileSnapshot],
) -> SafetyPlan:
    """
    Build a SafetyPlan describing which safety checks to run.
    """
    checks: List[SafetyCheck] = []

    checks.append(
        SafetyCheck(
            id="pii",
            description="Detect and flag any PII or sensitive personal information.",
            severity="high",
        )
    )
    checks.append(
        SafetyCheck(
            id="policy_violations",
            description="Detect potential policy violations (disallowed claims, discrimination, etc.).",
            severity="high",
        )
    )

    try:
        safety_tier_value = int(
            getattr(profile_spec.safety_tier, "value", profile_spec.safety_tier)
        )
    except (TypeError, ValueError):
        safety_tier_value = 1

    if safety_tier_value >= 2:
        checks.append(
            SafetyCheck(
                id="tone",
                description="Ensure tone is professional and non-inflammatory.",
                severity="medium",
            )
        )

    if meta_profile is not None and meta_profile.elevated_caution:
        checks.append(
            SafetyCheck(
                id="elevated_caution",
                description="Apply stricter thresholds due to elevated caution state.",
                severity="high",
            )
        )

    return SafetyPlan(checks=checks, tier=profile_spec.safety_tier)


# =============================================================================
# Top-level entrypoint
# =============================================================================


def build_workflow_plan_bundle(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    meta_profile: Optional[MetaProfileSnapshot] = None,
    routing_policy: Any | None = None,
    prompt_registry: Any | None = None,
) -> WorkflowPlanBundle:
    """Design the full plan for how this resume will be improved.

    This function is the main entry point into the planning layer. It looks at
    the job posting, the candidate's current resume, and configuration and
    then builds a detailed plan for the rest of the workflow. The plan covers
    strategy, what to retrieve, which sections to draft, what quality checks
    to run, and which safety checks to apply.

    For a business user, this means every resume is processed according to a
    clear, pre-agreed playbook rather than ad hoc logic. That playbook helps
    keep resumes tightly aligned to the job description, ensures important
    sections like Summary, Experience, and Skills are always addressed, and
    guarantees that quality and safety reviews are part of the process instead
    of optional extras.
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

    # Phase-1: run profile inference before building plans.
    profile_inference = _run_profile_inference(
        job_text=job_text,
        resume_text=resume_text,
        complexity=complexity,
    )

    strategy_plan = _build_strategy_plan(job, resume, complexity)
    rag_plan = _build_rag_plan(job, resume, config, profile_spec, complexity)
    drafting_plan = _build_drafting_plan(job, resume, config, complexity)
    qa_plan = _build_qa_plan(profile_spec, meta_profile, complexity)
    safety_plan = _build_safety_plan(profile_spec, meta_profile)

    prompt_meta = _build_prompt_meta(profile_spec, meta_profile)

    routing_meta = _map_meta_profile_to_routing_hint(meta_profile)
    routing_meta["profile_inference"] = profile_inference.model_dump()

    routing_hint = RoutingHint(
        complexity=complexity,
        reasoning_mode=reasoning_mode,
        execution_profile=execution_profile,
        meta=routing_meta,
    )

    return WorkflowPlanBundle(
        strategy=strategy_plan,
        rag=rag_plan,
        drafting=drafting_plan,
        qa=qa_plan,
        safety=safety_plan,
        routing_hint=routing_hint,
        prompt_meta=prompt_meta,
    )
