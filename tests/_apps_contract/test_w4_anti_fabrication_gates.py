"""W4 — Anti-Fabrication & Credential Integrity Gates Tests.

Verifies the W4 anti-fabrication gates:
- Provenance required: quantified claims must have sources
- Figure citation verification: numeric claims must appear in master_resume
- Tenure accuracy: stated years must match computed years ±1
- Anti-fabrication composite: aggregated gate checks

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W4)
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

from apps_rg.integrations.gates.post_ens_resume_gates import (
    _extract_quantified_claims,
    _extract_stated_tenure,
    provenance_required_gate,
    figure_citation_verification_gate,
    tenure_accuracy_gate,
    anti_fabrication_composite_gate,
)


@dataclass
class MockArtifact:
    """Mock artifact with text field."""
    text: str


class TestExtractQuantifiedClaims:
    """Test numeric claim extraction."""

    def test_extracts_dollar_amounts(self) -> None:
        """Extracts $X figures."""
        text = "Delivered $12M in savings and $500K revenue"
        claims = _extract_quantified_claims(text)
        
        assert len(claims) >= 2
        claim_nums = [c["number"] for c in claims]
        assert any("$12" in n for n in claim_nums)
        assert any("$500" in n for n in claim_nums)

    def test_extracts_percentages(self) -> None:
        """Extracts X% figures."""
        text = "Improved efficiency by 25% and reduced costs 15%"
        claims = _extract_quantified_claims(text)
        
        claim_nums = [c["number"] for c in claims]
        assert any("25" in n for n in claim_nums)
        assert any("15" in n for n in claim_nums)

    def test_extracts_user_counts(self) -> None:
        """Extracts count + unit figures."""
        text = "Served 5000 users and 250 customers"
        claims = _extract_quantified_claims(text)
        
        claim_nums = [c["number"] for c in claims]
        assert any("5000" in n for n in claim_nums)

    def test_no_claims_in_text_without_numbers(self) -> None:
        """Returns empty list for text without numbers."""
        text = "Delivered significant value to stakeholders"
        claims = _extract_quantified_claims(text)
        
        assert claims == []


class TestExtractStatedTenure:
    """Test tenure statement extraction."""

    def test_extracts_years_experience(self) -> None:
        """Extracts 'X years of experience'."""
        text = "SVP with 15 years of experience in AI"
        years = _extract_stated_tenure(text)
        
        assert 15 in years

    def test_extracts_over_years(self) -> None:
        """Extracts 'over X years'."""
        text = "Over 10 years building enterprise systems"
        years = _extract_stated_tenure(text)
        
        assert 10 in years

    def test_extracts_plus_years(self) -> None:
        """Extracts 'X+ years'."""
        text = "12+ years in technology leadership"
        years = _extract_stated_tenure(text)
        
        assert 12 in years

    def test_no_tenure_in_generic_text(self) -> None:
        """Returns empty for text without tenure statements."""
        text = "Expert in AI and machine learning"
        years = _extract_stated_tenure(text)
        
        assert years == []


class TestProvenanceRequiredGate:
    """Test provenance verification gate."""

    def test_passes_when_claims_in_master_resume(self) -> None:
        """Gate passes when numeric claims appear in master resume."""
        artifact = MockArtifact(
            text="Delivered $12M savings and 25% efficiency gain"
        )
        context = {
            "master_resume_text": "Delivered $12M in cost savings. Improved efficiency by 25%."
        }
        
        verdict = provenance_required_gate(artifact, context)
        
        assert verdict.gate_id == "provenance_required"
        assert verdict.result == Result.PASS
        assert "all_claims_verified" in verdict.reason_codes

    def test_fails_when_claims_not_in_sources(self) -> None:
        """Gate fails when claims have no provenance."""
        artifact = MockArtifact(text="Achieved $50M revenue growth")
        context = {
            "master_resume_text": "Worked on various projects and initiatives."
        }
        
        verdict = provenance_required_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "unverified_claims" in verdict.reason_codes

    def test_passes_when_no_quantified_claims(self) -> None:
        """No claims = nothing to verify = pass."""
        artifact = MockArtifact(text="Experienced leader in technology")
        context = {"master_resume_text": "Technology leader with experience"}
        
        verdict = provenance_required_gate(artifact, context)
        
        assert verdict.result == Result.PASS
        assert "no_claims" in verdict.reason_codes

    def test_checks_provenance_sources(self) -> None:
        """Checks multiple provenance sources."""
        artifact = MockArtifact(text="Managed 100 person team")
        context = {
            "master_resume_text": "General experience section",
            "provenance_sources": [
                {"text": "Managed team of 100 engineers"},
            ]
        }
        
        verdict = provenance_required_gate(artifact, context)
        
        assert verdict.result == Result.PASS


class TestFigureCitationVerificationGate:
    """Test figure citation verification gate."""

    def test_passes_when_citations_in_master_resume(self) -> None:
        """Gate passes when figures appear in master resume."""
        artifact = MockArtifact(text="Saved $5M annually through optimization")
        context = {
            "master_resume_text": "Optimization project saved $5M annually."
        }
        
        verdict = figure_citation_verification_gate(artifact, context)
        
        assert verdict.gate_id == "figure_citation_verification"
        assert verdict.result == Result.PASS
        assert "all_citations_verified" in verdict.reason_codes

    def test_fails_when_fabricated_citations(self) -> None:
        """Gate fails when figures not in master resume."""
        artifact = MockArtifact(text="Generated $100M new revenue")
        context = {
            "master_resume_text": "Regular software development work. No revenue responsibility."
        }
        
        verdict = figure_citation_verification_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "fabricated_claims_detected" in verdict.reason_codes

    def test_unknown_when_no_master_resume(self) -> None:
        """Cannot verify without master resume."""
        artifact = MockArtifact(text="Achieved 50% improvement")
        context = {}  # No master_resume_text
        
        verdict = figure_citation_verification_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN
        assert "missing_master_resume" in verdict.reason_codes

    def test_normalizes_for_comparison(self) -> None:
        """Handles case and spacing differences."""
        artifact = MockArtifact(text="$10 MILLION in savings")
        context = {
            "master_resume_text": "Project delivered $10 million savings"
        }
        
        verdict = figure_citation_verification_gate(artifact, context)
        
        # Should normalize and find match
        assert verdict.result == Result.PASS


class TestTenureAccuracyGate:
    """Test tenure accuracy gate."""

    def test_passes_when_stated_matches_computed(self) -> None:
        """Gate passes when stated years matches computed ±1."""
        artifact = MockArtifact(text="15 years of experience in AI")
        context = {"computed_years_experience": 15}
        
        verdict = tenure_accuracy_gate(artifact, context)
        
        assert verdict.gate_id == "tenure_accuracy"
        assert verdict.result == Result.PASS
        assert "tenure_accurate" in verdict.reason_codes

    def test_passes_within_one_year_tolerance(self) -> None:
        """±1 year tolerance allowed."""
        artifact = MockArtifact(text="15 years of experience")
        context = {"computed_years_experience": 14}  # 1 year diff
        
        verdict = tenure_accuracy_gate(artifact, context)
        
        assert verdict.result == Result.PASS

    def test_fails_when_difference_exceeds_tolerance(self) -> None:
        """Fails when stated differs by >1 year."""
        artifact = MockArtifact(text="20 years of experience")
        context = {"computed_years_experience": 15}  # 5 year diff
        
        verdict = tenure_accuracy_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "tenure_inaccuracy" in verdict.reason_codes

    def test_unknown_when_no_computed_tenure(self) -> None:
        """Cannot verify without computed years."""
        artifact = MockArtifact(text="15 years of experience")
        context = {}  # No computed_years_experience
        
        verdict = tenure_accuracy_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN
        assert "missing_computed_tenure" in verdict.reason_codes

    def test_passes_when_no_stated_tenure(self) -> None:
        """No stated years = nothing to verify = pass."""
        artifact = MockArtifact(text="Expert in technology leadership")
        context = {"computed_years_experience": 15}
        
        verdict = tenure_accuracy_gate(artifact, context)
        
        assert verdict.result == Result.PASS
        assert "no_stated_tenure" in verdict.reason_codes


class TestAntiFabricationCompositeGate:
    """Test composite anti-fabrication gate."""

    def test_passes_when_all_checks_pass(self) -> None:
        """Composite passes when all individual gates pass."""
        artifact = MockArtifact(text="General leadership description")
        context = {
            "master_resume_text": "General leadership description",
            "computed_years_experience": 15,
        }
        
        verdict = anti_fabrication_composite_gate(artifact, context)
        
        assert verdict.gate_id == "anti_fabrication_composite"
        assert verdict.result == Result.PASS
        assert "pass:" in verdict.reason_codes[0]

    def test_fails_when_any_check_fails(self) -> None:
        """Composite fails when any individual gate fails."""
        artifact = MockArtifact(text="Generated $100M in new revenue")  # Fabricated
        context = {
            "master_resume_text": "Regular development work",
            "computed_years_experience": 15,
        }
        
        verdict = anti_fabrication_composite_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "fail:" in verdict.reason_codes[0]

    def test_handles_mixed_results(self) -> None:
        """Handles mix of pass/fail/unknown."""
        artifact = MockArtifact(text="15 years experience and $100M revenue")
        context = {
            "master_resume_text": "Regular work",  # Will fail citation check
            "computed_years_experience": 15,  # Will pass tenure check
        }
        
        verdict = anti_fabrication_composite_gate(artifact, context)
        
        # Should fail because citation check fails
        assert verdict.result == Result.FAIL


class TestAntiFabricationIntegration:
    """Integration tests for W4 gates."""

    def test_detects_fabricated_executive_summary(self) -> None:
        """Full W4 check on fabricated exec summary."""
        # Generated text with fabricated claims
        generated = MockArtifact(
            text="SVP with 25 years experience. Delivered $500M revenue "
                 "and managed 10,000 person organization."
        )
        
        # Actual master resume
        context = {
            "master_resume_text": "Engineering manager with 12 years experience. "
                                  "Led team of 15 engineers. Delivered $2M project.",
            "computed_years_experience": 12,
        }
        
        # Run composite gate
        verdict = anti_fabrication_composite_gate(generated, context)
        
        # Should detect multiple fabrications
        assert verdict.result == Result.FAIL

    def test_accepts_accurate_summary(self) -> None:
        """Gate passes for accurate summary."""
        generated = MockArtifact(
            text="Engineering manager with 12 years experience. "
                 "Led 15 person team. Delivered $2M project."
        )
        
        context = {
            "master_resume_text": "Engineering manager with 12 years experience. "
                                  "Led team of 15 engineers. Delivered $2M project.",
            "computed_years_experience": 12,
        }
        
        verdict = anti_fabrication_composite_gate(generated, context)
        
        assert verdict.result == Result.PASS

    def test_provenance_gate_evidence_refs(self) -> None:
        """Unverified claims logged in evidence refs."""
        artifact = MockArtifact(text="Achieved $50M and $100M milestones")
        context = {"master_resume_text": "Regular work"}
        
        verdict = provenance_required_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        # Evidence refs should contain the unverified claim numbers
        assert len(verdict.evidence_refs) > 0
        assert any("claim:" in ref for ref in verdict.evidence_refs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
