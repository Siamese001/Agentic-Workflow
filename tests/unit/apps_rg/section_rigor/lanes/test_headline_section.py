"""Headline lane nuance: pipe segments, ledger rows, single-line display."""

from __future__ import annotations

import json
from typing import Any

from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates

# Anchors for gate-coverage audit (lane_registry LANE_CRITICAL_GATES["headline"])
HEADLINE_CRITICAL_GATES = frozenset(
    {
        "x2_headline_exactly_one_line",
        "x2_headline_pipe_four_segments",
        "x2_headline_word_count_10_to_13",
        "x2_headline_claim_ledger_rows_present",
        "x2_headline_claim_ledger_segment_decomposition",
        "x2_headline_segments_quality",
        "x2_headline_self_check_consistent",
        "x2_headline_raw_model_schema_valid",
        "x2_headline_source_supported",
        "x2_headline_claim_ledger_no_silent_row_drop",
        "x2_headline_text_claim_coverage_integrity",
    }
)


def _fake_judges() -> list[dict[str, Any]]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False, "pass": True},
    ]


def _segment_ledger(hl: str, fids: list[str]) -> list[dict[str, Any]]:
    parts = [p.strip() for p in hl.split(" | ")]
    if len(parts) >= 4:
        return [
            {"claim_text": parts[1], "source_fact_ids": fids},
            {"claim_text": parts[2], "source_fact_ids": fids},
            {"claim_text": parts[3], "source_fact_ids": fids},
        ]
    return [{"claim_text": hl, "source_fact_ids": fids}]


def _run(headline: str, **parsed_extra: Any) -> list[Any]:
    parsed: dict[str, Any] = {
        "headline_line": headline,
        "selected_fact_plan": {"section_id": "headline", "required_fact_ids": ["bul_unify_001"]},
        "claim_ledger": _segment_ledger(headline, ["bul_unify_001"]),
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "gap_notes": [],
        "change_log": [],
        "self_check": {},
    }
    parsed.update(parsed_extra)
    return run_headline_x2_gates(
        headline_line=headline,
        parsed_output=parsed,
        claim_ledger=parsed.get("claim_ledger") or [],
        jd_text="enterprise platform",
        target_company="",
        target_title="SVP Engineering",
        resume_support_blob=json.dumps({"employment": [], "header": {"name": "A B"}}),
        employer_names_lower=["contoso"],
        allowed_fact_ids={"bul_unify_001"},
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
    )


def _failed(gates: list[Any]) -> set[str]:
    return {g.gate_id for g in gates if not g.pass_}


def test_multiline_headline_fails_exactly_one_line_gate() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Runtime Infrastructure | Regulated Delivery\nExtra line"
    assert "x2_headline_exactly_one_line" in _failed(_run(hl))


def test_empty_claim_ledger_fails_rows_present_gate() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Runtime Infrastructure | Regulated Delivery"
    assert "x2_headline_claim_ledger_rows_present" in _failed(
        _run(hl, claim_ledger=[])
    )


def test_duplicate_tail_segments_fails_segments_quality_gate() -> None:
    hl = "SVP Engineering | Agentic AI Platforms | Agentic AI Platforms | Regulated Delivery"
    assert "x2_headline_segments_quality" in _failed(_run(hl))
