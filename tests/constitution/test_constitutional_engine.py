"""Unit tests for the ConstitutionalEngine rule detectors."""
from __future__ import annotations

from stacks_v10_8.constitutional_engine import ConstitutionalEngine


def _violation_ids(result):
    return {violation.rule_id for violation in result.violations}


def test_flags_unverifiable_claims() -> None:
    engine = ConstitutionalEngine()
    text = "I guarantee these projections are 300% accurate without evidence."
    result = engine.review_text(text)
    assert not result.passed
    assert "no_unverifiable_factual_claims" in _violation_ids(result)


def test_flags_invented_entities() -> None:
    engine = ConstitutionalEngine()
    result = engine.review_text("Partnered with Imaginary University to launch the study.")
    assert "no_invented_entities" in _violation_ids(result)


def test_flags_fake_contact_details() -> None:
    engine = ConstitutionalEngine()
    result = engine.review_text("Reach me at 555-0101 or fake@example.com for details.")
    assert "no_fake_contact_details" in _violation_ids(result)


def test_flags_political_persuasion() -> None:
    engine = ConstitutionalEngine()
    result = engine.review_text("Vote for our candidate in the upcoming election.")
    assert "no_political_persuasion" in _violation_ids(result)


def test_flags_discriminatory_language() -> None:
    engine = ConstitutionalEngine()
    result = engine.review_text("Women should not apply to this role.")
    assert "no_discriminatory_framing" in _violation_ids(result)


def test_requires_source_attribution() -> None:
    engine = ConstitutionalEngine()
    result = engine.review_text("According to analysts, revenues doubled last year.")
    assert "require_source_attribution" in _violation_ids(result)


def test_reports_multiple_violations() -> None:
    engine = ConstitutionalEngine()
    text = "Vote for progress. According to insiders, the market tripled."
    result = engine.review_text(text)
    ids = _violation_ids(result)
    assert "no_political_persuasion" in ids
    assert "require_source_attribution" in ids
    assert len(result.violations) >= 2


def test_passes_clean_text() -> None:
    engine = ConstitutionalEngine()
    text = (
        "According to Bureau of Labor Statistics data (Source: https://www.bls.gov), "
        "the sector grew 3%."
    )
    result = engine.review_text(text)
    assert result.passed
    assert result.violations == []
