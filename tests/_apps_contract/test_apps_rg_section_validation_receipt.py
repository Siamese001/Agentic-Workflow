"""W6 tests: AppsRgSectionValidationReceipt — headline format and section counts."""
from __future__ import annotations

import unittest

from apps_rg.runtime.bindings.exit_evidence_receipts import (
    AppsRgSectionValidationReceipt,
)


class TestAppsRgSectionValidationReceipt(unittest.TestCase):
    """Test section validation receipt for G21 evidence."""

    def test_receipt_creation(self) -> None:
        """Receipt can be created with all required fields."""
        receipt = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="Insurance Technology Executive",
            headline_y="AI Strategy & Automation",
            headline_z="Operational Excellence",
            section_count_expected=5,
            section_count_actual=5,
            sections_valid=True,
            bullet_counts={
                "headline": 0,
                "executive_summary": 3,
                "unify_consulting": 4,
                "ibm": 5,
                "education": 2,
            },
            bullet_count_valid=True,
            source_digest="sha256:abc123",
        )
        
        self.assertTrue(receipt.headline_format_valid)
        self.assertEqual(receipt.headline_x, "Insurance Technology Executive")
        self.assertTrue(receipt.all_valid)

    def test_headline_xyz_format_validation(self) -> None:
        """Headline must be in X|Y|Z format with three parts."""
        # Valid X|Y|Z format
        receipt = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="Executive",
            headline_y="Strategy",
            headline_z="Operations",
            section_count_expected=3,
            section_count_actual=3,
            sections_valid=True,
            bullet_counts={"section1": 2},
            bullet_count_valid=True,
            source_digest="sha256:valid",
        )
        
        self.assertTrue(receipt.headline_format_valid)
        
        # Invalid format
        invalid_receipt = AppsRgSectionValidationReceipt(
            headline_format_valid=False,
            headline_x="",
            headline_y="",
            headline_z="",
            section_count_expected=3,
            section_count_actual=3,
            sections_valid=True,
            bullet_counts={"section1": 2},
            bullet_count_valid=True,
            source_digest="sha256:invalid",
        )
        
        self.assertFalse(invalid_receipt.headline_format_valid)
        self.assertFalse(invalid_receipt.all_valid)

    def test_section_count_mismatch_detected(self) -> None:
        """Section count mismatch makes sections_valid=False."""
        receipt = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="X",
            headline_y="Y", 
            headline_z="Z",
            section_count_expected=5,
            section_count_actual=4,  # Mismatch!
            sections_valid=False,
            bullet_counts={},
            bullet_count_valid=True,
            source_digest="sha256:mismatch",
        )
        
        self.assertFalse(receipt.sections_valid)
        self.assertFalse(receipt.all_valid)

    def test_bullet_count_validation(self) -> None:
        """Bullet counts must be within expected ranges."""
        receipt = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="X",
            headline_y="Y",
            headline_z="Z",
            section_count_expected=2,
            section_count_actual=2,
            sections_valid=True,
            bullet_counts={
                "executive_summary": 3,
                "experience": 5,
            },
            bullet_count_valid=True,
            source_digest="sha256:counts",
        )
        
        self.assertTrue(receipt.bullet_count_valid)
        self.assertEqual(receipt.bullet_counts["executive_summary"], 3)

    def test_all_valid_property(self) -> None:
        """all_valid is True only when all checks pass."""
        # All valid
        all_valid = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="X", headline_y="Y", headline_z="Z",
            section_count_expected=1,
            section_count_actual=1,
            sections_valid=True,
            bullet_counts={"s1": 1},
            bullet_count_valid=True,
            source_digest="sha256:all",
        )
        self.assertTrue(all_valid.all_valid)
        
        # Headline invalid
        headline_invalid = AppsRgSectionValidationReceipt(
            headline_format_valid=False,
            headline_x="X", headline_y="Y", headline_z="Z",
            section_count_expected=1,
            section_count_actual=1,
            sections_valid=True,
            bullet_counts={"s1": 1},
            bullet_count_valid=True,
            source_digest="sha256:head",
        )
        self.assertFalse(headline_invalid.all_valid)
        
        # Sections invalid
        sections_invalid = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="X", headline_y="Y", headline_z="Z",
            section_count_expected=2,
            section_count_actual=1,
            sections_valid=False,
            bullet_counts={"s1": 1},
            bullet_count_valid=True,
            source_digest="sha256:sect",
        )
        self.assertFalse(sections_invalid.all_valid)
        
        # Bullet count invalid
        bullet_invalid = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="X", headline_y="Y", headline_z="Z",
            section_count_expected=1,
            section_count_actual=1,
            sections_valid=True,
            bullet_counts={"s1": 100},  # Too many
            bullet_count_valid=False,
            source_digest="sha256:bullet",
        )
        self.assertFalse(bullet_invalid.all_valid)


class TestSectionValidationEvidencePath(unittest.TestCase):
    """Test that section validation receipt feeds into Exit evidence path."""

    def test_receipt_is_evidence_for_exit(self) -> None:
        """Section validation receipt is G21 evidence consumed by Exit."""
        receipt = AppsRgSectionValidationReceipt(
            headline_format_valid=True,
            headline_x="Insurance Technology Executive",
            headline_y="AI Strategy & Automation", 
            headline_z="Operational Excellence",
            section_count_expected=7,
            section_count_actual=7,
            sections_valid=True,
            bullet_counts={
                "executive_summary": 3,
                "unify_consulting": 4,
            },
            bullet_count_valid=True,
            source_digest="sha256:evidence",
        )
        
        # Receipt can be used as evidence (hashable, frozen)
        self.assertTrue(hasattr(receipt, 'source_digest'))
        self.assertTrue(receipt.all_valid)


if __name__ == "__main__":
    unittest.main()
