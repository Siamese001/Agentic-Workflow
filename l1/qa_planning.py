"""
Quality assurance planning for résumé improvement validation.

Creates structured plans to ensure comprehensive résumé enhancement quality and accuracy.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models.models import (
    ExecutionContext,
    DraftingResult,
    RAGResult,
)
from l1.builders.prompt_builder import PromptInstance, build_qa_prompt


@dataclass(frozen=True)
class SemanticQAPlan:
    """
    Defines semantic quality assurance structure.

    Ensures thorough evaluation of résumé improvement content for accuracy and relevance.
    """

    prompt: PromptInstance


@dataclass(frozen=True)
class CouncilPlan:
    """
    Structures council review planning approach.

    Coordinates comprehensive evaluation of résumé enhancement recommendations.
    """

    prompt: PromptInstance


def plan_semantic_qa(
    qa_plan: Any,
    *,
    ctx: ExecutionContext,
    draft: DraftingResult,
    rag: RAGResult,
) -> SemanticQAPlan:
    """
    Creates semantic quality assurance plan for résumé validation.

    Structures evaluation approach to ensure comprehensive résumé improvement quality.
    """
    prompt = build_qa_prompt(
        plan=qa_plan,
        ctx=ctx,
        drafting=draft,
        rag=rag,
        prompt_id="system.qa.agent",
        layer="L2",
        agent="qa",
        model_tier="balanced",
    )
    return SemanticQAPlan(prompt=prompt)


def plan_council_review(
    council_plan: Any,
    *,
    ctx: ExecutionContext,
    draft: DraftingResult,
    rag: RAGResult,
) -> CouncilPlan:
    """
    Plans council review for comprehensive résumé assessment.

    Coordinates multi-perspective evaluation to ensure optimal résumé enhancement recommendations.
    """
    prompt = build_qa_prompt(
        plan=council_plan,
        ctx=ctx,
        drafting=draft,
        rag=rag,
        prompt_id="system.qa.council",
        layer="L2",
        agent="qa_council",
        model_tier="balanced",
    )
    return CouncilPlan(prompt=prompt)



