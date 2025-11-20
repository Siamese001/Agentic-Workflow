# FILE: 10_10/routing.py
"""
Routing Policy for Agentic Workflow v10_10
==========================================

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
from typing import Optional, Any

from models import ComplexityLevel
from meta_profile import MetaProfileSnapshot


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
            Prompt ID used by cognitive_agents, e.g.:
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
            # Otherwise balanced defaults
            return LIGHT_MODELS[provider]

        if complexity == ComplexityLevel.MEDIUM:
            if self.enforce_low_cost:
                return LIGHT_MODELS[provider]
            return MEDIUM_MODELS[provider]

        if complexity == ComplexityLevel.HIGH:
            if self.allow_heavy:
                return HEAVY_MODELS[provider]
            return MEDIUM_MODELS[provider]

        # Fallback
        return MEDIUM_MODELS[provider]


# =============================================================================
# Complexity Classifier (L1 Helper)
# =============================================================================

def classify_complexity(
    job: Any,
    resume: Any,
    config: Any,
    meta_profile: Optional[MetaProfileSnapshot],
) -> ComplexityLevel:
    """
    Heuristic classifier used by L1 to estimate ComplexityLevel.

    Factors (purely deterministic):
        • Job seniority
        • Count of job requirements
        • Resume length (experience sections)
        • QA/correction rates from meta_profile

    This logic is intentionally simple and stable.
    """
    score = 1.0  # baseline: between LOW and MEDIUM

    # Senior roles → more complexity
    if getattr(job, "seniority", "").lower() in ("director", "vp", "svp", "c-level", "chief"):
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

    # Meta-profile signal (recent QA/correction rates)
    if meta_profile is not None:
        if meta_profile.qa_failure_rate_last_10 > 0.4:
            score += 0.3
        if meta_profile.correction_rate_last_10 > 0.3:
            score += 0.2

    # Map score → ComplexityLevel
    if score < 1.2:
        return ComplexityLevel.LOW
    if score < 1.8:
        return ComplexityLevel.MEDIUM
    return ComplexityLevel.HIGH

