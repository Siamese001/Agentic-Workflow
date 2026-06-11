"""W3.2 — narrative mechanical X2 gates."""

from __future__ import annotations

from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences
from apps_rg.runtime.validators.narrative_mechanical_x2 import (
    check_narrative_bullet_overlap_threshold,
    check_narrative_forbidden_opener,
    check_narrative_metric_cap,
)
from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates


def _fake_judges() -> list[dict]:
    return [{"evaluator_mode": "MOCK", "pass": True}]


def test_split_sentences_abbreviation_safe() -> None:
    assert len(split_sentences("Led U.S. delivery for Dr. Smith at Acme Inc.")) == 1


def test_forbidden_opener_led() -> None:
    ok, hit, _ = check_narrative_forbidden_opener("Led enterprise platform delivery across programs.")
    assert not ok
    assert hit == "led"


def test_forbidden_opener_company_prefix_leadin() -> None:
    # Regression (2026-06-11): "At IBM, led ..." shipped because the opener gate
    # only checked mechanical verb openers, not scene-setting prepositions.
    ok, hit, reason = check_narrative_forbidden_opener(
        "At IBM, led enterprise-scale cloud modernization and data governance."
    )
    assert not ok
    assert hit == "at"
    assert "scene-setting lead-in" in (reason or "")


def test_forbidden_opener_temporal_and_role_leadins_blocked() -> None:
    for narrative in (
        "While at IBM, led the modernization program.",
        "During my tenure, scaled the engineering organization.",
        "As VP of Engineering, drove platform delivery.",
        "Throughout the engagement, governed regulatory lineage.",
    ):
        ok, _, _ = check_narrative_forbidden_opener(narrative)
        assert not ok, f"expected scene-setting lead-in to fail: {narrative!r}"


def test_action_verb_leadins_still_pass() -> None:
    for narrative in (
        "Stewarded Unify Consulting's end-to-end mandate to industrialize agentic AI.",
        "Modernized legacy policy administration platforms into AWS-based services.",
        "Directed a $15M regulatory analytics modernization program.",
    ):
        ok, hit, _ = check_narrative_forbidden_opener(narrative)
        assert ok, f"expected action-verb opener to pass: {narrative!r} (hit={hit!r})"


def test_metric_cap_exceeded() -> None:
    from apps_rg.runtime.validators.narrative_mechanical_x2 import UNIFY_NARRATIVE_METRIC_PATTERNS

    text = "Delivered $22M revenue, 20% margin, 8 to 28 scale, and six months to three weeks."
    ok, count, _ = check_narrative_metric_cap(text, metric_patterns=UNIFY_NARRATIVE_METRIC_PATTERNS, max_metrics=2)
    assert not ok
    assert count > 2


def test_bullet_overlap_threshold() -> None:
    companion = "bul_unify_001: Designed governed agentic AI platform capabilities for regulated enterprise."
    narrative = "Designed governed agentic AI platform capabilities for regulated enterprise outcomes."
    ok, hit, _ = check_narrative_bullet_overlap_threshold(narrative, companion)
    assert not ok
    assert hit


def test_unify_x2_registers_mechanical_gates() -> None:
    narrative = "Led platform outcomes."
    companion = "bul_unify_001: Distinct bullet text here."
    gates = run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output={"narrative_sentence": narrative, "claim_ledger": []},
        claim_ledger=[],
        jd_text="",
        runtime_generation_status="MOCKED",
        companion_bullet_texts=companion,
        x1d_judges=_fake_judges(),
    )
    by_id = {g.gate_id: g for g in gates}
    assert by_id["x2_unify_narrative_forbidden_opener"].pass_ is False
    assert "x2_unify_narrative_metric_cap" in by_id
    assert "x2_unify_narrative_bullet_overlap_threshold" in by_id
