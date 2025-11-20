# FILE: 10_10/l1.py
"""
Unified L1 Planning Layer (v10_10 · Phase 1)
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
    • NO tool execution.
    • NO state mutation (no persistence, no telemetry writes).
    • NO DAG orchestration or retries (that is L3+).
    • NO safety enforcement (that is L5); L1 only *plans* safety surfaces.

This module restores the richer planning behavior from v10_8 / v10_9
while conforming to the Phase 0 models and configuration system.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

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
    Aggregate job text fields into a single planning surface.
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
        # section is dict-like
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
# Helpers: profile + meta-profile interpretation
# =============================================================================


_DEFAULT_PROFILE_ID = "RESUME_HIGH_QUALITY"


def _resolve_profile_id(meta_profile: Optional[MetaProfileSnapshot]) -> str:
    """
    Determine which execution profile ID to use.

    Phase 1 behavior:
        • Use meta_profile.active_profile_id when available.
        • Fallback to a stable default profile for resumes.
    """
    if meta_profile is not None and getattr(meta_profile, "active_profile_id", None):
        return str(meta_profile.active_profile_id)
    return _DEFAULT_PROFILE_ID


def _to_execution_profile(spec: ExecutionProfileSpec) -> ExecutionProfile:
    """
    Map an ExecutionProfileSpec (Phase 0 config) into the simpler
    ExecutionProfile model used at L1 planning time.
    """
    # SafetyTier / ModelTier are enums in config_profiles; normalize to strings.
    safety_tier = spec.safety_tier.value if hasattr(spec.safety_tier, "value") else str(spec.safety_tier)
    model_tier = spec.model_tier.value if hasattr(spec.model_tier, "value") else str(spec.model_tier)

    return ExecutionProfile(
        id=spec.id,
        description=spec.description,
        reasoning_mode=spec.reasoning_mode,
        target_model_tier=model_tier,
        max_cost_usd=spec.max_cost_usd,
        max_latency_ms=spec.max_latency_ms,
        safety_tier=safety_tier,
    )


def _meta_rates(meta_profile: Optional[MetaProfileSnapshot]) -> Tuple[float, float]:
    """
    Extract QA failure and correction rates from the snapshot, with safe defaults.
    """
    if meta_profile is None:
        return 0.0, 0.0

    qa_rate = float(getattr(meta_profile, "qa_failure_rate_last_10", 0.0) or 0.0)
    corr_rate = float(getattr(meta_profile, "correction_rate_last_10", 0.0) or 0.0)
    return qa_rate, corr_rate


def _meta_flags(meta_profile: Optional[MetaProfileSnapshot]) -> Dict[str, bool]:
    """
    Extract boolean meta-flags that influence planning depth.
    """
    if meta_profile is None:
        return {
            "elevated_caution": False,
            "extra_qa_passes": False,
            "reinforce_strictness": False,
            "hil_preferred": False,
        }

    def _flag(name: str, default: bool = False) -> bool:
        return bool(getattr(meta_profile, name, default))

    return {
        "elevated_caution": _flag("elevated_caution"),
        "extra_qa_passes": _flag("extra_qa_passes"),
        "reinforce_strictness": _flag("reinforce_strictness"),
        "hil_preferred": _flag("hil_preferred"),
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

    This is intentionally simple and deterministic; richer behavior can be
    added later without changing the public contract.
    """
    total_tokens = len(job_text.split()) + len(resume_text.split())

    if total_tokens < 800:
        level: ComplexityLevel = ComplexityLevel.LOW
    elif total_tokens < 2500:
        level = ComplexityLevel.MEDIUM
    else:
        level = ComplexityLevel.HIGH

    # Execution profile nudges
    if profile_spec.reasoning_mode in (ReasoningMode.TOT, ReasoningMode.REACT):
        # Tree-of-thought and ReAct usually deserve at least MEDIUM.
        if level == ComplexityLevel.LOW:
            level = ComplexityLevel.MEDIUM

    safety_tier = profile_spec.safety_tier.value if hasattr(profile_spec.safety_tier, "value") else str(
        profile_spec.safety_tier
    )
    if "strict" in safety_tier.lower() and level == ComplexityLevel.LOW:
        level = ComplexityLevel.MEDIUM

    # Meta-profile nudges
    qa_rate, _ = _meta_rates(meta_profile)
    flags = _meta_flags(meta_profile)

    if qa_rate > 0.4 or flags["elevated_caution"] or flags["reinforce_strictness"]:
        # Increase complexity one notch to allocate more QA/safety effort.
        if level == ComplexityLevel.LOW:
            level = ComplexityLevel.MEDIUM
        elif level == ComplexityLevel.MEDIUM:
            level = ComplexityLevel.HIGH

    return level


def _select_drafting_mode(job: JobInput, resume: ResumeInput, complexity: ComplexityLevel) -> DraftingMode:
    """
    Choose a drafting mode based on role type, seniority, and complexity.
    """
    title = (job.title or "").lower()
    role_type = (job.role_type or "").lower()
    seniority = (job.seniority or "").lower()

    is_exec = any(k in seniority for k in ("vp", "vice president", "svp", "director", "chief", "head"))
    is_technical = any(k in role_type for k in ("engineer", "developer", "data", "ml", "ai"))

    if is_exec and complexity is ComplexityLevel.HIGH:
        return DraftingMode.HYBRID_EXEC_SUMMARY
    if is_technical and complexity is ComplexityLevel.MEDIUM:
        return DraftingMode.BULLET_HEAVY

    # Default balanced mode
    return DraftingMode.BALANCED


# =============================================================================
# Helpers: plan builders
# =============================================================================


def _build_routing_hint(
    config: WorkflowConfig,
    profile_spec: ExecutionProfileSpec,
    complexity: ComplexityLevel,
) -> RoutingHint:
    """
    Build a RoutingHint that reconciles workflow-level config with the
    global execution profile.
    """
    cost_budget = min(config.cost_budget, profile_spec.max_cost_usd)
    latency_slo_ms = min(config.latency_slo_ms, profile_spec.max_latency_ms)

    # Safety sensitivity is at least what the workflow requests, and may be
    # bumped for strict safety tiers.
    safety_sensitivity = config.safety_sensitivity
    safety_tier = profile_spec.safety_tier.value if hasattr(profile_spec.safety_tier, "value") else str(
        profile_spec.safety_tier
    )
    if "strict" in safety_tier.lower():
        safety_sensitivity = max(safety_sensitivity, 4)

    drafting_depth = max(config.drafting_depth, profile_spec.drafting_depth)

    return RoutingHint(
        complexity=complexity,
        cost_budget=cost_budget,
        latency_slo_ms=latency_slo_ms,
        safety_sensitivity=safety_sensitivity,
        drafting_depth=drafting_depth,
    )


def _build_strategy_plan(
    job: JobInput,
    resume: ResumeInput,
    complexity: ComplexityLevel,
) -> StrategyPlan:
    """
    Build a simple, interpretable strategy plan.

    The goal is to preserve v10_8/v10_9 behavior (clarify → analyze → draft → refine)
    while keeping the structure strictly typed via StrategyStep.
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
            description="Analyze job description to extract required skills, responsibilities, and signals.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="analyze_resume",
            order=order,
            description="Analyze resume to identify strengths, gaps, and transferable achievements.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="plan_structure",
            order=order,
            description="Plan resume structure and section emphasis based on role and seniority.",
        )
    )
    order += 1
    steps.append(
        StrategyStep(
            id="plan_personalization",
            order=order,
            description="Plan personalization strategy (company, domain, and recruiter-facing signals).",
        )
    )

    # For higher complexity workflows, add an explicit refinement step.
    if complexity is ComplexityLevel.HIGH:
        order += 1
        steps.append(
            StrategyStep(
                id="plan_refinement",
                order=order,
                description="Plan additional refinement passes for QA, safety, and tailoring depth.",
            )
        )

    return StrategyPlan(steps=steps, complexity=complexity)


def _build_rag_plan(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    profile_spec: ExecutionProfileSpec,
    complexity: ComplexityLevel,
) -> RAGPlan:
    """
    Build a RAGPlan describing which retrieval surfaces to use.

    Phase 1 focuses on shaping the hints and hybrid/HyDE knobs; actual
    retrieval/ranking behavior is implemented in retrieval.py / ranking.py.
    """
    max_hits = profile_spec.retrieval.max_hits

    job_chunks = min(config.rag_max_job_chunks, max_hits)
    resume_chunks = min(config.rag_max_resume_chunks, max_hits)
    hybrid_chunks = min(config.rag_max_hybrid_chunks, max_hits)

    hints: List[RAGQueryHint] = [
        RAGQueryHint(
            id="job_core",
            description="Extract core job requirements, responsibilities, and must-have keywords.",
            focus="job",
            max_chunks=job_chunks,
            importance=1.0,
        ),
        RAGQueryHint(
            id="resume_core",
            description="Extract high-signal resume bullets and achievements relevant to the job.",
            focus="resume",
            max_chunks=resume_chunks,
            importance=0.9,
        ),
        RAGQueryHint(
            id="hybrid_alignment",
            description="Retrieve hybrid signals to align resume content tightly with the job.",
            focus="hybrid",
            max_chunks=hybrid_chunks,
            importance=1.1 if complexity is ComplexityLevel.HIGH else 1.0,
        ),
    ]

    allow_hyde = config.rag_allow_hyde
    require_hybrid = config.rag_require_hybrid or profile_spec.retrieval.strategy == "hybrid"

    return RAGPlan(hints=hints, allow_hyde=allow_hyde, require_hybrid=require_hybrid)


def _build_drafting_plan(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    profile_spec: ExecutionProfileSpec,
    complexity: ComplexityLevel,
) -> DraftingPlan:
    """
    Build a DraftingPlan describing which sections to generate.
    """
    sections: List[DraftSectionPlan] = [
        DraftSectionPlan(
            id="header",
            title="Header",
            required=True,
            max_tokens=256,
            priority=1.0,
        ),
        DraftSectionPlan(
            id="summary",
            title="Summary",
            required=True,
            max_tokens=512,
            priority=1.0,
        ),
        DraftSectionPlan(
            id="experience",
            title="Experience",
            required=True,
            max_tokens=1024,
            priority=1.0,
        ),
        DraftSectionPlan(
            id="skills",
            title="Skills",
            required=True,
            max_tokens=512,
            priority=0.8,
        ),
    ]

    title = (job.title or "").lower()
    role_type = (job.role_type or "").lower()
    is_technical = any(k in role_type for k in ("engineer", "developer", "data", "ml", "ai"))

    if is_technical or (resume.projects and len(resume.projects) > 0):
        sections.append(
            DraftSectionPlan(
                id="projects",
                title="Projects",
                required=False,
                max_tokens=768,
                priority=0.7,
            )
        )

    # For very senior roles, add an optional "Leadership Highlights" section.
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

    Depth of QA is influenced by:
        • profile_spec.qa_depth ("shallow" | "medium" | "deep")
        • complexity (LOW/MEDIUM/HIGH)
        • meta-profile flags (e.g., elevated_caution, extra_qa_passes)
    """
    qa_depth = getattr(profile_spec, "qa_depth", "medium") or "medium"
    flags = _meta_flags(meta_profile)

    checks: List[QACheck] = []

    # Always-on checks
    checks.append(
        QACheck(
            id="jd_alignment",
            description="Check alignment between resume content and job description.",
            severity=4,
            enabled=True,
        )
    )
    checks.append(
        QACheck(
            id="keyword_coverage",
            description="Check coverage of high-signal keywords and skills.",
            severity=3,
            enabled=True,
        )
    )

    # Depth-dependent checks
    if qa_depth in ("medium", "deep") or complexity is not ComplexityLevel.LOW:
        checks.append(
            QACheck(
                id="factual_consistency",
                description="Check for internal consistency across sections and bullets.",
                severity=4,
                enabled=True,
            )
        )

    if qa_depth == "deep" or complexity is ComplexityLevel.HIGH or flags["extra_qa_passes"]:
        checks.append(
            QACheck(
                id="hallucination_risk",
                description="Check for unsupported claims or hallucinated details.",
                severity=5,
                enabled=True,
            )
        )
        checks.append(
            QACheck(
                id="tone_voice",
                description="Check that tone and voice match the target role and seniority.",
                severity=2,
                enabled=True,
            )
        )

    return QAPlan(checks=checks)


def _build_safety_plan(
    profile_spec: ExecutionProfileSpec,
    meta_profile: Optional[MetaProfileSnapshot],
) -> SafetyPlan:
    """
    Build a SafetyPlan describing which safety checks to run.

    Actual enforcement happens in L5; L1 only specifies which checks
    should be active for a given workflow.
    """
    safety_tier = profile_spec.safety_tier.value if hasattr(profile_spec.safety_tier, "value") else str(
        profile_spec.safety_tier
    )
    flags = _meta_flags(meta_profile)

    checks: List[SafetyCheck] = []

    # Baseline PII and policy checks for all tiers.
    checks.append(
        SafetyCheck(
            id="pii_detection",
            description="Scan for PII (emails, phone numbers, addresses) that should be redacted or handled carefully.",
            category="pii",
            enabled=True,
        )
    )
    checks.append(
        SafetyCheck(
            id="policy_compliance",
            description="Check content against high-level policy constraints.",
            category="policy",
            enabled=True,
        )
    )

    # Stricter tiers add toxicity and hallucination safety checks.
    if "strict" in safety_tier.lower() or flags["elevated_caution"] or flags["reinforce_strictness"]:
        checks.append(
            SafetyCheck(
                id="toxicity",
                description="Screen for toxic or inappropriate language.",
                category="toxicity",
                enabled=True,
            )
        )
        checks.append(
            SafetyCheck(
                id="sensitive_topics",
                description="Screen for sensitive or high-risk topics.",
                category="policy",
                enabled=True,
            )
        )

    return SafetyPlan(checks=checks)


# =============================================================================
# Public API
# =============================================================================


def build_workflow_plan_bundle(
    job: JobInput,
    resume: ResumeInput,
    config: WorkflowConfig,
    meta_profile: Optional[MetaProfileSnapshot],
    routing_policy: Any,
    prompt_registry: Any,
) -> WorkflowPlanBundle:
    """
    Main L1 planning entrypoint for v10_10 Phase 1.

    Inputs:
        • job, resume     – canonical user inputs (from models.JobInput/ResumeInput).
        • config          – workflow-level configuration (WorkflowConfig).
        • meta_profile    – MetaProfileSnapshot supplying routing/planning biases.
        • routing_policy  – reserved for future multi-agent routing (Phase 3).
        • prompt_registry – reserved for prompt ACL / governance (Phase 2).

    Output:
        • WorkflowPlanBundle – typed plan bundle for L2/L3/L4/L5.
    """
    # --------------------------------------------------------------
    # 1) Resolve execution profile and meta signals
    # --------------------------------------------------------------
    profile_id = _resolve_profile_id(meta_profile)
    profile_spec = get_profile(profile_id)
    execution_profile = _to_execution_profile(profile_spec)
    # NOTE: execution_profile is currently not returned but is used to
    # influence complexity/QA/safety planning. L2/L3 may accept it
    # explicitly in later phases.

    job_text = _extract_job_text(job)
    resume_text = _extract_resume_text(resume)

    complexity = _classify_complexity(job_text, resume_text, profile_spec, meta_profile)

    # --------------------------------------------------------------
    # 2) Build routing hint
    # --------------------------------------------------------------
    routing_hint = _build_routing_hint(config, profile_spec, complexity)

    # --------------------------------------------------------------
    # 3) Build individual plans
    # --------------------------------------------------------------
    strategy_plan = _build_strategy_plan(job, resume, complexity)
    rag_plan = _build_rag_plan(job, resume, config, profile_spec, complexity)
    drafting_plan = _build_drafting_plan(job, resume, config, profile_spec, complexity)
    qa_plan = _build_qa_plan(profile_spec, meta_profile, complexity)
    safety_plan = _build_safety_plan(profile_spec, meta_profile)

    # --------------------------------------------------------------
    # 4) Bundle and return
    # --------------------------------------------------------------
    return WorkflowPlanBundle(
        strategy=strategy_plan,
        rag=rag_plan,
        drafting=drafting_plan,
        qa=qa_plan,
        safety=safety_plan,
        routing_hint=routing_hint,
    )
