"""Focused regression tests for unify_bullets PATH_FRAMING (no full PA compile chain)."""

from __future__ import annotations

from typing import Any

from apps_rg.runtime.sections.unify_bullets_graph_evidence import (
    GRAPH_BULLET_EVIDENCE_PACK_MARKER,
    _PATH_FRAMING_ANGLES,
    append_unify_path_framing_to_messages,
    format_unify_graph_bullet_evidence_pack,
)
from apps_rg.runtime.validators.unify_bullets_x2 import UNIFY_BULLET_IDS


def _six_slot_facts() -> list[dict[str, Any]]:
    return [
        {
            "fact_id": f"bul_unify_{i:03d}",
            "claim_text": f"Archive bullet prose slot {i}.",
            "ledger_candidate_fact_id": f"fact_engineering_platform_{i:03d}",
            "metric_raw": "six months to three weeks" if i == 4 else "",
            "technologies": ["graphrag"] if i == 1 else [],
            "role_families_supported": ["ENGINEERING_PLATFORM"],
        }
        for i in range(1, 7)
    ]


def test_append_unify_path_framing_cycles_angles() -> None:
    messages = [{"role": "user", "content": "Compose six bullets."}]
    out0 = append_unify_path_framing_to_messages(messages, path_index=0, temperature=0.38)
    out5 = append_unify_path_framing_to_messages(messages, path_index=5, temperature=0.42)
    assert "PATH_FRAMING" in out0[-1]["content"]
    assert _PATH_FRAMING_ANGLES[0] in out0[-1]["content"]
    assert _PATH_FRAMING_ANGLES[5] in out5[-1]["content"]
    assert out0[-1]["content"] != out5[-1]["content"]
    assert messages[0]["content"] == "Compose six bullets."


def test_graph_evidence_pack_includes_c03_neighbor_hints() -> None:
    payload = {
        "selected_fact_plan": {"facts": _six_slot_facts()},
        "proof_pool_metadata": {
            "proof_pool_type": "augmented_skills_graph",
            "graph_ref": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
            "skills_authority_status": "PASS",
            "c03_graphrag_bound": {
                "graph_expansion_refs": ["neighbor:skill_a"],
            },
        },
    }
    body = format_unify_graph_bullet_evidence_pack(
        payload,
        allowed_block="",
        unify_id_hygiene="",
    )
    assert GRAPH_BULLET_EVIDENCE_PACK_MARKER in body
    assert "C0.3_GRAPH_NEIGHBOR_HINTS" in body
    assert "neighbor:skill_a" in body
    for slot in UNIFY_BULLET_IDS:
        assert slot in body
