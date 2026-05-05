"""apps_lic.engines.judges.tone_register_fit_judge — stub (v1).

IS_STUB=True: returns GRADER_UNKNOWN_SENTINEL until a real LLM judge is calibrated.
GRADER_ID registered in apps_lic grader_roster.yaml (lic::tone_register_fit_judge::v1).
"""

from __future__ import annotations

from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = True
IS_CALIBRATED: bool = False
GRADER_ID: str = "lic::tone_register_fit_judge::v1"


class ToneRegisterFitJudge:
    is_stub: bool = True
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        return GRADER_UNKNOWN_SENTINEL, []


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return ToneRegisterFitJudge().grade(dim, run_context)


__all__ = ["ToneRegisterFitJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
