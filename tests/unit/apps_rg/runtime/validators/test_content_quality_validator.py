from __future__ import annotations

from apps_rg.runtime.validators.content_quality_validator import ContentQualityValidator


def _validator(*, min_skill_matches: int = 3) -> ContentQualityValidator:
    return ContentQualityValidator(
        {
            "placeholder_patterns": [r"\[[A-Z _]+\]"],
            "skill_keywords": ["Python", "AWS", "Leadership", "Kubernetes"],
            "min_skill_matches": min_skill_matches,
        }
    )


def test_content_quality_flags_placeholders_sparse_metrics_and_skill_gaps() -> None:
    result = _validator(min_skill_matches=3).validate_content_quality(
        {
            "summary": "Senior platform leader for [TARGET COMPANY].",
            "experience": ["Led Python migration for 1 project."],
            "skills": ["Python"],
        },
        job_desc="Looking for AWS, Kubernetes, and leadership depth.",
    )

    assert result.passed is False
    assert result.metadata == {"validation_type": "deterministic"}
    assert any("placeholder" in issue for issue in result.issues)
    assert "Insufficient quantified achievements (1 found)" in result.issues
    assert "Insufficient skill matches (1 found)" in result.issues
    assert result.suggestions == ["Improve skill alignment with job description"]
    assert result.score is not None and result.score < 1.0


def test_content_quality_passes_when_metrics_and_skills_are_present() -> None:
    result = _validator(min_skill_matches=3).validate_content_quality(
        {
            "summary": "Executive platform leader.",
            "experience": [
                "Delivered 25% latency reduction across 4 projects.",
                "Managed $5,000,000 cloud modernization over 3 years.",
            ],
            "skills": ["Python", "AWS", "Leadership"],
            "education": ["MBA"],
            "certifications": ["AWS"],
        },
        job_desc="Python AWS Leadership for platform modernization.",
    )

    assert result.passed is True
    assert result.issues == []
    assert result.suggestions == []
    assert result.score == 1.0


def test_text_extraction_and_formatting_issues_are_deterministic() -> None:
    validator = _validator()

    text = validator.extract_resume_text({"summary": "LOUD AAAA", "details": ["ok"]})
    issues = validator.detect_formatting_issues("LOUD AAAA!!!! A. B. C. D.")

    assert "summary" in text
    assert "LOUD AAAA" in text
    assert "Excessive capitalization detected" in issues
    assert "Repeated characters detected" in issues
    assert "Too many very short sentences" in issues
