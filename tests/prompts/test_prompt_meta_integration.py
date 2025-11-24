from __future__ import annotations

from typing import Any

from core.models.models import (
    PromptMeta,
    StrategyPlan,
    DraftingPlan,
    QAPlan,
    SafetyPlan,
    RAGPlan,
    WorkflowPlanBundle,
)

from meta.prompt_builder import get_prompt_meta_from_plan


def _make_bundle_with_prompt_meta() -> WorkflowPlanBundle:
    meta = PromptMeta(
        sections=[{"id": "strategy", "role": "planner"}],
        injection_types=["job_posting"],
        taxonomy={"profile_id": "TEST"},
        meta_bias={"elevated_caution": True},
    )

    return WorkflowPlanBundle(
        strategy=StrategyPlan(),
        rag=RAGPlan(),
        drafting=DraftingPlan(),
        qa=QAPlan(),
        safety=SafetyPlan(),
        prompt_meta=meta,
    )


def test_get_prompt_meta_from_plan_returns_attached_meta() -> None:
    bundle = _make_bundle_with_prompt_meta()
    result = get_prompt_meta_from_plan(bundle)
    assert isinstance(result, PromptMeta)
    assert result.taxonomy.get("profile_id") == "TEST"
    assert result.meta_bias.get("elevated_caution") is True


def test_get_prompt_meta_from_plan_handles_none_and_missing() -> None:
    assert get_prompt_meta_from_plan(None) is None

    bundle = WorkflowPlanBundle(
        strategy=StrategyPlan(),
        rag=RAGPlan(),
        drafting=DraftingPlan(),
        qa=QAPlan(),
        safety=SafetyPlan(),
    )
    assert get_prompt_meta_from_plan(bundle) is None
