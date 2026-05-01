"""Property-based tests for apps_research.

Hypothesis explores topic / config variations; these tests enforce invariants
from `apps_research/SVP_ENGINEERING_REVIEW.md`:
  - Topic round-trips for any non-empty text.
  - Result types always expose gate_violations.
  - SourceEntry confidence enforces [0,1] across the full continuous range
    (when SourceEntry is exposed).

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import unittest

from hypothesis import assume, given, settings, strategies as st

from apps_research.types import (
    ResearchConfig,
    ResearchRequest,
    ResearchResult,
)


NON_EMPTY_TEXT = st.text(min_size=1, max_size=200).filter(lambda s: s.strip())


class TestResearchProperties(unittest.TestCase):
    @settings(max_examples=30, deadline=None)
    @given(topic=NON_EMPTY_TEXT)
    def test_topic_round_trip(self, topic: str) -> None:
        req = ResearchRequest(topic=topic)
        rebuilt = ResearchRequest.model_validate(req.model_dump())
        self.assertEqual(req.topic, rebuilt.topic)

    @settings(max_examples=10, deadline=None)
    @given(seed=st.integers())
    def test_default_result_has_gate_violations(self, seed: int) -> None:
        del seed
        result = ResearchResult()
        self.assertIsInstance(result.gate_violations, list)

    @settings(max_examples=15, deadline=None)
    @given(invalid_conf=st.one_of(
        st.floats(min_value=1.0001, max_value=2.0, allow_nan=False),
        st.floats(min_value=-1.0, max_value=-0.0001, allow_nan=False),
    ))
    def test_source_entry_rejects_out_of_range_confidence(self, invalid_conf: float) -> None:
        try:
            from apps_research.types import SourceEntry
        except ImportError:  # guardian: allow-defensive-import -- optional type export for property test
            self.skipTest("SourceEntry not exported")
            return
        # Skip exactly 1.0 / 0.0 boundary (those should be allowed).
        assume(invalid_conf > 1.0 or invalid_conf < 0.0)
        with self.assertRaises(Exception):
            SourceEntry(
                source_id="src-001",
                title="Test Source",
                confidence=invalid_conf,
            )

    @settings(max_examples=15, deadline=None)
    @given(valid_conf=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    def test_source_entry_accepts_in_range_confidence(self, valid_conf: float) -> None:
        try:
            from apps_research.types import SourceEntry
        except ImportError:  # guardian: allow-defensive-import -- optional type export for property test
            self.skipTest("SourceEntry not exported")
            return
        entry = SourceEntry(
            source_id="src-001",
            title="Test Source",
            confidence=valid_conf,
        )
        # Round-trip preserves the value.
        rebuilt = SourceEntry.model_validate(entry.model_dump())
        self.assertAlmostEqual(rebuilt.confidence, valid_conf, places=6)


if __name__ == "__main__":
    unittest.main()
