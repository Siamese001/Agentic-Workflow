# FILE: 10_10/routing.py
"""
Routing Policy for Agentic Workflow v10_10
=========================================

This is the v10_10 refactor of the v10_9 routing layer.

It removes:
    • PlanObject-dependent logic
    • L5.ModelRouter
    • PromptEnvelope construction
    • META-only routing criteria classes
    • direct meta_profile accessors (get_routing_bias, get_planning_bias, etc.)
    • simulated model invocation stubs

and replaces them with a **minimal, deterministic RoutingPolicy** that:

    • Selects models based on task + ComplexityLevel.
    • Is influenced by a MetaProfileSnapshot (read-only).
    • Provides ToT branch counts for StrategyLLMAgent.
    • Contains NO provider SDK calls.
    • Contains NO L1/L2/L3/L4/L5 logic.

This module is used only by L2 cognitive agents and L1 complexity
classification. It is **pure decision logic**.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Any, List, Dict

from models import ComplexityLevel, SkillClassifierResult, DomainClassifierResult
from meta_profile import MetaProfileSnapshot
from observability import get_all_events


# =============================================================================
# Model Family Definitions
# =============================================================================

# "Light" models: fast, cheap, shallow reasoning
LIGHT_MODELS = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-3-haiku",
}

# "Medium" models: balanced cost vs reasoning depth
MEDIUM_MODELS = {
    "openai": "gpt-5.1",
    "anthropic": "claude-3.5-sonnet",
}

# "Heavy" models: deep reasoning, longer outputs
HEAVY_MODELS = {
    "openai": "gpt-5.1-codex",
    "anthropic": "claude-3.5-opus",
}

# Specialized drafting models
DRAFTING_MODELS = {
    "openai": "gpt-5.1-codex",
    "anthropic": "claude-3.5-opus",
}

# Specialized QA/Safety models
QA_SAFETY_MODELS = {
    "openai": "gpt-4.1",
    "anthropic": "claude-3.5-sonnet",
}


# =============================================================================
# Routing Policy
# =============================================================================

@dataclass
class RoutingPolicy:
    """
    v10_10 RoutingPolicy: pure model-selection logic.

    Fields:
        prefer_anthropic: Prefer Anthropic models if True.
        prefer_openai:    Prefer OpenAI models if True.
        allow_heavy:      Allow heavy models (deep reasoning).
        enforce_low_cost: Prefer light models when possible.

    Notes:
        - MetaProfileSnapshot can override provider preference based on
          recent QA / correction rates.
    """

    prefer_anthropic: bool = False
    prefer_openai: bool = True
    allow_heavy: bool = True
    enforce_low_cost: bool = False

    # ---------------------------------------------------------------------
    # Provider selection
    # ---------------------------------------------------------------------
    def _choose_provider(self, meta_profile: Optional[MetaProfileSnapshot]) -> str:
        provider = "openai"

        if self.prefer_anthropic:
            provider = "anthropic"
        if self.prefer_openai:
            provider = "openai"

        # Let meta-profile override user-configured bias
        if meta_profile is not None:
            if meta_profile.prefers_anthropic:
                provider = "anthropic"
            if meta_profile.prefers_openai:
                provider = "openai"

        # Telemetry-aware adjustment: if recent exception volume is high,
        # bias toward the default provider ("openai") to stabilize behavior.
        try:
            events = get_all_events()
            exception_count = 0
            for evt in events:
                attrs = getattr(evt, "attributes", {}) or {}
                if attrs.get("event_type") == "exception":
                    exception_count += 1
            # If there are many recent exceptions and the current provider
            # is not the default, flip back to "openai".
            if exception_count > 20 and provider != "openai":
                provider = "openai"
        except Exception:
            # Telemetry must never break routing.
            pass

        return provider

    # ---------------------------------------------------------------------
    # ToT branch count for Strategy agent
    # ---------------------------------------------------------------------
    def strategy_branches_for(self, complexity: ComplexityLevel) -> int:
        """
        Number of branches StrategyLLMAgent should explore.
        """
        if complexity == ComplexityLevel.LOW:
            return 1
        if complexity == ComplexityLevel.MEDIUM:
            return 3
        return 4  # HIGH complexity → deeper exploration

    # ---------------------------------------------------------------------
    # Main model-selection entrypoint
    # ---------------------------------------------------------------------
    def select_model(
        self,
        task: str,
        complexity: Optional[ComplexityLevel],
        meta_profile: Optional[MetaProfileSnapshot],
    ) -> str:
        """
        Select the appropriate model for a given task and complexity.

        task:
            A string identifier describing the logical task, e.g.:
                - "strategy_generate_branch"
                - "strategy_select_branch"
                - "drafting_structure"
                - "drafting_narrative"
                - "drafting_compliance"
                - "qa_semantic_check"
                - "safety_check"

        complexity:
            L1-estimated ComplexityLevel for the workload.

        meta_profile:
            Optional MetaProfileSnapshot influencing provider choice.
        """
        provider = self._choose_provider(meta_profile)

        # Task-specific overrides
        if task.startswith("drafting_"):
            return DRAFTING_MODELS[provider]

        if task.startswith("qa_") or task.startswith("safety_"):
            return QA_SAFETY_MODELS[provider]

        if task in ("strategy_generate_branch", "strategy_select_branch"):
            if self.allow_heavy:
                return HEAVY_MODELS[provider]
            return MEDIUM_MODELS[provider]

        # Complexity-based routing
        if complexity == ComplexityLevel.LOW:
            # If low cost is enforced, always pick light models
            if self.enforce_low_cost:
                return LIGHT_MODELS[provider]
            return MEDIUM_MODELS[provider]

        if complexity == ComplexityLevel.MEDIUM:
            return MEDIUM_MODELS[provider]

        # HIGH complexity
        if self.allow_heavy:
            return HEAVY_MODELS[provider]
        return MEDIUM_MODELS[provider]


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
        • Job seniority / requirements
        • Resume length
        • QA / correction rates from meta_profile
        • Deterministic skill and domain classifiers (non-LLM)

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

    # Senior roles → more complexity
    seniority = str(getattr(job, "seniority", "")).lower()
    title = str(getattr(job, "title", "")).lower()
    if seniority in ("director", "vp", "svp", "c-level", "chief") or any(
        t in title for t in ("director", "vp", "svp", "chief", "head")
    ):
        score += 0.5

    # Many requirements → more alignment complexity
    try:
        reqs = getattr(job, "requirements", []) or []
        if len(reqs) > 8:
            score += 0.3
        if len(reqs) > 15:
            score += 0.3
    except Exception:
        pass

    # Long experience → more data to integrate
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

    # Map score → ComplexityLevel
    if score < 1.2:
        return ComplexityLevel.LOW
    if score < 1.8:
        return ComplexityLevel.MEDIUM
    return ComplexityLevel.HIGH
