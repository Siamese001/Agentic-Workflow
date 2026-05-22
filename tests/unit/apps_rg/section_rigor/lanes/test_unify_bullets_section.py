"""Unify bullets lane nuance: six bullets, rewrite distribution, metric anchors."""

from __future__ import annotations

import json
from typing import Any

from apps_rg.runtime.validators.unify_bullets_x2 import (
    DEFAULT_DISTRIBUTION,
    UNIFY_BULLET_IDS,
    run_unify_bullets_x2_gates,
)

UNIFY_BULLETS_CRITICAL_GATES = frozenset(
    {
        "x2_unify_bullet_count_6",
        "x2_unify_rewrite_distribution_valid",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_text_claim_coverage_integrity",
        "x2_unify_metric_anchor_bullet_ownership",
        "x2_unify_at_most_one_mechanism_dense_bullet",
    }
)


def _six_bullets(dist_override: dict[str, int] | None = None) -> tuple[list[dict], dict]:
    bullets = []
    ledger = []
    intensities = ["HEAVY", "HEAVY", "MODERATE", "MODERATE", "MODERATE", "LIGHT_PROTECTED"]
    for bid, intensity in zip(UNIFY_BULLET_IDS, intensities):
        text = f"Delivery outcome for {bid} with governance and platform impact."
        if bid == "bul_unify_004":
            text = "Reduced lab-to-production cycle time from six months to three weeks."
        if bid == "bul_unify_006":
            text = "Generated $22M in IP-led revenue, expanded gross margins by 20%, and scaled team from 8 to 28."
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": intensity,
                "source_fact_ids": [bid],
            }
        )
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
    dist = dict(DEFAULT_DISTRIBUTION)
    if dist_override:
        dist.update(dist_override)
    return bullets, {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": dist}


def test_invalid_rewrite_distribution_fails_gate() -> None:
    bullets, parsed = _six_bullets({"HEAVY": 3, "MODERATE": 2, "LIGHT_PROTECTED": 1})
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=[],
    )
    assert any(g.gate_id == "x2_unify_rewrite_distribution_valid" and not g.pass_ for g in gates)


def test_metric_anchor_missing_on_bul_unify_006_fails_ownership_gate() -> None:
    bullets, parsed = _six_bullets()
    for b in bullets:
        if b["bullet_id"] == "bul_unify_006":
            b["bullet_text"] = "Scaled engineering leadership across global platform programs."
    parsed["claim_ledger"] = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    gates = run_unify_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(UNIFY_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
    )
    assert any(g.gate_id == "x2_unify_metric_anchor_bullet_ownership" and not g.pass_ for g in gates)


def test_mock_output_passes_all_critical_gates() -> None:
    from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import (
        assert_critical_gates_pass,
        run_unify_bullets_x2,
        unify_bullets_parsed_from_mock,
    )

    parsed, allowed = unify_bullets_parsed_from_mock()
    gates = run_unify_bullets_x2(parsed, allowed)
    assert_critical_gates_pass("unify_bullets", gates)
