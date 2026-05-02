"""Tests for apps_rg.integrations.ats_coverage — ATS hardening gates."""

from __future__ import annotations

import pytest

from apps_rg.integrations.ats_coverage import (
    apply_ats_hardening,
    compute_ats_coverage,
    ensure_title_in_headline,
    headline_contains_title,
)


# ---------------------------------------------------------------- coverage


def test_coverage_passes_when_all_terms_present() -> None:
    resume = {
        "headline": "Strategic Advisory Leader",
        "executive_summary": "Agentic AI platform architect with governance and compliance expertise.",
    }
    result = compute_ats_coverage(
        resume, must_have=["agentic", "AI", "governance", "compliance"]
    )
    assert result.coverage == 1.0
    assert result.passed
    assert result.missing == []


def test_coverage_reports_missing_terms() -> None:
    resume = {"executive_summary": "Agentic AI platform architect."}
    result = compute_ats_coverage(
        resume,
        must_have=["agentic", "AI", "governance", "compliance"],
        floor=0.70,
    )
    # 2/4 = 0.5 — below floor
    assert 0.49 < result.coverage < 0.51
    assert not result.passed
    assert set(result.missing) == {"governance", "compliance"}


def test_coverage_case_insensitive_match() -> None:
    resume = {"headline": "MULTI-AGENT orchestration expertise"}
    result = compute_ats_coverage(resume, must_have=["multi-agent", "Orchestration"])
    assert result.coverage == 1.0


def test_coverage_word_boundary_prevents_substring_match() -> None:
    resume = {"headline": "Strategic advisor"}
    # "visor" should NOT match inside "advisor"
    result = compute_ats_coverage(resume, must_have=["visor"])
    assert result.coverage == 0.0


def test_coverage_empty_must_have_is_trivially_passing() -> None:
    result = compute_ats_coverage({"headline": "x"}, must_have=[])
    assert result.coverage == 1.0
    assert result.passed


def test_coverage_scans_nested_sections() -> None:
    resume = {
        "professional_experience": [
            {"bullet_pool": [{"text": "Drove agentic AI platform delivery."}]}
        ]
    }
    result = compute_ats_coverage(resume, must_have=["agentic", "delivery"])
    assert result.coverage == 1.0


# ------------------------------------------------------------ title match


def test_headline_contains_title_exact_substring() -> None:
    assert headline_contains_title("SVP, Agentic Transformation — Leader", "SVP, Agentic Transformation")


def test_headline_contains_title_reordered_tokens() -> None:
    # "Agentic Transformation SVP" contains all tokens of "SVP Agentic Transformation"
    assert headline_contains_title("Agentic Transformation SVP at Blend360", "SVP, Agentic Transformation")


def test_headline_missing_title_returns_false() -> None:
    assert not headline_contains_title("Strategic Advisory Leader", "SVP, Agentic Transformation")


def test_empty_target_title_is_trivially_true() -> None:
    assert headline_contains_title("anything", "")


def test_ensure_title_prepends_when_missing() -> None:
    resume = {"headline": "Strategic Advisory Leader"}
    new, modified = ensure_title_in_headline(
        resume, target_title="SVP, Agentic Transformation"
    )
    assert modified
    assert new.startswith("SVP, Agentic Transformation")
    assert resume["headline"].startswith("SVP, Agentic Transformation")


def test_ensure_title_noop_when_already_present() -> None:
    resume = {"headline": "SVP Agentic Transformation Leader"}
    new, modified = ensure_title_in_headline(
        resume, target_title="SVP, Agentic Transformation"
    )
    assert not modified
    assert resume["headline"] == "SVP Agentic Transformation Leader"


def test_ensure_title_builds_headline_when_missing() -> None:
    resume = {}
    new, modified = ensure_title_in_headline(
        resume, target_title="SVP, Agentic Transformation"
    )
    assert modified
    assert new == "SVP, Agentic Transformation"


# --------------------------------------------------- combined apply


def test_apply_ats_hardening_modifies_only_headline() -> None:
    """Policy lock (2026-05-01): title-match is the ONLY in-place mutation."""
    resume = {
        "headline": "Strategic Advisory Leader",
        "executive_summary": "Delivered consulting outcomes.",
    }
    report = apply_ats_hardening(
        resume,
        jd_must_have=["SVP", "agentic", "governance", "consulting"],
        target_title="SVP, Agentic Transformation",
    )
    # Title prepended to headline.
    assert report["title_modified"]
    assert resume["headline"].startswith("SVP, Agentic Transformation")
    # No injection happened — keywords_injected must be False.
    assert report["keywords_injected"] is False
    # No new keys added to resume_data.
    assert "ats_keywords" not in resume


def test_apply_ats_hardening_never_injects_into_any_field() -> None:
    """Authenticity guardrail — narrative AND any extra fields untouched."""
    original_summary = "Drove measurable outcomes for consulting clients over ten years."
    original_bullets = [{"text": "Delivered platform engagement."}]
    resume = {
        "headline": "SVP, Agentic Transformation — Senior Leader",
        "executive_summary": original_summary,
        "professional_experience": [{"bullet_pool": original_bullets}],
    }
    keys_before = set(resume.keys())
    apply_ats_hardening(
        resume,
        jd_must_have=["agentic", "governance", "compliance", "SOC 2"],
        target_title="SVP, Agentic Transformation",
    )
    # Narrative sections byte-identical.
    assert resume["executive_summary"] == original_summary
    assert resume["professional_experience"][0]["bullet_pool"] == original_bullets
    # No new resume fields were added.
    assert set(resume.keys()) == keys_before


def test_apply_ats_hardening_reports_missing_terms_for_diagnostic() -> None:
    """Coverage gaps are surfaced so the user can revise upstream."""
    resume = {"executive_summary": "Agentic AI delivery only."}
    report = apply_ats_hardening(
        resume,
        jd_must_have=["agentic", "governance", "SOC 2"],
        target_title="",
    )
    # governance + SOC 2 are missing.
    assert set(report["coverage_result"]["missing"]) == {"governance", "SOC 2"}
    assert report["coverage_result"]["coverage"] == pytest.approx(1 / 3, rel=0.01)
    assert not report["coverage_result"]["passed"]


def test_apply_ats_hardening_empty_must_have_is_noop() -> None:
    resume = {"headline": "Strategic Advisory Leader"}
    report = apply_ats_hardening(resume, jd_must_have=[], target_title="")
    assert not report["title_modified"]
    assert not report["keywords_injected"]
    assert report["coverage_result"]["coverage"] == 1.0


def test_injection_helper_is_not_exported() -> None:
    """Verify the removed helper stays removed — policy lock."""
    from apps_rg.integrations import ats_coverage

    assert not hasattr(ats_coverage, "inject_missing_keywords_into_ats_block")
    assert "inject_missing_keywords_into_ats_block" not in ats_coverage.__all__
