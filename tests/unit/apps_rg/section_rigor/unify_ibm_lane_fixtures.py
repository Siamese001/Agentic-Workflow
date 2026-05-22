"""Shared in-process fixtures for Unify/IBM bullets+narrative E2E rigor (no live vLLM)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[4]


def _fake_judges(*, pass_all: bool = True) -> list[dict[str, Any]]:
    return [
        {
            "provider_key": key,
            "evaluator_mode": "MOCKED",
            "provider_blocked": False,
            "pass": pass_all,
        }
        for key in ("gemini_pro", "openai_chatgpt", "anthropic_claude")
    ]


def unify_bullets_parsed_from_mock() -> tuple[dict[str, Any], set[str]]:
    from apps_rg.runtime.sections.unify_bullets_lane import (
        build_mock_output,
        build_runtime_payload,
        build_selected_fact_plan,
        extract_unify_employment,
        load_base_resume,
    )

    base, path, base_hash = load_base_resume()
    header, facts, allowed = extract_unify_employment(base)
    plan = build_selected_fact_plan(facts)
    rp = build_runtime_payload(
        base_json_path=path,
        base_hash=base_hash,
        unify_header=header,
        selected_fact_plan=plan,
        allowed_fact_ids=allowed,
        target_title="SVP IT Strategy & Innovation",
        target_company="Brown & Brown",
        jd_text="Enterprise AI platform leadership.",
        briefing="regulated insurance distribution",
    )
    return build_mock_output(rp), allowed


def ibm_bullets_parsed_from_mock() -> tuple[dict[str, Any], set[str]]:
    from apps_rg.runtime.resume_resolution import load_lane_base_resume_json
    from apps_rg.runtime.sections.ibm_bullets_lane import (
        build_mock_output,
        extract_ibm_employment,
    )
    from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS

    base, _path, _digest = load_lane_base_resume_json(repo_root=REPO)
    _hdr, facts, allowed = extract_ibm_employment(base)
    rp = {
        "selected_fact_plan": {"facts": facts},
        "jd_alignment": {"targeting_only": True},
    }
    parsed = build_mock_output(rp)
    return parsed, set(IBM_BULLET_IDS) & allowed


def unify_narrative_parsed_from_mock(*, companion_text: str = "- bul_unify_001: sample") -> dict[str, Any]:
    from apps_rg.runtime.sections.unify_narrative_lane import build_mock_output

    rp = {
        "selected_fact_plan": {"facts": []},
        "companion_bullets_text": companion_text,
        "companion_bullets_status": "ACCEPTED_FINALIZED",
        "companion_bullets_reason": "ok",
        "target_title": "SVP",
        "target_company": "Corp",
        "jd_text": "AI",
        "briefing": "brief",
    }
    return build_mock_output(rp)


def ibm_narrative_parsed_from_mock(*, companion_text: str = "- bul_ibm_001: sample") -> dict[str, Any]:
    from apps_rg.runtime.sections.ibm_narrative_lane_runtime import build_mock_output

    rp = {
        "selected_fact_plan": {"facts": []},
        "companion_bullets_text": companion_text,
        "companion_bullets_status": "ACCEPTED_FINALIZED",
        "companion_bullets_reason": "ok",
        "target_title": "SVP",
        "target_company": "Corp",
        "jd_text": "AI",
        "briefing": "brief",
    }
    return build_mock_output(rp)


def run_unify_bullets_x2(parsed: dict[str, Any], allowed: set[str]) -> list:
    from apps_rg.runtime.validators.unify_bullets_x2 import (
        build_unify_bullets_text_claim_coverage,
        run_unify_bullets_x2_gates,
    )

    bullets = parsed["bullets"]
    ledger = parsed["claim_ledger"]
    if "text_claim_coverage" not in parsed:
        parsed = dict(parsed)
        parsed["text_claim_coverage"] = build_unify_bullets_text_claim_coverage(
            bullets, ledger, allowed
        )
    return run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=allowed,
        jd_text="enterprise",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
    )


def run_ibm_bullets_x2(parsed: dict[str, Any], allowed: set[str]) -> list:
    from apps_rg.runtime.validators.ibm_bullets_x2 import (
        build_ibm_bullets_text_claim_coverage,
        run_ibm_bullets_x2_gates,
    )

    bullets = parsed["bullets"]
    ledger = parsed["claim_ledger"]
    if "text_claim_coverage" not in parsed:
        parsed = dict(parsed)
        parsed["text_claim_coverage"] = build_ibm_bullets_text_claim_coverage(
            bullets, ledger, allowed
        )
    return run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=allowed,
        jd_text="enterprise",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
    )


def run_unify_narrative_x2(
    parsed: dict[str, Any],
    *,
    runtime_generation_status: str = "MOCKED",
    companion_text: str = "",
    companion_status: str = "ACCEPTED_FINALIZED",
    companion_reason: str = "ok",
) -> list:
    from apps_rg.runtime.validators.unify_narrative_x2 import run_unify_narrative_x2_gates

    narrative = str(parsed.get("narrative_sentence") or "")
    ledger = parsed.get("claim_ledger") or []
    return run_unify_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=parsed,
        claim_ledger=ledger,
        jd_text="enterprise",
        runtime_generation_status=runtime_generation_status,
        companion_bullet_texts=companion_text,
        companion_bullets_status=companion_status,
        companion_bullets_reason=companion_reason,
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
        allowed_fact_ids={"bul_unify_001", "bul_unify_002"},
    )


def run_ibm_narrative_x2(
    parsed: dict[str, Any],
    *,
    runtime_generation_status: str = "MOCKED",
    companion_text: str = "",
    companion_status: str = "ACCEPTED_FINALIZED",
    companion_reason: str = "ok",
    companion_aware: bool = True,
) -> list:
    from apps_rg.runtime.validators.ibm_narrative_x2 import run_ibm_narrative_x2_gates

    narrative = str(parsed.get("narrative_sentence") or "")
    ledger = parsed.get("claim_ledger") or []
    return run_ibm_narrative_x2_gates(
        narrative_sentence=narrative,
        parsed_output=parsed,
        claim_ledger=ledger,
        jd_text="enterprise",
        runtime_generation_status=runtime_generation_status,
        companion_bullet_texts=companion_text,
        companion_bullets_status=companion_status,
        companion_bullets_reason=companion_reason,
        companion_aware=companion_aware,
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=_fake_judges(),
        allowed_fact_ids=["bul_ibm_001", "bul_ibm_002"],
    )


def gate_results_map(gates: list) -> dict[str, bool]:
    out: dict[str, bool] = {}
    for g in gates:
        gid = getattr(g, "gate_id", None) or (g.get("gate_id") if isinstance(g, dict) else None)
        if gid:
            out[str(gid)] = bool(getattr(g, "pass_", g.get("pass") if isinstance(g, dict) else False))
    return out


def assert_critical_gates_pass(lane: str, gates: list) -> None:
    from tests.unit.apps_rg.section_rigor.lane_registry import LANE_CRITICAL_GATES

    critical = LANE_CRITICAL_GATES[lane]
    results = gate_results_map(gates)
    missing = sorted(critical - set(results))
    assert not missing, f"{lane} missing gates: {missing}"
    failed = sorted(gid for gid in critical if not results.get(gid))
    assert not failed, f"{lane} critical failures: {[(g, results.get(g)) for g in failed]}"


def companion_bullets_l2_fixture(
    lane: str,
    *,
    product_quality: str = "PASS",
    runtime_status: str = "REAL_LLM",
    x3_code: str = "X3_ALLOW",
) -> dict[str, Any]:
    """Minimal accepted upstream bullets bundle for companion resolution tests."""
    if lane == "unify_bullets":
        parsed, _allowed = unify_bullets_parsed_from_mock()
        section_id = "unify_bullets"
    else:
        parsed, _allowed = ibm_bullets_parsed_from_mock()
        section_id = "ibm_bullets"
    return {
        "section_id": section_id,
        "product_quality_status": product_quality,
        "runtime_generation_status": runtime_status,
        "bullets": parsed["bullets"],
    }


__all__ = [
    "REPO",
    "assert_critical_gates_pass",
    "companion_bullets_l2_fixture",
    "gate_results_map",
    "ibm_bullets_parsed_from_mock",
    "ibm_narrative_parsed_from_mock",
    "run_ibm_bullets_x2",
    "run_ibm_narrative_x2",
    "run_unify_bullets_x2",
    "run_unify_narrative_x2",
    "unify_bullets_parsed_from_mock",
    "unify_narrative_parsed_from_mock",
]
