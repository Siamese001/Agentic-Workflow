"""W6 — POST-NARR Whole-Resume Coherence Gates Tests.

Verifies the W6 whole-resume checks:
- JD keyword coverage: ≥80% of JD keywords present
- Claim uniqueness: no duplicate claims across sections
- Cross-section consistency: coherent archetype/tenure/outcomes
- Bullet count per role: 3-5 bullets each
- Role chronology: date-descending, no unexplained gaps >12mo
- ATS composite: aggregated check

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W6)
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

from apps_rg.integrations.gates.post_narr_resume_gates import (
    _extract_keywords,
    _find_duplicate_claims,
    jd_keyword_coverage_min_gate,
    claim_uniqueness_gate,
    cross_section_consistency_gate,
    bullet_count_per_role_gate,
    role_chronology_gate,
    ats_composite_gate,
)


@dataclass
class MockArtifact:
    """Mock artifact with text field."""
    text: str


class TestExtractKeywords:
    """Test keyword extraction utility."""

    def test_extract_lowercase(self) -> None:
        """Keywords are normalized to lowercase."""
        text = "Python JavaScript MACHINE LEARNING"
        keywords = _extract_keywords(text)
        
        assert "python" in keywords
        assert "javascript" in keywords
        assert "machine" in keywords
        assert "learning" in keywords

    def test_filters_short_words(self) -> None:
        """Words <3 chars filtered out."""
        text = "AI and ML for the win"
        keywords = _extract_keywords(text)
        
        # Short words should be excluded
        assert "ai" not in keywords
        assert "ml" not in keywords
        # Longer words included
        assert "for" in keywords
        assert "the" in keywords
        assert "win" in keywords


class TestFindDuplicateClaims:
    """Test duplicate claim detection."""

    def test_finds_duplicate_across_sections(self) -> None:
        """Detects same claim in multiple sections."""
        sections = {
            "summary": "Delivered $5M savings",
            "experience": "Achieved $5M in cost reductions",
        }
        
        duplicates = _find_duplicate_claims(sections)
        
        # Should find $5M appears in both
        assert len(duplicates) >= 1
        assert any("$5m" in d["claim"].lower() for d in duplicates)

    def test_no_duplicates_unique_claims(self) -> None:
        """No duplicates when claims are unique."""
        sections = {
            "summary": "Delivered $5M savings",
            "experience": "Managed 50 person team",
        }
        
        duplicates = _find_duplicate_claims(sections)
        
        assert duplicates == []


class TestJdKeywordCoverageGate:
    """Test JD keyword coverage gate."""

    def test_passes_at_80_percent_coverage(self) -> None:
        """Gate passes when ≥80% JD keywords present."""
        artifact = MockArtifact(
            text="Python developer with machine learning expertise in cloud environments using aws"
        )
        context = {
            "jd_keywords": ["python", "machine learning", "cloud", "aws"],  # 4/4 = 100%
        }
        
        verdict = jd_keyword_coverage_min_gate(artifact, context)
        
        assert verdict.gate_id == "jd_keyword_coverage_min"
        assert verdict.result == Result.PASS
        assert "coverage_sufficient" in verdict.reason_codes

    def test_fails_below_80_percent(self) -> None:
        """Gate fails when <80% coverage."""
        artifact = MockArtifact(text="General software developer")
        context = {
            "jd_keywords": ["python", "machine learning", "cloud", "aws", "kubernetes"],
        }
        
        verdict = jd_keyword_coverage_min_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "coverage_insufficient" in verdict.reason_codes

    def test_unknown_when_no_jd_keywords(self) -> None:
        """Unknown when JD keywords not provided."""
        artifact = MockArtifact(text="Some resume text")
        context = {}
        
        verdict = jd_keyword_coverage_min_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN
        assert "missing_jd_keywords" in verdict.reason_codes

    def test_exactly_80_percent_boundary(self) -> None:
        """Exactly 80% passes."""
        # 4 out of 5 keywords = 80%
        artifact = MockArtifact(
            text="Python developer with machine learning and cloud expertise"
        )
        context = {
            "jd_keywords": ["python", "machine learning", "cloud", "aws", "kubernetes"],
            # has python, ml, cloud = 3... need 4
        }
        # Add "aws" to text to get 4/5 = 80%
        artifact = MockArtifact(
            text="Python developer with machine learning and cloud expertise on aws"
        )
        
        verdict = jd_keyword_coverage_min_gate(artifact, context)
        # Should be 4/5 = 80% which meets threshold
        assert verdict.result == Result.PASS


class TestClaimUniquenessGate:
    """Test claim uniqueness gate."""

    def test_passes_when_claims_unique(self) -> None:
        """Gate passes when no duplicate claims."""
        artifact = MockArtifact(text="any text")
        context = {
            "resume_sections": {
                "summary": "Delivered $5M savings",
                "experience": "Led 50 person team",
            }
        }
        
        verdict = claim_uniqueness_gate(artifact, context)
        
        assert verdict.gate_id == "claim_uniqueness"
        assert verdict.result == Result.PASS
        assert "claims_unique" in verdict.reason_codes

    def test_fails_on_duplicate_claims(self) -> None:
        """Gate fails when same claim in multiple sections."""
        artifact = MockArtifact(text="any text")
        context = {
            "resume_sections": {
                "summary": "Delivered $5M savings and 25% improvement",
                "experience": "Achieved $5M in cost reductions",  # Duplicate $5M
            }
        }
        
        verdict = claim_uniqueness_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "duplicate_claims" in verdict.reason_codes

    def test_unknown_when_no_sections(self) -> None:
        """Unknown when no resume sections provided."""
        artifact = MockArtifact(text="any text")
        context = {}
        
        verdict = claim_uniqueness_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN


class TestCrossSectionConsistencyGate:
    """Test cross-section consistency gate."""

    def test_passes_when_tenure_consistent(self) -> None:
        """Gate passes when tenure claims consistent."""
        artifact = MockArtifact(text="any text")
        context = {
            "resume_sections": {
                "summary": "15 years of experience in technology",
                "experience": "Over 15 years building systems",
            }
        }
        
        verdict = cross_section_consistency_gate(artifact, context)
        
        assert verdict.gate_id == "cross_section_consistency"
        assert verdict.result == Result.PASS

    def test_fails_when_tenure_inconsistent(self) -> None:
        """Gate fails when tenure varies >2 years."""
        artifact = MockArtifact(text="any text")
        context = {
            "resume_sections": {
                "summary": "20 years of experience",  # Says 20
                "experience": "15 years in software",  # Says 15
            }
        }
        
        verdict = cross_section_consistency_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "tenure_inconsistent" in verdict.reason_codes


class TestBulletCountPerRoleGate:
    """Test bullet count per role gate."""

    def test_passes_with_3_to_5_bullets(self) -> None:
        """Gate passes when each role has 3-5 bullets."""
        artifact = MockArtifact(text="any text")
        context = {
            "experience_roles": [
                {"title": "Role 1", "bullets": ["a", "b", "c"]},
                {"title": "Role 2", "bullets": ["d", "e", "f", "g"]},
            ]
        }
        
        verdict = bullet_count_per_role_gate(artifact, context)
        
        assert verdict.gate_id == "bullet_count_per_role"
        assert verdict.result == Result.PASS

    def test_fails_with_too_few_bullets(self) -> None:
        """Gate fails when role has <3 bullets."""
        artifact = MockArtifact(text="any text")
        context = {
            "experience_roles": [
                {"title": "Role 1", "bullets": ["a", "b"]},  # Only 2
            ]
        }
        
        verdict = bullet_count_per_role_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "bullet_count_invalid" in verdict.reason_codes

    def test_fails_with_too_many_bullets(self) -> None:
        """Gate fails when role has >5 bullets."""
        artifact = MockArtifact(text="any text")
        context = {
            "experience_roles": [
                {"title": "Role 1", "bullets": ["a", "b", "c", "d", "e", "f"]},  # 6
            ]
        }
        
        verdict = bullet_count_per_role_gate(artifact, context)
        
        assert verdict.result == Result.FAIL


class TestRoleChronologyGate:
    """Test role chronology gate."""

    def test_passes_valid_chronology(self) -> None:
        """Gate passes when roles in date-descending order."""
        artifact = MockArtifact(text="any text")
        context = {
            "experience_roles": [
                {"title": "Current", "start_date": "2020-01", "end_date": "2024-12"},
                {"title": "Previous", "start_date": "2018-01", "end_date": "2019-12"},
            ]
        }
        
        verdict = role_chronology_gate(artifact, context)
        
        assert verdict.gate_id == "role_chronology"
        assert verdict.result == Result.PASS

    def test_fails_on_large_gap(self) -> None:
        """Gate fails when unexplained gap >12 months."""
        artifact = MockArtifact(text="any text")
        context = {
            "experience_roles": [
                {"title": "Current", "start_date": "2022-01", "end_date": "2024-12"},
                {"title": "Old", "start_date": "2015-01", "end_date": "2016-12"},  # 5 year gap
            ]
        }
        
        verdict = role_chronology_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "chronology_invalid" in verdict.reason_codes


class TestAtsCompositeGate:
    """Test ATS composite gate."""

    def test_passes_all_checks(self) -> None:
        """Composite passes when all checks pass."""
        artifact = MockArtifact(text="Python expert with expertise")  # "python" and "expert"
        context = {
            "jd_keywords": ["python", "expert"],  # Both in text
            "resume_sections": {
                "summary": "Fifteen years experience",  # Consistent, spelled out
                "exp": "15 years in tech",  # Same years, numeric
            },
            "experience_roles": [
                {"title": "Role", "bullets": ["a", "b", "c"]},  # 3 bullets
            ],
        }
        
        verdict = ats_composite_gate(artifact, context)
        
        assert verdict.gate_id == "ats_composite"
        assert verdict.result == Result.PASS
        assert any("pass:" in code for code in verdict.reason_codes)

    def test_fails_when_any_check_fails(self) -> None:
        """Composite fails when any check fails."""
        artifact = MockArtifact(text="no keywords here")
        context = {
            "jd_keywords": ["python", "machine learning", "cloud"],
            "resume_sections": {
                "summary": "20 years experience",
                "exp": "15 years in tech",  # Inconsistent
            },
            "experience_roles": [
                {"title": "Role", "bullets": ["a", "b", "c"]},
            ],
        }
        
        verdict = ats_composite_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert any("fail:" in code for code in verdict.reason_codes)


class TestW6Integration:
    """Integration tests for W6 gates."""

    def test_ats_optimized_resume_passes(self) -> None:
        """Well-structured ATS resume passes all checks."""
        artifact = MockArtifact(
            text="Python developer with machine learning and cloud expertise"
        )
        context = {
            "jd_keywords": ["python", "machine learning", "cloud"],
            "resume_sections": {
                # Use different phrasing to avoid false "duplicate claim" detection
                "executive_summary": "Engineering leader with fifteen years of experience.",
                "experience": "Built scalable systems over 15 years in technology.",
            },
            "experience_roles": [
                {
                    "title": "Senior Engineer",
                    "bullets": ["Built API", "Led team", "Improved performance"],
                    "start_date": "2020-01",
                    "end_date": "2024-12",
                },
                {
                    "title": "Engineer",
                    "bullets": ["Developed features", "Fixed bugs", "Wrote tests"],
                    "start_date": "2018-06",
                    "end_date": "2019-12",
                },
            ],
        }
        
        verdict = ats_composite_gate(artifact, context)
        
        assert verdict.result == Result.PASS

    def test_poor_resume_fails_multiple_checks(self) -> None:
        """Poorly structured resume fails multiple ATS checks."""
        artifact = MockArtifact(text="Generic developer")
        context = {
            "jd_keywords": ["python", "machine learning", "cloud", "aws", "kubernetes"],
            "resume_sections": {
                "summary": "20 years of experience in technology",
                "experience": "15 years of experience in software",  # Inconsistent
            },
            "experience_roles": [
                {
                    "title": "Role 1",
                    "bullets": ["a", "b"],  # Too few
                    "start_date": "2023-01",
                    "end_date": "2024-12",
                },
                {
                    "title": "Role 2",
                    "bullets": ["c", "d", "e", "f", "g", "h", "i"],  # Too many
                    "start_date": "2015-01",
                    "end_date": "2016-12",  # Large gap
                },
            ],
        }
        
        verdict = ats_composite_gate(artifact, context)
        
        assert verdict.result == Result.FAIL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
