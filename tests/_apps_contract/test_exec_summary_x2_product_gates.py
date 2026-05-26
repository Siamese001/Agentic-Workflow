"""Deterministic executive_summary product gates (colon stitch, meta filler, coverage)."""
from __future__ import annotations

import json

from apps_rg.runtime.exit.executive_summary_x3 import NO_JUDGE_ROWS_EMITTED, aggregate_x3
from tests._apps_contract.fixtures import exec_summary_brown_20260526_183905 as brown_rca
from apps_rg.runtime.validators.executive_summary_x2 import (
    build_sentence_claim_coverage,
    check_claim_coverage_accounting,
    check_claim_field_maps_to_display_sentence,
    check_claim_ledger_row_count_matches_sentence_count,
    check_exec_summary_meta_filler_patterns,
    check_material_clause_coverage,
    check_north_star_style_example_echo_unsupported,
    check_raw_json_no_selected_fact_plan_echo,
    check_resume_display_colon_space_discipline,
    check_exec_summary_sentence_count_6,
    check_self_check_claim_ledger_consistent,
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
        "The executive thread ties platform modernization to governed agentic delivery at scale. "
        "Quantitative depth supports regulated program delivery when facts support that theme. "
        "Governed runtime delivery stays audit-ready without weakening commercial velocity."
    )
    assert check_resume_display_colon_space_discipline(good)[0] is True
    assert check_exec_summary_meta_filler_patterns(good)[0] is True
    assert check_exec_summary_sentence_count_6(good)[0] is True
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
        "The executive thread ties platform modernization to governed agentic delivery at scale. "
        "Quantitative depth supports regulated program delivery when facts support that theme. "
        "Governed runtime delivery stays audit-ready without weakening commercial velocity."
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
        {
            "claim_text": (
                "platform modernization governed agentic delivery at scale executive thread"
            ),
            "source_fact_ids": ["fact_test_001"],
        },
        {
            "claim_text": (
                "Quantitative depth supports regulated program delivery when facts support that theme"
            ),
            "source_fact_ids": ["fact_test_001"],
        },
        {
            "claim_text": (
                "Governed runtime delivery stays audit-ready without weakening commercial velocity"
            ),
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


def test_sentence_coverage_matches_display_claim_not_only_fact_wording():
    """Brown S5 regression: display paraphrase must bind via ledger ``claim``, not fact ``claim_text``."""
    allowed = {"fact_quant_hpc_003"}
    sentence = (
        "Quantitative rigor from capital and risk analytics practice sharpens platform "
        "investment and stress-analytics decisions for regulated program scale."
    )
    ledger = [
        {
            "claim": sentence,
            "claim_text": (
                "Built advanced quantitative foundation through derivatives pricing, "
                "multi-Greek hedging, capital modeling, and FSA credential across "
                "Towers Perrin, ING, and Aetna."
            ),
            "source_fact_ids": ["fact_quant_hpc_003"],
        },
    ]
    cov = build_sentence_claim_coverage(sentence, ledger, allowed)
    assert cov["overall_pass"] is True
    row = cov["sentences"][0]
    assert row["sentence_pass"] is True
    assert row["material_claims"][0]["support_status"] == "SUPPORTED"


def test_sentence_coverage_prefers_display_claim_over_fact_token_collision():
    """Thesis sentence must not pick a platform row via shared tokens in ``claim_text`` only."""
    allowed = {"fact_certs_001", "fact_engineering_platform_001"}
    thesis = (
        "Enterprise technology leader aligning governed AI platforms, regulatory lineage, "
        "and commercialization into one IT strategy and innovation agenda for decentralized "
        "regulated enterprises."
    )
    ledger = [
        {
            "claim": thesis,
            "claim_text": (
                "Holds AWS Certified Machine Learning Engineer - Associate, AWS Certified "
                "Solutions Architect - Professional, Databricks Lakehouse Fundamentals, and "
                "Fellow of the Society of Actuaries credentials."
            ),
            "source_fact_ids": ["fact_certs_001"],
        },
        {
            "claim": (
                "Designs and operates platform runtime with deterministic controls and "
                "traceable execution so innovation scales without sacrificing validation-ready delivery."
            ),
            "claim_text": (
                "Designed and operationalized governed agentic AI platform capabilities "
                "for regulated enterprise workflows, including deterministic routing."
            ),
            "source_fact_ids": ["fact_engineering_platform_001"],
        },
    ]
    cov = build_sentence_claim_coverage(thesis, ledger, allowed)
    assert cov["overall_pass"] is True
    assert len(cov["sentences"][0]["material_claims"]) == 1
    assert cov["sentences"][0]["material_claims"][0]["source_fact_ids"] == ["fact_certs_001"]


def test_claim_ledger_row_count_must_match_sentence_count():
    resume = (
        "First sentence about platform delivery with measurable outcomes. "
        "Second sentence about governance discipline across programs. "
        "Third sentence about commercial adoption and operating cadence. "
        "Fourth sentence about quantitative depth across regulated work. "
        "Fifth sentence about architecture standards and innovation programs. "
        "Sixth sentence about lineage discipline without weakening velocity."
    )
    ledger = [{"claim": "Only one row.", "claim_text": "Fact one.", "source_fact_ids": ["f1"]}]
    ok, reason = check_claim_ledger_row_count_matches_sentence_count(resume, ledger)
    assert ok is False
    assert reason is not None
    assert "display_sentences=6" in reason
    assert "claim_ledger_rows=1" in reason


def test_self_check_claim_ledger_flag_requires_coverage_pass():
    resume = "One supported sentence about platform modernization with outcomes."
    ledger = [
        {
            "claim": resume,
            "claim_text": "Platform modernization with measurable outcomes.",
            "source_fact_ids": ["f1"],
        },
    ]
    cov = build_sentence_claim_coverage(resume, ledger, {"f1"})
    parsed = {
        "self_check": {"every_material_claim_in_claim_ledger": True},
    }
    ok, reason = check_self_check_claim_ledger_consistent(parsed, cov)
    assert ok is True

    cov_fail = {
        "sentences": [{"sentence_pass": False}],
        "overall_pass": False,
    }
    ok2, reason2 = check_self_check_claim_ledger_consistent(parsed, cov_fail)
    assert ok2 is False
    assert reason2 is not None
    assert "every_material_claim_in_claim_ledger" in reason2


def test_claim_field_must_appear_in_resume_display():
    resume = "Engineering executive delivers platform outcomes across regulated programs."
    ledger = [
        {
            "claim": "Completely unrelated display line not present in resume body at all.",
            "claim_text": "Unrelated fact wording with no token overlap.",
            "source_fact_ids": ["f1"],
        },
    ]
    ok, reason = check_claim_field_maps_to_display_sentence(resume, ledger)
    assert ok is False
    assert reason is not None
    assert "row_1" in reason


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
    assert x3.x1d_evaluator_mode == NO_JUDGE_ROWS_EMITTED


def _coverage_sentence(coverage: dict, fragment: str) -> dict:
    matches = [row for row in coverage.get("sentences", []) if fragment in row.get("sentence_text", "")]
    assert len(matches) == 1, f"expected one sentence match for {fragment!r}, got {len(matches)}"
    return matches[0]


def test_brown_rca_20260526_s5_paraphrase_supported_s6_unsupported():
    """W0+W3: Brown S5 binds via display ``claim``; S6 has no ledger row (RCA exec_summary_20260526_183905)."""
    assert brown_rca.SOURCE_RUN_ID == "exec_summary_20260526_183905"
    allowed = set(brown_rca.BROWN_ALLOWED_FACT_IDS)
    cov = build_sentence_claim_coverage(
        brown_rca.BROWN_RESUME_DISPLAY_TEXT,
        brown_rca.BROWN_CLAIM_LEDGER,
        allowed,
    )
    s5 = _coverage_sentence(cov, brown_rca.BROWN_S5_FRAGMENT)
    assert s5["sentence_pass"] is True
    assert s5["material_claims"][0]["support_status"] == "SUPPORTED"
    assert s5["material_claims"][0]["source_fact_ids"] == ["fact_quant_hpc_003"]

    s6 = _coverage_sentence(cov, brown_rca.BROWN_S6_FRAGMENT)
    assert s6["sentence_pass"] is False
    assert any(
        c.get("support_status") == "UNSUPPORTED" for c in s6.get("material_claims", [])
    )
    assert cov["overall_pass"] is False


def test_brown_rca_20260526_w1_row_count_and_self_check_gates_fail():
    """W1: six display sentences vs five ledger rows; honor-system self_check contradicted."""
    allowed = set(brown_rca.BROWN_ALLOWED_FACT_IDS)
    cov = build_sentence_claim_coverage(
        brown_rca.BROWN_RESUME_DISPLAY_TEXT,
        brown_rca.BROWN_CLAIM_LEDGER,
        allowed,
    )
    row_ok, row_reason = check_claim_ledger_row_count_matches_sentence_count(
        brown_rca.BROWN_RESUME_DISPLAY_TEXT,
        brown_rca.BROWN_CLAIM_LEDGER,
    )
    assert row_ok is False
    assert row_reason is not None
    assert "display_sentences=6" in row_reason
    assert "claim_ledger_rows=5" in row_reason

    sc_ok, sc_reason = check_self_check_claim_ledger_consistent(
        {"self_check": brown_rca.BROWN_SELF_CHECK},
        cov,
    )
    assert sc_ok is False
    assert sc_reason is not None

    map_ok, map_reason = check_claim_field_maps_to_display_sentence(
        brown_rca.BROWN_RESUME_DISPLAY_TEXT,
        brown_rca.BROWN_CLAIM_LEDGER,
    )
    assert map_ok is True, map_reason


def test_brown_rca_20260526_run_x2_emits_w1_gates(tmp_path):
    """W3 integration: strategy-lane ``run_x2_gates`` surfaces W1 gate IDs on Brown shape."""
    from apps_rg.runtime.validators.executive_summary_x2 import REQUIRED_ARTIFACTS, run_x2_gates

    adir = tmp_path / "brown_proof"
    adir.mkdir()
    for name in REQUIRED_ARTIFACTS:
        (adir / name).write_text("{}\n", encoding="utf-8")

    allowed = set(brown_rca.BROWN_ALLOWED_FACT_IDS)
    cov = build_sentence_claim_coverage(
        brown_rca.BROWN_RESUME_DISPLAY_TEXT,
        brown_rca.BROWN_CLAIM_LEDGER,
        allowed,
    )
    parsed = {
        "resume_display_text": brown_rca.BROWN_RESUME_DISPLAY_TEXT,
        "claim_ledger": brown_rca.BROWN_CLAIM_LEDGER,
        "self_check": dict(brown_rca.BROWN_SELF_CHECK),
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [],
        "text_claim_coverage": cov,
    }
    gates = run_x2_gates(
        resume_display_text=brown_rca.BROWN_RESUME_DISPLAY_TEXT,
        parsed_output=parsed,
        claim_ledger=brown_rca.BROWN_CLAIM_LEDGER,
        text_claim_coverage=cov,
        allowed_fact_ids=allowed,
        target_company=brown_rca.BROWN_TARGET_COMPANY,
        target_role=brown_rca.BROWN_TARGET_ROLE,
        jd_text="IT strategy innovation decentralized regulated",
        temperature=0.45,
        runtime_generation_status="REAL_LLM",
        monolithic_prompt_invoked=False,
        strategic_tailor_v1_invoked=False,
        artifacts_dir=adir,
        raw_output=json.dumps(parsed),
    )
    gate_map = {g.gate_id: g.pass_ for g in gates}
    assert gate_map["x2_claim_ledger_row_count_matches_sentence_count"] is False
    assert gate_map["x2_self_check_claim_ledger_consistent"] is False
    assert gate_map["x2_sentence_coverage_pass"] is False
    assert gate_map["x2_unsupported_claim_zero"] is False


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
    assert "x2_exec_summary_sentence_count_6" in text
    assert "x2_exec_summary_no_credential_dump" in text
    assert "x2_no_selected_fact_plan_model_echo" in text
    assert "x2_north_star_style_echo_unsupported_zero" in text
    assert "x2_claim_ledger_row_count_matches_sentence_count" in text
    assert "x2_self_check_claim_ledger_consistent" in text
    assert "x2_claim_field_maps_to_display_sentence" in text
