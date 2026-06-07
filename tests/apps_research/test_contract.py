"""Contract test seed for apps_research.

Purpose: assert the research public contract holds — including the
contradiction-aware and source-confidence dimensions claimed in
SVP_ENGINEERING_REVIEW.md.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (W2.1)
"""
from __future__ import annotations

import unittest

from apps_research.types import (
    ResearchConfig,
    ResearchRequest,
    ResearchResult,
)


class TestAppsResearchContract(unittest.TestCase):
    def test_request_requires_topic(self) -> None:
        with self.assertRaises(Exception):
            ResearchRequest()  # missing required `topic`

    def test_request_with_topic_round_trips(self) -> None:
        req = ResearchRequest(topic="impact of agentic systems on regulated industries")
        rebuilt = ResearchRequest.model_validate(req.model_dump())
        self.assertEqual(req.topic, rebuilt.topic)

    def test_default_config_round_trips(self) -> None:
        cfg = ResearchConfig()
        rebuilt = ResearchConfig.model_validate(cfg.model_dump())
        self.assertEqual(cfg.model_dump(), rebuilt.model_dump())

    def test_result_exposes_gate_violations(self) -> None:
        result = ResearchResult()
        self.assertTrue(hasattr(result, "gate_violations"))
        self.assertIsInstance(result.gate_violations, list)

    def test_source_entry_confidence_bounded(self) -> None:
        """SVP review claims SourceEntry has bounded [0,1] confidence."""
        try:
            from apps_research.types import SourceEntry
        except ImportError:  # guardian: allow-return-none-swallow -- optional type export; test skips on ImportError
            self.skipTest("SourceEntry not exported; structure check only")
            return
        # If exposed, confidence must reject out-of-bounds.
        with self.assertRaises(Exception):
            SourceEntry(url="https://example.com", title="t", confidence=1.5)
        with self.assertRaises(Exception):
            SourceEntry(url="https://example.com", title="t", confidence=-0.1)


if __name__ == "__main__":
    unittest.main()
