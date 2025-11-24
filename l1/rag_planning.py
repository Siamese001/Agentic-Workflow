"""RAG planning module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from core.models.models import ExecutionContext, Evidence
from meta.prompt_builder import PromptInstance, build_rag_prompt, build_hyde_prompt


@dataclass(frozen=True)
class RAGReasoningPlan:
    """Pure planning artifact for RAG reasoning."""

    prompt: PromptInstance


@dataclass(frozen=True)
class HydePlan:
    """Pure planning artifact for HYDE query generation."""

    prompt: PromptInstance


def plan_rag_reasoning(
    rag_plan: Any,
    *,
    ctx: ExecutionContext,
    evidence: Sequence[Evidence],
) -> RAGReasoningPlan:
    """Generate a pure RAG reasoning plan."""
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
    """Generate a pure HYDE query plan."""
    prompt = build_hyde_prompt(
        plan=hyde_plan,
        ctx=ctx,
        prompt_id="system.hyde",
        layer="L2",
        agent="hyde",
        model_tier="balanced",
    )
    return HydePlan(prompt=prompt)
