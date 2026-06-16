"""Companion dependency chain: bullets finalize → narrative X2 gates (in-process E2E)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from apps_rg.runtime.validators.companion_bullet_finalization import (
    ACCEPTED_FINALIZED_COMPANION_STATUS,
    evaluate_companion_bullet_lane_finalized,
)
from apps_rg.runtime.validators.ibm_bullets_x2 import IBM_BULLET_IDS
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS
from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import (
    REPO,
    companion_bullets_l2_fixture,
    gate_results_map,
    ibm_bullets_parsed_from_mock,
    run_ibm_narrative_x2,
    run_unify_narrative_x2,
    unify_bullets_parsed_from_mock,
)


def _companion_text_from_parsed(parsed: dict) -> str:
    return "\n".join(
        f"- {b.get('bullet_id')}: {b.get('bullet_text', '')}"
        for b in (parsed.get("bullets") or [])
        if isinstance(b, dict)
    )


def test_unify_companion_accepts_real_llm_judge_blocked_upstream() -> None:
    l2 = companion_bullets_l2_fixture(
        "unify_bullets",
        x3_code="X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
    )
    status, reason = evaluate_companion_bullet_lane_finalized(
        upstream_section_id="unify_bullets",
        l2_data=l2,
        x3_code="X3_REVIEW_JUDGE_PROVIDER_BLOCKED",
        expected_bullet_ids=UNIFY_BULLET_IDS,
    )
    assert status == ACCEPTED_FINALIZED_COMPANION_STATUS
    assert reason == "ok"


def test_ibm_companion_rejects_mock_runtime_for_finalization() -> None:
    l2 = companion_bullets_l2_fixture("ibm_bullets", runtime_status="MOCKED", x3_code="X3_ALLOW")
    status, _ = evaluate_companion_bullet_lane_finalized(
        upstream_section_id="ibm_bullets",
        l2_data=l2,
        x3_code="X3_ALLOW",
        expected_bullet_ids=IBM_BULLET_IDS,
    )
    assert status == "NOT_FINALIZED"


@pytest.mark.parametrize(
    "lane,run_narrative,load_bullets",
    [
        ("unify", run_unify_narrative_x2, unify_bullets_parsed_from_mock),
        ("ibm", run_ibm_narrative_x2, ibm_bullets_parsed_from_mock),
    ],
)
def test_narrative_real_llm_passes_when_upstream_finalized(
    lane: str,
    run_narrative,
    load_bullets,
) -> None:
    bullets_parsed, _allowed = load_bullets()
    companion_text = _companion_text_from_parsed(bullets_parsed)
    narrative_parsed = {
        "narrative_sentence": (
            "At IBM, led enterprise-scale cloud, data, lineage, and observability foundations for regulated "
            "financial services, establishing reliability and governance discipline for governed analytics delivery."
            if lane == "ibm"
            else "Led the platform roadmap and commercialization of a production-grade agentic AI platform at Unify Consulting."
        ),
        "claim_ledger": [
            {
                "claim_text": "Enterprise platform and delivery discipline.",
                "source_fact_ids": ["bul_ibm_001"] if lane == "ibm" else ["bul_unify_001"],
            }
        ],
    }
    kwargs: dict = {
        "runtime_generation_status": "REAL_LLM",
        "companion_text": companion_text,
        "companion_status": ACCEPTED_FINALIZED_COMPANION_STATUS,
        "companion_reason": "ok",
    }
    if lane == "ibm":
        kwargs["companion_aware"] = True
    gates = run_narrative(narrative_parsed, **kwargs)
    results = gate_results_map(gates)
    gate_id = (
        "x2_ibm_narrative_requires_finalized_bullets"
        if lane == "ibm"
        else "x2_unify_narrative_requires_finalized_bullets"
    )
    assert results[gate_id] is True


@pytest.mark.parametrize(
    "lane,run_narrative",
    [
        ("unify", run_unify_narrative_x2),
        ("ibm", run_ibm_narrative_x2),
    ],
)
def test_narrative_real_llm_fails_without_finalized_companion(lane: str, run_narrative) -> None:
    narrative_parsed = {
        "narrative_sentence": "Led enterprise delivery across regulated programs.",
        "claim_ledger": [{"claim_text": "delivery", "source_fact_ids": ["bul_unify_001"]}],
    }
    kwargs: dict = {
        "runtime_generation_status": "REAL_LLM",
        "companion_text": "",
        "companion_status": "NOT_FINALIZED",
        "companion_reason": "missing_upstream",
    }
    if lane == "ibm":
        kwargs["companion_aware"] = True
    gates = run_narrative(narrative_parsed, **kwargs)
    results = gate_results_map(gates)
    gate_id = (
        "x2_ibm_narrative_requires_finalized_bullets"
        if lane == "ibm"
        else "x2_unify_narrative_requires_finalized_bullets"
    )
    assert results[gate_id] is False


def test_load_companion_unify_from_latest_successful_pointer(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate pointer write + load_companion after live-style finalize."""
    from apps_rg.runtime.runtime_proof_layout import finalize_runtime_proof_run, lane_root
    from apps_rg.runtime.sections.unify_narrative_lane import load_companion_unify_bullets_context

    monkeypatch.setenv("APPS_RG_TEST_HARNESS", "1")
    parsed, _allowed = unify_bullets_parsed_from_mock()
    art = (
        REPO
        / "artifacts"
        / "apps_rg"
        / "runtime_proofs"
        / "contract_harness"
        / "_test_companion_chain_unify"
    )
    art.mkdir(parents=True, exist_ok=True)
    l2 = {
        "section_id": "unify_bullets",
        "product_quality_status": "PASS",
        "runtime_generation_status": "REAL_LLM",
        "bullets": parsed["bullets"],
    }
    (art / "l2_output.json").write_text(json.dumps(l2), encoding="utf-8")
    (art / "x3_disposition.json").write_text(
        json.dumps({"x3_code": "X3_REVIEW_JUDGE_PROVIDER_BLOCKED", "x2_failed_gates": []}),
        encoding="utf-8",
    )
    (art / "provider_request.json").write_text(
        json.dumps({"provider_requested": "external_claude"}),
        encoding="utf-8",
    )
    finalize_runtime_proof_run(
        REPO,
        "unify_bullets",
        "external_claude",
        art,
        run_id="unify_bullets_test_chain",
        section_id="unify_bullets",
        runtime_generation_status="REAL_LLM",
        provider_requested="external_claude",
        provider_attempted=True,
    )
    ptr = lane_root(REPO, "unify_bullets") / "latest_successful_real_run.json"
    assert ptr.is_file()
    ctx = load_companion_unify_bullets_context()
    assert ctx["status"] == ACCEPTED_FINALIZED_COMPANION_STATUS
    assert ctx["x3_code"] == "X3_REVIEW_JUDGE_PROVIDER_BLOCKED"
    assert len(ctx.get("bullet_ids") or []) == len(UNIFY_BULLET_IDS)
