"""Deterministic executive_summary product gates (colon stitch, meta filler, coverage)."""
from __future__ import annotations

from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3
from apps_rg.runtime.validators.executive_summary_x2 import (
    build_sentence_claim_coverage,
    check_claim_coverage_accounting,
    check_exec_summary_meta_filler_patterns,
    check_material_clause_coverage,
    check_north_star_style_example_echo_unsupported,
    check_raw_json_no_selected_fact_plan_echo,
    check_resume_display_colon_space_discipline,
    check_exec_summary_sentence_count_4_5,
    check_synthesis_quality,
)


def test_colon_stitched_label_fails_colon_gate():
    bad = (
        "Enterprise Agentic AI Platform Architecture: engineering executive delivers governed runtime controls "
        "for regulated programs."
    )
    ok, reason = check_resume_display_colon_space_discipline(bad)
    assert ok is False
    assert reason is not None


def test_scope_described_selected_facts_fails_meta_gate():
    bad = "Engineering executive delivers outcomes across the scope described in selected facts."
    ok, reason = check_exec_summary_meta_filler_patterns(bad)
    assert ok is False
    assert reason is not None


def test_active_voice_governance_phrase_fails_meta_gate():
    bad = (
        "Engineering executive leads platform delivery with active-voice delivery and governance discipline "
        "for enterprise stakeholders."
    )
    ok, reason = check_exec_summary_meta_filler_patterns(bad)
    assert ok is False
    assert reason is not None


def test_this_summary_and_candidate_fail_meta_gate():
    for bad in (
        "This summary highlights platform delivery for senior stakeholders.",
        "The candidate operationalizes AI platforms with measurable outcomes.",
    ):
        ok, reason = check_exec_summary_meta_filler_patterns(bad)
        assert ok is False, reason


def test_valid_synthesis_passes_shape_and_meta_gates():
    good = (
        "Engineering executive builds governed AI platforms and deterministic runtime controls for enterprise "
        "delivery with traceable execution and policy-aware behavior. "
        "The role combines architecture leadership with reliability engineering and platform modernization "
        "across regulated enterprise programs. "
        "Delivery cycles tightened as teams adopted repeatable production controls without weakening audit posture. "
        "The executive thread ties platform modernization to governed agentic delivery at scale."
    )
    assert check_resume_display_colon_space_discipline(good)[0] is True
    assert check_exec_summary_meta_filler_patterns(good)[0] is True
    assert check_exec_summary_sentence_count_4_5(good)[0] is True
    assert check_synthesis_quality(good)[0] is True


def test_valid_synthesis_coverage_and_material_clauses():
    allowed = {"fact_test_001"}
    selected_facts = [
        {
            "fact_id": "fact_test_001",
            "claim_text": "Engineering executive builds platforms and drives delivery in regulated enterprises.",
        }
    ]
    good = (
        "Engineering executive builds governed AI platforms and deterministic runtime controls for enterprise "
        "delivery with traceable execution and policy-aware behavior. "
        "The role combines architecture leadership with reliability engineering and platform modernization "
        "across regulated enterprise programs. "
        "Delivery cycles tightened as teams adopted repeatable production controls without weakening audit posture. "
        "The executive thread ties platform modernization to governed agentic delivery at scale."
    )
    ledger = [
        {
            "claim_text": (
                "Engineering executive builds governed AI platforms enterprise delivery traceable execution "
                "policy-aware behavior"
            ),
            "source_fact_ids": ["fact_test_001"],
        },
        {
            "claim_text": (
                "architecture leadership reliability engineering platform modernization regulated enterprise programs"
            ),
            "source_fact_ids": ["fact_test_001"],
        },
        {
            "claim_text": "delivery cycles repeatable production controls audit posture",
            "source_fact_ids": ["fact_test_001"],
        },
    ]
    cov = build_sentence_claim_coverage(good, ledger, allowed)
    assert cov["overall_pass"] is True
    assert check_material_clause_coverage(good, cov, selected_facts)[0] is True
    parsed = {
        "resume_display_text": good,
        "selected_fact_plan": {"facts": []},
        "claim_ledger": ledger,
        "jd_alignment": {},
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
        "text_claim_coverage": cov,
    }
    assert check_claim_coverage_accounting(good, parsed, cov, ledger)[0] is True


def test_claim_ledger_cannot_hide_unsupported_display_sentence():
    allowed = {"f1"}
    resume = (
        "Engineering executive delivers platform modernization with measurable outcomes. "
        "This unsupported sentence is not backed by any claim row."
    )
    ledger = [
        {
            "claim_text": "Engineering executive platform modernization measurable outcomes",
            "source_fact_ids": ["f1"],
        },
    ]
    cov = build_sentence_claim_coverage(resume, ledger, allowed)
    assert cov["overall_pass"] is False


def test_x3_blocks_when_exec_summary_x2_gate_fails():
    x2 = [
        {"gate_id": "x2_exec_summary_colon_stitch_zero", "pass": False},
        {"gate_id": "x2_schema_valid", "pass": True},
    ]
    x3 = aggregate_x3(
        resume_display_text="x",
        claim_ledger=[],
        x2_gates=x2,
        x1d_judges=[],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
    )
    assert x3.x3_code == "X3_BLOCK"
    assert "x2_exec_summary_colon_stitch_zero" in x3.x2_failed_gates


def test_sentence_stacked_user_example_fails_synthesis_gate():
    bad = (
        "Engineering executive specializing in governed agentic AI platforms. "
        "Built deterministic routing. Built GraphRAG retrieval. Built telemetry instrumentation. "
        "Reduced deployment cycles."
    )
    ok, reason = check_synthesis_quality(bad)
    assert ok is False
    assert reason


def test_north_star_style_echo_without_selected_facts_fails():
    facts = [{"fact_id": "a", "claim_text": "Led platform work."}]
    bad = "Engineering executive with productized AI revenue and Fellow of the Society of Actuaries."
    ok, reason = check_north_star_style_example_echo_unsupported(bad, facts)
    assert ok is False
    assert reason


def test_raw_json_with_selected_fact_plan_fails_model_echo_gate():
    raw = '{"resume_display_text":"x","selected_fact_plan":{},"claim_ledger":[]}'
    ok, reason = check_raw_json_no_selected_fact_plan_echo(raw)
    assert ok is False
    assert reason


def test_x2_registers_harmonization_gate_ids():
    from pathlib import Path

    p = Path(__file__).resolve().parents[2] / "apps_rg" / "runtime" / "validators" / "executive_summary_x2.py"
    text = p.read_text(encoding="utf-8")
    assert "x2_exec_summary_sentence_count_4_5" in text
    assert "x2_exec_summary_no_credential_dump" in text
    assert "x2_no_selected_fact_plan_model_echo" in text
    assert "x2_north_star_style_echo_unsupported_zero" in text
