"""Typed execution receipts for the L6 four-level eval ladder."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any


class EvalLevel(str, Enum):
    MICRO = "MICRO"
    LANE = "LANE"
    SUITE = "SUITE"
    META = "META"


@dataclass(frozen=True, slots=True)
class L6EvalExecutionReceipt:
    eval_level: str
    deterministic_only: bool
    writer_live: bool
    graders_live: bool
    human_labels_present: bool
    calibration_fresh: bool
    execution_claim_status: str
    reason_codes: tuple[str, ...]
    current_run_authority: str = "NONE"
    future_run_only: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_l6_eval_execution_receipt(
    *,
    eval_level: EvalLevel | str,
    deterministic_only: bool,
    writer_live: bool,
    graders_live: bool,
    human_labels_present: bool = False,
    calibration_fresh: bool = False,
) -> L6EvalExecutionReceipt:
    level = EvalLevel(str(eval_level))
    reasons: list[str] = []
    if level is EvalLevel.MICRO:
        if writer_live or graders_live:
            reasons.append("micro_eval_must_not_claim_live_writer_or_graders")
    elif level in {EvalLevel.LANE, EvalLevel.SUITE}:
        if deterministic_only:
            reasons.append("deterministic_fixture_cannot_claim_lane_or_suite_eval")
        if not writer_live:
            reasons.append("live_writer_required")
        if not graders_live:
            reasons.append("live_graders_required")
    elif level is EvalLevel.META:
        if deterministic_only:
            reasons.append("deterministic_fixture_cannot_claim_meta_eval")
        if not graders_live:
            reasons.append("live_grader_panel_required")
        if not human_labels_present:
            reasons.append("human_labels_required")
        if not calibration_fresh:
            reasons.append("fresh_calibration_required")

    return L6EvalExecutionReceipt(
        eval_level=level.value,
        deterministic_only=deterministic_only,
        writer_live=writer_live,
        graders_live=graders_live,
        human_labels_present=human_labels_present,
        calibration_fresh=calibration_fresh,
        execution_claim_status="PASS" if not reasons else "FAIL",
        reason_codes=tuple(reasons),
    )


__all__ = ["EvalLevel", "L6EvalExecutionReceipt", "build_l6_eval_execution_receipt"]
