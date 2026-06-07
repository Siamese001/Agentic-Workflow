"""Property-based tests for apps_rfp.

Hypothesis explores problem-statement variations; these tests enforce
invariants from `apps_rfp/SVP_ENGINEERING_REVIEW.md`:
  - Problem statement round-trips for any non-empty text.
  - Result types always expose gate_violations.
  - RoadmapPhase rejects out-of-range duration (when exposed).

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import unittest

from hypothesis import assume, given, settings, strategies as st

from apps_rfp.types import (
    RfpConfig,
    RfpRequest,
    RfpResult,
)


# RfpRequest.problem_statement requires minLength=20.
PROBLEM_STATEMENT_TEXT = st.text(min_size=25, max_size=500).filter(
    lambda s: len(s.strip()) >= 20
)


class TestRfpProperties(unittest.TestCase):
    @settings(max_examples=25, deadline=None)
    @given(problem=PROBLEM_STATEMENT_TEXT)
    def test_problem_statement_round_trip(self, problem: str) -> None:
        req = RfpRequest(problem_statement=problem)
        rebuilt = RfpRequest.model_validate(req.model_dump())
        self.assertEqual(req.problem_statement, rebuilt.problem_statement)

    @settings(max_examples=10, deadline=None)
    @given(seed=st.integers())
    def test_default_result_has_gate_violations(self, seed: int) -> None:
        del seed
        result = RfpResult()
        self.assertIsInstance(result.gate_violations, list)

    @settings(max_examples=15, deadline=None)
    @given(weeks=st.one_of(
        st.integers(max_value=0),
        st.integers(min_value=53, max_value=200),
    ))
    def test_roadmap_phase_rejects_out_of_range_duration(self, weeks: int) -> None:
        try:
            from apps_rfp.types import RoadmapPhase
        except ImportError:  # guardian: allow-return-none-swallow -- optional type export; property test skips on ImportError
            self.skipTest("RoadmapPhase not exported")
            return
        assume(weeks <= 0 or weeks >= 53)
        with self.assertRaises(Exception):
            RoadmapPhase(phase_id="p1", name="phase-x", duration_weeks=weeks)

    @settings(max_examples=15, deadline=None)
    @given(weeks=st.integers(min_value=1, max_value=52))
    def test_roadmap_phase_accepts_in_range_duration(self, weeks: int) -> None:
        try:
            from apps_rfp.types import RoadmapPhase
        except ImportError:  # guardian: allow-return-none-swallow -- optional type export; property test skips on ImportError
            self.skipTest("RoadmapPhase not exported")
            return
        phase = RoadmapPhase(
            phase_id="p1", name="phase-x", duration_weeks=weeks,
        )
        self.assertEqual(phase.duration_weeks, weeks)


if __name__ == "__main__":
    unittest.main()
