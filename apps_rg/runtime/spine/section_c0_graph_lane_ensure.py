"""Ensure ``c0_graph_lane_receipt.json`` is present after section spine C0 wiring."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.runtime.spine.c0_graph_lane_receipt import (
    C0_GRAPH_LANE_RECEIPT_ARTIFACT,
    build_c0_graph_lane_receipt_from_bridge,
    build_c0_graph_lane_receipt_from_spine_retrieve,
    emit_c0_graph_lane_receipt,
)


def ensure_section_c0_graph_lane_receipt(
    artifact_dir: Path | str,
    *,
    runtime_payload: dict[str, Any],
    section_id: str,
) -> Path:
    """Emit graph-lane receipt when missing; prefer spine retrieve receipt when live."""
    root = Path(artifact_dir)
    target = root / C0_GRAPH_LANE_RECEIPT_ARTIFACT
    if target.is_file():
        return target

    spine_rec = runtime_payload.get("spine_c0_retrieve_receipt")
    if isinstance(spine_rec, dict) and spine_rec:
        graph_receipt = build_c0_graph_lane_receipt_from_spine_retrieve(
            spine_rec,
            section_id=section_id,
        )
        return emit_c0_graph_lane_receipt(root, graph_receipt)

    spine_path = root / "section_spine_c0_retrieve_receipt.json"
    if spine_path.is_file():
        spine_rec = json.loads(spine_path.read_text(encoding="utf-8"))
        if isinstance(spine_rec, dict):
            graph_receipt = build_c0_graph_lane_receipt_from_spine_retrieve(
                spine_rec,
                section_id=section_id,
            )
            return emit_c0_graph_lane_receipt(root, graph_receipt)

    bridge = runtime_payload.get("section_fec_bridge")
    if isinstance(bridge, dict) and bridge:
        graph_receipt = build_c0_graph_lane_receipt_from_bridge(
            bridge,
            section_id=section_id,
        )
        return emit_c0_graph_lane_receipt(root, graph_receipt)

    bridge_path = root / "final_evidence_contract.json"
    if bridge_path.is_file():
        bridge_doc = json.loads(bridge_path.read_text(encoding="utf-8"))
        if isinstance(bridge_doc, dict):
            graph_receipt = build_c0_graph_lane_receipt_from_bridge(
                bridge_doc,
                section_id=section_id,
            )
            return emit_c0_graph_lane_receipt(root, graph_receipt)

    graph_receipt = build_c0_graph_lane_receipt_from_bridge(
        {"section_id": section_id},
        section_id=section_id,
    )
    return emit_c0_graph_lane_receipt(root, graph_receipt)


__all__ = ["ensure_section_c0_graph_lane_receipt"]
