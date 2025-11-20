# FILE: 10_10/routing.py
"""
Routing Policy for Agentic Workflow v10_10
==========================================

This module handles *all* model selection decisions.

Responsibilities:
    • Choose the correct LLM model family for each task.
    • Use ComplexityLevel, RoutingHint, and MetaProfileSnapshot.
    • Balance cost, latency, safety sensitivity, and reasoning needs.
    • Provide number-of-branches for Strategy ToT.
    • Remain pure (no I/O, no LLM calls).

Non-Responsibilities:
    • No prompt logic (PromptRegistry handles that).
    • No network calls (runtime_utils.invoke_model handles that).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any

from models import ComplexityLevel, RoutingHint
from meta_profile import MetaProfileSnapshot


# ==============================================================================
# Model Families
# ==============================================================================

# Light, cheap, fast — shallow reasoning
LIGHT_MODELS = {
    "openai": "gpt-4.1-mini",
    "anthropic": "claude-3-haiku",
}

# Balanced — solid reasoning, moderate price
MEDIUM_MODELS = {
    "openai": "gpt-5.1",
    "anthropic": "claude-3.5-sonnet",
}

# Heavy — deep reasoning, best for complex planning & strategy
HEAVY_MODELS = {
    "openai": "gpt-5.1-codex",
    "anthropic": "claude-3.5-opus",
}

# Specialized for multi-step narrative generation
DRAFTING_MODELS = {
    "openai": "gpt-5.1-codex",
    "anthropic": "claude-3.5-opus",
}

# Specialized for QA & Safety JSON output requirements
QA_SAFETY_MODELS = {
    "openai": "gpt-4.1",
    "anthropic": "claude-3.5-sonnet",
}


# ==============================================================================
# Routing Policy
# ==============================================================================

@dataclass
class RoutingPolicy:
    """
    RoutingPolicy encapsulates provider & model preferences.

    Fields:
        prefer_anthropic: bias toward Anthropic models (semantic/long outputs)
        prefer_openai:    bias toward OpenAI models (structured/code reasoning)
        allow_heavy:      whether heavy models are allowed under current budgets
        enforce_low_cost: if True, light-tier is preferred unless complexity=high
    """

    prefer_anthropic: bool = False
    prefer_openai: bool = True
    allow_heavy: bool = True
    enforce_low_cost: bool = False

    def _choose_provider(
        self, meta_profile: Optional[MetaProfileSnapshot]
    ) -> str:
        """
        Decide between OpenAI and Anthropic.
        """
        provider = "openai"

        if self.prefer_anthropic:
            provider = "anthropic"
        if self.prefer_openai:
            provider = "openai"

        # Meta-learning overrides user bias
        if meta_profile:
            if meta_profile.prefers_anthropic:
                provider = "anthropic"
            if meta_profile.prefers_openai:
                provider = "openai"

        return provider

    # ----------------------------------------------------------------------
    # Strategy ToT branch depth
    # ----------------------------------------------------------------------
    def strategy_branches_for(self, complexity: ComplexityLevel) -> int:
        if complexity == ComplexityLevel.LOW:
            return 1
        if complexity == ComplexityLevel.MEDIUM:
            return 3
        return 4  # HIGH -> deeper ToT exploration

    # ----------------------------------------------------------------------
    # Main routing logic
    # ----------------------------------------------------------------------
    def select_model(
        self,
        task: str,
        complexity: Optional[ComplexityLevel],
        meta_profile: Optional[MetaProfileSnapshot],
    ) -> str:
        """
        Top-level router used by ALL cognitive agents.

        Inputs:
            task         — prompt ID (e.g. "drafting_narrative", "qa_semantic_check")
            complexity   — ComplexityLevel
            meta_profile — historical signals

        Output:
            model string (e.g. "gpt-5.1-codex")
        """
        provider = self._choose_provider(meta_profile)

        # 1. Task-specific overrides first
        if task.startswith("drafting_"):
            return DRAFTING_MODELS[provider]

        if task.startswith("qa_") or task.startswith("safety_"):
            return QA_SAFETY_MODELS[provider]

        if task in ("strategy_generate_branch", "strategy_select_branch"):
            if self.allow_heavy:
                return HEAVY_MODELS[provider]
            return MEDIUM_MODELS[provider]

        # 2. Complexity-based general routing
        if complexity == ComplexityLevel.LOW:
            return LIGHT_MODELS[provider]

        if complexity == ComplexityLevel.MEDIUM:
            # Enforce low-cost mode if enabled
            if self.enforce_low_cost:
                return LIGHT_MODELS[provider]
            return MEDIUM_MODELS[provider]

        if complexity == ComplexityLevel.HIGH:
            if self.allow_heavy:
                return HEAVY_MODELS[provider]
            return MEDIUM_MODELS[provider]

        # 3. Fallback (unlikely)
        return MEDIUM_MODELS[provider]


# ==============================================================================
# Complexity Classifier (used in L1)
# ==============================================================================

def classify_complexity(
    job: Any,
    resume: Any,
    config: Any,
    meta_profile: Optional[MetaProfileSnapshot],
) -> ComplexityLevel:
    """
    Lightweight heuristic classifier used by L1.

    Factors:
        • Job seniority
        • Resume length / density
        • Requirement count
        • Meta-profile failure history
    """
    score = 1.0  # start baseline at medium-ish

    # Senior jobs → more complexity
    if job.seniority in ("Director", "VP", "SVP", "C-level"):
        score += 0.5

    # Long resumes -> more reasoning complexity
    if len(resume.experience_sections) > 6:
        score += 0.4

    # Many job requirements → more alignment work
    if len(job.requirements) > 8:
        score += 0.3

    # Meta-learning feedback
    if meta_profile:
        if meta_profile.qa_failure_rate_last_10 > 0.4:
            score += 0.3
        if meta_profile.correction_rate_last_10 > 0.3:
            score += 0.2

    if score < 1.2:
        return ComplexityLevel.LOW
    elif score < 1.8:
        return ComplexityLevel.MEDIUM
    else:
        return ComplexityLevel.HIGH
