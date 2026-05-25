"""D7 FEC ≡ resolver pool set equality (graph-skills quality W5)."""
from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from apps_rg.runtime.internal.generated_lane_rollup import GENERATED_LANES
from apps_rg.runtime.proof_pool_resolver import SectionProofPool
from apps_rg.runtime.spine.c0_fec_compose import SectionFecBridge, build_spine_c0_fec_artifact
from apps_rg.runtime.spine.front_contracts import build_section_front_spine_from_args

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"

# Six generated lanes (headline uses a distinct compact pool — excluded from strict D7 gate).
D7_SET_EQUALITY_LANES: tuple[str, ...] = tuple(
    lane for lane in GENERATED_LANES if lane != "headline"
)


def _default_args(**overrides: object) -> SimpleNamespace:
    base = {
        "target_company": "Brown & Brown",
        "target_title": "SVP IT Strategy & Innovation",
        "target_role": "SVP IT Strategy & Innovation",
        "jd_text": "Lead platform engineering and agentic AI systems.",
        "briefing": "Emphasize regulated delivery and innovation.",
        "base_resume_ref": "",
        "selected_role_fact_set": "",
    }
    base.update(overrides)
    return SimpleNamespace(**base)


def extract_fec_fact_ids(bridge_doc: dict[str, Any]) -> set[str]:
    """Fact IDs carried on the FEC bridge (canonical pool for PA)."""
    ids: set[str] = set()
    for raw in bridge_doc.get("source_fact_ids") or []:
        text = str(raw).strip()
        if text:
            ids.add(text)
    snap = bridge_doc.get("final_evidence_contract") or bridge_doc.get("final_evidence_contract_snapshot")
    if isinstance(snap, dict):
        for raw in snap.get("allowed_fact_ids") or []:
            text = str(raw).strip()
            if text:
                ids.add(text)
    for item in bridge_doc.get("evidence_items") or []:
        if not isinstance(item, dict):
            continue
        for key in ("source_fact_id", "fact_id"):
            text = str(item.get(key) or "").strip()
            if text:
                ids.add(text)
    return ids


def extract_resolver_fact_ids(pool: SectionProofPool) -> set[str]:
    return {str(x).strip() for x in pool.allowed_fact_ids_ordered if str(x).strip()}


def audit_d7_fec_resolver_set_equality(
    *,
    section_id: str,
    pool: SectionProofPool,
    bridge: SectionFecBridge,
) -> dict[str, Any]:
    """Strict D7 audit — fec_only and resolver_only must be empty for PASS."""
    resolver_ids = extract_resolver_fact_ids(pool)
    fec_ids = extract_fec_fact_ids(bridge.bridge_doc)
    fec_only = sorted(fec_ids - resolver_ids)
    resolver_only = sorted(resolver_ids - fec_ids)
    exclusions: list[dict[str, str]] = []
    for fid in fec_only:
        exclusions.append({"fact_id": fid, "reason_code": "fec_only_not_in_resolver"})
    for fid in resolver_only:
        exclusions.append({"fact_id": fid, "reason_code": "resolver_only_missing_from_fec"})
    set_equal = not fec_only and not resolver_only
    return {
        "lane": section_id,
        "schema": "graph_skills_fec_set_equality_v1",
        "plan_id": PLAN_ID,
        "fec_ids": sorted(fec_ids),
        "resolver_ids": sorted(resolver_ids),
        "fec_only_ids": fec_only,
        "resolver_only_ids": resolver_only,
        "fec_id_count": len(fec_ids),
        "resolver_id_count": len(resolver_ids),
        "set_equal": set_equal,
        "status": "PASS" if set_equal else "FAIL",
        "exclusions": exclusions,
    }


def build_lane_fec_bridge_for_audit(
    *,
    section_id: str,
    pool: SectionProofPool,
    repo_root: Any,
) -> SectionFecBridge:
    import os
    from pathlib import Path

    os.environ.setdefault("APPS_RG_SECTION_SPINE_C0_SKIP", "1")
    os.environ.setdefault("APPS_RG_C0_EVIDENCE_ROOM", "0")
    spine = build_section_front_spine_from_args(
        section_id=section_id,
        args=_default_args(),
        repo_root=Path(repo_root),
    )
    return build_spine_c0_fec_artifact(
        section_id=section_id,
        front_spine=spine,
        pool=pool,
    )


def audit_all_d7_lanes(
    *,
    repo_root: Any,
    lanes: tuple[str, ...] = D7_SET_EQUALITY_LANES,
    target_company: str = "Brown & Brown",
    target_role: str = "SVP IT Strategy & Innovation",
    jd_text: str = "",
    briefing_text: str = "",
) -> dict[str, Any]:
    from pathlib import Path

    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    root = Path(repo_root)
    lane_rows: list[dict[str, Any]] = []
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
        bridge = build_lane_fec_bridge_for_audit(section_id=lane, pool=pool, repo_root=root)
        lane_rows.append(audit_d7_fec_resolver_set_equality(section_id=lane, pool=pool, bridge=bridge))

    pass_count = sum(1 for r in lane_rows if r.get("status") == "PASS")
    target = len(lanes)
    return {
        "schema": "graph_skills_fec_set_equality_receipt_v1",
        "plan_id": PLAN_ID,
        "wave": "W5",
        "d7_lanes": list(lanes),
        "d7_pass_count": pass_count,
        "d7_target_count": target,
        "d7_all_pass": pass_count == target,
        "status": "PASS" if pass_count == target else "FAIL",
        "lanes": lane_rows,
    }


__all__ = [
    "D7_SET_EQUALITY_LANES",
    "audit_all_d7_lanes",
    "audit_d7_fec_resolver_set_equality",
    "build_lane_fec_bridge_for_audit",
    "extract_fec_fact_ids",
    "extract_resolver_fact_ids",
]
