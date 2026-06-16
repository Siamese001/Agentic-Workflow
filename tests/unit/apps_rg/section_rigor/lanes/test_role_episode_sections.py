from __future__ import annotations

from typing import Any, Callable

import pytest

from apps_rg.runtime.sections import role_episode_lane


ROLE_EPISODE_CRITICAL_GATES: dict[str, tuple[str, ...]] = {
    "insurtech_bullets": (
        "x2_insurtech_bullets_allowed_fact_ids_non_empty",
        "x2_insurtech_bullets_source_fact_ids_supported",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_insurtech_bullets_runtime_real_llm",
        "x2_no_first_person",
        "x2_no_em_dash",
        "x2_insurtech_bullets_bullet_count_3",
        "x2_insurtech_bullets_bullet_single_thought",
        "x2_insurtech_bullets_bullet_no_embedded_newline",
    ),
    "ey_bullets": (
        "x2_ey_bullets_allowed_fact_ids_non_empty",
        "x2_ey_bullets_source_fact_ids_supported",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_ey_bullets_runtime_real_llm",
        "x2_no_first_person",
        "x2_no_em_dash",
        "x2_ey_bullets_bullet_count_3",
        "x2_ey_bullets_bullet_single_thought",
        "x2_ey_bullets_bullet_no_embedded_newline",
    ),
    "insurtech_narrative": (
        "x2_insurtech_narrative_allowed_fact_ids_non_empty",
        "x2_insurtech_narrative_source_fact_ids_supported",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_insurtech_narrative_runtime_real_llm",
        "x2_no_first_person",
        "x2_no_em_dash",
        "x2_insurtech_narrative_exactly_one_sentence",
        "x2_insurtech_narrative_word_budget",
        "x2_insurtech_narrative_char_budget",
    ),
    "ey_narrative": (
        "x2_ey_narrative_allowed_fact_ids_non_empty",
        "x2_ey_narrative_source_fact_ids_supported",
        "x2_claim_ledger_claim_text_non_empty",
        "x2_ey_narrative_runtime_real_llm",
        "x2_no_first_person",
        "x2_no_em_dash",
        "x2_ey_narrative_exactly_one_sentence",
        "x2_ey_narrative_word_budget",
        "x2_ey_narrative_char_budget",
    ),
}


ROLE_EPISODE_PROOF_POOL_GATES: dict[str, tuple[str, ...]] = {
    "insurtech_bullets": ("x2_insurtech_bullets_graph_role_episode_bundle_consumed",),
    "ey_bullets": ("x2_ey_bullets_graph_role_episode_bundle_consumed",),
}


_RUNNERS: dict[str, Callable[..., list[dict[str, Any]]]] = {
    "insurtech_bullets": role_episode_lane.run_insurtech_bullets_x2_gates,
    "ey_bullets": role_episode_lane.run_ey_bullets_x2_gates,
    "insurtech_narrative": role_episode_lane.run_insurtech_narrative_x2_gates,
    "ey_narrative": role_episode_lane.run_ey_narrative_x2_gates,
}


def _fact_id(section_id: str) -> str:
    return f"fact_{section_id}_001"


def _bullet_prefix(section_id: str) -> str:
    return "bul_insurtech" if section_id.startswith("insurtech") else "bul_ey"


def _passing_l2(section_id: str) -> dict[str, Any]:
    fact_id = _fact_id(section_id)
    if section_id.endswith("_bullets"):
        prefix = _bullet_prefix(section_id)
        bullets = [
            {
                "bullet_id": f"{prefix}_{idx:03d}",
                "bullet_text": f"Delivered governed platform control outcome {idx} with audited adoption.",
                "source_fact_ids": [fact_id],
            }
            for idx in range(1, 4)
        ]
        return {
            "section_id": section_id,
            "bullets": bullets,
            "claim_ledger": [
                {"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]}
                for b in bullets
            ],
        }
    text = "Delivered governed platform controls with audited adoption across regulated operations."
    return {
        "section_id": section_id,
        "narrative_sentence": text,
        "claim_ledger": [{"claim_text": text, "source_fact_ids": [fact_id]}],
    }


def _gates(section_id: str, l2: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    rows = _RUNNERS[section_id](
        l2=l2 or _passing_l2(section_id),
        allowed=[_fact_id(section_id)],
        runtime_generation_status="REAL_LLM",
    )
    return {str(row["gate_id"]): row for row in rows}


@pytest.mark.parametrize("section_id", sorted(ROLE_EPISODE_CRITICAL_GATES))
def test_role_episode_section_gates_are_present_and_pass_for_valid_payload(section_id: str) -> None:
    gates = _gates(section_id)

    assert set(ROLE_EPISODE_CRITICAL_GATES[section_id]) <= set(gates)
    for gate_id in ROLE_EPISODE_CRITICAL_GATES[section_id]:
        assert gates[gate_id]["pass"] is True, gate_id


def test_role_episode_proof_pool_gate_ids_stay_dedicated_coverage_literals() -> None:
    assert ROLE_EPISODE_PROOF_POOL_GATES == {
        "insurtech_bullets": ("x2_insurtech_bullets_graph_role_episode_bundle_consumed",),
        "ey_bullets": ("x2_ey_bullets_graph_role_episode_bundle_consumed",),
    }


@pytest.mark.parametrize("section_id", ("insurtech_bullets", "ey_bullets"))
def test_role_episode_bullet_lanes_fail_wrong_bullet_count(section_id: str) -> None:
    l2 = _passing_l2(section_id)
    l2["bullets"] = l2["bullets"][:2]
    l2["claim_ledger"] = [
        {"claim_text": b["bullet_text"], "source_fact_ids": b["source_fact_ids"]}
        for b in l2["bullets"]
    ]

    gates = _gates(section_id, l2)

    assert gates[f"x2_{section_id}_bullet_count_3"]["pass"] is False


@pytest.mark.parametrize("section_id", ("insurtech_narrative", "ey_narrative"))
def test_role_episode_narrative_lanes_fail_two_sentences(section_id: str) -> None:
    l2 = _passing_l2(section_id)
    l2["narrative_sentence"] = "Delivered governed controls. Expanded audited adoption."
    l2["claim_ledger"] = [
        {"claim_text": l2["narrative_sentence"], "source_fact_ids": [_fact_id(section_id)]}
    ]

    gates = _gates(section_id, l2)

    assert gates[f"x2_{section_id}_exactly_one_sentence"]["pass"] is False
