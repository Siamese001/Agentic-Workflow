"""Property-based tests for apps_underwriting_ai — replay parity invariants.

Hypothesis explores variations on the canonical sample request; these tests
enforce invariants from `apps_underwriting_ai/SVP_ENGINEERING_REVIEW.md` and
`THREAT_MODEL.md`:
  - Round-trip parity: re-serializing a valid request must preserve every
    business-critical field exactly. (replay parity foundation)
  - Numeric bounds: requested_amount and requested_term_months must remain
    strictly positive across re-serialization.
  - Submission timestamp must round-trip without drift (per RUNBOOK §3
    determinism requirement).

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W2.2)
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from hypothesis import given, settings, strategies as st

from apps_underwriting_ai.types import UnderwritingRequest

SAMPLE_PATH = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "sample_underwriting_request.json"
)


def _load_sample() -> dict:
    return json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))


class TestUnderwritingProperties(unittest.TestCase):
    @settings(max_examples=20, deadline=None)
    @given(amount=st.integers(min_value=1_000, max_value=100_000_000))
    def test_requested_amount_round_trip(self, amount: int) -> None:
        payload = _load_sample()
        payload["requested_amount"] = amount
        req = UnderwritingRequest.model_validate(payload)
        rebuilt = UnderwritingRequest.model_validate(json.loads(req.model_dump_json()))
        self.assertEqual(req.requested_amount, rebuilt.requested_amount)
        self.assertEqual(rebuilt.requested_amount, amount)
        self.assertGreater(rebuilt.requested_amount, 0)

    @settings(max_examples=20, deadline=None)
    @given(term=st.integers(min_value=1, max_value=600))
    def test_requested_term_round_trip(self, term: int) -> None:
        payload = _load_sample()
        payload["requested_term_months"] = term
        req = UnderwritingRequest.model_validate(payload)
        rebuilt = UnderwritingRequest.model_validate(json.loads(req.model_dump_json()))
        self.assertEqual(req.requested_term_months, term)
        self.assertEqual(rebuilt.requested_term_months, term)

    @settings(max_examples=10, deadline=None)
    @given(suffix=st.text(min_size=1, max_size=8, alphabet=st.characters(min_codepoint=ord("A"), max_codepoint=ord("Z"))))
    def test_request_id_round_trip(self, suffix: str) -> None:
        payload = _load_sample()
        payload["request_id"] = f"UW-PROP-{suffix}"
        req = UnderwritingRequest.model_validate(payload)
        rebuilt = UnderwritingRequest.model_validate(json.loads(req.model_dump_json()))
        self.assertEqual(req.request_id, rebuilt.request_id)

    def test_submission_ts_round_trip_no_drift(self) -> None:
        """Determinism: submission_ts MUST round-trip identically to enable
        replay parity (per RUNBOOK §3 + THREAT_MODEL Boundary 4)."""
        payload = _load_sample()
        req = UnderwritingRequest.model_validate(payload)
        for _ in range(5):
            req = UnderwritingRequest.model_validate(json.loads(req.model_dump_json()))
        original = UnderwritingRequest.model_validate(payload)
        self.assertEqual(req.submission_ts, original.submission_ts)


if __name__ == "__main__":
    unittest.main()
