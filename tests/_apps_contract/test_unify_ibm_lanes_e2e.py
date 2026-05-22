"""Aggressive in-process E2E for Unify/IBM bullets+narrative (mock L2 + full critical X2 + X3 edges)."""

from __future__ import annotations

import json
from typing import Any

import pytest

from apps_rg.runtime.validators.companion_bullet_finalization import (
    ACCEPTED_FINALIZED_COMPANION_STATUS,
)
from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import (
    assert_critical_gates_pass,
    gate_results_map,
    ibm_bullets_parsed_from_mock,
    ibm_narrative_parsed_from_mock,
    run_ibm_bullets_x2,
    run_ibm_narrative_x2,
    run_unify_bullets_x2,
    run_unify_narrative_x2,
    unify_bullets_parsed_from_mock,
    unify_narrative_parsed_from_mock,
)

FOUR_LANES = ("unify_bullets", "unify_narrative", "ibm_bullets", "ibm_narrative")


@pytest.mark.parametrize("lane", FOUR_LANES)
def test_mock_output_passes_lane_critical_x2(lane: str) -> None:
    if lane == "unify_bullets":
        parsed, allowed = unify_bullets_parsed_from_mock()
        gates = run_unify_bullets_x2(parsed, allowed)
    elif lane == "ibm_bullets":
        parsed, allowed = ibm_bullets_parsed_from_mock()
        gates = run_ibm_bullets_x2(parsed, allowed)
    elif lane == "unify_narrative":
        parsed = unify_narrative_parsed_from_mock()
        gates = run_unify_narrative_x2(parsed)
    else:
        parsed = ibm_narrative_parsed_from_mock()
        gates = run_ibm_narrative_x2(parsed)
    assert_critical_gates_pass(lane, gates)


@pytest.mark.parametrize("lane", ("unify_bullets", "ibm_bullets"))
def test_bullets_mock_has_expected_counts_and_distribution(lane: str) -> None:
    if lane == "unify_bullets":
        parsed, _ = unify_bullets_parsed_from_mock()
        expected_count = 6
        dist = parsed["rewrite_distribution"]
    else:
        parsed, _ = ibm_bullets_parsed_from_mock()
        expected_count = 5
        dist = parsed["rewrite_distribution"]
    assert len(parsed["bullets"]) == expected_count
    assert dist.get("HEAVY") == 0 if lane == "ibm_bullets" else dist.get("HEAVY") == 2
    assert dist.get("total") == expected_count


def test_unify_narrative_two_sentences_fails_exactly_one_gate() -> None:
    parsed = unify_narrative_parsed_from_mock()
    parsed["narrative_sentence"] = "First sentence. Second sentence."
    gates = run_unify_narrative_x2(parsed)
    results = gate_results_map(gates)
    assert results["x2_unify_narrative_exactly_one_sentence"] is False


def test_ibm_narrative_meta_disclaimer_fails_display_gate() -> None:
    parsed = ibm_narrative_parsed_from_mock()
    parsed["narrative_sentence"] = (
        "At IBM, led cloud work without claiming IBM delivered agentic platform products."
    )
    parsed["claim_ledger"] = [
        {"claim_text": parsed["narrative_sentence"], "source_fact_ids": ["bul_ibm_001"]}
    ]
    gates = run_ibm_narrative_x2(parsed)
    results = gate_results_map(gates)
    assert results["x2_ibm_narrative_no_meta_disclaimer_in_display"] is False


def _minimal_section_input_usage_ledger() -> dict[str, Any]:
    return {
        "schema": "section_input_usage_ledger_v1",
        "evidence_boundary": {
            "non_evidence_inputs_used_as_claim_evidence": False,
            "non_evidence_inputs_in_source_fact_ids": False,
        },
        "claim_support_summary": {
            "claims_with_targeting_input_in_source_fact_ids": 0,
            "claims_with_context_input_in_source_fact_ids": 0,
        },
    }


def _model_backed_judge_passes() -> list[dict[str, Any]]:
    return [
        {
            "provider_key": key,
            "evaluator_mode": "MODEL_BACKED",
            "provider_status": "MODEL_BACKED_PASS",
            "pass": True,
            "decisive_failure": False,
            "normalized_score": 5.0,
            "normalized_threshold": 4.0,
        }
        for key in ("gemini_pro", "openai_chatgpt", "anthropic_claude")
    ]


def test_unify_bullets_x3_allow_when_x2_and_judges_pass() -> None:
    from apps_rg.runtime.exit.unify_bullets_x3 import aggregate_x3

    parsed, allowed = unify_bullets_parsed_from_mock()
    gates = run_unify_bullets_x2(parsed, allowed)
    gate_dicts = [g.to_dict() for g in gates if g.pass_]
    display = "\n".join(b["bullet_text"] for b in parsed["bullets"])
    x3 = aggregate_x3(
        resume_display_text=display,
        claim_ledger=parsed["claim_ledger"],
        x2_gates=gate_dicts,
        x1d_judges=_model_backed_judge_passes(),
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=_minimal_section_input_usage_ledger(),
    )
    assert x3.x3_code == "X3_ALLOW"


def test_unify_bullets_x3_blocks_when_critical_x2_fails() -> None:
    from apps_rg.runtime.exit.unify_bullets_x3 import aggregate_x3

    parsed, allowed = unify_bullets_parsed_from_mock()
    gates = run_unify_bullets_x2(parsed, allowed)
    gate_dicts = [g.to_dict() for g in gates]
    display = "\n".join(b["bullet_text"] for b in parsed["bullets"])
    gate_dicts_fail = [
        {**g, "pass": False} if g["gate_id"] == "x2_unify_bullet_count_6" else g for g in gate_dicts
    ]
    x3_block = aggregate_x3(
        resume_display_text=display,
        claim_ledger=parsed["claim_ledger"],
        x2_gates=gate_dicts_fail,
        x1d_judges=_model_backed_judge_passes(),
        runtime_generation_status="REAL_LLM",
        product_quality_status="FAIL",
        section_input_usage_ledger=_minimal_section_input_usage_ledger(),
    )
    assert x3_block.x3_code == "X3_BLOCK"
    assert "x2_unify_bullet_count_6" in x3_block.x2_failed_gates


def test_ibm_narrative_x3_blocks_on_clause_decomposition_failure() -> None:
    from apps_rg.runtime.exit.ibm_narrative_x3 import aggregate_x3

    parsed = ibm_narrative_parsed_from_mock()
    parsed["narrative_sentence"] = (
        "At IBM, led cloud foundations, establishing discipline that supported later production AI leadership."
    )
    parsed["claim_ledger"] = [{"claim_text": parsed["narrative_sentence"], "source_fact_ids": ["bul_ibm_001"]}]
    gates = run_ibm_narrative_x2(parsed, runtime_generation_status="REAL_LLM", companion_aware=True)
    gate_dicts = [g.to_dict() for g in gates]
    x3 = aggregate_x3(
        resume_display_text=parsed["narrative_sentence"],
        claim_ledger=parsed["claim_ledger"],
        x2_gates=gate_dicts,
        x1d_judges=_model_backed_judge_passes(),
        runtime_generation_status="REAL_LLM",
        product_quality_status="FAIL",
        section_input_usage_ledger=_minimal_section_input_usage_ledger(),
    )
    assert x3.x3_code == "X3_BLOCK"
    assert "x2_ibm_narrative_claim_ledger_clause_decomposition" in x3.x2_failed_gates


def test_bullets_to_narrative_chain_unify() -> None:
    bullets_parsed, _allowed = unify_bullets_parsed_from_mock()
    companion_text = "\n".join(
        f"- {b['bullet_id']}: {b['bullet_text']}" for b in bullets_parsed["bullets"]
    )
    narrative_parsed = unify_narrative_parsed_from_mock(companion_text=companion_text)
    gates = run_unify_narrative_x2(
        narrative_parsed,
        runtime_generation_status="REAL_LLM",
        companion_text=companion_text,
        companion_status=ACCEPTED_FINALIZED_COMPANION_STATUS,
    )
    assert_critical_gates_pass("unify_narrative", gates)


def test_bullets_to_narrative_chain_ibm() -> None:
    bullets_parsed, _allowed = ibm_bullets_parsed_from_mock()
    companion_text = "\n".join(
        f"- {b['bullet_id']}: {b['bullet_text']}" for b in bullets_parsed["bullets"]
    )
    narrative_parsed = ibm_narrative_parsed_from_mock(companion_text=companion_text)
    gates = run_ibm_narrative_x2(
        narrative_parsed,
        runtime_generation_status="REAL_LLM",
        companion_text=companion_text,
        companion_status=ACCEPTED_FINALIZED_COMPANION_STATUS,
        companion_aware=True,
    )
    assert_critical_gates_pass("ibm_narrative", gates)


@pytest.mark.parametrize(
    "bad_narrative,forbidden",
    [
        ("without claiming", "without claiming"),
        ("supported later", "supported later"),
        ("without asserting", "without asserting"),
    ],
)
def test_ibm_display_forbidden_phrases_fail_x2(bad_narrative: str, forbidden: str) -> None:
    parsed = ibm_narrative_parsed_from_mock()
    parsed["narrative_sentence"] = f"At IBM, led cloud foundations {bad_narrative} agentic products."
    parsed["claim_ledger"] = [
        {"claim_text": parsed["narrative_sentence"], "source_fact_ids": ["bul_ibm_001"]}
    ]
    gates = run_ibm_narrative_x2(parsed)
    results = gate_results_map(gates)
    meta_fail = not results.get("x2_ibm_narrative_no_meta_disclaimer_in_display", True)
    clause_fail = not results.get("x2_ibm_narrative_claim_ledger_clause_decomposition", True)
    assert meta_fail or clause_fail, f"expected failure for {forbidden!r}"


def test_unify_bullets_structural_coverage_matches_ledger() -> None:
    from apps_rg.runtime.validators.unify_bullets_x2 import (
        build_unify_bullets_text_claim_coverage,
        check_unify_bullets_text_claim_coverage_integrity,
    )

    parsed, allowed = unify_bullets_parsed_from_mock()
    cov = build_unify_bullets_text_claim_coverage(
        parsed["bullets"], parsed["claim_ledger"], allowed
    )
    ok, reason = check_unify_bullets_text_claim_coverage_integrity(
        parsed["bullets"], parsed["claim_ledger"], cov, allowed
    )
    assert ok is True
    assert reason is None
    parsed["text_claim_coverage"] = cov
    gates = run_unify_bullets_x2(parsed, allowed)
    assert gate_results_map(gates)["x2_text_claim_coverage_integrity"] is True
