# FILE: l1.py
"""
Unified L1 Cognition Layer (v10_9) — FULL AGENTIC PLANNING (REFINED)

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

Additionally, L1 now **consumes META profile biases** from `meta_profile`
to adapt its planning:

    • routing_bias    → complexity and RAG planning preferences.
    • planning_bias   → conservative/exploratory reasoning choices.
    • qa_bias         → QA-heavy vs standard planning.
    • safety_bias     → safety/sensitivity emphasis.

This file is designed to restore full planning capabilities from v10_8,
while respecting the v10_9 layered agentic architecture and maximizing
scores on the 14 OpenAI agentic subdomains.
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
    AccessPolicy,
    SelfCorrectionSurface,
)

from meta_profile import (
    get_routing_bias,
    get_planning_bias,
    get_qa_bias,
    get_safety_bias,
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

    This restores the "deep QA/safety hints" behavior v10_8
    provided to QA and safety stacks, in a typed structure.
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

    return "mid"


def _infer_domains(job_text: str, resume_text: str) -> List[str]:
    """
    Heuristic domain tagging from job/resume content.
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
    """
    risk_flags: List[str] = []
    jt = job_text.lower()
    rt = resume_text.lower()

    must_have_keywords = [
        "must have",
        "required",
        "strongly preferred",
    ]
    if any(k in jt for k in must_have_keywords):
        if len(rt.split()) < 300:
            risk_flags.append("jd_alignment_low")

    if any(k in jt for k in ["pci", "phi", "hipaa", "pii"]):
        risk_flags.append("heavy_pii_risk")

    if any(k in jt for k in ["immediately", "asap", "tight timeline"]):
        risk_flags.append("aggressive_timeline")

    return risk_flags


def infer_profile_signals(job_text: str, resume_text: str) -> ProfileSignals:
    """
    Public entry point for L1 profile inference.
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


def estimate_task_complexity(job_text: str, resume_text: str) -> ComplexityLevel:
    """
    Estimate problem complexity from simple heuristics plus meta-biases.

    Base heuristic: token count of job + resume.
    Meta-bias adjustments (from meta_profile):

        • planning_bias.conservative  → push complexity upward.
        • planning_bias.exploratory   → pull complexity downward.
        • routing_bias.prefer_fast    → lean toward lower complexity.
    """
    base_tokens = len(job_text.split()) + len(resume_text.split())

    if base_tokens < 800:
        level: ComplexityLevel = ComplexityLevel.SIMPLE
    elif base_tokens < 2500:
        level = ComplexityLevel.MODERATE
    else:
        level = ComplexityLevel.COMPLEX

    planning_bias = get_planning_bias()
    routing_bias = get_routing_bias()

    # Conservative bias: treat problems as harder.
    if planning_bias.get("conservative"):
        if level == ComplexityLevel.SIMPLE:
            level = ComplexityLevel.MODERATE
        elif level == ComplexityLevel.MODERATE:
            level = ComplexityLevel.COMPLEX

    # Exploratory bias: treat hardest problems as moderately complex.
    if planning_bias.get("exploratory") and level == ComplexityLevel.COMPLEX:
        level = ComplexityLevel.MODERATE

    # prefer_fast: lean away from deeper complexity when borderline.
    if routing_bias.get("prefer_fast") and level == ComplexityLevel.MODERATE:
        level = ComplexityLevel.SIMPLE

    return level


def select_reasoning_strategy(
    complexity: ComplexityLevel,
    risk_flags: Sequence[str],
) -> ReasoningStrategy:
    """
    Map complexity + risk + meta-biases into a reasoning strategy hint.

    Meta-bias influence:

        • planning_bias.conservative     → prefer COT_WITH_CRITIQUE.
        • planning_bias.exploratory      → prefer TOT_WITH_CRITIQUE.
        • planning_bias.deterministic_recovery → prefer TOT_WITH_CRITIQUE.
        • qa_bias.recent_failures        → prefer critique variants.
    """
    planning_bias = get_planning_bias()
    qa_bias = get_qa_bias()

    high_risk = bool(risk_flags) or qa_bias.get("recent_failures", False)

    # Explicit meta forcing.
    if planning_bias.get("exploratory"):
        return ReasoningStrategy.TOT_WITH_CRITIQUE
    if planning_bias.get("conservative"):
        return ReasoningStrategy.COT_WITH_CRITIQUE
    if planning_bias.get("deterministic_recovery"):
        return ReasoningStrategy.TOT_WITH_CRITIQUE

    # Base mapping.
    if complexity == ComplexityLevel.SIMPLE and not high_risk:
        return ReasoningStrategy.DIRECT

    if complexity == ComplexityLevel.MODERATE and not high_risk:
        return ReasoningStrategy.COT

    if high_risk and complexity != ComplexityLevel.SIMPLE:
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

    Hint sources:
        • profile (seniority, domains, risk_flags)
        • complexity
        • safety_profile
        • meta safety/planning biases
    """
    safety_bias = get_safety_bias()

    qa_hints: List[str] = []
    safety_hints: List[str] = []
    context_hints: List[str] = []
    optimization_hints: List[str] = []

    # QA hints.
    if profile.seniority in ("executive", "director"):
        qa_hints.append("validate_executive_outcomes_are_quantified")
        qa_hints.append("ensure_alignment_with_business_outcomes")
    else:
        qa_hints.append("enforce_action_metric_outcome_pattern")

    # Safety hints.
    if safety_profile.enable_prompt_injection_detection:
        safety_hints.append("run_prompt_injection_detector")
    if safety_profile.enable_pii_detection:
        safety_hints.append("run_pii_scan_on_all_outputs")
    if safety_bias.get("heightened_caution"):
        safety_hints.append("tighten_safety_thresholds")

    # Context hints.
    if "insurance" in profile.domains:
        context_hints.append("preserve_insurance_regulatory_language")
    if "foundation_models" in profile.domains:
        context_hints.append("preserve_llm_and_rag_architecture_details")

    # Optimization hints.
    if complexity == ComplexityLevel.SIMPLE:
        optimization_hints.append("prefer_low_cost_models_for_initial_pass")
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

    v10_8 implicitly allowed these dependencies; here we make them explicit.
    """
    deps = CrossModeDependencies()

    # Notes for RAG.
    deps.rag_notes.append("prioritize_company_and_role_specific_docs")
    if "insurance" in profile.domains:
        deps.rag_notes.append("retrieve_insurance_domain_case_studies")
    if complexity != ComplexityLevel.SIMPLE:
        deps.rag_notes.append("use_multi_query_fusion_for_complex_tasks")

    # Notes for drafting.
    deps.drafting_notes.append("respect_seniority_in_tone_and_scope")
    if profile.seniority in ("executive", "director"):
        deps.drafting_notes.append("emphasize_org_wide_impact_and_strategy")
    else:
        deps.drafting_notes.append("emphasize_hands_on_delivery_and_impact")

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
    Build a PLAN for the "strategy" mode with meta-aware adjustments.
    """
    planning_bias = get_planning_bias()
    qa_bias = get_qa_bias()
    safety_bias = get_safety_bias()

    profile = infer_profile_signals(job_text, resume_text)
    complexity = estimate_task_complexity(job_text, resume_text)
    reasoning = select_reasoning_strategy(complexity, profile.risk_flags)
    hints = build_planning_hints(profile, complexity, safety_profile)
    deps = build_cross_mode_dependencies(profile, complexity)

    steps = _linear_strategy_steps()

    if planning_bias.get("conservative"):
        steps.append(
            {"id": "fallback", "description": "Add conservative fallback reasoning path."}
        )
    if planning_bias.get("deterministic_recovery"):
        steps.append(
            {"id": "recovery", "description": "Plan deterministic recovery for failures."}
        )
    if qa_bias.get("recent_failures"):
        steps.append(
            {"id": "qa_focus", "description": "Increase QA coverage emphasis in strategy."}
        )

    adjusted_tone = framing.tone or "professional"
    if safety_bias.get("heightened_caution"):
        adjusted_tone = "formal"

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "strategy",
        "objective": framing.goal,
        "tone": adjusted_tone,
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
        "surfaces": [
            SelfCorrectionSurface.RAG_RETRY.value,
            SelfCorrectionSurface.DRAFT_RETRY.value,
            SelfCorrectionSurface.QA_RECHECK.value,
            SelfCorrectionSurface.SAFETY_RISK.value,
        ],
    }

    if access_policy is not None:
        plan_dict["access_policy"] = {
            "tools": [asdict(tp) for tp in access_policy.tool_permissions],
            "routes": [asdict(rp) for rp in access_policy.routing_permissions],
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

    Restores v10_8 RAG planning behavior with meta-aware tweaks.
    """
    routing_bias = get_routing_bias()

    base_queries: List[str] = [
        "job_description_core_requirements",
        "company_strategy_and_recent_news",
        "role_specific_success_profiles",
    ]

    if "insurance" in profile.domains:
        base_queries.append("insurance_domain_case_studies")
        base_queries.append("insurance_ai_use_cases")
    if "foundation_models" in profile.domains:
        base_queries.append("llm_and_rag_architecture_patterns")

    if complexity != ComplexityLevel.SIMPLE:
        base_queries.append("industry_benchmarks_and_best_practices")

    explainability = {
        "resume_aware_scoring": True,
        "jd_requirement_boost": True,
        "multi_query_fusion": complexity != ComplexityLevel.SIMPLE,
    }

    retrieval_cfg: Dict[str, Any] = {
        "queries": base_queries,
        "ranking": {
            "strategy": "hybrid",
            "enable_hyde": True,
        },
        "resume_aware_scoring": True,
        "jd_requirement_boost": True,
    }

    if routing_bias.get("prefer_robust_retrieval"):
        retrieval_cfg["ranking"]["strategy"] = "hybrid"
        retrieval_cfg["ranking"]["enable_hyde"] = True

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "rag",
        "objective": "Retrieve structured evidence to support strategy and drafting.",
        "profile_signals": profile.to_dict(),
        "complexity": complexity.value,
        "retrieval": retrieval_cfg,
        "explainability": explainability,
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
    Plan drafting structure (sections, tone, personalization).
    """
    planning_bias = get_planning_bias()

    seniority = profile.seniority

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

    if planning_bias.get("conservative"):
        sections.append({"id": "risk_mitigation", "required": False})

    objective = (
        "Draft a personalized, domain-aware artifact aligned with the strategy plan."
    )

    plan_dict: Dict[str, Any] = {
        "layer": "l1",
        "mode": "drafting",
        "objective": objective,
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
    """
    planning_bias = get_planning_bias()

    skeleton: Dict[str, Any] = {
        "pattern": "action_metric_outcome",
        "seniority_scaling": profile.seniority,
        "guild_transform": "default",
    }

    if "executive_communication" in profile.skill_clusters:
        skeleton["guild_transform"] = "executive_storytelling"

    if planning_bias.get("conservative"):
        skeleton["enforce_metric_presence"] = True

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
    Plan QA checks and surfaces (v10_8 correction framework).
    """
    qa_bias = get_qa_bias()

    checks: List[str] = [
        "jd_coverage",
        "keyword_coverage",
        "resume_alignment",
    ]

    if complexity != ComplexityLevel.SIMPLE:
        checks.append("rag_evidence_alignment")

    if qa_bias.get("recent_failures"):
        checks.append("extra_qa_pass")

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
    """
    safety_bias = get_safety_bias()

    rules: List[Dict[str, Any]] = []

    if safety_profile.enable_pii_detection:
        rules.append({"id": "pii_detection", "severity": "high"})
    if safety_profile.enable_toxicity_detection:
        rules.append({"id": "toxicity_detection", "severity": "high"})
    if safety_profile.enable_bias_detection:
        rules.append({"id": "bias_detection", "severity": "medium"})
    if safety_profile.enable_prompt_injection_detection:
        rules.append({"id": "prompt_injection_detection", "severity": "high"})

    if safety_bias.get("heightened_caution"):
        rules.append({"id": "strict_mode", "severity": "high"})

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

    Supported modes:

        • "strategy"
        • "rag"
        • "drafting"
        • "bullets"
        • "qa"
        • "safety"
        • "meta_learning"
        • "prompt_engineering"
    """
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

    raise ValueError(f"Unsupported L1 planning mode: {mode!r}")
