"""W5 — PER-CAND Resume Domain Gates Tests.

Verifies the W5 quality gates that run per ensemble candidate:
- Length parity: word count within ±15% of reference
- Quantified outcomes: ≥2 numeric claims required
- Target company absence: prevents flattery/contrived customization
- Forbidden fillers: bans buzzwords and clichés
- Sentence max length: no sentence >40 words
- Archetype lead: opening sentence must establish archetype

Spec reference: .windsurf/plans/apps-rg-runtime-gate-catalog-c4d7e1.md (W5)
"""

from __future__ import annotations

import pytest
from dataclasses import dataclass

from agentic_core.L5_safety.runtime_gates.types import Result
from agentic_core.runtime_gates import GateVerdict

from apps_rg.integrations.gates.per_cand_resume_gates import (
    FORBIDDEN_FILLERS,
    _count_words,
    _split_sentences,
    _count_quantified_outcomes,
    length_parity_strict_gate,
    quantified_outcome_count_gate,
    target_company_name_absence_gate,
    forbidden_filler_strict_gate,
    sentence_max_length_gate,
    archetype_lead_gate,
    per_cand_quality_composite_gate,
)


@dataclass
class MockArtifact:
    """Mock artifact with text field."""
    text: str


class TestWordCount:
    """Test word counting utility."""

    def test_count_words_simple(self) -> None:
        """Count words in simple text."""
        assert _count_words("hello world test") == 3

    def test_count_words_empty(self) -> None:
        """Empty string has 0 words."""
        assert _count_words("") == 0

    def test_count_words_multiple_spaces(self) -> None:
        """Multiple spaces handled correctly."""
        assert _count_words("hello   world") == 2


class TestSplitSentences:
    """Test sentence splitting utility."""

    def test_split_simple_sentences(self) -> None:
        """Split sentences on period."""
        text = "First sentence. Second sentence. Third."
        sentences = _split_sentences(text)
        assert len(sentences) == 3

    def test_split_with_punctuation(self) -> None:
        """Handle exclamation and question marks."""
        text = "Hello! How are you? Fine."
        sentences = _split_sentences(text)
        assert len(sentences) == 3


class TestQuantifiedOutcomeCounting:
    """Test quantified outcome detection."""

    def test_count_dollar_amounts(self) -> None:
        """Detect $X as quantified outcome."""
        text = "Delivered $5M in savings"
        assert _count_quantified_outcomes(text) >= 1

    def test_count_percentages(self) -> None:
        """Detect X% as quantified outcome."""
        text = "Improved efficiency by 25% and reduced costs 15%"
        assert _count_quantified_outcomes(text) >= 2

    def test_no_outcomes_in_generic_text(self) -> None:
        """No numbers = no outcomes."""
        text = "Experienced leader in technology"
        assert _count_quantified_outcomes(text) == 0


class TestLengthParityStrictGate:
    """Test length parity gate."""

    def test_passes_within_tolerance(self) -> None:
        """Gate passes when within ±15%."""
        artifact = MockArtifact(text="word " * 100)  # 100 words
        context = {"reference_word_count": 100}

        verdict = length_parity_strict_gate(artifact, context)

        assert verdict.gate_id == "length_parity_strict"
        assert verdict.result == Result.PASS
        assert "length_within_tolerance" in verdict.reason_codes

    def test_passes_at_lower_boundary(self) -> None:
        """Gate passes at -15% boundary (85 words for 100 ref)."""
        artifact = MockArtifact(text="word " * 85)
        context = {"reference_word_count": 100}

        verdict = length_parity_strict_gate(artifact, context)
        assert verdict.result == Result.PASS

    def test_passes_at_upper_boundary(self) -> None:
        """Gate passes at +15% boundary (115 words for 100 ref)."""
        # Create exactly 115 words without trailing space issues
        words = ["word"] * 115
        artifact = MockArtifact(text=" ".join(words))
        context = {"reference_word_count": 100}

        verdict = length_parity_strict_gate(artifact, context)
        assert verdict.result == Result.PASS

    def test_fails_below_tolerance(self) -> None:
        """Gate fails when < -15%."""
        artifact = MockArtifact(text="word " * 80)  # 20% below 100
        context = {"reference_word_count": 100}

        verdict = length_parity_strict_gate(artifact, context)
        assert verdict.result == Result.FAIL
        assert "length_outside_tolerance" in verdict.reason_codes

    def test_fails_above_tolerance(self) -> None:
        """Gate fails when > +15%."""
        artifact = MockArtifact(text="word " * 120)  # 20% above 100
        context = {"reference_word_count": 100}

        verdict = length_parity_strict_gate(artifact, context)
        assert verdict.result == Result.FAIL

    def test_uses_seed_text_as_fallback(self) -> None:
        """Uses seed_text if reference_word_count not provided."""
        artifact = MockArtifact(text="word " * 100)
        context = {"seed_text": "word " * 100}

        verdict = length_parity_strict_gate(artifact, context)
        assert verdict.result == Result.PASS

    # W1: Asymmetric tolerance tests

    def test_asymmetric_tolerance_passes_at_lower_bound(self) -> None:
        """W1: Asymmetric -10% tolerance passes at 110 words for 122 target."""
        artifact = MockArtifact(text="word " * 110)
        context = {"reference_word_count": 122}

        verdict = length_parity_strict_gate(
            artifact, context, tolerance_below=0.10, tolerance_above=0.25
        )

        assert verdict.result == Result.PASS
        assert "tolerance_below:0.1" in verdict.evidence_refs
        assert "tolerance_above:0.25" in verdict.evidence_refs

    def test_asymmetric_tolerance_passes_at_upper_bound(self) -> None:
        """W1: Asymmetric +25% tolerance passes at 152 words for 122 target.

        Note: round(122 * 1.25) = round(152.5) = 152 in Python (banker's rounding).
        """
        words = ["word"] * 152
        artifact = MockArtifact(text=" ".join(words))
        context = {"reference_word_count": 122}

        verdict = length_parity_strict_gate(
            artifact, context, tolerance_below=0.10, tolerance_above=0.25
        )

        assert verdict.result == Result.PASS

    def test_asymmetric_tolerance_fails_above_upper_bound(self) -> None:
        """W1: 153 words fails asymmetric +25% tolerance for 122 target."""
        artifact = MockArtifact(text="word " * 153)
        context = {"reference_word_count": 122}

        verdict = length_parity_strict_gate(
            artifact, context, tolerance_below=0.10, tolerance_above=0.25
        )

        assert verdict.result == Result.FAIL
        assert "length_outside_tolerance" in verdict.reason_codes

    def test_asymmetric_tolerance_fails_below_lower_bound(self) -> None:
        """W1: 109 words fails asymmetric -10% tolerance for 122 target."""
        artifact = MockArtifact(text="word " * 109)
        context = {"reference_word_count": 122}

        verdict = length_parity_strict_gate(
            artifact, context, tolerance_below=0.10, tolerance_above=0.25
        )

        assert verdict.result == Result.FAIL
        assert "length_outside_tolerance" in verdict.reason_codes


class TestQuantifiedOutcomeCountGate:
    """Test quantified outcome count gate."""

    def test_passes_with_two_outcomes(self) -> None:
        """Gate passes with ≥2 quantified outcomes."""
        artifact = MockArtifact(
            text="Delivered $5M savings and 25% efficiency improvement"
        )
        
        verdict = quantified_outcome_count_gate(artifact, {})
        
        assert verdict.gate_id == "quantified_outcome_count"
        assert verdict.result == Result.PASS
        assert "sufficient_outcomes" in verdict.reason_codes

    def test_fails_with_one_outcome(self) -> None:
        """Gate fails with <2 outcomes."""
        artifact = MockArtifact(text="Saved $5M in costs")
        
        verdict = quantified_outcome_count_gate(artifact, {})
        
        assert verdict.result == Result.FAIL
        assert "insufficient_outcomes" in verdict.reason_codes

    def test_fails_with_zero_outcomes(self) -> None:
        """Gate fails with no quantified outcomes."""
        artifact = MockArtifact(text="Experienced leader with proven track record")
        
        verdict = quantified_outcome_count_gate(artifact, {})
        
        assert verdict.result == Result.FAIL


class TestTargetCompanyNameAbsenceGate:
    """Test target company absence gate."""

    def test_passes_when_company_absent(self) -> None:
        """Gate passes when target company not in text."""
        artifact = MockArtifact(text="SVP with 15 years experience in AI")
        context = {"target_company": "Acme Corp"}
        
        verdict = target_company_name_absence_gate(artifact, context)
        
        assert verdict.gate_id == "target_company_name_absence"
        assert verdict.result == Result.PASS
        assert "target_company_absent" in verdict.reason_codes

    def test_fails_when_company_present(self) -> None:
        """Gate fails when target company in text."""
        artifact = MockArtifact(text="Excited to join Acme Corp team")
        context = {"target_company": "Acme Corp"}
        
        verdict = target_company_name_absence_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "target_company_present" in verdict.reason_codes

    def test_case_insensitive_match(self) -> None:
        """Company name match is case-insensitive."""
        artifact = MockArtifact(text="Looking forward to acme corp")
        context = {"target_company": "Acme Corp"}
        
        verdict = target_company_name_absence_gate(artifact, context)
        
        assert verdict.result == Result.FAIL

    def test_unknown_when_company_not_provided(self) -> None:
        """Unknown when target_company missing from context."""
        artifact = MockArtifact(text="Some text")
        context = {}
        
        verdict = target_company_name_absence_gate(artifact, context)
        
        assert verdict.result == Result.UNKNOWN


class TestForbiddenFillerStrictGate:
    """Test forbidden filler/buzzword gate."""

    def test_passes_with_clean_text(self) -> None:
        """Gate passes with no forbidden words."""
        artifact = MockArtifact(text="Engineering leader with proven delivery record")
        
        verdict = forbidden_filler_strict_gate(artifact, {})
        
        assert verdict.gate_id == "forbidden_filler_strict"
        assert verdict.result == Result.PASS
        assert "no_forbidden_fillers" in verdict.reason_codes

    def test_fails_with_synergy(self) -> None:
        """Gate fails on 'synergy'."""
        artifact = MockArtifact(text="Created synergy between teams")
        
        verdict = forbidden_filler_strict_gate(artifact, {})
        
        assert verdict.result == Result.FAIL
        assert "forbidden_filler_found" in verdict.reason_codes

    def test_fails_with_leverage(self) -> None:
        """Gate fails on 'leverage'."""
        artifact = MockArtifact(text="Leverage our core competencies")
        
        verdict = forbidden_filler_strict_gate(artifact, {})
        
        assert verdict.result == Result.FAIL

    def test_fails_with_thinking_outside_box(self) -> None:
        """Gate fails on cliché phrase."""
        artifact = MockArtifact(text="Thinking outside the box to solve problems")
        
        verdict = forbidden_filler_strict_gate(artifact, {})
        
        assert verdict.result == Result.FAIL

    def test_multiple_violations_reported(self) -> None:
        """Reports multiple forbidden fillers."""
        artifact = MockArtifact(
            text="Leverage synergies and move the needle"
        )
        
        verdict = forbidden_filler_strict_gate(artifact, {})
        
        assert verdict.result == Result.FAIL
        # Should have evidence refs for violations
        assert len(verdict.evidence_refs) >= 1


class TestSentenceMaxLengthGate:
    """Test sentence length gate."""

    def test_passes_with_short_sentences(self) -> None:
        """Gate passes when all sentences ≤40 words."""
        artifact = MockArtifact(text="Short sentence. Another brief one. Third.")
        
        verdict = sentence_max_length_gate(artifact, {})
        
        assert verdict.gate_id == "sentence_max_length"
        assert verdict.result == Result.PASS

    def test_fails_with_long_sentence(self) -> None:
        """Gate fails when any sentence >40 words."""
        long_sentence = "word " * 45  # 45 words
        artifact = MockArtifact(text=long_sentence)
        
        verdict = sentence_max_length_gate(artifact, {})
        
        assert verdict.result == Result.FAIL
        assert "sentence_too_long" in verdict.reason_codes

    def test_at_boundary(self) -> None:
        """Exactly 40 words passes."""
        boundary = "word " * 40
        artifact = MockArtifact(text=boundary)
        
        verdict = sentence_max_length_gate(artifact, {})
        
        assert verdict.result == Result.PASS


class TestArchetypeLeadGate:
    """Test archetype lead gate."""

    def test_passes_with_archetype_in_first_sentence(self) -> None:
        """Gate passes when archetype in opening."""
        artifact = MockArtifact(
            text="SVP of Engineering with 15 years experience. Led teams to deliver."
        )
        context = {"archetype": "SVP Engineering"}
        
        verdict = archetype_lead_gate(artifact, context)
        
        assert verdict.gate_id == "archetype_lead"
        assert verdict.result == Result.PASS
        assert "archetype_present" in verdict.reason_codes

    def test_fails_without_archetype(self) -> None:
        """Gate fails when archetype not in opening."""
        artifact = MockArtifact(
            text="15 years experience in technology. SVP of Engineering."
        )
        context = {"archetype": "SVP Engineering"}
        
        verdict = archetype_lead_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert "archetype_missing" in verdict.reason_codes

    def test_partial_match_works(self) -> None:
        """Partial archetype match (e.g., 'Engineering' from 'VP Engineering')."""
        artifact = MockArtifact(text="Engineering leader with deep expertise")
        context = {"archetype": "VP Engineering"}
        
        verdict = archetype_lead_gate(artifact, context)
        
        assert verdict.result == Result.PASS


class TestPerCandCompositeGate:
    """Test PER-CAND quality composite gate."""

    def test_passes_all_checks(self) -> None:
        """Composite passes when all individual gates pass."""
        # Build text that passes all gates:
        # - 100 words (for length parity)
        # - ≥2 quantified outcomes
        # - no target company mention
        # - no forbidden fillers
        # - short sentences
        # - archetype in first sentence
        base_text = (
            "Engineering leader with deep technical expertise and proven delivery record. "
            "Delivered $5M cost savings and 25% efficiency gains across multiple initiatives. "
            "Scaled team from 10 to 50 engineers while maintaining quality. "
        )
        # Pad to ~100 words without buzzwords
        padding = "Led high-performing teams. Drove strategic initiatives. " * 10
        text = base_text + padding
        
        artifact = MockArtifact(text=text)
        context = {
            "reference_word_count": 100,
            "target_company": "OtherCorp",  # Not in text
            "archetype": "Engineering",  # In first sentence
        }
        
        verdict = per_cand_quality_composite_gate(artifact, context)
        
        assert verdict.gate_id == "per_cand_quality_composite"
        assert verdict.result == Result.PASS

    def test_fails_when_any_check_fails(self) -> None:
        """Composite fails when any gate fails."""
        artifact = MockArtifact(text="Created synergy")  # Has forbidden word
        context = {
            "reference_word_count": 100,  # Too short, will fail length
            "target_company": "Acme",
            "archetype": "Missing",
        }
        
        verdict = per_cand_quality_composite_gate(artifact, context)
        
        assert verdict.result == Result.FAIL
        assert any("fail:" in code for code in verdict.reason_codes)


class TestW5Integration:
    """Integration tests for W5 gates."""

    def test_high_quality_candidate_passes(self) -> None:
        """Excellent candidate passes all W5 checks."""
        # Build high-quality text that passes all gates
        # Must have: proper length, 2+ outcomes, no buzzwords, no target company, archetype lead
        sections = [
            "SVP of Engineering with 15 years experience building elite technical organizations.",
            "Delivered $50M revenue growth and 40% efficiency improvements.",
            "Scaled engineering from 20 to 200 while maintaining 99.9% uptime.",
            "Led cloud transformation saving $5M annually.",
        ]
        # Repeat to reach ~100 words
        text = " ".join(sections) + " "
        text = text + "Led cross-functional teams. Drived technical strategy. Built scalable systems. " * 8
        
        artifact = MockArtifact(text=text)
        context = {
            "reference_word_count": 100,
            "target_company": "DifferentCorp",  # Not in text
            "archetype": "Engineering",
        }
        
        verdict = per_cand_quality_composite_gate(artifact, context)
        
        assert verdict.result == Result.PASS

    def test_low_quality_candidate_fails(self) -> None:
        """Poor candidate fails multiple W5 checks."""
        text = (
            "Leveraging synergies to move the needle. "
            "Thinking outside the box with innovative paradigm shifts. "
        )
        
        artifact = MockArtifact(text=text)
        context = {
            "reference_word_count": 100,  # Will fail length
            "target_company": "Target Corp",  # Not in text, OK
            "archetype": "CTO",  # Not in text, will fail
        }
        
        verdict = per_cand_quality_composite_gate(artifact, context)
        
        assert verdict.result == Result.FAIL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
