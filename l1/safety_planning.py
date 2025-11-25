"""
Safety planning for résumé improvement validation.

Creates structured plans to ensure professional standards and compliance in résumé enhancement.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models.models import (
    ExecutionContext,
    DraftingResult,
    RAGResult,
    QAResult,
)
from l1.builders.prompt_builder import PromptInstance, build_safety_prompt


@dataclass(frozen=True)
class SafetyPlan:
    """
    Defines safety validation structure for résumé content.

    Ensures professional standards and compliance in résumé improvement recommendations.
    """

    prompt: PromptInstance


def plan_safety_review(
    safety_plan: Any,
    *,
    ctx: ExecutionContext,
    draft: DraftingResult,
    rag: RAGResult,
    qa: QAResult,
) -> SafetyPlan:
    """
    Creates comprehensive safety plan for résumé validation.

    Structures evaluation approach to ensure professional résumé enhancement standards.
    """
    prompt = build_safety_prompt(
        plan=safety_plan,
        ctx=ctx,
        drafting=draft,
        qa=qa,
        prompt_id="system.safety.agent",
        layer="L2",
        agent="safety",
        model_tier="balanced",
    )
    return SafetyPlan(prompt=prompt)



