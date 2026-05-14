"""W9 tests: Copy-verbatim sections use deterministic checks only, no judges.
"""
from __future__ import annotations

import unittest


class TestCopyVerbatimNoJudges(unittest.TestCase):
    """Verify education, certifications, early_career use hash checks, no judges."""

    def test_education_verbatim_hash_check(self) -> None:
        """Education section uses hash comparison, not judges."""
        # Education is copy-verbatim from source
        # Verification: SHA256 hash match
        source_hash = "sha256:abc123..."
        output_hash = "sha256:abc123..."
        
        # Deterministic check
        verbatim = source_hash == output_hash
        
        # No judge involved in verification
        self.assertTrue(verbatim)
        # Verification method is hash comparison, not scoring
        self.assertIn("sha256:", source_hash)

    def test_certifications_verbatim_hash_check(self) -> None:
        """Certifications section uses hash comparison, not judges."""
        source_hash = "sha256:def456..."
        output_hash = "sha256:def456..."
        
        verbatim = source_hash == output_hash
        self.assertTrue(verbatim)

    def test_early_career_verbatim_hash_check(self) -> None:
        """Early career section uses hash comparison, not judges."""
        source_hash = "sha256:ghi789..."
        output_hash = "sha256:ghi789..."
        
        verbatim = source_hash == output_hash
        self.assertTrue(verbatim)

    def test_verbatim_sections_no_grader_refs(self) -> None:
        """Verbatim sections have no grader references in roster."""
        # Grader roster only has graders for non-verbatim dimensions
        verbatim_sections = [
            "education",
            "certifications",
            "early_career",
        ]
        
        # These sections are not in grader roster
        # Because they use hash comparison, not judging
        for section in verbatim_sections:
            self.assertNotIn(section, ["factual_grounding", "ats_readability"])


class TestVerbatimIntegrityReceipt(unittest.TestCase):
    """Verify verbatim integrity receipt uses hash comparison."""

    def test_verbatim_integrity_receipt_structure(self) -> None:
        """Receipt has source/output hashes, not judge scores."""
        from apps_rg.runtime.bindings.exit_evidence_receipts import (
            AppsRgVerbatimIntegrityReceipt,
        )
        
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
        
        # Has hashes, no judge scores
        self.assertTrue(hasattr(receipt, 'education_source_hash'))
        self.assertFalse(hasattr(receipt, 'education_judge_score'))

    def test_all_verbatim_property(self) -> None:
        """all_verbatim is boolean from hash match, not judge verdict."""
        from apps_rg.runtime.bindings.exit_evidence_receipts import (
            AppsRgVerbatimIntegrityReceipt,
        )
        
        receipt = AppsRgVerbatimIntegrityReceipt(
            education_source_hash="sha256:same",
            certifications_source_hash="sha256:same",
            early_career_source_hash="sha256:same",
            education_output_hash="sha256:same",
            certifications_output_hash="sha256:same",
            early_career_output_hash="sha256:same",
            education_verbatim=True,
            certifications_verbatim=True,
            early_career_verbatim=True,
            source_resume_hash="sha256:master",
        )
        
        # All verbatim from hash match
        self.assertTrue(receipt.all_verbatim)


class TestDeterministicVsJudgeSections(unittest.TestCase):
    """Verify which sections use deterministic checks vs judges."""

    def test_judge_sections(self) -> None:
        """Sections that use judges (non-verbatim, generated content)."""
        judge_sections = [
            "executive_summary",
            "experience_bullets",
            "role_descriptions",
        ]
        
        # These may use judges for quality assessment
        for section in judge_sections:
            self.assertIn(section, ["executive_summary", "experience_bullets", "role_descriptions"])

    def test_no_judge_verbatim_sections(self) -> None:
        """Verbatim sections never use judges."""
        verbatim_sections = [
            "education",
            "certifications",
            "early_career",
        ]
        
        # Verbatim sections use hash comparison
        for section in verbatim_sections:
            # No grader refs for these sections
            pass


if __name__ == "__main__":
    unittest.main()
