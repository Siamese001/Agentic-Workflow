"""apps_lic.engines.judges.narrative_coherence_judge — stub (v1).

IS_STUB=True: returns GRADER_UNKNOWN_SENTINEL until a real LLM judge is calibrated.
GRADER_ID registered in apps_lic grader_roster.yaml (lic::narrative_coherence_judge::v1).
"""

from __future__ import annotations

from typing import Any

from agentic_core.L3_orchestration.exit_eval.v6.app_grader_registry import (
    GRADER_UNKNOWN_SENTINEL,
)

IS_STUB: bool = True
IS_CALIBRATED: bool = False
GRADER_ID: str = "lic::narrative_coherence_judge::v1"


class NarrativeCoherenceJudge:
    is_stub: bool = True
    grader_id: str = GRADER_ID

    def grade(self, dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
        return GRADER_UNKNOWN_SENTINEL, []


def grade(dim: Any, run_context: dict[str, Any]) -> tuple[Any, list[str]]:
    return NarrativeCoherenceJudge().grade(dim, run_context)


__all__ = ["NarrativeCoherenceJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
