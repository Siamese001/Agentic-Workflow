"""Unit tests for InsurTech/EY role-episode deterministic X2 gates."""

from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.sections import role_episode_lane
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
        "role_episode_bundle_consumed": True,
    }
    gates = run_insurtech_bullets_x2_gates(
        l2=l2,
        allowed=allowed,
        runtime_generation_status="REAL_LLM",
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


def test_role_episode_empty_llm_bullets_fail_closed_without_graph_render() -> None:
    cfg = role_episode_lane._ROLE_LANES["insurtech_bullets"]
    parsed, parse_error = role_episode_lane._parse_json_object("")
    facts = [
        {
            "fact_id": f"bul_insurtech_{idx:03d}",
            "claim_text": f"Delivered regulated platform control outcome {idx}.",
        }
        for idx in range(1, 4)
    ]

    bullets, receipt = role_episode_lane._materialize_bullet_generation(
        cfg=cfg,
        parsed=parsed,
        parse_error=parse_error,
        provider_runtime_generation_status="REAL_LLM",
        facts=facts,
        allowed=[f["fact_id"] for f in facts],
        graph_packet_digest="digest://graph-packet",
    )

    assert bullets == []
    assert receipt["generation_method"] == "model_output_invalid"
    assert receipt["llm_generation_status"] == "empty_output"
    assert receipt["llm_output_used"] is False
    assert receipt["evidence_authority"] == "augmented_skills_graph"
    assert receipt["source_fact_ids"] == []
    assert receipt["graph_packet_digest"] == "digest://graph-packet"
    assert receipt["renderer_version"] == ""
    assert receipt["rendered_source_fact_ids_within_allowed_packet"] is True


def test_role_episode_deterministic_graph_render_excludes_out_of_packet_facts() -> None:
    cfg = role_episode_lane._ROLE_LANES["ey_bullets"]
    facts = [
        {"fact_id": "bul_ey_001", "claim_text": "Led audited delivery controls."},
        {"fact_id": "outside_fact_999", "claim_text": "This fact is not allowed."},
    ]

    bullets = role_episode_lane._deterministic_graph_bullet_render(
        cfg=cfg,
        facts=facts,
        allowed=["bul_ey_001"],
    )

    assert [b["source_fact_ids"] for b in bullets] == [["bul_ey_001"]]
    assert all("outside_fact_999" not in b["source_fact_ids"] for b in bullets)


def test_role_episode_bullet_path_has_no_fallback_bullet_symbol() -> None:
    source = Path(role_episode_lane.__file__).read_text(encoding="utf-8")

    assert "_fallback_bullets_from_facts" not in source
    assert "deterministic_graph_render" in source
