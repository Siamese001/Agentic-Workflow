"""Unit tests: synthesis regen bounds and repair prompts."""

from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

from apps_rg.runtime.sections.executive_summary_lane import (
    _build_synthesis_repair_user,
    _regen_candidate_preferred,
    _shape_failure_count,
    _synthesis_shape_reject_reason,
    retry_provider_for_synthesis,
)
from apps_rg.runtime.sections.executive_summary_repair_policy import (
    SYNTHESIS_REGEN_MAX_ATTEMPTS,
    synthesis_regen_max_attempts,
)

# apps-test-model: APP CONTRACT


def test_synthesis_regen_max_attempts_default_is_two(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS", raising=False)
    assert synthesis_regen_max_attempts() == SYNTHESIS_REGEN_MAX_ATTEMPTS == 2


def test_synthesis_regen_max_attempts_env_clamped_only_when_caps_enabled(monkeypatch) -> None:
    monkeypatch.delenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", raising=False)
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS", "9")
    assert synthesis_regen_max_attempts() == 9
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_REGEN_CAPS", "1")
    assert synthesis_regen_max_attempts() == 3
    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS", "1")
    assert synthesis_regen_max_attempts() == 1


def test_synthesis_regen_receipt_distinguishes_improvement_from_shape_acceptance(
    monkeypatch,
    tmp_path: Path,
) -> None:
    import apps_rg.runtime.sections.executive_summary_lane as lane

    monkeypatch.setenv("APPS_RG_EXEC_SUMMARY_SYNTHESIS_REGEN_MAX_ATTEMPTS", "2")
    responses = iter(("retry one", "retry two"))

    def fake_shape(text, *_args, **_kwargs):
        return False, "cross_fact_display_conflation:too_many_source_fact_ids_in_one_sentence"

    def fake_budgeted(*_args, **_kwargs):
        text = next(responses)
        result = SimpleNamespace(
            runtime_generation_status="REAL_LLM",
            raw_model_output=json.dumps(
                {"resume_display_text": text, "claim_ledger": []}
            ),
            to_dict=lambda: {"raw_model_output": text},
        )
        attempt = int(_kwargs["attempt_index"])
        return SimpleNamespace(
            result=result,
            call_id=f"retry-{attempt}",
            dispatch_allowed=True,
            block_reason=None,
        )

    monkeypatch.setattr(lane, "_synthesis_shape_reject_reason", fake_shape)
    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_regen_dispatch.budgeted_regen_call",
        fake_budgeted,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_regen_dispatch.mark_regen_call_parse",
        lambda *_args, **_kwargs: None,
    )
    monkeypatch.setattr(
        "apps_rg.runtime.sections.executive_summary_synthesis_monotonic.evaluate_synthesis_regen_monotonicity",
        lambda **_kwargs: (True, {"accepted": True}),
    )

    raw = json.dumps({"resume_display_text": "initial", "claim_ledger": []})
    returned_raw, _, _ = retry_provider_for_synthesis(
        [{"role": "user", "content": "prompt"}],
        {"model": "test"},
        raw,
        {"resume_display_text": "initial", "claim_ledger": []},
        artifact_dir=tmp_path,
    )

    assert returned_raw == raw
    receipt = json.loads(
        (tmp_path / "synthesis_regen_receipt.json").read_text(encoding="utf-8")
    )
    assert receipt["accepted"] is False
    assert receipt["reverted_to_first_pass"] is True
    assert receipt["judge_stage_eligible_from_retry"] is False
    assert receipt["initial_candidate_digest"]
    assert receipt["authoritative_candidate_digest"] == receipt["initial_candidate_digest"]
    assert all(
        row["acceptance_scope"] == "MONOTONIC_IMPROVEMENT_ONLY"
        for row in receipt["attempts"]
    )
    assert all(row["shape_gate_snapshot"]["pass"] is False for row in receipt["attempts"])


def test_repair_user_includes_evidence_weave_and_anti_shrink() -> None:
    msg = _build_synthesis_repair_user(
        "claim_ledger_rows_4_with_pool_7_need_at_least_5; sentence 0: mechanism_inventory:6_terms",
        attempt_index=0,
        prior_word_count=102,
        prior_ledger_rows=4,
        last_monotonicity_rejected=True,
    )
    assert "EVIDENCE_WEAVE" in msg
    assert "MECHANISM_CONTROL" in msg
    assert "PRIOR REGEN SHRANK" in msg
    assert "102" in msg


def test_regen_candidate_preferred_rejects_mono_rejected_shrink_with_lower_fail_count() -> None:
    assert (
        _regen_candidate_preferred(
            new_fail_count=1,
            new_ledger_rows=4,
            new_word_count=62,
            best_fail_count=2,
            best_ledger_rows=5,
            best_word_count=81,
            monotonicity_accepted=False,
        )
        is False
    )


def test_regen_candidate_preferred_accepts_mono_ok_weave_gain() -> None:
    assert (
        _regen_candidate_preferred(
            new_fail_count=2,
            new_ledger_rows=5,
            new_word_count=81,
            best_fail_count=4,
            best_ledger_rows=4,
            best_word_count=74,
            monotonicity_accepted=True,
        )
        is True
    )


def test_build_synthesis_repair_user_includes_conflation_guidance() -> None:
    msg = _build_synthesis_repair_user(
        "cross_fact_display_conflation:platform_and_governance",
        attempt_index=1,
        prior_word_count=80,
        prior_ledger_rows=5,
    )
    assert "fact_governance_003" in msg
    assert "Led/Successfully/Also/Built" in msg


def test_synthesis_shape_rejects_robotic_transition_and_overcompression() -> None:
    text = (
        "Technology strategy executive who led AWS modernization execution for monolithic policy administration and insurance platform workloads across regulated cloud migration. "
        "Through that migration discipline, IBM-AWS alliance co-sell motions for financial-services modernization pair with agentic AI platform control-plane architecture and distributed cloud and data execution infrastructure to align partner GTM with governed runtime delivery. "
        "That operating foundation also connects decision-support data models and BI views to reusable offering accelerators packaging cloud, data, and AI modernization patterns for repeatable client pursuits. "
        "In parallel, insurer and regulatory engagement on cloud controls and data security standards keeps partner-led deployment aligned with adoption requirements. "
        "Building on that governance base, platform productization and IP-led revenue growth scale team capacity while expanding operating margins across partner-enabled programs. "
        "AI partnerships and alliance GTM leadership position continued scale of partner-led AI solution architecture across cloud and GSI ecosystems."
    )
    parsed = {
        "resume_display_text": text,
        "claim_ledger": [
            {
                "claim_text": "s1",
                "source_fact_ids": ["reb_insurtech_aws_migration_execution"],
            },
            {
                "claim_text": "s2",
                "source_fact_ids": [
                    "reb_ibm_aws_alliance_partner_cosell_gtm",
                    "reb_unify_agentic_platform_architecture",
                    "reb_unify_distributed_ecosystem_engineering",
                    "reb_ibm_aws_modernization_architecture",
                ],
            },
        ],
    }

    ok, reason = _synthesis_shape_reject_reason(text, parsed, selected_facts=[])

    assert ok is False
    assert "robotic_transition_stack" in reason
    assert "too_many_source_fact_ids" in reason


def test_build_synthesis_repair_user_includes_robotic_transition_guidance() -> None:
    msg = _build_synthesis_repair_user(
        "robotic_transition_stack:3_in_s2_s5; cross_fact_display_conflation:too_many_source_fact_ids_in_one_sentence",
        attempt_index=0,
        prior_word_count=105,
        prior_ledger_rows=6,
    )
    assert "That operating foundation" in msg
    assert "more than three source_fact_ids" in msg


def test_shape_failure_count_increases_with_more_issues() -> None:
    bad = {
        "resume_display_text": "I am bad. Short. Short.",
        "claim_ledger": [],
    }
    n = _shape_failure_count(bad["resume_display_text"], bad, selected_facts=[])
    assert n >= 2


def test_synthesis_repair_sentence_count_note_fires_on_5_sentences() -> None:
    """sentence_count_note must fire when reject reason names wrong sentence count."""
    reject = (
        "resume_display_text must have exactly 6 sentences; found 5 "
        "(legacy 4–5 and 5–6 bands retired)"
    )
    msg = _build_synthesis_repair_user(
        reject,
        attempt_index=0,
        prior_word_count=85,
        prior_ledger_rows=5,
    )
    assert "SENTENCE COUNT HARD FAIL" in msg, (
        "sentence_count_note must fire when reject reason reports found 5 sentences"
    )
    assert "EXACTLY 6" in msg or "exactly 6" in msg, (
        "sentence_count_note must state EXACTLY 6"
    )
    assert "use 5" not in msg.lower(), (
        "No ambiguous 'use 5' guidance when sentence count failed — gate requires exactly 6"
    )


def test_synthesis_repair_evidence_weave_fires_on_sentences_blob() -> None:
    """utilization_note must fire when 'sentences' appears in reject reason."""
    reject = "Output has 5 sentences; executive synthesis requires exactly 6 sentences"
    msg = _build_synthesis_repair_user(
        reject,
        attempt_index=0,
        prior_word_count=85,
        prior_ledger_rows=5,
    )
    assert "EVIDENCE_WEAVE" in msg, (
        "utilization_note must fire when reject reason contains 'sentences'"
    )
    # Ensure the ambiguous fallback is gone
    assert "use 5 when the pool is tighter" not in msg, (
        "Ambiguous 'use 5 when the pool is tighter' must be removed — gate requires exactly 6"
    )


def test_synthesis_repair_no_ambiguous_fallback_when_count_fails() -> None:
    """'Prefer 6 ... use 5 when tighter' phrase must not appear in any sentence-count failure."""
    for reject in [
        "resume_display_text must have exactly 6 sentences; found 4 (legacy 4–5 and 5–6 bands retired)",
        "Output has 5 sentences; executive synthesis requires exactly 6 sentences",
    ]:
        msg = _build_synthesis_repair_user(
            reject,
            attempt_index=1,
            prior_word_count=90,
            prior_ledger_rows=5,
        )
        assert "use 5 when the pool is tighter" not in msg, (
            f"Ambiguous fallback must be absent for reject: {reject!r}"
        )
