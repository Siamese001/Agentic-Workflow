"""Direct contract tests for the executive_summary lane helper surface."""

from __future__ import annotations

from argparse import Namespace

from apps_rg.runtime.sections.executive_summary_lane import (
    _build_word_budget_repair_user,
    _args_jd_text,
    _args_target_title,
    _first_sentence_from_prose,
    _strip_targeting_cap_notice,
    build_selected_fact_plan,
    coerce_resume_display_sentence_count_band,
    check_executive_summary_narrative_shape,
    check_l2_resume_voice,
    normalize_executive_summary_llm_output,
    parse_model_json,
    reconcile_claim_ledger_to_sentence_count,
)
from apps_rg.runtime.sections.executive_summary_targeting_cap import _CAP_NOTICE
from apps_rg.runtime.validators.executive_summary_sentence_utils import split_sentences


def _five_sentence_resume() -> str:
    return (
        "First sentence establishes the context. "
        "Second sentence keeps the pace. "
        "The operating model keeps release cadence steady, enabling the team to prove policy "
        "controls without slowing delivery. "
        "Fourth sentence closes the middle. "
        "Fifth sentence closes the arc."
    )


def test_normalize_executive_summary_llm_output_coerces_resume_and_uses_runtime_plan() -> None:
    parsed = {
        "executive_summary": _five_sentence_resume(),
        "claim_ledger_emitted": [{"claim_text": "claimed", "source_fact_ids": ["fact_1"]}],
        "gap_notes": ("not", "a", "list"),
        "change_log": [{"operation": "seed"}],
        "self_check": {"ok": True},
        "source_sensitive_phrase_ledger": ["phrase"],
        "input_payload_hash": "input-hash",
        "output_payload_hash": "output-hash",
        "claim_ledger_hash": "ledger-hash",
        "allowed_fact_ids_hash": "facts-hash",
    }
    runtime_selected_fact_plan = {
        "section_id": "executive_summary",
        "facts": [{"fact_id": "fact_1", "claim_text": "claimed"}],
    }

    normalized = normalize_executive_summary_llm_output(parsed, runtime_selected_fact_plan)

    assert split_sentences(normalized["resume_display_text"]) == [
        "First sentence establishes the context.",
        "Second sentence keeps the pace.",
        "The operating model keeps release cadence steady.",
        "That capability enables the team to prove policy controls without slowing delivery.",
        "Fourth sentence closes the middle.",
        "Fifth sentence closes the arc.",
    ]
    assert normalized["selected_fact_plan"] == runtime_selected_fact_plan
    assert normalized["claim_ledger"] == parsed["claim_ledger_emitted"]
    assert normalized["gap_notes"] == []
    assert normalized["change_log"] == parsed["change_log"]
    assert normalized["self_check"] == parsed["self_check"]
    assert normalized["source_sensitive_phrase_ledger"] == parsed["source_sensitive_phrase_ledger"]
    assert normalized["input_payload_hash"] == "input-hash"
    assert normalized["output_payload_hash"] == "output-hash"
    assert normalized["claim_ledger_hash"] == "ledger-hash"
    assert normalized["allowed_fact_ids_hash"] == "facts-hash"


def test_coerce_resume_display_sentence_count_band_splits_one_compound_sentence() -> None:
    coerced = coerce_resume_display_sentence_count_band(_five_sentence_resume())

    assert split_sentences(coerced) == [
        "First sentence establishes the context.",
        "Second sentence keeps the pace.",
        "The operating model keeps release cadence steady.",
        "That capability enables the team to prove policy controls without slowing delivery.",
        "Fourth sentence closes the middle.",
        "Fifth sentence closes the arc.",
    ]
    assert ".." not in coerced


def test_reconcile_claim_ledger_to_sentence_count_appends_split_sentence_row() -> None:
    parsed = {
        "resume_display_text": coerce_resume_display_sentence_count_band(_five_sentence_resume()),
        "claim_ledger": [
            {"claim_text": "First sentence establishes the context.", "source_fact_ids": ["fact_1"]},
            {"claim_text": "Second sentence keeps the pace.", "source_fact_ids": ["fact_2"]},
            {
                "claim_text": "The operating model keeps release cadence steady.",
                "source_fact_ids": ["fact_3"],
            },
            {
                "claim_text": "Fourth sentence closes the middle.",
                "source_fact_ids": ["fact_4"],
            },
            {
                "claim_text": "Fifth sentence closes the arc.",
                "source_fact_ids": ["fact_5", "fact_5_metric_1234"],
                "support_class": "FACT_ONLY",
            },
        ],
    }

    reconcile_claim_ledger_to_sentence_count(parsed)

    ledger = parsed["claim_ledger"]
    assert len(ledger) == 6
    assert ledger[-1] == {
        "claim": "Fifth sentence closes the arc.",
        "claim_text": "Fifth sentence closes the arc.",
        "source_fact_ids": ["fact_5", "fact_5_metric_1234"],
        "support_class": "FACT_ONLY",
        "deterministic_split_continuation": True,
    }


def test_check_l2_resume_voice_rejects_first_person_and_bridge_phrases() -> None:
    first_person_ok, first_person_reason = check_l2_resume_voice("I led the launch.")
    bridge_ok, bridge_reason = check_l2_resume_voice(
        "The program delivered policy controls. This was achieved through careful sequencing."
    )

    assert first_person_ok is False
    assert first_person_reason is not None
    assert "First-person pronoun" in first_person_reason
    assert bridge_ok is False
    assert bridge_reason is not None
    assert "Bridge phrase" in bridge_reason


def test_check_executive_summary_narrative_shape_rejects_empty_and_stacked_forms() -> None:
    empty_ok, empty_reason = check_executive_summary_narrative_shape("")
    stacked_ok, stacked_reason = check_executive_summary_narrative_shape(
        "Generated release plan. Generated rollout plan. Generated launch plan.",
        [
            {"claim_text": "Generated release plan."},
            {"claim_text": "Generated rollout plan."},
            {"claim_text": "Generated launch plan."},
        ],
    )
    enumerated_ok, enumerated_reason = check_executive_summary_narrative_shape(
        "One, two, three, four, five, six, seven."
    )

    assert empty_ok is False
    assert empty_reason == "Empty executive summary"
    assert stacked_ok is False
    assert stacked_reason is not None
    assert "sentence-stacked proof" in stacked_reason
    assert enumerated_ok is False
    assert enumerated_reason is not None
    assert "Long capability enumeration" in enumerated_reason


def test_parse_model_json_salvages_truncated_payload() -> None:
    parsed, err = parse_model_json('{"resume_display_text": "Hello", "self_check": {')

    assert err == ""
    assert parsed is not None
    assert parsed["resume_display_text"] == "Hello"
    assert parsed["self_check"]["salvaged_truncated_json"] is True


def test_lane_argument_helpers_and_targeting_cap_notice_normalization() -> None:
    args = Namespace(target_title="  VP Platform  ", target_role="fallback role", jd_text="  JD line  ", jd="fallback jd")
    fallback_args = Namespace(target_role="Fallback Role", jd="Fallback JD")

    assert _args_target_title(args) == "VP Platform"
    assert _args_jd_text(args) == "JD line"
    assert _args_target_title(fallback_args) == "Fallback Role"
    assert _args_jd_text(fallback_args) == "Fallback JD"
    assert _strip_targeting_cap_notice(f"alpha{_CAP_NOTICE}beta") == "alpha\nbeta"


def test_lane_fact_plan_and_repair_prompt_helpers() -> None:
    selected_facts = [
        {"fact_id": f"fact_{idx}", "claim_text": f"Claim {idx}"} for idx in range(1, 6)
    ]

    plan = build_selected_fact_plan(selected_facts)
    prompt = _build_word_budget_repair_user(123, word_ceiling=120)

    assert plan["section_id"] == "executive_summary"
    assert plan["selection_method"] == "resume_document_order_top_n"
    assert plan["required_fact_ids"] == ["fact_1", "fact_2", "fact_3", "fact_4"]
    assert [row["fact_id"] for row in plan["facts"]] == ["fact_1", "fact_2", "fact_3", "fact_4"]
    assert _first_sentence_from_prose("First sentence. Second sentence.", min_len=0) == "First sentence."
    assert "123 words" in prompt
    assert "120 words" in prompt
    assert "six sentences" in prompt

