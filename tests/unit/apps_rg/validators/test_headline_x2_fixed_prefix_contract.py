"""Deterministic headline X2 gates for fixed-prefix SVP Engineering | X | Y | Z contract."""
from __future__ import annotations

import json
from typing import Any

from apps_rg.runtime.dispatch.headline_dispatch import build_mock_output, normalize_parsed_output
from apps_rg.runtime.exit.headline_x3 import aggregate_x3
from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates


def _fake_judges() -> list[dict[str, Any]]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False},
    ]

def _base_kwargs(headline: str, **over) -> dict[str, Any]:
    allowed = {"bul_1", "bul_2", "bul_unify_001", "bul_ibm_001", "bul_unify_004"}
    parsed = {
        "headline_line": headline,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": ["bul_1"]},
        "claim_ledger": [{"claim_text": headline, "source_fact_ids": ["bul_1"]}],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "t",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    parsed.update(over.pop("parsed_extra", {}))
    base: dict[str, Any] = {
        "parsed_output": parsed,
        "claim_ledger": parsed["claim_ledger"],
        "jd_text": "enterprise platform delivery",
        "target_company": "",
        "target_title": "SVP Engineering",
        "resume_support_blob": json.dumps({"employment": [], "header": {"name": "A B"}}),
        "employer_names_lower": ["contoso", "fabrikam"],
        "allowed_fact_ids": allowed,
        "runtime_generation_status": "REAL_LLM",
        "provider_requested": "qwen_vllm",
        "provider_attempted": "qwen_vllm",
        "raw_output": json.dumps(parsed),
        "x1d_judges": _fake_judges(),
        "companion_context": "",
    }
    base.update(over)
    return base


def _failed_ids(gates: list[Any]) -> list[str]:
    out: list[str] = []
    for g in gates:
        d = g.to_dict() if hasattr(g, "to_dict") else g
        if not d["pass"]:
            out.append(d["gate_id"])
    return out


def test_valid_canonical_derived_passes() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert _failed_ids(gates) == []


def test_three_segment_line_fails_pipe_gate() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_pipe_four_segments" in _failed_ids(gates)


def test_missing_fixed_prefix_fails() -> None:
    hl = "Engineering Executive | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_pipe_four_segments" in _failed_ids(gates)


def test_word_count_too_short_fails() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | More Here | Extra Bit"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_word_count_10_to_13" in _failed_ids(gates)


def test_word_count_too_long_fails() -> None:
    hl = (
        "SVP Engineering | Agentic AI Platform Products | Distributed AI Infrastructure Systems | "
        "Governed Enterprise Architecture And Scale Delivery"
    )
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_word_count_10_to_13" in _failed_ids(gates)


def test_keyword_stuffing_heuristic_fails() -> None:
    hl = (
        "SVP Engineering | AI ML Cloud Data Security | Digital Transformation | "
        "Innovation Leadership Scope"
    )
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_no_keyword_stuffing_heuristic" in _failed_ids(gates)


def test_metrics_fail() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | $22M Revenue Growth | Distributed Infrastructure"
    gates = run_headline_x2_gates(headline_line=hl, **_base_kwargs(hl))
    assert "x2_headline_no_metrics" in _failed_ids(gates)


def test_target_company_in_headline_fails() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Contoso Holdings International | Enterprise Systems"
    gates = run_headline_x2_gates(
        headline_line=hl,
        **_base_kwargs(hl, target_company="Contoso Holdings International"),
    )
    assert "x2_no_target_company_as_experience" in _failed_ids(gates)


def test_unsupported_claim_fact_ids_fail() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": ["bul_1"]},
        "claim_ledger": [{"claim_text": hl, "source_fact_ids": ["bul_nope"]}],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
            "selected_theme": "t",
            "anti_stuffing_check": "passed",
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    gates = run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        jd_text="x",
        target_company="",
        target_title="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids={"bul_1"},
        runtime_generation_status="REAL_LLM",
        provider_requested="qwen_vllm",
        provider_attempted="qwen_vllm",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
        companion_context="",
    )
    assert "x2_headline_source_supported" in _failed_ids(gates)


def test_dispatch_normalize_merges_schema_keys_for_parser() -> None:
    runtime_payload = {
        "selected_fact_plan": {
            "section_id": "headline",
            "selection_method": "canonical_base_resume_employment_bullets",
            "required_fact_ids": ["bul_unify_001", "bul_ibm_001", "bul_unify_004"],
            "facts": [],
        }
    }
    allowed = {"bul_unify_001", "bul_ibm_001", "bul_unify_004"}
    mo = build_mock_output(runtime_payload)
    out = normalize_parsed_output(mo, runtime_payload, allowed, str(mo["headline_line"]))
    assert out is not None
    for k in ("headline_line", "jd_alignment", "self_check", "claim_ledger"):
        assert k in out
    jd = out["jd_alignment"]
    assert jd.get("jd_used_as_proof") is False
    assert jd.get("briefing_used_as_proof") is False
    assert out["self_check"].get("separator_count") == 3
    assert out["self_check"].get("segment_count") == 4


def test_mocked_runtime_with_passing_x2_still_not_x3_allow() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Distributed AI Infrastructure | Governed Enterprise Systems"
    kwargs = _base_kwargs(
        hl,
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
    )
    gates = run_headline_x2_gates(headline_line=hl, **kwargs)
    assert _failed_ids(gates) == []
    x2_dicts = [g.to_dict() for g in gates]
    x3 = aggregate_x3(
        resume_display_text=hl,
        claim_ledger=kwargs["claim_ledger"],
        x2_gates=x2_dicts,
        x1d_judges=_fake_judges(),
        runtime_generation_status="MOCKED",
        product_quality_status="PASS",
    )
    assert x3.x3_code != "X3_ALLOW"
    assert x3.pass_ is False
