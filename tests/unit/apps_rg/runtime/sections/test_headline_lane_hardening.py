"""Hardened regression tests for headline lane proof/ledger seams."""

from __future__ import annotations

import json

import pytest

from apps_rg.runtime.claim_ledger.headline_claim_ledger import build_headline_text_claim_coverage
from apps_rg.runtime.sections.headline_lane import (
    W3_EXECUTION_PATH_BUCKET,
    build_headline_allowed_fact_packet,
    ensure_claim_ledger,
    normalize_parsed_output,
    sync_selected_fact_plan_required_ids,
)
from apps_rg.runtime.validators.headline_x2 import run_headline_x2_gates
from apps_rg.runtime.w3_execution_path_labels import BUCKET_GOVERNED_PA_L2_EXIT

HL = "SVP Engineering | Governed Agentic Platforms | Runtime Infrastructure | Regulated Delivery"
METRIC_ID = "fact_engineering_platform_001_metric_deadbeef"
BASE_ID = "fact_engineering_platform_001"


def _runtime_payload_srfs() -> dict:
    facts = [{"fact_id": BASE_ID, "metric_raw": "deadbeef", "claim_text": "platform"}]
    return {
        "selected_fact_plan": {
            "section_id": "headline",
            "facts": facts,
            "required_fact_ids": [],
        },
        "proof_pool_metadata": {"proof_pool_type": "augmented_skills_graph"},
    }


def test_w3_bucket_is_governed_pa_l2_exit() -> None:
    assert W3_EXECUTION_PATH_BUCKET == BUCKET_GOVERNED_PA_L2_EXIT


def test_resolve_metric_derivative_id_in_ledger_sanitize() -> None:
    allowed = {BASE_ID, METRIC_ID}
    parsed = {
        "claim_ledger": [
            {
                "claim_text": "Governed Agentic Platforms",
                "source_fact_ids": [METRIC_ID],
            },
            {
                "claim_text": "Runtime Infrastructure",
                "source_fact_ids": [METRIC_ID],
            },
            {
                "claim_text": "Regulated Delivery",
                "source_fact_ids": [METRIC_ID],
            },
        ],
    }
    ensure_claim_ledger(HL, parsed, allowed)
    ids = parsed["claim_ledger"][0]["source_fact_ids"]
    assert METRIC_ID in ids


def test_sync_selected_fact_plan_includes_metric_derivative() -> None:
    allowed = {BASE_ID, METRIC_ID}
    parsed = {
        "claim_ledger": [
            {"claim_text": "Governed Agentic Platforms", "source_fact_ids": [METRIC_ID]},
            {"claim_text": "Runtime Infrastructure", "source_fact_ids": [METRIC_ID]},
            {"claim_text": "Regulated Delivery", "source_fact_ids": [METRIC_ID]},
        ],
    }
    payload = _runtime_payload_srfs()
    sync_selected_fact_plan_required_ids(parsed, payload, allowed)
    req = set(parsed["selected_fact_plan"]["required_fact_ids"])
    assert METRIC_ID in req


def test_srfs_resolution_row_drop_accounted() -> None:
    allowed = {BASE_ID}
    payload = _runtime_payload_srfs()
    parsed = {
        "headline_line": HL,
        "claim_ledger": [
            {"claim_text": "Governed Agentic Platforms", "source_fact_ids": ["bul_unify_001"]},
            {"claim_text": "Runtime Infrastructure", "source_fact_ids": ["bul_unify_099"]},
            {"claim_text": "Regulated Delivery", "source_fact_ids": ["bul_unify_005"]},
        ],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
    }
    out = normalize_parsed_output(parsed, payload, allowed, HL, proof_pool_metadata=payload["proof_pool_metadata"])
    assert out is not None
    dropped = int(out.get("_headline_ledger_rows_dropped") or 0)
    assert dropped == 2
    receipt = out.get("fact_id_resolution_receipt") or {}
    assert receipt.get("resolution_status") == "FAIL" or int(receipt.get("unresolved_alias_count") or 0) >= 1


def test_parsed_output_artifact_omits_internal_drop_marker() -> None:
    """normalize leaves marker on dict; execution strips before parsed_output.json — unit-check strip."""
    parsed = {"claim_ledger": [], "_headline_ledger_rows_dropped": 2}
    public = {k: v for k, v in parsed.items() if k != "_headline_ledger_rows_dropped"}
    assert "_headline_ledger_rows_dropped" not in public


def test_text_claim_coverage_requires_token_overlap_not_substring_false_positive() -> None:
    hl = HL
    ledger = [
        {"claim_text": "Enterprise Transformation Leadership", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Runtime Infrastructure", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Regulated Delivery", "source_fact_ids": ["bul_1"]},
    ]
    doc = build_headline_text_claim_coverage(hl, ledger, {"bul_1"})
    by_seg = {row["segment_text"]: row["pass"] for row in doc["segments"]}
    assert by_seg["Governed Agentic Platforms"] is False
    assert by_seg["Runtime Infrastructure"] is True
    assert by_seg["Regulated Delivery"] is True


def test_build_headline_allowed_fact_packet_includes_facts_and_anchor() -> None:
    plan = {
        "facts": [{"fact_id": "fact_001", "claim_text": "platform scale"}],
        "required_fact_ids": ["fact_001"],
    }
    packet = build_headline_allowed_fact_packet(
        selected_fact_plan=plan,
        proof_pool_ref="artifacts/srfs.json",
        proof_pool_digest="abc123",
    )
    assert any(r.get("fact_id") == "fact_001" for r in packet)
    assert any(r.get("kind") == "proof_pool_anchor" for r in packet)


def _fake_judges() -> list[dict]:
    return [
        {"provider_key": "gemini_pro", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "openai_chatgpt", "evaluator_mode": "MOCKED", "provider_blocked": False},
        {"provider_key": "anthropic_claude", "evaluator_mode": "MOCKED", "provider_blocked": False},
    ]


def test_x2_silent_row_drop_gate_fires() -> None:
    hl = HL
    parsed = {
        "headline_line": hl,
        "_headline_ledger_rows_dropped": 2,
        "selected_fact_plan": {"required_fact_ids": []},
        "claim_ledger": [],
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
    }
    gates = run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=[],
        jd_text="",
        target_company="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids=set(),
        runtime_generation_status="MOCKED",
        x1d_judges=_fake_judges(),
    )
    failed = [g.gate_id for g in gates if not g.pass_]
    assert "x2_headline_claim_ledger_no_silent_row_drop" in failed


def test_x2_text_claim_coverage_gate_fires_when_segments_unsupported() -> None:
    hl = HL
    ledger = [
        {"claim_text": "Unrelated Theme", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Another Theme", "source_fact_ids": ["bul_1"]},
        {"claim_text": "Third Theme", "source_fact_ids": ["bul_1"]},
    ]
    coverage = build_headline_text_claim_coverage(hl, ledger, {"bul_1"})
    parsed = {
        "headline_line": hl,
        "selected_fact_plan": {"required_fact_ids": ["bul_1"]},
        "claim_ledger": ledger,
        "jd_alignment": {
            "targeting_only": True,
            "jd_used_as_proof": False,
            "briefing_used_as_proof": False,
        },
        "text_claim_coverage": coverage,
    }
    gates = run_headline_x2_gates(
        headline_line=hl,
        parsed_output=parsed,
        claim_ledger=ledger,
        jd_text="",
        target_company="",
        resume_support_blob="{}",
        employer_names_lower=[],
        allowed_fact_ids={"bul_1"},
        runtime_generation_status="MOCKED",
        text_claim_coverage=coverage,
        x1d_judges=_fake_judges(),
    )
    failed = [g.gate_id for g in gates if not g.pass_]
    assert "x2_headline_text_claim_coverage_integrity" in failed
    assert "x2_headline_claim_ledger_segment_decomposition" in failed


def test_weak_payload_segment_decomposition_fails() -> None:
    from tests.unit.apps_rg.section_rigor.weak_payloads import (
        _gate_pass,
        _headline_weak_segment_decomposition,
    )

    assert not _gate_pass(_headline_weak_segment_decomposition(), "x2_headline_claim_ledger_segment_decomposition")


def test_weak_payload_silent_row_drop_fails() -> None:
    from tests.unit.apps_rg.section_rigor.weak_payloads import (
        _gate_pass,
        _headline_weak_silent_row_drop,
    )

    assert not _gate_pass(_headline_weak_silent_row_drop(), "x2_headline_claim_ledger_no_silent_row_drop")
