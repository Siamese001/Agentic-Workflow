"""Whole-run resume spine skill bundle (graph-skills quality W5 / D5)."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.proof_pool_resolver import SectionProofPool, resolve_section_proof_pool

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
BUNDLE_SCHEMA = "resume_spine_skill_bundle_v1"


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _skill_rows_from_pool(pool: SectionProofPool) -> list[dict[str, Any]]:
    meta = pool.proof_pool_metadata if isinstance(pool.proof_pool_metadata, dict) else {}
    rows: list[dict[str, Any]] = []
    for raw in meta.get("selected_skill_rows") or meta.get("skill_rows") or []:
        if isinstance(raw, dict) and raw.get("skill_id"):
            rows.append(dict(raw))
    track = meta.get("track_weighted_graph_expansion") or {}
    for sk in track.get("selected_skills") or []:
        if not isinstance(sk, dict):
            continue
        sid = str(sk.get("skill_id") or "").strip()
        if not sid:
            continue
        fid = str(sk.get("fact_id") or "").strip()
        links = [fid] if fid else []
        if not links:
            hop = sk.get("graph_hop_path") or []
            if isinstance(hop, list) and hop:
                links = [str(hop[-1])]
        rows.append(
            {
                "skill_id": sid,
                "fact_id_links": links,
                "graph_hop_path": sk.get("graph_hop_path"),
                "career_track": sk.get("career_track"),
                "pillar": sk.get("pillar"),
            }
        )
    for sid in meta.get("c03_selected_skill_ids") or []:
        text = str(sid).strip()
        if text and not any(str(r.get("skill_id")) == text for r in rows):
            rows.append({"skill_id": text, "fact_id_links": []})
    return rows


def _dedupe_skill_rows(per_lane_rows: dict[str, list[dict[str, Any]]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Merge per-lane skill rows; return (bundle_rows, dedupe_receipt_rows)."""
    by_id: dict[str, dict[str, Any]] = {}
    collisions: list[dict[str, Any]] = []
    for lane, rows in per_lane_rows.items():
        for row in rows:
            sid = str(row.get("skill_id") or "").strip()
            if not sid:
                continue
            existing = by_id.get(sid)
            if existing is None:
                by_id[sid] = {
                    "skill_id": sid,
                    "lanes": [lane],
                    "fact_id_links": sorted(
                        {str(x) for x in (row.get("fact_id_links") or []) if str(x).strip()}
                    ),
                    "activation_status": row.get("activation_status"),
                    "graph_hop_path": row.get("graph_hop_path"),
                }
                continue
            lanes = list(existing.get("lanes") or [])
            if lane not in lanes:
                lanes.append(lane)
            existing["lanes"] = sorted(lanes)
            new_links = {str(x) for x in (row.get("fact_id_links") or []) if str(x).strip()}
            old_links = set(existing.get("fact_id_links") or [])
            if new_links != old_links:
                collisions.append(
                    {
                        "skill_id": sid,
                        "reason_code": "fact_id_links_diverge_across_lanes",
                        "lane": lane,
                        "existing_links": sorted(old_links),
                        "incoming_links": sorted(new_links),
                    }
                )
            existing["fact_id_links"] = sorted(old_links | new_links)
    bundle_rows = sorted(by_id.values(), key=lambda r: str(r.get("skill_id")))
    return bundle_rows, collisions


def build_resume_spine_skill_bundle(
    *,
    repo_root: Any,
    lanes: tuple[str, ...] = GENERATED_LANES,
    target_company: str = "Brown & Brown",
    target_role: str = "SVP IT Strategy & Innovation",
    jd_text: str = "",
    briefing_text: str = "",
) -> dict[str, Any]:
    """Aggregate graph-selected skills across generated lanes with dedupe matrix."""
    from pathlib import Path

    root = Path(repo_root)
    per_lane: dict[str, Any] = {}
    per_lane_rows: dict[str, list[dict[str, Any]]] = {}
    for lane in lanes:
        pool = resolve_section_proof_pool(
            section=lane,
            repo_root=root,
            product_visible=False,
            target_company=target_company,
            target_role=target_role,
            jd_text=jd_text,
            briefing_text=briefing_text,
        )
        rows = _skill_rows_from_pool(pool)
        per_lane_rows[lane] = rows
        per_lane[lane] = {
            "allowed_fact_count": len(pool.allowed_fact_ids_ordered),
            "skill_row_count": len(rows),
            "proof_source": pool.proof_source,
            "selection_method": (pool.selected_fact_plan or {}).get("selection_method"),
        }

    bundle_rows, collisions = _dedupe_skill_rows(per_lane_rows)
    payload = {
        "schema": BUNDLE_SCHEMA,
        "plan_id": PLAN_ID,
        "generated_at": _utc_now(),
        "lanes": list(lanes),
        "per_lane_summary": per_lane,
        "skill_rows": bundle_rows,
        "unique_skill_count": len(bundle_rows),
        "dedupe_collision_count": len(collisions),
        "dedupe_collisions": collisions,
        "dedupe_pass": len(collisions) == 0,
    }
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    payload["bundle_digest"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    return payload


__all__ = ["BUNDLE_SCHEMA", "PLAN_ID", "build_resume_spine_skill_bundle"]
