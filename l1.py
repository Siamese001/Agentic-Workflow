# FILE: l1.py
"""
Unified L1 Cognition Layer (v10_9) — FULL AGENTIC PLANNING

This module implements ALL L1 responsibilities for the v10_9 agentic
workflow. It is strictly *cognition-only*:

    • Performs profile inference (seniority, domain, skills).
    • Estimates task complexity and selects reasoning mode (CoT vs ToT).
    • Builds linear strategy plans (clarify → context → structure).
    • Plans RAG intents (queries, evidence targets, sources).
    • Plans drafting structure (sections, tone, personalization).
    • Plans bullet frameworks (action–metric–outcome; seniority scaling).
    • Plans QA and safety surfaces (checks, hints, escalation paths).
    • Plans meta-learning signals and logging surfaces.
    • Plans prompt-engineering constraints and governance hooks.

L1 DOES NOT:

    • Call tools, databases, or LLMs.
    • Execute retrieval, drafting, QA, or safety checks.
    • Perform orchestration / control-flow.
    • Mutate global state or storage.
    • Make final safety/policy decisions.

Instead, L1 emits typed PlanObjects which are:

    • Consumed by L2 for execution.
    • Routed by L3 in DAG-style workflows.
    • Stored and evolved by L4.
    • Evaluated and constrained by L5.

This file is designed to restore the full planning capabilities that
existed in v10_8 (per the functionality variance table) while
respecting the v10_9 layered agentic architecture and the 14 OpenAI
agentic subdomains at the highest maturity level.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Sequence, Tuple

from models import (
    PlanObject,
    FramingProfile,
    ContextProfile,
    ToolingProfile,
    SafetyOutputProfile,
    SelfCorrectionSurface,
    AccessPolicy,
)


# =============================================================================
# 1. ENUMS & SMALL TYPES
# =============================================================================


class ComplexityLevel(str, Enum):
    """Coarse-grained complexity buckets for planning."""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"


class ReasoningStrategy(str, Enum):
    """Preferred reasoning mode for L2 / downstream layers."""

    DIRECT = "direct"          # minimal CoT
    COT = "cot"                # structured chain-of-thought
    TOT = "tot"                # tree-of-thought / branching search
    COT_WITH_CRITIQUE = "cot_with_critique"
    TOT_WITH_CRITIQUE = "tot_with_critique"


@dataclass
class ProfileSignals:
    """
    Inferred profile signals from job input + resume.

    This encapsulates behavior previously implemented ad-hoc in v10_8
    planners: seniority inference, domain tagging, and skill clustering.
    """

    seniority: str
    domains: List[str] = field(default_factory=list)
    skill_clusters: List[str] = field(default_factory=list)
    risk_flags: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PlanningHints:
    """
    Cross-cutting hints that L2/L3/L5 may consult.

    This restores v10_8's "deep QA/safety hints" behavior in a typed
    form appropriate for v10_9.
    """

    qa_hints: List[str] = field(default_factory=list)
    safety_hints: List[str] = field(default_factory=list)
    context_hints: List[str] = field(default_factory=list)
    optimization_hints: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CrossModeDependencies:
    """
    Cross-mode planning dependencies.

    v10_8 allowed strategy to shape RAG, drafting, QA, and safety.
    This structure makes those dependencies explicit and typed.
    """

    rag_required: bool = True
    drafting_required: bool = True
    bullets_required: bool = True
    qa_required: bool = True
    safety_required: bool = True
    meta_learning_required: bool = True
    prompt_engineering_required: bool = True

    # Optional notes/hints per mode.
    rag_notes: List[str] = field(default_factory=list)
    drafting_notes: List[str] = field(default_factory=list)
    qa_notes: List[str] = field(default_factory=list)
    safety_notes: List[str] = field(default_factory=list)
    meta_notes: List[str] = field(default_factory=list)
    prompt_notes: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# =============================================================================
# 2. PROFILE INFERENCE
# =============================================================================


def _infer_seniority(job_text: str, resume_text: str) -> str:
    """
    Very small heuristic seniority inference.

    This is intentionally simple but structured, so it can be easily
    overridden or replaced by a more sophisticated classifier without
    changing downstream contracts.
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

    # Fallback: treat as mid-level.
    return "mid"


def _infer_domains(job_text: str, resume_text: str) -> List[str]:
    """
    Heuristic domain tagging from job/resume content.

    This replaces the implicit v10_8 domain tagging with a portable,
    transparent heuristic that can be upgraded later.
    """
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
    """
    Rough skill clustering based on keyword families.

    This mirrors v10_8 behavior where planners would cluster skills
    into thematic groups for bullet/drafting planning.
    """
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


def _infer_risk_flags(job_text: str, resume_text: str) -> List[str]:
    """
    Heuristic risk flags that QA and Safety can later validate.

    Example flags:
        • jd_alignment_low
        • heavy_pii_risk
        • aggressive_timeline
    """
    risk_flags: List[str] = []
    jt = job_text.lower()
    rt = resume_text.lower()

    # Very naive alignment heuristic: overlap of "must have" keywords.
    must_have_keywords = [
        "must have",
        "required",
        "strongly preferred",
    ]
    if any(k in jt for k in must_have_keywords):
        # If resume is short or missing domain tags, mark as risk.
        if len(rt.split()) < 300:  # very small resume
            risk_flags.append("jd_alignment_low")

    if any(k in jt for k in ["pci", "phi", "hipaa", "pii"]):
        risk_flags.append("heavy_pii_risk")

    if any(k in jt for k in ["immediately", "asap", "tight timeline"]):
        risk_flags.append("aggressive_timeline")

    return risk_flags


def infer_profile_signals(job_text: str, resume_text: str) -> ProfileSignals:
    """
    Public entry point for L1 profile inference.

    Downstream layers and tests can call this directly if needed, but
    typical usage is via plan_*() functions in this module.
    """
    seniority = _infer_seniority(job_text, resume_text)
    domains = _infer_domains(job_text, resume_text)
    skill_clusters = _infer_skill_clusters(job_text, resume_text)
    risk_flags = _infer_risk_flags(job_text, resume_text)

    return ProfileSignals(
        seniority=seniority,
        domains=domains,
        skill_clusters=skill_clusters,
        risk_flags=risk_flags,
    )


# =============================================================================
# 3. COMPLEXITY & REASONING STRATEGY
# =============================================================================


# --- L1: UPDATED ---
def estimate_task_complexity(job_text: str, resume_text: str) -> ComplexityLevel:
    """
    Updated to incorporate META profile biases:
        • planning_bias.conservative  → push complexity upward
        • planning_bias.exploratory   → push complexity downward
        • routing_bias.prefer_fast    → slightly reduce complexity to favor shallow passes
    """
    from meta_profile import get_planning_bias, get_routing_bias

    base = len(job_text.split()) + len(resume_text.split())

    if base < 800:
        level = ComplexityLevel.SIMPLE
    elif base < 2500:
        level = ComplexityLevel.MODERATE
    else:
        level = ComplexityLevel.COMPLEX

    planning = get_planning_bias()
    routing = get_routing_bias()

    # Conservative bias → treat tasks as harder
    if planning.get("conservative"):
        if level == ComplexityLevel.SIMPLE:
            level = ComplexityLevel.MODERATE
        elif level == ComplexityLevel.MODERATE:
            level = ComplexityLevel.COMPLEX

    # Exploratory → treat tasks as slightly easier
    if planning.get("exploratory") and level == ComplexityLevel.COMPLEX:
        level = ComplexityLevel.MODERATE

    # prefer_fast → bias away from deep reasoning complexity
    if routing.get("prefer_fast") and level == ComplexityLevel.MODERATE:
        level = ComplexityLevel.SIMPLE

    return level

# --- L1: UPDATED ---
def select_reasoning_strategy(
    complexity: ComplexityLevel,
    risk_flags: Sequence[str]
) -> ReasoningStrategy:
    """
    Updated to incorporate META ReasoningBias:
        • enable_critique → use *_WITH_CRITIQUE variants
        • conservative_mode → bias away from ToT
        • use_tot → force ToT
    """
    from meta_profile import get_planning_bias, get_qa_bias

    bias = get_planning_bias()
    qa = get_qa_bias()

    high_risk = bool(risk_flags) or qa.get("recent_failures", False)

    # Explicit forcing of ToT from meta bias
    if bias.get("exploratory") or bias.get("deterministic_recovery"):
        return ReasoningStrategy.TOT_WITH_CRITIQUE

    # Conservative mode shrinks strategy footprint
    if bias.get("conservative"):
        return ReasoningStrategy.COT_WITH_CRITIQUE

    # Default model (same logic as before, but overridden by biases)
    if complexity == ComplexityLevel.SIMPLE and not high_risk:
        return ReasoningStrategy.DIRECT

    if complexity == ComplexityLevel.MODERATE and not high_risk:
        return ReasoningStrategy.COT

    if high_risk:
        return ReasoningStrategy.COT_WITH_CRITIQUE

    return ReasoningStrategy.TOT_WITH_CRITIQUE



# =============================================================================
# 4. PLANNING HINTS
# =============================================================================


def build_planning_hints(
    profile: ProfileSignals,
    complexity: ComplexityLevel,
    safety_profile: SafetyOutputProfile,
) -> PlanningHints:
    """
    Construct QA, safety, context, and optimization hints for downstream layers.

    These hints restore the "deep QA/safety hints" behavior v10_8
    provided to QA and safety stacks, but in a clean, typed structure.
    """
    qa_hints: List[str] = []
    safety_hints: List[str] = []
    context_hints: List[str] = []
    optimization_hints: List[str] = []

    # QA: emphasize alignment and quantification for senior roles.
    if profile.seniority in ("executive", "director"):
        qa_hints.append("verify_executive_outcomes_are_quantified")
        qa_hints.append("check_alignment_with_business_outcomes")
    else:
        qa_hints.append("ensure_bullets_use_action_metric_outcome_pattern")

    # Safety: adjust based on safety mode.
    if safety_profile.mode == safety_profile.mode.STRICT:
        safety_hints.append("enforce_strict_pii_redaction")
        safety_hints.append("enforce_conservative_tool_usage")
    elif safety_profile.mode == safety_profile.mode.PERMISSIVE:
        safety_hints.append("allow_non_critical_style_deviations")

    if safety_profile.enable_prompt_injection_detection:
        safety_hints.append("run_prompt_injection_detector_on_all_external_inputs")

    # Context: highlight domain-specific context usage.
    if "insurance" in profile.domains:
        context_hints.append("preserve_insurance_regulatory_language")
    if "foundation_models" in profile.domains:
        context_hints.append("preserve_llm_and_rag_architecture_details")

    # Optimization: nudge L2/L3 toward cost-aware strategies.
    if complexity == ComplexityLevel.SIMPLE:
        optimization_hints.append("prefer_cheaper_models_for_initial_pass")
    elif complexity == ComplexityLevel.COMPLEX:
        optimization_hints.append("prefer_high_capability_models_for_core_reasoning")

    return PlanningHints(
        qa_hints=qa_hints,
        safety_hints=safety_hints,
        context_hints=context_hints,
        optimization_hints=optimization_hints,
    )


# =============================================================================
# 5. CROSS-MODE DEPENDENCIES
# =============================================================================


def build_cross_mode_dependencies(
    profile: ProfileSignals,
    complexity: ComplexityLevel,
) -> CrossModeDependencies:
    """
    Encode cross-mode dependencies (strategy → RAG → drafting → QA → safety).

    v10_8 implicitly allowed these dependencies; in v10_9, we make
    them explicit and inspectable.
    """
    deps = CrossModeDependencies()

    # Notes for RAG.
    deps.rag_notes.append("prioritize_company_and_role_specific_docs")
    if "insurance" in profile.domains:
        deps.rag_notes.append("retrieve_insurance_domain_case_studies")
    if complexity != ComplexityLevel.SIMPLE:
        deps.rag_notes.append("expand_queries_with_synonyms_and_related_terms")

    # Notes for drafting.
    deps.drafting_notes.append("respect_seniority_in_tone_and_scope")
    if profile.seniority in ("executive", "director"):
        deps.drafting_notes.append("emphasize_org-wide_impact_and_strategy")
    else:
        deps.drafting_notes.append("emphasize_hands_on_impact_and_implementation")

    # Notes for QA.
    deps.qa_notes.append("validate_rag_evidence_covers_key_jd_requirements")
    deps.qa_notes.append("validate_quantification_for_top_achievements")

    # Notes for safety.
    deps.safety_notes.append("check_for_pii_in_all_free_text_sections")
    if "heavy_pii_risk" in profile.risk_flags:
        deps.safety_notes.append("run_additional_pii_scans_on_rag_snippets")

    # Notes for meta-learning.
    deps.meta_notes.append("log_complexity_and_seniority_for_future_routing_bias")
    deps.meta_notes.append("capture_qa_failures_for_correction_journal")

    # Notes for prompt engineering.
    deps.prompt_notes.append("attach_prompt_taxonomy_version_and_section_types")

    return deps


# =============================================================================
# 6. MODE-SPECIFIC PLAN BUILDERS
# =============================================================================


def _linear_strategy_steps() -> List[Dict[str, Any]]:
    """
    Restore the linear strategy plan steps from v10_8:

        clarify → context → structure
    """
    return [
        {
            "id": "clarify",
            "description": "Clarify role, seniority, domain, and hiring manager priorities.",
        },
        {
            "id": "context",
            "description": "Map candidate experience and achievements to job context.",
        },
        {
            "id": "structure",
            "description": "Define sections, themes, and narrative progression.",
        },
    ]


# --- L1: UPDATED ---
def build_strategy_plan(
    job_text: str,
    resume_text: str,
    framing: FramingProfile,
    context_profile: ContextProfile,
    tooling_profile: ToolingProfile,
    safety_profile: SafetyOutputProfile,
    access_policy: Optional[AccessPolicy] = None,
) -> PlanObject:
    """
    Updated to incorporate META profile biases:
        • planning_bias.conservative/exploratory affects steps + surfaces
        • routing_bias.prefer_fast adjusts strategy depth
        • qa_bias.recent_failures adds verification surfaces
        • safety_bias.heightened_caution adjusts tone and constraints
        • tone_bias influences narrative tone
    """
    from meta_profile import (
        get_planning_bias, get_routing_bias,
        get_qa_bias, get_safety_bias, get_tone_bias
    )

    planning_bias = get_planning_bias()
    routing_bias = get_routing_bias()
    qa_bias = get_qa_bias()
    safety_bias = get_safety_bias()
    tone_bias = get_tone_bias()

    profile = infer_profile_signals(job_text, resume_text)
    complexity = estimate_task_complexity(job_text, resume_text)
    reasoning = select_reasoning_strategy(complexity, profile.risk_flags)
    hints = build_planning_hints(profile, complexity, safety_profile)
    deps = build_cross_mode_dependencies(profile, complexity)

    steps = _linear_strategy_steps()

    # Meta-driven modifications
    if planning_bias.get("conservative"):
        steps.append({"id": "fallback", "description": "Add conservative fallback reasoning path."})

    if planning_bias.get("deterministic_recovery"):
        steps.append({"id": "recovery", "description": "Enable deterministic recovery logic."})

    if qa_bias.get("recent_failures"):
        steps.append({"id": "qa_focus", "description": "Increase QA-coverage emphasis."})

    # Tone + safety affect tone used downstream
    adjusted_tone = tone_bias.get("tone", "professional")
    if safety_bias.get("heightened_caution"):
        adjusted_tone = "formal"

    plan_dict = {
        "layer": "l1",
        "mode": "strategy",
        "objective": framing.goal,
        "tone_override": adjusted_tone,
        "framing_profile": framing.to_dict(),
        "context_profile": context_profile.to_dict(),
        "tooling_profile": tooling_profile.to_dict(),
        "safety_profile": safety_profile.to_dict(),
        "profile_signals": profile.to_dict(),
        "complexity": complexity.value,
        "reasoning_strategy": reasoning.value,
        "planning_hints": hints.to_dict(),
        "dependencies": deps.to_dict(),
        "steps": steps,
    }

    if access_policy:
        plan_dict["access_policy"] = {
            "tools": [dict(tp.__dict__) for tp in access_policy.tool_permissions],
            "routes": [dict(rp.__dict__) for rp in access_policy.routing_permissions],
        }

    return PlanObject(plan_dict)



def build_rag_plan(
    job_text: str,
    resume_text: str,
    profile: ProfileSignals,
    complexity: ComplexityLevel,
    context_profile: ContextProfile,
) -> PlanObject:
    """
    Plan retrieval queries and evidence targets.

    This restores v10_8 RAG planning behavior in a clean form:
    multi-query fusion, resume-aware scoring, and explainability hooks.
    """
    base_queries: List[str] = []

    # Core queries.
    base_queries.append("job_description_core_requirements")
    base_queries.append("company_strategy_and_recent_news")
    base_queries.append("role_specific_success_profiles")

    if "insurance" in profile.domains:
        base_queries.append("insurance_domain_case_studies")
        base_queries.append("insurance_ai_use_cases")
    if "foundation_models" in profile.domains:
        base_queries.append("llm_and_rag_architecture_patterns")

    # Additional queries for complex tasks.
    if complexity != ComplexityLevel.SIMPLE:
        base_queries.append("industry_benchmarks_and_best_practices")

    # Explainability: why these queries exist.
    explainability = {
        "resume_aware_scoring": True,
        "jd_alignment_boosting": True,
        "multi_query_fusion": complexity != ComplexityLevel.SIMPLE,
        "rag_explainability_enabled": True,
    }

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "rag",
        "objective": "Retrieve structured evidence that maximally supports strategy and drafting.",
        "profile_signals": profile.to_dict(),
        "complexity": complexity.value,
        "queries": base_queries,
        "fusion": {
            "enabled": complexity != ComplexityLevel.SIMPLE,
            "explainability": explainability,
        },
        "scoring": {
            "resume_aware": True,
            "jd_requirement_boost": True,
        },
        "context_profile": context_profile.to_dict(),
    }

    return PlanObject(plan_dict)


def build_drafting_plan(
    job_text: str,
    resume_text: str,
    profile: ProfileSignals,
    complexity: ComplexityLevel,
    framing: FramingProfile,
) -> PlanObject:
    """
    Plan the drafting structure (sections, tone, personalization).

    This restores v10_8's behavior where drafting is explicitly aware
    of strategy and RAG surfaces.
    """
    seniority = profile.seniority

    # Sections depend on seniority.
    sections: List[Dict[str, Any]] = [
        {"id": "header", "required": True},
        {"id": "summary", "required": True},
        {"id": "experience", "required": True},
        {"id": "skills", "required": True},
    ]

    if seniority in ("executive", "director"):
        sections.append({"id": "executive_highlights", "required": True})
        sections.append({"id": "strategy_and_vision", "required": True})
    else:
        sections.append({"id": "projects", "required": False})

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "drafting",
        "objective": "Draft a personalized, domain-aware artifact aligned with the strategy plan.",
        "profile_signals": profile.to_dict(),
        "complexity": complexity.value,
        "framing_profile": framing.to_dict(),
        "sections": sections,
        "tone": framing.tone or "professional",
        "personalization": {
            "use_domain_examples": bool(profile.domains),
            "highlight_skill_clusters": profile.skill_clusters,
        },
    }

    return PlanObject(plan_dict)


def build_bullets_plan(
    profile: ProfileSignals,
    complexity: ComplexityLevel,
) -> PlanObject:
    """
    Plan the bullet framework for L2.

    Restores v10_8's advanced bullet system:
        • action–metric–outcome
        • seniority scaling
        • guild-level transformations
    """
    skeleton = {
        "pattern": "action_metric_outcome",
        "seniority_scaling": profile.seniority,
        "guild_transform": "default",
    }

    if "executive_communication" in profile.skill_clusters:
        skeleton["guild_transform"] = "executive_storytelling"

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "bullets",
        "objective": "Define bullet schemas and seniority scaling logic.",
        "profile_signals": profile.to_dict(),
        "complexity": complexity.value,
        "framework": skeleton,
    }

    return PlanObject(plan_dict)


def build_qa_plan(
    profile: ProfileSignals,
    complexity: ComplexityLevel,
    hints: PlanningHints,
) -> PlanObject:
    """
    Plan QA checks and surfaces.

    Restores v10_8's correction validation framework for:
        • JD mismatch
        • keyword coverage
        • resume alignment
    """
    checks: List[Dict[str, Any]] = [
        {"id": "jd_coverage", "severity": "high"},
        {"id": "keyword_coverage", "severity": "medium"},
        {"id": "resume_alignment", "severity": "high"},
    ]

    if complexity != ComplexityLevel.SIMPLE:
        checks.append({"id": "rag_evidence_alignment", "severity": "high"})

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "qa",
        "objective": "Define QA checks and validation surfaces for downstream execution.",
        "profile_signals": profile.to_dict(),
        "complexity": complexity.value,
        "checks": checks,
        "hints": hints.to_dict(),
    }

    return PlanObject(plan_dict)


def build_safety_plan(
    profile: ProfileSignals,
    safety_profile: SafetyOutputProfile,
    hints: PlanningHints,
) -> PlanObject:
    """
    Plan safety surfaces and escalation paths.

    Restores v10_8's SafetyConfig layer conceptually:
        • safety modes
        • injection detection
        • deny/allow lists (through SafetyOutputProfile & AccessPolicy)
    """
    rules: List[Dict[str, Any]] = []

    if safety_profile.enable_pii_detection:
        rules.append({"id": "pii_detection", "severity": "high"})
    if safety_profile.enable_toxicity_detection:
        rules.append({"id": "toxicity_detection", "severity": "high"})
    if safety_profile.enable_bias_detection:
        rules.append({"id": "bias_detection", "severity": "medium"})
    if safety_profile.enable_prompt_injection_detection:
        rules.append({"id": "prompt_injection_detection", "severity": "high"})

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "safety",
        "objective": "Define safety checks and escalation behavior for L5.",
        "profile_signals": profile.to_dict(),
        "safety_profile": safety_profile.to_dict(),
        "rules": rules,
        "hints": hints.to_dict(),
    }

    return PlanObject(plan_dict)


def build_meta_learning_plan(
    profile: ProfileSignals,
    complexity: ComplexityLevel,
) -> PlanObject:
    """
    Plan meta-learning signals and logging surfaces.

    Restores v10_8's cross-run learning and correction journaling
    behavior in a typed planning form.
    """
    signals: List[str] = [
        "log_complexity_and_seniority",
        "log_qa_failures_to_correction_journal",
        "log_safety_blocks_and_escalations",
    ]

    if complexity == ComplexityLevel.COMPLEX:
        signals.append("log_model_routing_and_cost_metrics")

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "meta_learning",
        "objective": "Define meta-learning logging and signal collection for this run.",
        "profile_signals": profile.to_dict(),
        "complexity": complexity.value,
        "signals": signals,
    }

    return PlanObject(plan_dict)


def build_prompt_engineering_plan(
    framing: FramingProfile,
    context_profile: ContextProfile,
) -> PlanObject:
    """
    Plan prompt taxonomy, sections, and governance metadata.

    Restores v10_8's prompt taxonomy API conceptually:
        • section names/types
        • injection types
        • template metadata
    """
    sections = [
        {"id": "system", "type": "system"},
        {"id": "instructions", "type": "instructions"},
        {"id": "examples", "type": "few_shot"},
        {"id": "user_input", "type": "user"},
        {"id": "tools", "type": "tool_spec"},
    ]

    injection_types = [
        "goal_override",
        "role_override",
        "data_exfiltration",
        "tool_abuse",
        "safety_bypass",
        "prompt_leak",
    ]

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "prompt_engineering",
        "objective": "Define prompt structure, taxonomy, and governance metadata.",
        "framing_profile": framing.to_dict(),
        "context_profile": context_profile.to_dict(),
        "sections": sections,
        "injection_types": injection_types,
        "taxonomy": {
            "version": "v1",
            "section_count": len(sections),
        },
    }

    return PlanObject(plan_dict)


# =============================================================================
# 7. PUBLIC ENTRY POINT
# =============================================================================


def plan(
    *,
    mode: str,
    job_text: str,
    resume_text: str,
    framing_profile: FramingProfile,
    context_profile: ContextProfile,
    tooling_profile: ToolingProfile,
    safety_profile: SafetyOutputProfile,
    access_policy: Optional[AccessPolicy] = None,
) -> PlanObject:
    """
    Public L1 planning entrypoint.

    This is the only function L2/L3 should call directly. It returns a
    PlanObject whose "mode" matches the requested planning mode.

    Supported modes (restoring all v10_8 planning surfaces):

        • "strategy"
        • "rag"
        • "drafting"
        • "bullets"
        • "qa"
        • "safety"
        • "meta_learning"
        • "prompt_engineering"
    """
    # Shared signals used across most modes.
    profile = infer_profile_signals(job_text, resume_text)
    complexity = estimate_task_complexity(job_text, resume_text)
    hints = build_planning_hints(profile, complexity, safety_profile)

    mode = mode.lower()

    if mode == "strategy":
        return build_strategy_plan(
            job_text=job_text,
            resume_text=resume_text,
            framing=framing_profile,
            context_profile=context_profile,
            tooling_profile=tooling_profile,
            safety_profile=safety_profile,
            access_policy=access_policy,
        )

    if mode == "rag":
        return build_rag_plan(
            job_text=job_text,
            resume_text=resume_text,
            profile=profile,
            complexity=complexity,
            context_profile=context_profile,
        )

    if mode == "drafting":
        return build_drafting_plan(
            job_text=job_text,
            resume_text=resume_text,
            profile=profile,
            complexity=complexity,
            framing=framing_profile,
        )

    if mode == "bullets":
        return build_bullets_plan(
            profile=profile,
            complexity=complexity,
        )

    if mode == "qa":
        return build_qa_plan(
            profile=profile,
            complexity=complexity,
            hints=hints,
        )

    if mode == "safety":
        return build_safety_plan(
            profile=profile,
            safety_profile=safety_profile,
            hints=hints,
        )

    if mode == "meta_learning":
        return build_meta_learning_plan(
            profile=profile,
            complexity=complexity,
        )

    if mode == "prompt_engineering":
        return build_prompt_engineering_plan(
            framing=framing_profile,
            context_profile=context_profile,
        )

    # If we get here, the caller passed an unsupported mode.
    raise ValueError(f"Unsupported L1 planning mode: {mode!r}")
