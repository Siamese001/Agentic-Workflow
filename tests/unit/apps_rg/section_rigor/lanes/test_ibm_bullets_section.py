"""IBM bullets lane nuance: five bullets, zero HEAVY distribution, metric anchors."""

from __future__ import annotations

import json

from apps_rg.runtime.validators.ibm_bullets_x2 import (
    IBM_BULLET_IDS,
    IBM_DEFAULT_DISTRIBUTION,
    run_ibm_bullets_x2_gates,
)

IBM_BULLETS_CRITICAL_GATES = frozenset(
    {
        "x2_ibm_bullet_count_5",
        "x2_ibm_rewrite_distribution_valid",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_text_claim_coverage_integrity",
        "x2_ibm_metric_anchor_bullet_ownership",
    }
)


def _five_bullets(heavy: int = 0) -> tuple[list[dict], dict]:
    intensities = ["MODERATE", "MODERATE", "MODERATE", "LIGHT_PROTECTED", "LIGHT_PROTECTED"]
    if heavy:
        intensities[0] = "HEAVY"
    bullets = []
    ledger = []
    for bid, intensity in zip(IBM_BULLET_IDS, intensities):
        text = f"IBM delivery outcome for {bid} with cloud and governance impact."
        if bid == "bul_ibm_005":
            text = "Delivered $15M savings, 99.9% uptime, and 30% efficiency gains across programs."
        bullets.append(
            {
                "bullet_id": bid,
                "bullet_text": text,
                "rewrite_intensity": intensity,
                "source_fact_ids": [bid],
            }
        )
        ledger.append({"claim_text": text, "source_fact_ids": [bid]})
    dist = dict(IBM_DEFAULT_DISTRIBUTION)
    dist["HEAVY"] = heavy
    return bullets, {"bullets": bullets, "claim_ledger": ledger, "rewrite_distribution": dist}


def test_heavy_bullet_fails_ibm_rewrite_distribution_gate() -> None:
    bullets, parsed = _five_bullets(heavy=1)
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
        provider_requested="mock",
        provider_attempted="mock",
        raw_output=json.dumps(parsed),
        x1d_judges=[],
    )
    assert any(g.gate_id == "x2_ibm_rewrite_distribution_valid" and not g.pass_ for g in gates)


def test_missing_core_metrics_on_anchor_bullet_fails_ownership_gate() -> None:
    bullets, parsed = _five_bullets()
    for b in bullets:
        if b["bullet_id"] == "bul_ibm_005":
            b["bullet_text"] = "Led cloud foundations and observability programs for regulated clients."
    parsed["claim_ledger"] = [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets]
    gates = run_ibm_bullets_x2_gates(
        bullets=bullets,
        parsed_output=parsed,
        claim_ledger=parsed["claim_ledger"],
        allowed_fact_ids=set(IBM_BULLET_IDS),
        jd_text="",
        runtime_generation_status="MOCKED",
    )
    assert any(g.gate_id == "x2_ibm_metric_anchor_bullet_ownership" and not g.pass_ for g in gates)


def test_mock_output_passes_all_critical_gates() -> None:
    from tests.unit.apps_rg.section_rigor.unify_ibm_lane_fixtures import (
        assert_critical_gates_pass,
        ibm_bullets_parsed_from_mock,
        run_ibm_bullets_x2,
    )

    parsed, allowed = ibm_bullets_parsed_from_mock()
    gates = run_ibm_bullets_x2(parsed, allowed)
    assert_critical_gates_pass("ibm_bullets", gates)
