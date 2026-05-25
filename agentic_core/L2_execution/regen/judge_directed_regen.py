"""Policy-free judge-directed regen step contract (ADR-086 apps orchestration SSOT).

Core owns step ordering and contract validation only. Apps own trigger policy,
X2 re-check, judge rescore, and disposition.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any


class JudgeDirectedRegenStep(str, Enum):
    EVALUATE_TRIGGER = "evaluate_trigger"
    SAME_AUTHORITY_REGEN = "same_authority_regen"
    PREPARE_CANDIDATE = "prepare_candidate"
    X2_PRE_SNAPSHOT = "x2_pre_snapshot"
    X2_POST_REGEN = "x2_post_regen"
    X2_REPAIR = "x2_repair"
    JUDGE_RESCORE = "judge_rescore"
    EMIT_RECEIPTS = "emit_receipts"


DEFAULT_STEP_ORDER: tuple[JudgeDirectedRegenStep, ...] = (
    JudgeDirectedRegenStep.EVALUATE_TRIGGER,
    JudgeDirectedRegenStep.SAME_AUTHORITY_REGEN,
    JudgeDirectedRegenStep.PREPARE_CANDIDATE,
    JudgeDirectedRegenStep.X2_PRE_SNAPSHOT,
    JudgeDirectedRegenStep.X2_POST_REGEN,
    JudgeDirectedRegenStep.X2_REPAIR,
    JudgeDirectedRegenStep.JUDGE_RESCORE,
    JudgeDirectedRegenStep.EMIT_RECEIPTS,
)


@dataclass(frozen=True, slots=True)
class JudgeDirectedRegenPlan:
    """Immutable loop plan — apps executor walks these steps."""

    steps: tuple[JudgeDirectedRegenStep, ...] = DEFAULT_STEP_ORDER
    require_x2_pass_before_rescore: bool = True
    allow_x2_repair: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {
            "schema": "judge_directed_regen_plan_v1",
            "steps": [s.value for s in self.steps],
            "require_x2_pass_before_rescore": self.require_x2_pass_before_rescore,
            "allow_x2_repair": self.allow_x2_repair,
        }


def validate_step_order(steps: tuple[JudgeDirectedRegenStep, ...]) -> None:
    """Ensure x2 post-regen precedes judge rescore when both present."""
    if (
        JudgeDirectedRegenStep.JUDGE_RESCORE in steps
        and JudgeDirectedRegenStep.X2_POST_REGEN in steps
    ):
        if steps.index(JudgeDirectedRegenStep.X2_POST_REGEN) > steps.index(
            JudgeDirectedRegenStep.JUDGE_RESCORE,
        ):
            raise ValueError("X2_POST_REGEN must precede JUDGE_RESCORE")


__all__ = [
    "DEFAULT_STEP_ORDER",
    "JudgeDirectedRegenPlan",
    "JudgeDirectedRegenStep",
    "validate_step_order",
]
