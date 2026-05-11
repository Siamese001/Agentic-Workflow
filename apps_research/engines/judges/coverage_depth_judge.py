"""apps_research.engines.judges.coverage_depth_judge — Core-backed compatibility facade.

W9 BOUNDARY ENFORCEMENT
========================
apps_research does NOT own judge execution. All coverage_depth scoring logic
lives in ``agentic_core.evaluation.judges.deterministic_graders``. This file is
a compatibility facade only — it re-exports core symbols so that existing
callers (grader_roster.yaml, AppGraderRegistry dispatch, spine alignment tests)
continue to work without any scoring logic residing in apps_research.

PROMOTION HISTORY
=================
- v1 original implementation (DS-D plan): local heuristic scorer in apps_research.
- v2 (W2R, W9 closure): scoring logic migrated to
  ``agentic_core.evaluation.judges.deterministic_graders.grade_coverage_depth_run_context``.
  This file is now a zero-logic compatibility alias. IS_STUB=False because the
  grader is backed by real core logic, not a raise-only stub.

Integration contract
--------------------
Callable: grade(dim, run_context) -> tuple[float | int, list[str]]
Returns (score in [0, 1], evidence_refs) or (GRADER_UNKNOWN_SENTINEL, [])
when abstaining. Delegated entirely to core.
"""

from __future__ import annotations

from agentic_core.evaluation.judges.deterministic_graders import (
    grade_coverage_depth_run_context as grade,
)

IS_STUB: bool = False
IS_CALIBRATED: bool = True
GRADER_ID: str = "research::coverage_depth_judge::v1"


class CoverageDepthJudge:
    """Compatibility facade. Execution is delegated to agentic_core deterministic graders.

    apps_research does not own judge execution (W9 boundary). Scoring logic
    lives in agentic_core.evaluation.judges.deterministic_graders.
    """

    is_stub: bool = False
    grader_id: str = GRADER_ID

    def __call__(self, dim: str, run_context: object) -> object:
        return grade(dim, run_context)  # type: ignore[arg-type]


__all__ = ["CoverageDepthJudge", "grade", "IS_STUB", "IS_CALIBRATED", "GRADER_ID"]
