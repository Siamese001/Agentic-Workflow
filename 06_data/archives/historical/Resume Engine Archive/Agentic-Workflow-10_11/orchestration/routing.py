# FILE: 10_10/routing.py
"""
Routing Policy for Agentic Workflow v10_10
=========================================

This is the v10_10 refactor of the v10_9 routing layer.

It removes:
    - PlanObject-dependent logic
    - L5.ModelRouter
    - PromptEnvelope construction
    - META-only routing criteria classes
    - direct meta_profile accessors (get_routing_bias, get_planning_bias, etc.)
    - simulated model invocation stubs

and replaces them with a **minimal, deterministic RoutingPolicy** that:

    - Selects models based on task + ComplexityLevel.
    - Is influenced by a MetaProfileSnapshot (read-only).
    - Provides ToT branch counts for StrategyLLMAgent.
    - Contains NO provider SDK calls.
    - Contains NO L1/L2/L3/L4/L5 logic.

This module is used only by L2 cognitive agents and L1 complexity
classification. It is **pure decision logic**.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, List, Dict

from core.models.models import (
    ComplexityLevel,
    SkillClassifierResult,
    DomainClassifierResult,
    MultiAgentCouncilResult,
    RoutingDecisionEvent,
)
from config.meta_profile import MetaProfileSnapshot
from observability import record_event


# =============================================================================
# Model Family Definitions
# =============================================================================

# "Light" models: fast, cheap, shallow reasoning
LIGHT_MODELS = {
    "gpt-4o-mini",
    "gpt-3.5-turbo",
    "claude-3-haiku-20240307",
}

# "Standard" models: default production models
STANDARD_MODELS = {
    "gpt-4o",
    "gpt-4-turbo",
    "claude-3-sonnet-20240229",
    "claude-3-5-sonnet-20240620",
}

# "Heavy" models: expensive, strong reasoning
HEAVY_MODELS = {
    "gpt-4-turbo-preview",
    "claude-3-opus-20240229",
    "o1-preview",
    "o1-mini",
}


# =============================================================================
# Routing Policy Dataclass
# =============================================================================

@dataclass
class RoutingPolicy:
    """
    Minimal routing policy used by L2 cognitive agents.

    Fields:
        default_model: fallback model for unspecified tasks.
        strategy_model: model used for strategy generation.
        drafting_model: model used for draft generation.
        qa_model: model used for QA checks.
        safety_model: model used for safety evaluation.
        tot_branch_count: Tree-of-Thought branching factor.
    """

    default_model: str = "gpt-4o"
    strategy_model: str = "gpt-4o"
    drafting_model: str = "gpt-4o"
    qa_model: str = "gpt-4o-mini"
    safety_model: str = "gpt-4o-mini"
    tot_branch_count: int = 3


# =============================================================================
# Policy Factory
# =============================================================================

def build_routing_policy(
    complexity: ComplexityLevel,
    meta_profile: Optional[MetaProfileSnapshot] = None,
) -> RoutingPolicy:
    """
    Construct a RoutingPolicy based on ComplexityLevel and optional meta_profile.

    Rules:
        LOW complexity -> light models, 2 branches.
        MEDIUM complexity -> standard models, 3 branches.
        HIGH complexity -> heavy models, 5 branches.

    If meta_profile contains bias overrides, they are applied here.
    """
    if complexity == ComplexityLevel.LOW:
        policy = RoutingPolicy(
            default_model="gpt-4o-mini",
            strategy_model="gpt-4o-mini",
            drafting_model="gpt-4o-mini",
            qa_model="gpt-4o-mini",
            safety_model="gpt-4o-mini",
            tot_branch_count=2,
        )
    elif complexity == ComplexityLevel.MEDIUM:
        policy = RoutingPolicy(
            default_model="gpt-4o",
            strategy_model="gpt-4o",
            drafting_model="gpt-4o",
            qa_model="gpt-4o-mini",
            safety_model="gpt-4o-mini",
            tot_branch_count=3,
        )
    else:
        policy = RoutingPolicy(
            default_model="gpt-4-turbo-preview",
            strategy_model="gpt-4-turbo-preview",
            drafting_model="gpt-4o",
            qa_model="gpt-4o",
            safety_model="gpt-4o",
            tot_branch_count=5,
        )

    # Apply meta_profile biases if present
    if meta_profile is not None:
        try:
            if hasattr(meta_profile, "preferred_strategy_model") and meta_profile.preferred_strategy_model:
                policy.strategy_model = meta_profile.preferred_strategy_model
            if hasattr(meta_profile, "preferred_drafting_model") and meta_profile.preferred_drafting_model:
                policy.drafting_model = meta_profile.preferred_drafting_model
        except Exception:
            pass

    return policy


# =============================================================================
# Model Selection Helper
# =============================================================================

def select_model_for_task(
    task: str,
    policy: RoutingPolicy,
    council: Optional[MultiAgentCouncilResult] = None,
) -> str:
    """
    Return the model name for a given task using the policy.

    Tasks: "strategy", "drafting", "qa", "safety", or fallback to default.

    If a council vote is provided and has a model override, use it.
    """
    if council is not None and hasattr(council, "metadata"):
        override = council.metadata.get("model_override")
        if override:
            return str(override)

    task_lower = task.lower()
    if task_lower == "strategy":
        return policy.strategy_model
    if task_lower == "drafting":
        return policy.drafting_model
    if task_lower == "qa":
        return policy.qa_model
    if task_lower == "safety":
        return policy.safety_model
    return policy.default_model


# =============================================================================
# Routing Decision Recording
# =============================================================================

def record_routing_decision(
    agent_role: str,
    decision: str,
    reason: str,
    council: Optional[MultiAgentCouncilResult] = None,
) -> str:
    """
    Record a routing decision event for observability.

    Returns the decision string unchanged.
    """
    attrs: Dict[str, Any] = {
        "agent_role": agent_role,
        "decision": decision,
        "reason": reason,
    }

    if council is not None:
        attrs["council_selected_id"] = council.metadata.get("selected_id")
        attrs["council_aggregated_decision"] = council.aggregated_decision
        attrs["council_vote_count"] = len(council.votes)

    event = RoutingDecisionEvent(
        name="routing_decision",
        agent_id=agent_role,
        provider="meta_routing",
        model_name="",
        reason=reason,
        attributes=attrs,
    )
    try:
        record_event(event.name, event.attributes)
    except Exception:
        # Observability must never break routing.
        pass

    return decision


# =============================================================================
# Skill / Domain Classifiers (non-LLM, deterministic)
# =============================================================================

def classify_skill_profile(job: Any, resume: Any) -> SkillClassifierResult:
    """Deterministic, rule-based skill classifier (non-LLM).

    Uses simple keyword / structural heuristics on job + resume to
    derive a coarse skill profile. This is intentionally conservative
    but stable for routing and complexity decisions.
    """
    labels: List[str] = []
    features: Dict[str, Any] = {}

    title = str(getattr(job, "title", "")).lower()
    desc = str(getattr(job, "description", "")).lower()
    resume_text = str(getattr(resume, "raw_text", "")).lower()

    # Seniority
    senior_tokens = ("vp", "vice president", "chief", "director", "head", "principal")
    mid_tokens = ("manager", "lead", "senior")
    if any(t in title for t in senior_tokens):
        labels.append("senior_leadership")
    elif any(t in title for t in mid_tokens):
        labels.append("senior_individual_contributor")
    else:
        labels.append("individual_contributor")

    # Technical focus
    if "machine learning" in desc or "ml" in desc or "data science" in desc:
        labels.append("ml_data_science")
    if "llm" in desc or "prompt" in desc or "rag" in desc:
        labels.append("llm_systems")
    if "actuary" in desc or "insurance" in desc:
        labels.append("actuarial_insurance")

    # Resume signals
    exp_sections = getattr(resume, "experience_sections", []) or []
    features["experience_sections"] = len(exp_sections)
    features["title"] = title
    features["resume_contains_llm"] = "llm" in resume_text

    primary_label = labels[0] if labels else None
    confidence = 0.7 if primary_label is not None else 0.0

    return SkillClassifierResult(
        labels=labels,
        primary_label=primary_label,
        confidence=confidence,
        features=features,
    )


def classify_domain_profile(job: Any, resume: Any) -> DomainClassifierResult:
    """Deterministic domain / industry classifier (non-LLM)."""
    labels: List[str] = []
    features: Dict[str, Any] = {}

    company = str(getattr(job, "company", "")).lower()
    desc = str(getattr(job, "description", "")).lower()
    industry = (
        str(getattr(job, "metadata", {}).get("industry", "")).lower()
        if hasattr(job, "metadata")
        else ""
    )

    text_blob = " ".join([company, desc, industry])

    if any(tok in text_blob for tok in ("insurance", "actuarial", "p&c", "life insurance")):
        labels.append("insurance")
    if any(tok in text_blob for tok in ("bank", "fintech", "asset management", "trading", "brokerage")):
        labels.append("financial_services")
    if any(tok in text_blob for tok in ("healthcare", "hospital", "pharma", "biotech")):
        labels.append("healthcare")
    if any(tok in text_blob for tok in ("retail", "ecommerce", "marketplace")):
        labels.append("retail_ecommerce")

    if not labels:
        labels.append("general")

    primary_label = labels[0]
    confidence = 0.6

    features["company"] = company
    features["industry"] = industry

    return DomainClassifierResult(
        labels=labels,
        primary_label=primary_label,
        confidence=confidence,
        features=features,
    )


# =============================================================================
# Complexity Classification (used by L1)
# =============================================================================

def classify_complexity(
    job: Any,
    resume: Any,
    config: Any,
    meta_profile: Optional[MetaProfileSnapshot],
) -> ComplexityLevel:
    """Heuristic classifier used by L1 to estimate ComplexityLevel.

    This version incorporates:
        - Job seniority / requirements
        - Resume length
        - QA / correction rates from meta_profile
        - Deterministic skill and domain classifiers (non-LLM)

    All logic is deterministic and side-effect free.
    """
    # Baseline between LOW and MEDIUM
    score = 1.0

    # Skill / domain profiles (non-LLM, deterministic)
    try:
        skill_profile = classify_skill_profile(job, resume)
        domain_profile = classify_domain_profile(job, resume)
    except Exception:
        # Classifier failure must not break complexity classification.
        skill_profile = None
        domain_profile = None

    # Senior roles -> more complexity
    seniority = str(getattr(job, "seniority", "")).lower()
    title = str(getattr(job, "title", "")).lower()
    if seniority in ("director", "vp", "svp", "c-level", "chief") or any(
        t in title for t in ("director", "vp", "svp", "chief", "head")
    ):
        score += 0.5

    # Many requirements -> more alignment complexity
    try:
        reqs = getattr(job, "requirements", []) or []
        if len(reqs) > 8:
            score += 0.3
        if len(reqs) > 15:
            score += 0.3
    except Exception:
        pass

    # Long experience -> more data to integrate
    try:
        exp_sections = getattr(resume, "experience_sections", []) or []
        if len(exp_sections) > 6:
            score += 0.3
        if len(exp_sections) > 10:
            score += 0.3
    except Exception:
        pass

    # Skill / domain-based adjustments
    if skill_profile is not None and "senior_leadership" in (skill_profile.labels or []):
        score += 0.2
    if domain_profile is not None and domain_profile.primary_label in (
        "insurance",
        "financial_services",
        "healthcare",
    ):
        score += 0.1

    # Meta-profile signal (recent QA/correction rates)
    if meta_profile is not None:
        try:
            if meta_profile.qa_failure_rate_last_10 > 0.4:
                score += 0.3
            if meta_profile.correction_rate_last_10 > 0.3:
                score += 0.2
        except Exception:
            pass

    # Map score -> ComplexityLevel
    if score < 1.2:
        return ComplexityLevel.LOW
    if score < 1.8:
        return ComplexityLevel.MEDIUM
    return ComplexityLevel.HIGH


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "LIGHT_MODELS",
    "STANDARD_MODELS",
    "HEAVY_MODELS",
    "RoutingPolicy",
    "build_routing_policy",
    "select_model_for_task",
    "record_routing_decision",
    "classify_skill_profile",
    "classify_domain_profile",
    "classify_complexity",
]
