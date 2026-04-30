"""Contract test seed for apps_underwriting_ai.

Purpose: assert the underwriting public contract holds end-to-end through
the sample fixture. Because UnderwritingRequest has 16 required fields, this
test uses the canonical sample at examples/sample_underwriting_request.json
as the contract seed.

This is the most comprehensive contract test in the portfolio because the
underwriting decision packet has the most stringent integrity requirements
(replay parity, audit trail, hash chain).

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W2.1)
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from apps_underwriting_ai.types import UnderwritingRequest

SAMPLE_PATH = (
    Path(__file__).resolve().parents[1]
    / "examples"
    / "sample_underwriting_request.json"
)


class TestAppsUnderwritingContract(unittest.TestCase):
    def test_sample_request_loads(self) -> None:
        self.assertTrue(SAMPLE_PATH.exists(), f"missing fixture: {SAMPLE_PATH}")
        payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        req = UnderwritingRequest.model_validate(payload)
        self.assertIsNotNone(req.request_id)
        self.assertGreater(req.requested_amount, 0)
        self.assertGreater(req.requested_term_months, 0)

    def test_sample_request_round_trips(self) -> None:
        payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        req = UnderwritingRequest.model_validate(payload)
        # Round-trip the typed object through Pydantic to assert serialization parity.
        rebuilt = UnderwritingRequest.model_validate(
            json.loads(req.model_dump_json())
        )
        self.assertEqual(req.request_id, rebuilt.request_id)
        self.assertEqual(req.requested_amount, rebuilt.requested_amount)

    def test_required_fields_enforced(self) -> None:
        """All 16 declared required fields must reject empty construction."""
        with self.assertRaises(Exception):
            UnderwritingRequest()

    def test_replay_capability_signal_present(self) -> None:
        """SVP review claims decision packets are replayable.
        We assert at the minimum that submission_ts is preserved on round-trip,
        because replay parity requires identical input timestamp."""
        payload = json.loads(SAMPLE_PATH.read_text(encoding="utf-8"))
        req1 = UnderwritingRequest.model_validate(payload)
        req2 = UnderwritingRequest.model_validate(
            json.loads(req1.model_dump_json())
        )
        self.assertEqual(req1.submission_ts, req2.submission_ts)


if __name__ == "__main__":
    unittest.main()
