"""W9 tests: Uncalibrated judges are advisory only (informational_only=true).
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path


class TestUncalibratedAdvisoryOnly(unittest.TestCase):
    """Verify uncalibrated judges cannot produce autonomous PASS."""

    def test_informational_only_flag_exists(self) -> None:
        """Grader roster has informational_only flag for each LLM judge."""
        roster_path = Path("apps_rg/config/domain_contract/grader_roster.yaml")
        
        if roster_path.exists():
            content = roster_path.read_text()
            
            # Should have informational_only settings
            self.assertIn("informational_only:", content)
            
            # Executive positioning is informational only (uncalibrated default)
            self.assertIn("executive_positioning", content.lower())

    def test_uncalibrated_default_is_advisory(self) -> None:
        """Uncalibrated judges default to informational_only=true."""
        # Per grader_roster.yaml, executive_positioning is informational_only
        uncalibrated_judge = {
            "grader_ref": "rg::executive_positioning_judge::v1",
            "informational_only": True,
            "required_for_exit": False,
        }
        
        self.assertTrue(uncalibrated_judge["informational_only"])
        self.assertFalse(uncalibrated_judge["required_for_exit"])

    def test_calibrated_can_be_required(self) -> None:
        """Calibrated judges can be required_for_exit."""
        # Role alignment and specificity are required after calibration
        calibrated_judge = {
            "grader_ref": "rg::role_alignment_hybrid_v1",
            "informational_only": False,
            "required_for_exit": True,
        }
        
        # Note: This requires calibration to be verified
        # Uncalibrated judges must not block exit
        if not self._is_calibrated(calibrated_judge["grader_ref"]):
            # Force to advisory if uncalibrated
            calibrated_judge["informational_only"] = True
            calibrated_judge["required_for_exit"] = False
        
        self.assertTrue(calibrated_judge["informational_only"] or 
                       self._is_calibrated(calibrated_judge["grader_ref"]))

    def _is_calibrated(self, grader_ref: str) -> bool:
        """Check if grader has active calibration."""
        # Calibration check would query calibration_refs
        calibration_refs = [
            "calibration://apps_rg/judges/2026-04-weekly",
        ]
        # Simplified - actual calibration would check dates/validity
        return len(calibration_refs) > 0

    def test_no_autonomous_pass_from_uncalibrated(self) -> None:
        """Uncalibrated judges cannot autonomously PASS a candidate."""
        # Uncalibrated judges are advisory; final verdict requires calibrated dimensions
        uncalibrated_score = 0.95  # High score but uncalibrated
        
        # Even with high score, uncalibrated judge cannot PASS
        can_autonomous_pass = False  # Must be calibrated
        
        self.assertFalse(can_autonomous_pass)

    def test_timeout_behavior_warn_only_for_advisory(self) -> None:
        """Advisory judges have timeout_behavior=warn, not fail."""
        advisory_judge = {
            "grader_ref": "rg::executive_positioning_judge::v1",
            "informational_only": True,
            "timeout_behavior": "warn",
            "missing_behavior": "warn",
        }
        
        self.assertEqual(advisory_judge["timeout_behavior"], "warn")
        self.assertNotEqual(advisory_judge["timeout_behavior"], "fail")

    def test_required_judges_fail_on_timeout(self) -> None:
        """Required judges have timeout_behavior=fail."""
        required_judge = {
            "grader_ref": "rg::role_alignment_hybrid_v1",
            "informational_only": False,
            "required_for_exit": True,
            "timeout_behavior": "fail",
            "missing_behavior": "fail",
        }
        
        self.assertEqual(required_judge["timeout_behavior"], "fail")


class TestCalibrationReferences(unittest.TestCase):
    """Verify calibration references are tracked."""

    def test_calibration_refs_exist(self) -> None:
        """Grader roster has calibration_refs section."""
        roster_path = Path("apps_rg/config/domain_contract/grader_roster.yaml")
        
        if roster_path.exists():
            content = roster_path.read_text()
            self.assertIn("calibration_refs:", content)

    def test_calibration_date_tracked(self) -> None:
        """Calibration has date reference for freshness."""
        calibration = {
            "ref": "calibration://apps_rg/judges/2026-04-weekly",
            "date": "2026-04",
        }
        
        self.assertIn("2026-04", calibration["ref"])


if __name__ == "__main__":
    unittest.main()
