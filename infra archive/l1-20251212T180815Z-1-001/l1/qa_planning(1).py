"""
Quality assurance planning for resume improvement validation and accuracy.

Creates structured plans to ensure comprehensive resume enhancement
quality and job alignment.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

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

    Ensures thorough evaluation of resume improvement content
    for accuracy and job alignment.
    """

    prompt: PromptInstance


@dataclass(frozen=True)
class CouncilPlan:
    """
    Structures council review planning approach.

    Coordinates comprehensive evaluation of resume enhancement
    recommendations for improved quality.
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
    Creates semantic quality assurance plan for resume validation.

    Ensures thorough evaluation of resume content for accuracy
    and improved job alignment.
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


def plan_qa(
    question: str,
    context: Optional[str] = None,
    *,
    model_tier: str = "balanced",
) -> SemanticQAPlan:
    """
    Plan a QA response for the given question and context.
    
    Args:
        question: The question to answer
        context: Optional context for the question
        model_tier: Model tier to use
        
    Returns:
        QA plan with semantic search and response generation
    """
    return plan_semantic_qa(question, context, model_tier=model_tier)


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



