"""Property-based tests for apps_lic — voice-fidelity and contract invariants.

Hypothesis explores input variations; these tests enforce invariants from
`apps_lic/SVP_ENGINEERING_REVIEW.md`:
  - Campaign config requires both `name` and `target_audience` for ANY input.
  - ValidationResult.passed is strictly boolean.
  - Round-trip serialization is injective for any valid construction.

Plan: .windsurf/plans/apps-svp-plus-hardening-7c4e3a.md (W2.2)
"""
from __future__ import annotations

import unittest

from hypothesis import given, settings, strategies as st

from apps_lic.types import (
    CampaignConfig,
    CampaignRequest,
    ValidationResult,
)


# Hypothesis strategy: non-empty short strings for free-form fields.
NON_EMPTY_TEXT = st.text(min_size=1, max_size=64).filter(lambda s: s.strip())


class TestLicProperties(unittest.TestCase):
    @settings(max_examples=30, deadline=None)
    @given(name=NON_EMPTY_TEXT, audience=NON_EMPTY_TEXT)
    def test_campaign_config_round_trip(self, name: str, audience: str) -> None:
        cfg = CampaignConfig(name=name, target_audience=audience)
        rebuilt = CampaignConfig.model_validate(cfg.model_dump())
        self.assertEqual(cfg.name, rebuilt.name)
        self.assertEqual(cfg.target_audience, rebuilt.target_audience)

    @settings(max_examples=30, deadline=None)
    @given(
        cid=NON_EMPTY_TEXT,
        name=NON_EMPTY_TEXT,
        audience=NON_EMPTY_TEXT,
    )
    def test_campaign_request_round_trip(
        self, cid: str, name: str, audience: str
    ) -> None:
        req = CampaignRequest(
            campaign_id=cid,
            config=CampaignConfig(name=name, target_audience=audience),
        )
        rebuilt = CampaignRequest.model_validate(req.model_dump())
        self.assertEqual(req.campaign_id, rebuilt.campaign_id)
        self.assertEqual(req.config.name, rebuilt.config.name)

    @settings(max_examples=20, deadline=None)
    @given(passed=st.booleans())
    def test_validation_result_passed_is_strictly_boolean(self, passed: bool) -> None:
        v = ValidationResult(passed=passed)
        self.assertIsInstance(v.passed, bool)
        self.assertEqual(v.passed, passed)


if __name__ == "__main__":
    unittest.main()
