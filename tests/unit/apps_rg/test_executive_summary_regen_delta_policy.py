"""W4 — delta_class, G5 scope, cycles v2 receipts, cert guards."""

from __future__ import annotations

from typing import Any

import pytest


@pytest.fixture(autouse=True)
def _enable_regen_caps_for_policy_tests(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", "1")

from apps_rg.runtime.sections.executive_summary_candidate_pool import (
    SCORES_FRESHNESS_CARRIED_FORWARD,
    SCORES_FRESHNESS_FULL_PANEL,
)
from apps_rg.runtime.sections.executive_summary_judge_remediation import (
    collect_judge_remediation_delta_lines,
)
from apps_rg.runtime.sections.executive_summary_regen_delta_policy import (
    DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL,
    DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE,
    DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH,
    DELTA_CLASS_RESUME_VOICE_HUMANIZE,
    DELTA_CLASS_S6_FORWARD_SYNTHESIS,
    JUDGE_REMEDIATION_CYCLES_SCHEMA_VERSION,
    build_judge_remediation_cycles_receipt,
    build_regen_sentence_allowlist,
    cert_block_for_published_scores_freshness,
    compute_regen_outcome,
    evaluate_g5_delta_scope,
    evaluate_g5_delta_scope_v2,
    format_delta_class_regen_instruction,
    format_edit_budget_line,
    format_sentence_allowlist_label,
    infer_sentence_indexes_from_text,
    resolve_delta_class,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    exploratory_full_paragraph_regen_enabled,
)


def _soft_fail(dim: str, *, major: bool = True) -> dict[str, Any]:
    sev = "major" if major else "minor"
    dv = {
        dim: {"pass": False, "severity": sev, "codes": ["x"]},
    }
    for other in (
        "factual_support",
        "executive_signal",
        "resume_voice",
        "ats_alignment_without_keyword_stuffing",
        "anti_overfit",
        "synthesis_quality",
        "evidence_utilization",
        "deterministic_alignment",
    ):
        if other not in dv:
            dv[other] = {"pass": True, "severity": "none", "codes": []}
    return {
        "provider_key": "anthropic_claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "score": 3.5,
        "dimension_verdicts": dv,
    }


def test_cycles_receipt_schema_v2() -> None:
    doc = build_judge_remediation_cycles_receipt(
        max_cycles=3,
        generation_material_digest="abc",
        targeting_parity_at_regen_start=True,
        judge_packet_targeting_audit={},
        operator_judge_pass_floor=4.2,
    )
    assert doc["schema_version"] == JUDGE_REMEDIATION_CYCLES_SCHEMA_VERSION
    assert doc["schema"].endswith("_v2")


def test_resolve_delta_class_executive_signal() -> None:
    judges = [_soft_fail("executive_signal")]
    assert resolve_delta_class(judges) == DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL


def test_resolve_delta_class_s6_synthesis_only() -> None:
    judges = [_soft_fail("synthesis_quality")]
    assert resolve_delta_class(judges) == DELTA_CLASS_S6_FORWARD_SYNTHESIS


def test_default_delta_instruction_bans_full_s2_s6_rewrite() -> None:
    text = format_delta_class_regen_instruction(DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL)
    assert "S2–S6" not in text
    assert "rewrite S2" not in text.lower() or "at most five" in text


def test_resolve_delta_class_voice_prose_over_executive_signal_dimension() -> None:
    judges = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["Additionally and Furthermore openers; repetitive mechanical phrasing."],
            "dimension_verdicts": {
                "executive_signal": {"pass": False, "severity": "major", "codes": ["thin_arc"]},
                "resume_voice": {"pass": True, "severity": "none", "codes": []},
            },
        },
    ]
    assert resolve_delta_class(judges) == DELTA_CLASS_RESUME_VOICE_HUMANIZE


def test_format_edit_budget_line_uses_allowlist_indexes() -> None:
    line = format_edit_budget_line(
        DELTA_CLASS_RESUME_VOICE_HUMANIZE,
        frozenset({2, 3, 4, 5}),
    )
    assert "indexes 2, 3, 4, 5" in line
    assert "S2–S5" in line
    assert "freeze all other sentences verbatim" in line


def test_format_sentence_allowlist_label_contiguous_range() -> None:
    assert format_sentence_allowlist_label(frozenset({2, 3, 4, 5})) == "S2–S5"


def _brown_svp_soft_fail_panel() -> list[dict]:
    """Brown SVP pattern: Claude stack + Gemini voice; ChatGPT pass."""
    return [
        {
            "provider_key": "anthropic_claude",
            "provider_name": "Anthropic Claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["Sentences 2-5 read as achievement bullet stack."],
            "remediation_suggestions": ["Replace S2-S5 bullet stack with connective narrative."],
            "cited_sentence_indexes": [2, 3, 4, 5],
            "dimension_verdicts": {
                "executive_signal": {"pass": False, "severity": "major", "codes": ["bullet_stack"]},
            },
        },
        {
            "provider_key": "gemini_pro",
            "provider_name": "Gemini Pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["Additionally/Furthermore openers; repetitive mechanical phrasing."],
            "remediation_suggestions": ["Humanize S2-S5 connective tissue; vary sentence openers."],
            "cited_sentence_indexes": [2, 3, 4, 5],
            "dimension_verdicts": {
                "resume_voice": {"pass": False, "severity": "major", "codes": ["mechanical_opener"]},
            },
        },
        {
            "provider_key": "openai_chatgpt",
            "provider_name": "OpenAI ChatGPT",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
        },
    ]


def test_brown_delta_includes_gemini_voice_and_claude_stack_feedback() -> None:
    lines = collect_judge_remediation_delta_lines(
        _brown_svp_soft_fail_panel(),
        unused_fact_ids=[],
        allowed_fact_count=8,
        prior_word_count=120,
        prior_ledger_rows=6,
        compact=True,
    )
    joined = "\n".join(lines)
    assert resolve_delta_class(_brown_svp_soft_fail_panel()) == DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE
    assert "JUDGE_DELTA_SOURCE provider_key=gemini_pro" in joined
    assert "mechanical phrasing" in joined
    assert "JUDGE_DELTA_SOURCE provider_key=anthropic_claude" in joined
    assert "bullet stack" in joined
    assert "executive_signal_and_voice_v1" in joined
    assert "indexes 1, 2, 3, 4, 5, 6" in joined
    assert "metric_weave_s3_s5" in joined.lower()


def test_resolve_delta_class_composite_when_voice_and_executive_signal_on_one_judge() -> None:
    judges = [_soft_fail("resume_voice")]
    judges[0]["dimension_verdicts"]["executive_signal"] = {
        "pass": False,
        "severity": "major",
        "codes": ["thin_arc"],
    }
    assert resolve_delta_class(judges) == DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE


def test_g5_rejects_excess_sentence_edits() -> None:
    prior = "One. Two. Three. Four. Five. Six."
    after = "A. B. C. D. Five. Six."
    g5 = evaluate_g5_delta_scope(prior, after, DELTA_CLASS_S6_FORWARD_SYNTHESIS)
    assert g5["passed"] is False
    assert g5["reject_gate"] == "delta_scope_violation"


def test_g5_allows_within_budget() -> None:
    prior = "One. Two. Three. Four. Five. Six."
    after = "One. Two. Three. Four. Five. Revised six."
    g5 = evaluate_g5_delta_scope(prior, after, DELTA_CLASS_S6_FORWARD_SYNTHESIS)
    assert g5["passed"] is True


def test_infer_sentence_indexes_s2_s5_range() -> None:
    found = infer_sentence_indexes_from_text("Replace S2-S5 bullet stack; strengthen S6.")
    assert found == {2, 3, 4, 5, 6}


def test_build_allowlist_merges_judge_cited_and_fallback() -> None:
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "cited_sentence_indexes": [6],
        },
    ]
    allow, meta = build_regen_sentence_allowlist(
        judges,
        DELTA_CLASS_S6_FORWARD_SYNTHESIS,
    )
    assert 6 in allow
    assert "judge_cited_or_inferred" in meta["allowlist_sources"]


def test_g5v2_passes_multi_sentence_edits_within_allowlist() -> None:
    prior = "One. Two. Three. Four. Five. Six."
    after = "One. B. C. D. E. F."
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["S2-S5 read as bullet stack; strengthen S6."],
            "cited_sentence_indexes": [2, 3, 4, 5, 6],
        },
    ]
    g5 = evaluate_g5_delta_scope_v2(
        prior,
        after,
        DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE,
        x1d_judges=judges,
    )
    assert g5["schema"] == "executive_summary_g5_delta_scope_v2"
    assert g5["passed"] is True
    assert g5["allowlist_passed"] is True
    assert g5["edited_sentence_count"] == 5
    assert g5["g5_legacy_budget_advisory"]["passed"] is True


def test_g5v2_s6_forward_synthesis_allowlist_is_s6_only() -> None:
    prior = "One. Two. Three. Four. Five. Six."
    after = "One. Two. Three. Four. Five. Revised six."
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["S6 thin recap."],
            "cited_sentence_indexes": [6],
        },
    ]
    g5 = evaluate_g5_delta_scope_v2(
        prior,
        after,
        DELTA_CLASS_S6_FORWARD_SYNTHESIS,
        x1d_judges=judges,
    )
    assert g5["passed"] is True
    assert g5["allowlist"] == [6]


def test_g5v2_fails_s1_thesis_edit_without_allowlist() -> None:
    prior = "One. Two. Three. Four. Five. Six."
    after = "Thesis changed. Two. Three. Four. Five. Six."
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["S2-S5 stack."],
            "cited_sentence_indexes": [2, 3, 4, 5],
        },
    ]
    g5 = evaluate_g5_delta_scope_v2(
        prior,
        after,
        DELTA_CLASS_DIMENSION_EXECUTIVE_SIGNAL,
        x1d_judges=judges,
    )
    assert g5["passed"] is False
    assert g5["reject_gate"] == "delta_scope_violation_allowlist"
    assert 1 in g5["out_of_allowlist_indices"]


def test_g5v2_brown_pattern_four_edits_not_blocked_by_legacy_budget() -> None:
    """Brown exec_summary_20260526_193949: 4 edits on S3-S6, legacy budget=3 would fail."""
    prior = (
        "Brown thesis on enterprise IT strategy. "
        "Led platform modernization across claims. "
        "Scaled analytics for underwriting. "
        "Drove cloud migration programs. "
        "Built innovation portfolio governance. "
        "Forward path remains generic."
    )
    after = (
        "Brown thesis on enterprise IT strategy. "
        "Led platform modernization across claims. "
        "Scaled analytics for underwriting revised. "
        "Drove cloud migration programs revised. "
        "Built innovation portfolio governance revised. "
        "Forward path with specific enterprise IT direction."
    )
    judges = [
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_FAIL",
            "pass": False,
            "findings": ["Achievement bullet stack in S2-S5; thin S6."],
            "cited_sentence_indexes": [2, 3, 4, 5, 6],
        },
    ]
    g5 = evaluate_g5_delta_scope_v2(
        prior,
        after,
        DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE,
        x1d_judges=judges,
    )
    assert g5["passed"] is True
    assert g5["edited_sentence_count"] == 4
    assert g5["g5_legacy_budget_advisory"]["passed"] is True
    assert g5["g5_legacy_budget_advisory"]["max_sentence_edits_allowed"] == 6


def test_g5v2_caps_disabled_still_requires_six_sentences(monkeypatch: pytest.MonkeyPatch) -> None:
    """Brown RCA I3: regen must not publish 5-sentence drafts when caps are disabled."""
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", raising=False)
    prior = "One. Two. Three. Four. Five. Six."
    after = "One. Two. Three. Four. Five."
    g5 = evaluate_g5_delta_scope_v2(
        prior,
        after,
        DELTA_CLASS_EXECUTIVE_SIGNAL_AND_VOICE,
        x1d_judges=[],
    )
    assert g5["passed"] is False
    assert g5["reject_gate"] == "regen_sentence_count_invariant"
    assert g5["after_sentence_count"] == 5


def test_regen_outcome_scratch_when_no_acceptable_regen() -> None:
    cycles = [
        {
            "accepted": False,
            "publish_eligible": False,
            "reject_gate": "trigger_judge_regression",
        },
    ]
    assert (
        compute_regen_outcome(
            cycles=cycles,
            final_publish_baseline="scratch",
            all_model_backed_judges_pass=False,
        )
        == "no_acceptable_candidate"
    )


def test_regen_outcome_not_improved_when_scratch_wins_despite_accepted_regen() -> None:
    cycles = [
        {"accepted": True, "publish_eligible": True},
    ]
    assert (
        compute_regen_outcome(
            cycles=cycles,
            final_publish_baseline="scratch",
            all_model_backed_judges_pass=False,
        )
        == "no_acceptable_candidate"
    )


def test_cert_blocked_without_full_panel_on_material_change() -> None:
    blocked, reason = cert_block_for_published_scores_freshness(
        SCORES_FRESHNESS_CARRIED_FORWARD,
        published_candidate_id="regen_cycle_1",
        scratch_digest="a" * 64,
        published_digest="b" * 64,
    )
    assert blocked is True
    assert reason == "stale_non_trigger_scores"


def test_cert_not_blocked_scratch_full_panel() -> None:
    digest = "c" * 64
    blocked, reason = cert_block_for_published_scores_freshness(
        SCORES_FRESHNESS_FULL_PANEL,
        published_candidate_id="scratch",
        scratch_digest=digest,
        published_digest=digest,
    )
    assert blocked is False
    assert reason is None


def test_exploratory_delta_class_env_default_off(monkeypatch: Any) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_EXPLORATORY_FULL_PARAGRAPH_REGEN", raising=False)
    assert exploratory_full_paragraph_regen_enabled() is False
    assert resolve_delta_class([_soft_fail("executive_signal")]) != DELTA_CLASS_EXPLORATORY_FULL_PARAGRAPH


def _claude_holistic_soft_fail_s6_thin() -> dict[str, Any]:
    return {
        "provider_key": "anthropic_claude",
        "evaluator_mode": "MODEL_BACKED",
        "provider_status": "MODEL_BACKED_FAIL",
        "pass": False,
        "score": 4.0,
        "quality_flags": ["s6_forward_synthesis_slightly_thin"],
        "findings": [
            "All deterministic gates pass; no structural or compliance failures.",
            "Minor: S6 forward synthesis is somewhat thin.",
        ],
        "remediation_suggestions": [
            "Strengthen S6 with a more specific forward-looking synthesis.",
        ],
        "dimension_verdicts": {
            "synthesis_quality": {
                "pass": True,
                "severity": "minor",
                "codes": ["s6_thin_recap"],
            },
            "factual_support": {"pass": True, "severity": "none", "codes": []},
            "executive_signal": {"pass": True, "severity": "none", "codes": []},
            "resume_voice": {"pass": True, "severity": "none", "codes": []},
            "ats_alignment_without_keyword_stuffing": {
                "pass": True,
                "severity": "none",
                "codes": [],
            },
            "anti_overfit": {"pass": True, "severity": "none", "codes": []},
            "evidence_utilization": {"pass": True, "severity": "none", "codes": []},
            "deterministic_alignment": {"pass": True, "severity": "none", "codes": []},
        },
    }


def test_resolve_delta_class_holistic_floor_s6_thin_without_major_dim() -> None:
    judges = [_claude_holistic_soft_fail_s6_thin()]
    assert (
        resolve_delta_class(judges, operator_judge_pass_floor=4.2)
        == DELTA_CLASS_S6_FORWARD_SYNTHESIS
    )


def test_resolve_delta_class_claude_only_binding_s6() -> None:
    judges = [_claude_holistic_soft_fail_s6_thin()]
    assert resolve_delta_class(judges) == DELTA_CLASS_S6_FORWARD_SYNTHESIS
