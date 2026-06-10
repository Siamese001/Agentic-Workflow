"""Unit tests for InsurTech/EY role-episode deterministic X2 gates."""

from __future__ import annotations

import pytest

from apps_rg.runtime.sections.role_episode_lane import (
    ROLE_EPISODE_X2_GATE_IDS_BY_RUN_FUNCTION,
    run_ey_bullets_x2_gates,
    run_ey_narrative_x2_gates,
    run_insurtech_bullets_x2_gates,
    run_insurtech_narrative_x2_gates,
)
from apps_rg.runtime.sections.section_product_shape_ssot import (
    NARRATIVE_MAX_CHARS,
    NARRATIVE_MAX_WORDS,
    product_shape_gate_ids_for_lane,
)


def _gate_map(gates: list[dict]) -> dict[str, bool]:
    return {str(g["gate_id"]): bool(g["pass"]) for g in gates}


def _valid_bullets(prefix: str) -> list[dict]:
    return [
        {
            "bullet_id": f"{prefix}_{i:03d}",
            "bullet_text": f"Outcome {i} for regulated delivery.",
            "source_fact_ids": [f"{prefix}_{i:03d}"],
        }
        for i in range(1, 4)
    ]


def test_insurtech_bullets_valid_payload_passes_core_gates() -> None:
    bullets = _valid_bullets("bul_insurtech")
    allowed = [b["bullet_id"] for b in bullets]
    l2 = {
        "bullets": bullets,
        "claim_ledger": [{"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]} for b in bullets],
    }
    gates = run_insurtech_bullets_x2_gates(
        l2=l2,
        allowed=allowed,
        runtime_generation_status="REAL_LLM",
        bundle_consumed=True,
    )
    by_id = _gate_map(gates)
    assert by_id["x2_insurtech_bullets_bullet_count_3"] is True
    assert by_id["x2_insurtech_bullets_graph_role_episode_bundle_consumed"] is True
    assert by_id["x2_insurtech_bullets_source_fact_ids_supported"] is True
    assert by_id["x2_no_first_person"] is True


def test_ey_narrative_valid_sentence_passes_budget_gates() -> None:
    narrative = "Led enterprise risk analytics modernization across regulated insurance programs."
    l2 = {
        "narrative_sentence": narrative,
        "claim_ledger": [{"claim_text": narrative, "source_fact_ids": ["bul_ey_001"]}],
    }
    gates = run_ey_narrative_x2_gates(
        l2=l2,
        allowed=["bul_ey_001", "bul_ey_002", "bul_ey_003"],
        runtime_generation_status="REAL_LLM",
    )
    by_id = _gate_map(gates)
    assert by_id["x2_ey_narrative_exactly_one_sentence"] is True
    assert by_id["x2_ey_narrative_word_budget"] is True
    assert by_id["x2_ey_narrative_char_budget"] is True
    assert len(narrative.split()) <= NARRATIVE_MAX_WORDS
    assert len(narrative) <= NARRATIVE_MAX_CHARS


@pytest.mark.parametrize(
    "run_fn,lane",
    [
        (run_insurtech_bullets_x2_gates, "insurtech_bullets"),
        (run_insurtech_narrative_x2_gates, "insurtech_narrative"),
        (run_ey_bullets_x2_gates, "ey_bullets"),
        (run_ey_narrative_x2_gates, "ey_narrative"),
    ],
)
def test_role_episode_gate_registry_matches_product_shape_ssot(run_fn, lane: str) -> None:
    fn_name = run_fn.__name__
    advertised = ROLE_EPISODE_X2_GATE_IDS_BY_RUN_FUNCTION[fn_name]
    assert advertised == product_shape_gate_ids_for_lane(lane) | {
        "x2_x1d_required_judges_present",
        "x2_x1d_schema_valid",
    }
