"""Unit tests for the live deterministic ATS validator."""

from __future__ import annotations

import pytest

from apps_rg.runtime.validators.ats_validator import AtsValidator


def _validator() -> AtsValidator:
    return AtsValidator(
        {
            "standard_headers": {
                "experience": ["professional experience", "work experience"],
                "education": ["education"],
                "skills": ["skills"],
            },
            "allowed_non_standard_sections": ["summary"],
            "ats_unfriendly_patterns": [r"(?i)two-column", r"text box"],
            "keyword_optimization": {
                "min_score_threshold": 0.6,
                "stop_words": ["and", "for", "the", "with"],
            },
        }
    )


def test_validate_ats_compatibility_passes_clean_resume() -> None:
    result = _validator().validate_ats_compatibility(
        {
            "experience": "Built governance platform delivery programs.",
            "skills": ["Python", "Governance", "Platform"],
            "_internal": "ignored by header validation",
        },
        job_desc="Python governance platform",
    )

    assert result.passed
    assert result.issues == []
    assert result.score == pytest.approx(1.0)
    assert result.metadata == {"validation_type": "deterministic"}


def test_validate_ats_compatibility_reports_patterns_headers_and_low_keywords() -> None:
    result = _validator().validate_ats_compatibility(
        {
            "Creative Layout": "Two-column resume with text box callouts.",
            "experience": "Python delivery.",
        },
        job_desc="Python governance platform",
    )

    assert not result.passed
    assert "ATS-unfriendly pattern found: (?i)two-column" in result.issues
    assert "ATS-unfriendly pattern found: text box" in result.issues
    assert "Non-standard section header: Creative Layout" in result.issues
    assert "Low keyword match (33%)" in result.issues
    assert result.score == pytest.approx(1 / 3)


def test_keyword_score_returns_full_score_when_job_words_are_only_stop_words() -> None:
    assert _validator().calculate_keyword_score(
        {"experience": "No keyword-bearing job terms are required."},
        "the and with for",
    ) == pytest.approx(1.0)


def test_extract_keywords_normalizes_and_removes_stop_words() -> None:
    assert _validator().extract_keywords("The Agentic and Governance AI", min_length=3) == {
        "agentic",
        "governance",
    }


def test_validate_formatting_reports_control_chars_line_breaks_and_mixed_endings() -> None:
    issues = _validator().validate_formatting("line one\r\nline two\n\n\n\x01")

    assert issues == [
        "Contains control characters",
        "Excessive line breaks",
        "Mixed line ending formats",
    ]
