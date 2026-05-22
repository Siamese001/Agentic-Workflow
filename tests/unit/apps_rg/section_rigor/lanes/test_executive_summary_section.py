"""Executive summary lane nuance: 4–5 sentences, style, paragraph bounds, prompt authority."""

from __future__ import annotations

from pathlib import Path

from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_no_mechanism_inventory,
    check_exec_summary_paragraph_max_words,
    check_prompt_template_authority,
    run_x2_gates,
)

EXEC_SUMMARY_CRITICAL_GATES = frozenset(
    {
        "x2_exec_summary_sentence_count_4_5",
        "x2_exec_summary_paragraph_max_words",
        "x2_exec_summary_jd_alignment_proof_flags",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_first_person_zero",
        "x2_em_dash_count_zero",
        "x2_exec_summary_no_mechanism_inventory",
        "x2_exec_summary_no_credential_dump",
        "x2_exec_summary_prompt_template_authority",
    }
)


def _jd_alignment() -> dict:
    return {
        "targeting_only": True,
        "jd_used_as_proof": False,
        "briefing_used_as_proof": False,
        "companion_context_used_as_proof": False,
    }


def _four_sentences() -> str:
    return (
        "Engineering executive builds governed agentic AI platforms for regulated enterprise delivery. "
        "The leader scales deterministic routing, orchestration, and policy-gated execution across programs. "
        "Platform lifecycle work ties architecture decisions to commercial adoption and operating discipline. "
        "Prior roles show measurable delivery outcomes grounded in selected executive facts."
    )


def test_paragraph_max_words_fails_when_over_cap() -> None:
    long_text = " ".join(["word"] * 221)
    ok, reason = check_exec_summary_paragraph_max_words(long_text, parsed_output={})
    assert ok is False
    assert reason is not None and "exceeds maximum" in reason


def test_paragraph_max_words_passes_for_short_four_sentence_paragraph() -> None:
    short = (
        "Engineering executive builds governed platforms. "
        "Leader scales routing and orchestration. "
        "Lifecycle work ties architecture to adoption. "
        "Outcomes stay grounded in facts."
    )
    ok, _ = check_exec_summary_paragraph_max_words(short, parsed_output={})
    assert ok is True


def test_mechanism_inventory_gate_fires_on_dense_stack() -> None:
    bad = (
        "Engineering executive builds governed platforms. "
        "The leader delivers deterministic routing, multi-agent orchestration, GraphRAG retrieval, "
        "sandboxed execution, policy gating, validation controls, and replayable traces. "
        "Platform lifecycle work spans architecture and operating model design. "
        "Outcomes stay grounded in selected executive facts."
    )
    ok, _ = check_exec_summary_no_mechanism_inventory(bad)
    assert ok is False


def test_first_person_and_em_dash_fail_style_gates() -> None:
    text = (
        "I build governed agentic AI platforms for enterprise delivery—spanning routing and orchestration. "
        "We scale platform lifecycle and commercial adoption across programs. "
        "Delivery outcomes remain grounded in selected executive facts. "
        "Prior roles show measurable outcomes grounded in selected executive facts."
    )
    gates = run_x2_gates(
        resume_display_text=text,
        parsed_output={"resume_display_text": text, "jd_alignment": _jd_alignment()},
        claim_ledger=[{"claim_text": "platform delivery", "source_fact_ids": ["bul_unify_001"]}],
        text_claim_coverage={"sentences": [], "overall_pass": False},
        allowed_fact_ids={"bul_unify_001"},
        target_company="Synthetic Enterprise Corp.",
        jd_text="enterprise AI",
        temperature=0.45,
        runtime_generation_status="MOCKED",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        x1d_judges=[],
    )
    failed = {g.gate_id for g in gates if not g.pass_}
    assert "x2_first_person_zero" in failed
    assert "x2_em_dash_count_zero" in failed


def test_prompt_template_authority_requires_trace(tmp_path: Path) -> None:
    ok, _ = check_prompt_template_authority(tmp_path)
    assert ok is False
