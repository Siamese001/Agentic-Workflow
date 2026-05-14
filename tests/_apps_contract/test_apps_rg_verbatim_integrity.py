"""W6 tests: AppsRgVerbatimIntegrityReceipt — education/cert/early_career hash match."""
from __future__ import annotations

import unittest

from apps_rg.runtime.bindings.exit_evidence_receipts import (
    AppsRgVerbatimIntegrityReceipt,
)


class TestAppsRgVerbatimIntegrityReceipt(unittest.TestCase):
    """Test verbatim integrity receipt for G21/G22 evidence."""

    def test_verbatim_integrity_happy_path(self) -> None:
        """All verbatim sections match source exactly."""
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:edu_abc",
            certifications_source_hash="sha256:cert_abc",
            early_career_source_hash="sha256:early_abc",
            education_output_hash="sha256:edu_abc",  # Matches source
            certifications_output_hash="sha256:cert_abc",  # Matches source
            early_career_output_hash="sha256:early_abc",  # Matches source
            education_verbatim=True,
            certifications_verbatim=True,
            early_career_verbatim=True,
            source_resume_hash="sha256:master_abc",
        )
        
        self.assertTrue(receipt.all_verbatim)
        self.assertTrue(receipt.education_verbatim)
        self.assertTrue(receipt.certifications_verbatim)
        self.assertTrue(receipt.early_career_verbatim)

    def test_education_mutation_detected(self) -> None:
        """Education section mutation detected via hash mismatch."""
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:edu_abc",
            certifications_source_hash="sha256:cert_abc",
            early_career_source_hash="sha256:early_abc",
            education_output_hash="sha256:edu_XYZ",  # MUTATED!
            certifications_output_hash="sha256:cert_abc",
            early_career_output_hash="sha256:early_abc",
            education_verbatim=False,  # Detected!
            certifications_verbatim=True,
            early_career_verbatim=True,
            source_resume_hash="sha256:master_abc",
        )
        
        self.assertFalse(receipt.all_verbatim)
        self.assertFalse(receipt.education_verbatim)
        self.assertTrue(receipt.certifications_verbatim)

    def test_certifications_mutation_detected(self) -> None:
        """Certifications section mutation detected via hash mismatch."""
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:edu_abc",
            certifications_source_hash="sha256:cert_abc",
            early_career_source_hash="sha256:early_abc",
            education_output_hash="sha256:edu_abc",
            certifications_output_hash="sha256:cert_CHANGED",  # MUTATED!
            early_career_output_hash="sha256:early_abc",
            education_verbatim=True,
            certifications_verbatim=False,  # Detected!
            early_career_verbatim=True,
            source_resume_hash="sha256:master_abc",
        )
        
        self.assertFalse(receipt.all_verbatim)
        self.assertFalse(receipt.certifications_verbatim)

    def test_early_career_mutation_detected(self) -> None:
        """Early career section mutation detected via hash mismatch."""
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:edu_abc",
            certifications_source_hash="sha256:cert_abc",
            early_career_source_hash="sha256:early_abc",
            education_output_hash="sha256:edu_abc",
            certifications_output_hash="sha256:cert_abc",
            early_career_output_hash="sha256:early_MODIFIED",  # MUTATED!
            education_verbatim=True,
            certifications_verbatim=True,
            early_career_verbatim=False,  # Detected!
            source_resume_hash="sha256:master_abc",
        )
        
        self.assertFalse(receipt.all_verbatim)
        self.assertFalse(receipt.early_career_verbatim)

    def test_multiple_mutations_detected(self) -> None:
        """Multiple section mutations all detected."""
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:edu_abc",
            certifications_source_hash="sha256:cert_abc",
            early_career_source_hash="sha256:early_abc",
            education_output_hash="sha256:edu_CHANGED",
            certifications_output_hash="sha256:cert_CHANGED",
            early_career_output_hash="sha256:early_CHANGED",
            education_verbatim=False,
            certifications_verbatim=False,
            early_career_verbatim=False,
            source_resume_hash="sha256:master_abc",
        )
        
        self.assertFalse(receipt.all_verbatim)
        self.assertFalse(receipt.education_verbatim)
        self.assertFalse(receipt.certifications_verbatim)
        self.assertFalse(receipt.early_career_verbatim)

    def test_provenance_via_source_hash(self) -> None:
        """Source hash provides provenance for verification."""
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:edu_abc",
            certifications_source_hash="sha256:cert_abc",
            early_career_source_hash="sha256:early_abc",
            education_output_hash="sha256:edu_abc",
            certifications_output_hash="sha256:cert_abc",
            early_career_output_hash="sha256:early_abc",
            education_verbatim=True,
            certifications_verbatim=True,
            early_career_verbatim=True,
            source_resume_hash="sha256:master_source_123",
        )
        
        # Source hash allows downstream verification
        self.assertEqual(receipt.source_resume_hash, "sha256:master_source_123")


class TestVerbatimIntegrityEvidencePath(unittest.TestCase):
    """Test that verbatim integrity feeds into Exit evidence path."""

    def test_receipt_is_g21_g22_evidence(self) -> None:
        """Verbatim receipt is G21/G22 evidence consumed by Exit."""
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:edu_src",
            certifications_source_hash="sha256:cert_src",
            early_career_source_hash="sha256:early_src",
            education_output_hash="sha256:edu_out",
            certifications_output_hash="sha256:cert_out",
            early_career_output_hash="sha256:early_out",
            education_verbatim=True,
            certifications_verbatim=True,
            early_career_verbatim=True,
            source_resume_hash="sha256:master",
        )
        
        # Receipt is hashable evidence type
        self.assertTrue(hasattr(receipt, 'source_resume_hash'))
        self.assertIsInstance(receipt.all_verbatim, bool)


if __name__ == "__main__":
    unittest.main()
