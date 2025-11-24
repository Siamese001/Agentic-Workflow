"""QA planning module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models.models import (
    ExecutionContext,
    DraftingResult,
    RAGResult,
)
from meta.prompt_builder import PromptInstance, build_qa_prompt


@dataclass(frozen=True)
class SemanticQAPlan:
    """Pure planning artifact for semantic QA."""

    prompt: PromptInstance


@dataclass(frozen=True)
class CouncilPlan:
    """Pure planning artifact for council review aggregation."""

    prompt: PromptInstance


def plan_semantic_qa(
    qa_plan: Any,
    *,
    ctx: ExecutionContext,
    draft: DraftingResult,
    rag: RAGResult,
) -> SemanticQAPlan:
    """Generate a pure semantic QA plan."""
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
    """Generate a pure council review plan."""
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
