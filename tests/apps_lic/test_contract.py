"""Contract test seed for apps_lic.

Purpose: assert the campaign-composition public contract holds. apps_lic is
the architecturally richest app (5-hop registry, retry policy, control plane,
determinism digest), so this seed asserts the input/output contract; W2.2
property tests cover voice-fidelity invariants; W4 will cover end-to-end
hop-chain replay.

Plan: docs/archive/windsurf/legacy-tree/plans/apps-svp-plus-hardening-7c4e3a.md (W2.1)
"""
from __future__ import annotations

import unittest

from apps_lic.types import (
    CampaignConfig,
    CampaignRequest,
    CampaignResult,
    ValidationResult,
)


class TestAppsLicContract(unittest.TestCase):
    def test_campaign_config_requires_name_and_audience(self) -> None:
        with self.assertRaises(Exception):
            CampaignConfig()
        with self.assertRaises(Exception):
            CampaignConfig(name="x")
        with self.assertRaises(Exception):
            CampaignConfig(target_audience="y")

    def test_campaign_config_round_trips(self) -> None:
        cfg = CampaignConfig(name="senior-eng-outreach", target_audience="senior_engineers")
        rebuilt = CampaignConfig.model_validate(cfg.model_dump())
        self.assertEqual(cfg.model_dump(), rebuilt.model_dump())

    def test_campaign_request_requires_id_and_config(self) -> None:
        cfg = CampaignConfig(name="x", target_audience="y")
        with self.assertRaises(Exception):
            CampaignRequest()
        with self.assertRaises(Exception):
            CampaignRequest(campaign_id="abc")  # missing config
        # Valid construction must succeed.
        req = CampaignRequest(campaign_id="abc-001", config=cfg)
        rebuilt = CampaignRequest.model_validate(req.model_dump())
        self.assertEqual(req.campaign_id, rebuilt.campaign_id)

    def test_campaign_result_default_round_trips(self) -> None:
        result = CampaignResult()
        rebuilt = CampaignResult.model_validate(result.model_dump())
        self.assertEqual(result.model_dump(), rebuilt.model_dump())

    def test_validation_result_requires_passed_field(self) -> None:
        # The `passed` field is the boolean verdict — required because every
        # validator in apps_lic is a hard gate (per SVP review).
        with self.assertRaises(Exception):
            ValidationResult()
        v_pass = ValidationResult(passed=True)
        v_fail = ValidationResult(passed=False)
        self.assertTrue(v_pass.passed)
        self.assertFalse(v_fail.passed)


if __name__ == "__main__":
    unittest.main()
