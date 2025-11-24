"""Safety planning module."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models.models import (
    ExecutionContext,
    DraftingResult,
    RAGResult,
    QAResult,
)
from prompt_builder import PromptInstance, build_safety_prompt


@dataclass(frozen=True)
class SafetyPlan:
    """Pure planning artifact for safety review."""

    prompt: PromptInstance


def plan_safety_review(
    safety_plan: Any,
    *,
    ctx: ExecutionContext,
    draft: DraftingResult,
    rag: RAGResult,
    qa: QAResult,
) -> SafetyPlan:
    """Generate a pure safety review plan."""
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
