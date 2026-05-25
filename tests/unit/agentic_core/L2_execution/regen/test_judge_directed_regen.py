"""Tests for judge_directed_regen plan contract."""

from __future__ import annotations

import pytest

from agentic_core.L2_execution.regen.judge_directed_regen import (
    DEFAULT_STEP_ORDER,
    JudgeDirectedRegenPlan,
    JudgeDirectedRegenStep,
    validate_step_order,
)


def test_default_step_order_x2_before_rescore() -> None:
    assert DEFAULT_STEP_ORDER.index(JudgeDirectedRegenStep.X2_POST_REGEN) < DEFAULT_STEP_ORDER.index(
        JudgeDirectedRegenStep.JUDGE_RESCORE,
    )


def test_validate_step_order_rejects_rescore_before_x2() -> None:
    bad = (
        JudgeDirectedRegenStep.EVALUATE_TRIGGER,
        JudgeDirectedRegenStep.JUDGE_RESCORE,
        JudgeDirectedRegenStep.X2_POST_REGEN,
    )
    with pytest.raises(ValueError, match="X2_POST_REGEN must precede"):
        validate_step_order(bad)


def test_plan_serializes() -> None:
    plan = JudgeDirectedRegenPlan()
    body = plan.as_dict()
    assert body["schema"] == "judge_directed_regen_plan_v1"
    assert "same_authority_regen" in body["steps"]
