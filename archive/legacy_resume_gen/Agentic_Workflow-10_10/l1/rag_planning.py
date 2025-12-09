"""
RAG planning for comprehensive résumé evidence gathering.

Creates structured plans to retrieve relevant data for optimal résumé improvement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from core.models.models import ExecutionContext, Evidence
from l1.builders.prompt_builder import PromptInstance, build_rag_prompt, build_hyde_prompt


@dataclass(frozen=True)
class RAGReasoningPlan:
    """
    Defines evidence analysis structure for résumé improvement.

    Ensures systematic processing of retrieved data for comprehensive résumé enhancement.
    """

    prompt: PromptInstance


@dataclass(frozen=True)
class HydePlan:
    """
    Structures hypothetical document query planning.

    Creates enhanced search strategies for better résumé evidence retrieval.
    """

    prompt: PromptInstance


def plan_rag_reasoning(
    rag_plan: Any,
    *,
    ctx: ExecutionContext,
    evidence: Sequence[Evidence],
) -> RAGReasoningPlan:
    """
    Creates evidence analysis plan for résumé improvement.

    Structures approach to process retrieved data for comprehensive résumé enhancement.
    """
    prompt = build_rag_prompt(
        plan=rag_plan,
        ctx=ctx,
        evidence=evidence,
        prompt_id="system.rag.reasoning",
        layer="L2",
        agent="rag",
        model_tier="balanced",
    )
    return RAGReasoningPlan(prompt=prompt)


def plan_hyde_query(
    hyde_plan: Any,
    *,
    ctx: ExecutionContext,
) -> HydePlan:
    """
    Plans enhanced query generation for résumé evidence retrieval.

    Creates hypothetical documents to improve search relevance for résumé improvement.
    """
    prompt = build_hyde_prompt(
        plan=hyde_plan,
        ctx=ctx,
        prompt_id="system.hyde",
        layer="L2",
        agent="hyde",
        model_tier="balanced",
    )
    return HydePlan(prompt=prompt)



