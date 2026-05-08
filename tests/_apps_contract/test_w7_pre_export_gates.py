"""W7 — PRE-EXPORT Artifact Gate Tests.

Verifies the W7 final export validation gates:
- Education/certification unchanged: SHA verification against master
- No orphan sections: detects empty sections, placeholders, null values
- Pre-export composite: aggregated validation

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W7)
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

import pytest

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

from apps_rg.integrations.gates.pre_export_resume_gates import (
    _compute_sha256,
    degree_certification_unchanged_gate,
    docx_render_no_orphan_gate,
    pre_export_composite_gate,
)


@dataclass
class MockArtifact:
    """Mock artifact for testing."""
    education_section: str = ""
    sections: dict = None


class TestComputeSha256:
    """Test SHA256 computation."""

    def test_compute_bytes(self) -> None:
        """Compute SHA of bytes."""
        data = b"test education data"
        sha = _compute_sha256(data)
        
        expected = hashlib.sha256(data).hexdigest()
        assert sha == expected
        assert len(sha) == 64


class TestDegreeCertificationUnchangedGate:
    """Test education/certification integrity gate."""

    def test_passes_when_sha_matches(self) -> None:
        """Gate passes when education section unchanged."""
        edu_text = "B.S. Computer Science, MIT"
        expected_sha = _compute_sha256(edu_text.encode("utf-8"))
        
        artifact = MockArtifact(education_section=edu_text)
        context = {"master_resume_education_sha": expected_sha}
        
        verdict = degree_certification_unchanged_gate(artifact, context)
        
        assert verdict.gate_id == "degree_certification_unchanged"
        assert verdict.result == Result.PASS
        assert "education_unchanged" in verdict.reason_codes

    def test_fails_when_sha_mismatches(self) -> None:
        """Gate fails when education section modified."""
        artifact = MockArtifact(education_section="Modified education text")
        context = {"master_resume_education_sha": "a" * 64}  # Wrong SHA
        
        verdict = degree_certification_unchanged_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "education_modified" in verdict.reason_codes

    def test_unknown_when_no_education_section(self) -> None:
        """Unknown when no education to verify."""
        artifact = MockArtifact(education_section="")
        context = {"master_resume_education_sha": "a" * 64}
        
        verdict = degree_certification_unchanged_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN
        assert "missing_education_section" in verdict.reason_codes

    def test_unknown_when_no_reference(self) -> None:
        """Unknown when no master reference."""
        artifact = MockArtifact(education_section="Some education")
        context = {}  # No reference
        
        verdict = degree_certification_unchanged_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN
        assert "missing_master_reference" in verdict.reason_codes


class TestDocxRenderNoOrphanGate:
    """Test no orphan sections gate."""

    def test_passes_with_complete_sections(self) -> None:
        """Gate passes when all sections have content."""
        artifact = MockArtifact(sections={
            "headline": "Engineering Leader",
            "summary": "Experienced professional with track record",
            "experience": "Senior Engineer at Tech Corp",
        })
        
        verdict = docx_render_no_orphan_gate(artifact, {})
        
        assert verdict.gate_id == "docx_render_no_orphan"
        assert verdict.result == Result.PASS
        assert "no_orphans" in verdict.reason_codes

    def test_fails_on_empty_section(self) -> None:
        """Gate fails when section is empty."""
        artifact = MockArtifact(sections={
            "headline": "Engineering Leader",
            "summary": "",  # Empty
        })
        
        verdict = docx_render_no_orphan_gate(artifact, {})
        
        assert verdict.result == Result.FAIL
        assert "orphan_sections_detected" in verdict.reason_codes

    def test_fails_on_placeholder(self) -> None:
        """Gate fails when placeholder text detected."""
        artifact = MockArtifact(sections={
            "headline": "Engineering Leader",
            "summary": "[PLACEHOLDER] fill in later",
        })
        
        verdict = docx_render_no_orphan_gate(artifact, {})
        
        assert verdict.result == Result.FAIL
        assert "orphan_sections_detected" in verdict.reason_codes

    def test_fails_on_tbd(self) -> None:
        """Gate fails when TBD marker detected."""
        artifact = MockArtifact(sections={
            "headline": "TBD",
            "summary": "Content here",
        })
        
        verdict = docx_render_no_orphan_gate(artifact, {})
        
        assert verdict.result == Result.FAIL

    def test_fails_on_null_string(self) -> None:
        """Gate fails when null rendered as string."""
        artifact = MockArtifact(sections={
            "headline": "null",
            "summary": "Content",
        })
        
        verdict = docx_render_no_orphan_gate(artifact, {})
        
        assert verdict.result == Result.FAIL

    def test_fails_on_none_string(self) -> None:
        """Gate fails when None rendered as string."""
        artifact = MockArtifact(sections={
            "headline": "None",
            "summary": "Content",
        })
        
        verdict = docx_render_no_orphan_gate(artifact, {})
        
        assert verdict.result == Result.FAIL

    def test_detects_multiple_issues(self) -> None:
        """Reports all section issues."""
        artifact = MockArtifact(sections={
            "headline": "Valid content",
            "summary": "",  # Empty
            "experience": "[PLACEHOLDER]",  # Placeholder
            "education": "null",  # Null
        })
        
        verdict = docx_render_no_orphan_gate(artifact, {})
        
        assert verdict.result == Result.FAIL
        # Should have evidence refs for multiple issues
        assert len(verdict.evidence_refs) >= 2


class TestPreExportCompositeGate:
    """Test pre-export composite gate."""

    def test_passes_all_checks(self) -> None:
        """Composite passes when all export checks pass."""
        edu_text = "B.S. Computer Science"
        edu_sha = _compute_sha256(edu_text.encode("utf-8"))
        
        artifact = MockArtifact(
            education_section=edu_text,
            sections={"headline": "Title", "summary": "Content"},
        )
        context = {"master_resume_education_sha": edu_sha}
        
        verdict = pre_export_composite_gate(artifact, context)
        
        assert verdict.gate_id == "pre_export_composite"
        assert verdict.result == Result.PASS
        assert any("pass:" in code for code in verdict.reason_codes)

    def test_fails_when_any_check_fails(self) -> None:
        """Composite fails when any check fails."""
        artifact = MockArtifact(
            education_section="Wrong content",
            sections={"headline": ""},  # Empty section
        )
        context = {"master_resume_education_sha": "a" * 64}  # Wrong SHA
        
        verdict = pre_export_composite_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert any("fail:" in code for code in verdict.reason_codes)


class TestW7Integration:
    """Integration tests for W7 gates."""

    def test_ready_for_export_passes(self) -> None:
        """Complete valid resume passes pre-export validation."""
        edu_text = "M.S. Engineering, Stanford University"
        edu_sha = _compute_sha256(edu_text.encode("utf-8"))
        
        artifact = MockArtifact(
            education_section=edu_text,
            sections={
                "headline": "SVP Engineering",
                "executive_summary": "15 years building scalable systems",
                "experience": "Led engineering at Tech Corp",
                "education": edu_text,
                "skills": "Python, ML, Cloud",
            },
        )
        context = {"master_resume_education_sha": edu_sha}
        
        verdict = pre_export_composite_gate(artifact, context)
        
        assert verdict.result == Result.PASS

    def test_incomplete_resume_blocked(self) -> None:
        """Resume with placeholders blocked from export."""
        edu_text = "B.A. Economics"
        edu_sha = _compute_sha256(edu_text.encode("utf-8"))
        
        artifact = MockArtifact(
            education_section=edu_text,  # Valid
            sections={
                "headline": "Title",
                "executive_summary": "[PLACEHOLDER - ADD SUMMARY]",
                "experience": "TODO: fill in experience",
            },
        )
        context = {"master_resume_education_sha": edu_sha}
        
        verdict = pre_export_composite_gate(artifact, context)
        
        assert verdict.result == Result.FAIL

    def test_modified_education_blocked(self) -> None:
        """Resume with modified education section blocked."""
        original_edu = "B.S. Computer Science, MIT"
        original_sha = _compute_sha256(original_edu.encode("utf-8"))
        
        # Modified education (added honors)
        modified_edu = "B.S. Computer Science, MIT, summa cum laude"
        
        artifact = MockArtifact(
            education_section=modified_edu,
            sections={"headline": "Title", "summary": "Content"},
        )
        context = {"master_resume_education_sha": original_sha}
        
        verdict = pre_export_composite_gate(artifact, context)
        
        # Education check fails, no orphans check may pass
        assert verdict.result in [Result.FAIL, Result.UNKNOWN]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
