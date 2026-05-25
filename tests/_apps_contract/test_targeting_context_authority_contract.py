"""Contract tests: generation/judge targeting material parity (apps_rg)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.targeting_context_authority import (
    GenerationMaterialContext,
    JudgeMaterialContext,
    TargetingAuthorityError,
    evaluate_targeting_parity,
    extract_material_targeting_from_compiled_prompt,
    generation_material_context_from_compiled_prompt,
    judge_material_context_from_packet,
    material_targeting_digest,
    merge_targeting_parity_into_usage_ledger,
    require_material_targeting_bundle,
    store_material_targeting_bundle,
    MaterialTargetingBundle,
)
from apps_rg.runtime.judges.executive_summary_judge_packet import build_executive_summary_judge_packet

REPO = Path(__file__).resolve().parents[2]


def _sample_compiled(jd: str, briefing: str) -> str:
    body = (
        f"TARGET_TITLE (positioning only - NOT PROOF): SVP\n"
        f"TARGET_COMPANY (targeting only - NOT PROOF): Acme\n"
        f"JD_TEXT (targeting only - NOT PROOF): {jd}\n"
        f"BRIEFING (targeting only - NOT PROOF): {briefing}\n"
        "Use JD_TEXT and BRIEFING to rank and frame evidenced themes only - never as proof. "
        "jd_alignment: targeting_only=true; jd_used_as_proof=false; briefing_used_as_proof=false.\n"
    )
    return json.dumps([{"role": "user", "content": body}], ensure_ascii=False)


def test_parity_fails_when_judge_richer_than_generation() -> None:
    gen = GenerationMaterialContext(
        jd_text_material="jd-short",
        briefing_text_material="brief692",
        generation_material_digest=material_targeting_digest("jd-short", "brief692"),
    )
    judge = JudgeMaterialContext(
        jd_text_material="jd-short",
        briefing_text_material="x" * 15210,
        judge_material_digest=material_targeting_digest("jd-short", "x" * 15210),
    )
    receipt = evaluate_targeting_parity(generation=gen, judge=judge, bundle=None)
    assert receipt["parity_match"] is False
    assert receipt["substantive_jd_fit_certification_allowed"] is False
    assert receipt["generation_briefing_chars"] == len("brief692")
    assert receipt["judge_briefing_chars"] == 15210


def test_parity_passes_when_identical_material_context() -> None:
    jd, br = "enterprise AI", "regulated enterprise " * 200
    digest = material_targeting_digest(jd, br)
    gen = GenerationMaterialContext(jd, br, digest)
    judge = JudgeMaterialContext(jd, br, digest)
    receipt = evaluate_targeting_parity(generation=gen, judge=judge, bundle=None)
    assert receipt["parity_match"] is True
    assert receipt["generation_material_digest"] == receipt["judge_material_digest"]


def test_generation_material_extracted_from_compiled_prompt() -> None:
    jd, br = "role jd line", "brief line two"
    compiled = _sample_compiled(jd, br)
    gen = generation_material_context_from_compiled_prompt(compiled)
    assert gen.jd_text_material == jd
    assert gen.briefing_text_material == br
    assert gen.generation_material_digest == material_targeting_digest(jd, br)


def test_ledger_briefing_hash_is_generation_digest_not_cli() -> None:
    gen = generation_material_context_from_compiled_prompt(
        _sample_compiled("jd", "L2-only-brief")
    )
    judge = JudgeMaterialContext("jd", "CLI-15k-briefing-not-seen-by-L2", material_targeting_digest("jd", "CLI-15k-briefing-not-seen-by-L2"))
    parity = evaluate_targeting_parity(generation=gen, judge=judge, bundle=None)
    doc = {"schema": "section_input_usage_ledger_v1", "input_refs": {}, "required_input_usage": {}}
    merged = merge_targeting_parity_into_usage_ledger(doc, parity)
    assert merged["input_refs"]["briefing_hash"] == gen.generation_material_digest
    assert merged["parity_match"] is False
    assert merged["required_input_usage"]["briefing_research"]["material_delivered_to_l2"] is True


def test_require_bundle_rejects_missing_frozen_bundle() -> None:
    with pytest.raises(TargetingAuthorityError):
        require_material_targeting_bundle({})


def test_judge_packet_targeting_matches_generation_material_not_raw_cli() -> None:
    jd, br = "frozen-jd", "frozen-brief-4k"
    gen = generation_material_context_from_compiled_prompt(_sample_compiled(jd, br))
    packet = build_executive_summary_judge_packet(
        resume_display_text="Six sentences of executive summary.",
        claim_ledger=[],
        allowed_fact_packet=[],
        allowed_fact_ids=set(),
        target_title="SVP",
        target_company="Acme",
        jd_text=gen.jd_text_material,
        briefing_text=gen.briefing_text_material,
        parsed_output={"executive_summary": "text"},
    )
    judge_ctx = judge_material_context_from_packet(packet)
    assert judge_ctx.judge_material_digest == gen.generation_material_digest
    tc = packet["targeting_context"]
    assert tc["jd_text"] == jd
    assert tc["briefing"] == br
    assert "CLI-15k" not in tc["briefing"]


def test_raw_cli_briefing_must_not_equal_judge_digest_when_l2_narrowed() -> None:
    """Regression: 140149 had judge digest from 15k CLI vs 692-char L2 brief."""
    l2_brief = "x" * 692
    cli_brief = "y" * 15210
    gen = generation_material_context_from_compiled_prompt(_sample_compiled("jd", l2_brief))
    judge_rich = JudgeMaterialContext("jd", cli_brief, material_targeting_digest("jd", cli_brief))
    assert judge_rich.judge_material_digest != gen.generation_material_digest


def test_x3_parity_violation_codes_from_aggregate() -> None:
    from apps_rg.runtime.exit.executive_summary_x3 import aggregate_x3

    ledger = {
        "schema": "section_input_usage_ledger_v1",
        "parity_match": False,
        "generation_material_digest": "aaa",
        "judge_material_digest": "bbb",
        "targeting_context_parity": {"parity_match": False},
        "evidence_boundary": {
            "non_evidence_inputs_used_as_claim_evidence": False,
            "non_evidence_inputs_in_source_fact_ids": False,
        },
        "claim_support_summary": {
            "claims_with_targeting_input_in_source_fact_ids": 0,
            "claims_with_context_input_in_source_fact_ids": 0,
        },
    }
    x3_review = aggregate_x3(
        resume_display_text="summary",
        claim_ledger=[],
        x2_gates=[{"gate_id": "x2_ok", "pass": True}],
        x1d_judges=[{"provider_key": "openai", "evaluator_mode": "MODEL_BACKED", "pass": True, "provider_status": "MODEL_BACKED_PASS"}],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=ledger,
    )
    assert x3_review.x3_code == "X3_REVIEW_CONTEXT_PARITY_VIOLATION"
    assert x3_review.proceed_to_runtime is False

    x3_block = aggregate_x3(
        resume_display_text="summary",
        claim_ledger=[],
        x2_gates=[{"gate_id": "x2_fail", "pass": False}],
        x1d_judges=[{"provider_key": "openai", "evaluator_mode": "MODEL_BACKED", "pass": True, "provider_status": "MODEL_BACKED_PASS"}],
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=ledger,
    )
    assert x3_block.x3_code == "X3_BLOCK_CONTEXT_PARITY_VIOLATION"
