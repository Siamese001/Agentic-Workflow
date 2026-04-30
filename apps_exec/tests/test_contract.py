"""Contract test seed for apps_exec.

Purpose: assert the brief-generation public contract holds.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W2.1)
"""
from __future__ import annotations

import unittest

from apps_exec.types import (
    BriefSection,
    ExecBriefConfig,
    ExecBriefRequest,
    ExecBriefResult,
)


class TestAppsExecContract(unittest.TestCase):
    def test_default_request_round_trips(self) -> None:
        req = ExecBriefRequest()
        rebuilt = ExecBriefRequest.model_validate(req.model_dump())
        self.assertEqual(req.model_dump(), rebuilt.model_dump())

    def test_default_config_round_trips(self) -> None:
        cfg = ExecBriefConfig()
        rebuilt = ExecBriefConfig.model_validate(cfg.model_dump())
        self.assertEqual(cfg.model_dump(), rebuilt.model_dump())

    def test_result_exposes_gate_violations(self) -> None:
        result = ExecBriefResult()
        self.assertTrue(hasattr(result, "gate_violations"))
        self.assertIsInstance(result.gate_violations, list)

    def test_brief_section_body_min_length_enforced(self) -> None:
        # Body validation: SVP review claims min 50 chars.
        with self.assertRaises(Exception):
            BriefSection(
                section_id="s1", heading="h", body="too short"
            ).model_dump()

    def test_brief_section_accepts_valid_body(self) -> None:
        section = BriefSection(
            section_id="s1",
            heading="Executive Summary",
            body="x" * 80,
        )
        self.assertGreaterEqual(len(section.body), 50)


if __name__ == "__main__":
    unittest.main()
