"""Pure planning (L1) interfaces shared across Strategy/RAG/QA/Safety layers."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional

from .strategy_planning import (
    StrategyPromptPlan,
    DraftingPromptPlan,
    plan_strategy_prompt,
    plan_drafting_prompt,
)
from .rag_planning import (
    RAGReasoningPlan,
    HydeQueryPlan,
    build_rag_reasoning_plan,
    build_hyde_query_plan,
)
from .qa_planning import (
    SemanticQAPlan,
    plan_semantic_qa_prompt,
    plan_council_prompt,
)
from .safety_planning import (
    SafetyReviewPlan,
    plan_safety_review_prompt,
)
from .reasoning import (
    LatentThinkingPlan,
    generate_latent_thinking_plan,
)


class ReasoningMode(str, Enum):
    """Supported reasoning modes for L1 components."""

    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    REACT = "react"
    REFLEXION = "reflexion"


@dataclass
class ReasoningContext:
    """Context for reasoning operations."""

    mode: ReasoningMode = ReasoningMode.CHAIN_OF_THOUGHT
    max_steps: int = 10
    temperature: float = 0.7


class BaseReasoner:
    """Base class for all L1 reasoning components."""

    def reason(self, prompt: str, context: Optional[ReasoningContext] = None) -> str:  # pragma: no cover - interface only
        raise NotImplementedError()


__all__ = [
    "ReasoningMode",
    "ReasoningContext",
    "BaseReasoner",
    "StrategyPromptPlan",
    "DraftingPromptPlan",
    "RAGReasoningPlan",
    "HydeQueryPlan",
    "SemanticQAPlan",
    "SafetyReviewPlan",
    "LatentThinkingPlan",
    "plan_strategy_prompt",
    "plan_drafting_prompt",
    "build_rag_reasoning_plan",
    "build_hyde_query_plan",
    "plan_semantic_qa_prompt",
    "plan_council_prompt",
    "plan_safety_review_prompt",
    "generate_latent_thinking_plan",
]
