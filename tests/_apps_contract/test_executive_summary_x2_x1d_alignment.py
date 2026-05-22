"""E2E alignment: X2 product gates, judge packet snapshot, and X3 aggregate policy."""

from __future__ import annotations

from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3
from apps_rg.runtime.judges.executive_summary_judge_packet import (
    build_deterministic_gate_summary,
    build_executive_summary_judge_packet,
    reconcile_grade_only_judge_result,
)
from apps_rg.runtime.validators.executive_summary_x2 import (
    check_exec_summary_meta_filler_patterns,
    check_exec_summary_no_credential_dump,
    check_exec_summary_no_mechanism_inventory,
    check_exec_summary_sentence_count_4_5,
)


def _good_four_sentence_summary() -> str:
    return (
        "Engineering executive building governed agentic AI platforms for regulated enterprise delivery "
        "with traceable execution, commercial discipline, and accountable operating cadence across "
        "large programs. "
        "The platform generated proof-backed revenue and margin outcomes while scaling engineering "
        "delivery across enterprise programs and cross-functional product portfolios. "
        "Implementation of Basel III and CCAR data lineage frameworks reduced regulatory reporting errors "
        "and improved audit readiness for risk and finance stakeholders. "
        "Re-architected risk analytics with containerized microservices achieved faster calculations, "
        "real-time stress testing, and more reliable decision support for senior leadership."
    )


def test_meta_filler_rejects_this_individual() -> None:
    bad = (
        "An experienced leader in regulated enterprise workflows, this individual has designed "
        "governed agentic AI platform capabilities."
    )
    ok, reason = check_exec_summary_meta_filler_patterns(bad)
    assert ok is False
    assert reason and "this individual" in reason.lower()


def test_x2_product_gates_pass_on_aligned_candidate() -> None:
    text = _good_four_sentence_summary()
    assert check_exec_summary_sentence_count_4_5(text)[0]
    assert check_exec_summary_no_credential_dump(text)[0]
    assert check_exec_summary_no_mechanism_inventory(text)[0]
    assert check_exec_summary_meta_filler_patterns(text)[0]


def test_judge_packet_gate_summary_matches_product_gates() -> None:
    text = _good_four_sentence_summary()
    ledger = [
        {
            "claim_text": "Governed agentic AI platform delivery.",
            "source_fact_ids": ["fact_engineering_platform_001"],
        }
    ]
    summary = build_deterministic_gate_summary(
        resume_display_text=text,
        parsed_output={"resume_display_text": text},
        claim_ledger=ledger,
        allowed_fact_ids={"fact_engineering_platform_001"},
    )
    assert summary["x2_exec_summary_no_credential_dump"]["pass"] is True
    assert summary["x2_exec_summary_no_mechanism_inventory"]["pass"] is True
    assert summary["x2_exec_summary_sentence_count_4_5"]["pass"] is True
    assert "x2_exec_summary_evidence_utilization" in summary
    assert "x2_exec_summary_srfs_density_word_count" not in summary
    assert "x2_exec_summary_srfs_sentence_count_4_5" not in summary
    assert "x2_exec_summary_srfs_sentence_responsibility_shape" not in summary


def test_reconcile_clears_decisive_failure_on_retired_arc_when_gates_pass() -> None:
    gates = {
        "x2_exec_summary_no_credential_dump": {"pass": True, "detail": "ok"},
        "x2_exec_summary_sentence_count_4_5": {"pass": True, "detail": "ok"},
    }
    raw = {
        "score_scale": "0_to_5",
        "score": 1.2,
        "threshold": 4.0,
        "pass": False,
        "decisive_failure": True,
        "findings": ["Missing S5 credibility sentence and S2 mechanism-only violation."],
        "cited_sentence_indexes": [0, 1],
        "remediation_suggestions": [],
    }
    out = reconcile_grade_only_judge_result(raw, gates)
    assert out["decisive_failure"] is False
    assert float(out["score"]) >= 4.0


def test_x3_allow_when_x2_pass_and_all_judges_model_backed_pass() -> None:
    judges = [
        {
            "provider_key": "gemini_pro",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "provider_blocked": False,
            "normalized_score": 0.85,
            "normalized_threshold": 0.8,
        },
        {
            "provider_key": "openai_chatgpt",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "provider_blocked": False,
            "normalized_score": 0.9,
            "normalized_threshold": 0.8,
        },
        {
            "provider_key": "anthropic_claude",
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "provider_blocked": False,
            "normalized_score": 0.82,
            "normalized_threshold": 0.8,
        },
    ]
    x3 = aggregate_x3(
        resume_display_text=_good_four_sentence_summary(),
        claim_ledger=[],
        x2_gates=[{"gate_id": "x2_exec_summary_no_credential_dump", "pass": True}],
        x1d_judges=judges,
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger={
            "schema": "section_input_usage_ledger_v1",
            "evidence_boundary": {
                "non_evidence_inputs_used_as_claim_evidence": False,
                "non_evidence_inputs_in_source_fact_ids": False,
            },
            "claim_support_summary": {
                "claims_with_targeting_input_in_source_fact_ids": 0,
                "claims_with_context_input_in_source_fact_ids": 0,
            },
        },
    )
    assert x3.x3_code == "X3_ALLOW"


def test_build_judge_packet_includes_reconcilable_gate_summary() -> None:
    text = _good_four_sentence_summary()
    packet = build_executive_summary_judge_packet(
        resume_display_text=text,
        claim_ledger=[
            {
                "claim_text": "Platform delivery.",
                "source_fact_ids": ["fact_engineering_platform_001"],
            }
        ],
        allowed_fact_packet=[
            {
                "fact_id": "fact_engineering_platform_001",
                "claim_text": "Designed governed agentic AI platform capabilities.",
            }
        ],
        allowed_fact_ids={"fact_engineering_platform_001"},
        target_title="SVP Engineering",
        target_company="Acme",
        jd_text="JD targeting only.",
        briefing_text="Briefing context only.",
        parsed_output={"resume_display_text": text},
    )
    assert packet["deterministic_gate_summary"]["x2_exec_summary_no_mechanism_inventory"]["pass"] is True
