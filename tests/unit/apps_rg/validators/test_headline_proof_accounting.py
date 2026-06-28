"""REAL_LLM headline proof-accounting gates: receipt denial, raw ledger schema, self_check truth."""

from __future__ import annotations

import json
from typing import Any

from apps_rg.runtime.exit.headline_x3 import aggregate_x3
from apps_rg.runtime.validators.headline_x2 import (
    headline_runtime_self_check_truth,
    polish_claim_text_when_headline_has_no_metrics,
    run_headline_x2_gates,
    validate_raw_headline_claim_ledger,
)

CANONICAL_HL = (
    "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
)


def _segment_claim_ledger(hl: str, source_fact_ids: list[str]) -> list[dict[str, Any]]:
    parts = [p.strip() for p in hl.split(" | ")]
    if len(parts) >= 4:
        return [
            {"claim_text": parts[1], "source_fact_ids": list(source_fact_ids)},
            {"claim_text": parts[2], "source_fact_ids": list(source_fact_ids)},
            {"claim_text": parts[3], "source_fact_ids": list(source_fact_ids)},
        ]
    return [{"claim_text": hl, "source_fact_ids": list(source_fact_ids)}]


def _minimal_usage_ledger() -> dict[str, Any]:
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


def _fake_judges() -> list[dict[str, Any]]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False},
    ]


def _failed_ids(gates: list[Any]) -> list[str]:
    out: list[str] = []
    for g in gates:
        d = g.to_dict() if hasattr(g, "to_dict") else g
        if not d["pass"]:
            out.append(d["gate_id"])
    return out


def _kwargs_real_llm(**overrides: Any) -> dict[str, Any]:
    hl = str(overrides.pop("headline_line", CANONICAL_HL))
    rt = headline_runtime_self_check_truth(hl, target_company="", employer_names_lower=["contoso", "fabrikam"])
    parsed: dict[str, Any] = {
        "headline_line": hl,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": ["bul_1"]},
        "claim_ledger": _segment_claim_ledger(hl, ["bul_1"]),
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "t",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": dict(rt),
    }
    po_extra = overrides.pop("parsed_extra", None)
    if isinstance(po_extra, dict):
        parsed.update(po_extra)
    raw_pre = overrides.pop("raw_model_parsed_before_normalize", None)
    if raw_pre is None:
        raw_pre = json.loads(json.dumps(parsed))
    base: dict[str, Any] = {
        "headline_line": hl,
        "parsed_output": parsed,
        "claim_ledger": list(parsed["claim_ledger"]),
        "jd_text": "enterprise platform delivery",
        "target_company": "",
        "target_title": "SVP Engineering",
        "resume_support_blob": json.dumps({"employment": [], "header": {"name": "A B"}}),
        "employer_names_lower": ["contoso", "fabrikam"],
        "allowed_fact_ids": {"bul_1", "bul_2", "bul_unify_001", "bul_ibm_001", "bul_unify_004"},
        "runtime_generation_status": "REAL_LLM",
        "provider_requested": "retired_provider_profile",
        "provider_attempted": "retired_provider_profile",
        "raw_output": json.dumps(parsed),
        "x1d_judges": _fake_judges(),
        "companion_context": "",
        "raw_model_parsed_before_normalize": raw_pre,
        "reasoning_execution_receipt": {},
    }
    base.update(overrides)
    return base


def test_prompt_reasoning_receipt_aggregate_blocked_fails() -> None:
    gates = run_headline_x2_gates(**_kwargs_real_llm(reasoning_execution_receipt={"aggregate_blocked": True}))
    assert "x2_headline_prompt_reasoning_receipt_clean" in _failed_ids(gates)


def test_prompt_reasoning_receipt_quality_denied_fails() -> None:
    gates = run_headline_x2_gates(
        **_kwargs_real_llm(reasoning_execution_receipt={"quality_certification_denied": True}),
    )
    assert "x2_headline_prompt_reasoning_receipt_clean" in _failed_ids(gates)


def test_flat_raw_claim_ledger_fails_raw_schema_gate() -> None:
    kwargs = _kwargs_real_llm()
    kwargs["raw_model_parsed_before_normalize"] = {
        **kwargs["parsed_output"],
        "claim_ledger": ["bul_1"],
    }
    gates = run_headline_x2_gates(**kwargs)
    assert "x2_headline_raw_model_schema_valid" in _failed_ids(gates)


def test_self_check_word_count_matches_runtime_passes_gate() -> None:
    gates = run_headline_x2_gates(**_kwargs_real_llm())
    assert "x2_headline_self_check_consistent" not in _failed_ids(gates)


def test_single_row_full_headline_claim_ledger_fails_segment_decomposition() -> None:
    hl = CANONICAL_HL
    kwargs = _kwargs_real_llm()
    kwargs["claim_ledger"] = [{"claim_text": hl, "source_fact_ids": ["bul_1"]}]
    kwargs["parsed_output"]["claim_ledger"] = kwargs["claim_ledger"]
    gates = run_headline_x2_gates(**kwargs)
    assert "x2_headline_claim_ledger_segment_decomposition" in _failed_ids(gates)


def test_validate_raw_headline_claim_ledger_rejects_flat_strings() -> None:
    ok, detail, obs = validate_raw_headline_claim_ledger(
        {"headline_line": "x", "claim_ledger": ["bul_1"]},
    )
    assert not ok
    assert detail == "claim_ledger_flat_string_fact_ids_invalid"
    assert obs == ["bul_1"]


def test_validate_raw_headline_claim_ledger_accepts_object_rows() -> None:
    hl = CANONICAL_HL
    ok, detail, obs = validate_raw_headline_claim_ledger(
        {
            "headline_line": hl,
            "claim_ledger": [{"claim_text": "theme", "source_fact_ids": ["bul_1"]}],
        },
    )
    assert ok and detail == "ok" and obs is None


def test_normalized_claim_ledger_ok_does_not_mask_flat_raw_schema_failure() -> None:
    kwargs = _kwargs_real_llm()
    kwargs["raw_model_parsed_before_normalize"] = {
        **kwargs["parsed_output"],
        "claim_ledger": ["bul_1"],
    }
    gates = run_headline_x2_gates(**kwargs)
    failed = _failed_ids(gates)
    assert "x2_headline_raw_model_schema_valid" in failed
    assert "x2_headline_schema_valid" not in failed


def test_x3_blocks_when_raw_schema_invalid_even_with_valid_normalized_parse() -> None:
    kwargs = _kwargs_real_llm()
    kwargs["raw_model_parsed_before_normalize"] = {
        **kwargs["parsed_output"],
        "claim_ledger": ["bul_1"],
    }
    gates = run_headline_x2_gates(**kwargs)
    x3 = aggregate_x3(
        resume_display_text=kwargs["headline_line"],
        claim_ledger=kwargs["claim_ledger"],
        x2_gates=[g.to_dict() for g in gates],
        x1d_judges=_fake_judges(),
        runtime_generation_status="REAL_LLM",
        product_quality_status="PASS",
        section_input_usage_ledger=_minimal_usage_ledger(),
    )
    assert x3.x3_code == "X3_BLOCK"
    assert "x2_headline_raw_model_schema_valid" in x3.x2_failed_gates


def test_self_check_word_count_11_vs_runtime_10_fails() -> None:
    hl = "SVP Engineering | A B C D | E F | G H"
    assert (
        headline_runtime_self_check_truth(hl, target_company="", employer_names_lower=["contoso", "fabrikam"])[
            "word_count"
        ]
        == 10
    )
    kwargs = _kwargs_real_llm(headline_line=hl)
    po = kwargs["parsed_output"]
    rt = headline_runtime_self_check_truth(hl, target_company="", employer_names_lower=["contoso", "fabrikam"])
    po["self_check"] = {**dict(rt), "word_count": 11}
    kwargs["raw_model_parsed_before_normalize"] = json.loads(json.dumps(po))
    gates = run_headline_x2_gates(**kwargs)
    assert "x2_headline_self_check_consistent" in _failed_ids(gates)


def test_self_check_word_count_mismatch_large_fails() -> None:
    kwargs = _kwargs_real_llm()
    po = kwargs["parsed_output"]
    assert isinstance(po["self_check"], dict)
    po["self_check"] = {**po["self_check"], "word_count": 999}
    kwargs["raw_model_parsed_before_normalize"] = json.loads(json.dumps(po))
    gates = run_headline_x2_gates(**kwargs)
    assert "x2_headline_self_check_consistent" in _failed_ids(gates)


def test_polish_claim_text_strips_metric_phrases_when_headline_is_metric_free() -> None:
    hl = CANONICAL_HL
    raw = "Architected platforms operating at 99.9% uptime at enterprise scale."
    out = polish_claim_text_when_headline_has_no_metrics(hl, raw)
    assert "%" not in out
    assert "99.9" not in out


def test_polish_claim_text_leaves_plain_percent_when_row_not_metric_heavy() -> None:
    hl = CANONICAL_HL
    raw = "Platform delivery focus"
    out = polish_claim_text_when_headline_has_no_metrics(hl, raw)
    assert out == raw
