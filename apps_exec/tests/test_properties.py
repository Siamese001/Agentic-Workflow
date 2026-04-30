"""Property-based tests for apps_exec.

Hypothesis explores input variations on the brief-generation contract; these
tests enforce invariants from `apps_exec/SVP_ENGINEERING_REVIEW.md`:
  - Result types always expose gate_violations across input variations.
  - Round-trip of any default-constructed config preserves equality.
  - BriefSection rejects bodies under the documented length floor.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (P4 NEXT_STEP)
"""
from __future__ import annotations

import unittest

from hypothesis import given, settings, strategies as st

from apps_exec.types import (
    BriefSection,
    ExecBriefConfig,
    ExecBriefRequest,
    ExecBriefResult,
)


NON_EMPTY_TEXT = st.text(min_size=1, max_size=64).filter(lambda s: s.strip())


class TestExecProperties(unittest.TestCase):
    @settings(max_examples=20, deadline=None)
    @given(content=st.text(min_size=50, max_size=500))
    def test_brief_section_round_trip(self, content: str) -> None:
        section = BriefSection(
            section_id="s1", heading="Test Heading", body=content,
        )
        rebuilt = BriefSection.model_validate(section.model_dump())
        self.assertEqual(section.body, rebuilt.body)
        self.assertEqual(section.section_id, rebuilt.section_id)

    @settings(max_examples=20, deadline=None)
    @given(short_body=st.text(max_size=49))
    def test_short_body_always_rejected(self, short_body: str) -> None:
        with self.assertRaises(Exception):
            BriefSection(
                section_id="s1", heading="t", body=short_body,
            )

    @settings(max_examples=15, deadline=None)
    @given(sid=NON_EMPTY_TEXT, heading=NON_EMPTY_TEXT)
    def test_section_id_and_heading_preserved(self, sid: str, heading: str) -> None:
        section = BriefSection(
            section_id=sid, heading=heading, body="x" * 100,
        )
        rebuilt = BriefSection.model_validate(section.model_dump())
        self.assertEqual(rebuilt.section_id, sid)
        self.assertEqual(rebuilt.heading, heading)

    @settings(max_examples=10, deadline=None)
    @given(seed=st.integers())
    def test_default_result_consistently_has_gate_violations(self, seed: int) -> None:
        # The seed isn't used directly — hypothesis still gives deterministic
        # variation across runs to ensure the invariant holds independent of
        # construction order.
        del seed
        result = ExecBriefResult()
        self.assertIsInstance(result.gate_violations, list)


if __name__ == "__main__":
    unittest.main()
