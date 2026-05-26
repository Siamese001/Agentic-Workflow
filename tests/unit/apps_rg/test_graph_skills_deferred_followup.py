"""Deferred follow-on plan — spine C0.3 authority + c0_graph_lane receipt (DS-11)."""
from __future__ import annotations

from pathlib import Path

import pytest

from apps_rg.runtime.bindings.c0_binding import C0_GRAPH_LANE_NA_REF
from apps_rg.runtime.spine.c0_graph_lane_receipt import (
    build_c0_graph_lane_receipt,
    build_c0_graph_lane_receipt_from_spine_retrieve,
)
from apps_rg.runtime.spine.spine_c03_authority import (
    overlay_spine_graph_authority_on_bridge,
    spine_graph_refs_live,
)


def test_spine_graph_refs_live_detects_traverse_ref() -> None:
    assert spine_graph_refs_live(["ref:graph:traverse:abc123"]) is True
    assert spine_graph_refs_live([C0_GRAPH_LANE_NA_REF]) is False


def test_c0_graph_lane_receipt_claims_unified_when_spine_live() -> None:
    rec = build_c0_graph_lane_receipt(
        section_id="executive_summary",
        graph_lane_ref="ref:graph:traverse:deadbeef",
        graph_expansion_refs=["ref:graph:traverse:deadbeef"],
        skills_graph_bound=True,
    )
    assert rec["canonical_c0_3_graph_rag_claimed"] is True
    assert rec["unified_pipeline_bound"] is True
    assert rec["graph_lane_deferred"] is False
    assert rec["c03_graphrag_bound_status"] == "BOUND"


def test_spine_retrieve_receipt_builder_live() -> None:
    spine = {
        "section_id": "executive_summary",
        "graph_expansion_refs": ["ref:graph:traverse:867e5a2d557a0bed"],
        "graph_lane_na_ref": "ref:graph:traverse:867e5a2d557a0bed",
        "graph_lane_deferred": False,
        "canonical_c0_3_graph_claimed": True,
    }
    out = build_c0_graph_lane_receipt_from_spine_retrieve(spine)
    assert out["canonical_c0_3_graph_rag_claimed"] is True


def test_overlay_spine_demotes_shim_only_bridge(tmp_path: Path) -> None:
    bridge = {
        "proof_pool_shim_only": True,
        "canonical_c0_3_claimed": False,
        "pa_proof_authority_metadata": {
            "c03_graphrag_bound": {"c03_graphrag_bound_status": "NOT_BOUND"},
        },
        "explicit_non_claims": ["not canonical C0.3 governed graph traverse unless spine traverse ran"],
    }
    out = overlay_spine_graph_authority_on_bridge(
        bridge,
        spine_graph_expansion_refs=["ref:graph:node:skill_test"],
    )
    assert out["proof_pool_shim_only"] is False
    assert out["canonical_c0_3_claimed"] is True
    pa = out["pa_proof_authority_metadata"]
    assert pa["c03_graphrag_bound_status"] == "BOUND"
    assert pa.get("spine_graph_authority") is True
