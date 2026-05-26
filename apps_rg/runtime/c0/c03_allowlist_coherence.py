"""Executive-summary C03/FEC allowlist coherence (pool-wins SSOT)."""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.c03_graph_sqlite_context import PROOF_CLASSIFICATION

AUTHORITY_CLASS_GRAPH_TARGETING_NON_PROOF = "GRAPH_TARGETING_NON_PROOF"

GRAPH_NON_PROOF_STAMP: dict[str, Any] = {
    "authority_class": AUTHORITY_CLASS_GRAPH_TARGETING_NON_PROOF,
    "proof_classification": PROOF_CLASSIFICATION,
    "claim_support_allowed": False,
}


def fact_id_base(fid: str) -> str:
    s = str(fid or "").strip()
    return s.split("_metric_", 1)[0] if "_metric_" in s else s


def fact_id_in_allowed_pool(fid: str, allowed_fact_ids: set[str]) -> bool:
    s = str(fid or "").strip()
    if not s or not allowed_fact_ids:
        return False
    if s in allowed_fact_ids:
        return True
    base = fact_id_base(s)
    if base in allowed_fact_ids:
        return True
    for aid in allowed_fact_ids:
        if fact_id_base(aid) == base:
            return True
    return False


def stamp_graph_non_proof(doc: dict[str, Any]) -> dict[str, Any]:
    out = dict(doc)
    out.update(GRAPH_NON_PROOF_STAMP)
    return out


def _fact_id_from_evidence_item(item: dict[str, Any]) -> str:
    for key in ("source_fact_id", "fact_id"):
        val = str(item.get(key) or "").strip()
        if val:
            return val
    ref = str(item.get("graph_node_ref") or "")
    if ref.startswith("node_fact:"):
        return ref.split(":", 1)[1]
    if ref.startswith("node_fact_"):
        return ref[len("node_fact_") :]
    eid = str(item.get("evidence_id") or "")
    if eid.startswith("evidence:track_weighted:"):
        return eid.split(":", 2)[-1]
    if eid.startswith("evidence:graph:"):
        return eid.split(":", 2)[-1]
    return ""


def collect_expansion_fact_ids(
    *,
    c03_bound: dict[str, Any] | None,
    track_expansion: dict[str, Any] | None,
) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for src in (track_expansion, c03_bound):
        if not isinstance(src, dict):
            continue
        for key in ("c03_selected_fact_ids",):
            for fid in src.get(key) or []:
                s = str(fid).strip()
                if s and s not in seen:
                    seen.add(s)
                    out.append(s)
        for f in src.get("selected_facts") or []:
            if isinstance(f, dict):
                s = str(f.get("fact_id") or "").strip()
                if s and s not in seen:
                    seen.add(s)
                    out.append(s)
    if isinstance(c03_bound, dict):
        snap = c03_bound.get("final_evidence_contract_snapshot")
        if isinstance(snap, dict):
            for it in snap.get("evidence_items") or []:
                if isinstance(it, dict):
                    s = _fact_id_from_evidence_item(it)
                    if s and s not in seen:
                        seen.add(s)
                        out.append(s)
    return out


def filter_c03_evidence_to_allowed_pool(
    c03_bound: dict[str, Any],
    allowed_fact_ids: set[str],
    *,
    track_expansion: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Strip claimable evidence outside ``allowed_fact_ids``; stamp non-proof graph fields."""
    allowed = {str(x).strip() for x in allowed_fact_ids if str(x).strip()}
    expansion_ids = collect_expansion_fact_ids(c03_bound=c03_bound, track_expansion=track_expansion)
    filtered_out = sorted({fid for fid in expansion_ids if not fact_id_in_allowed_pool(fid, allowed)})
    context_ids = list(filtered_out)
    claimable_expansion = sorted(
        {fid for fid in expansion_ids if fact_id_in_allowed_pool(fid, allowed)}
    )

    out = stamp_graph_non_proof(dict(c03_bound))
    snap = dict(out.get("final_evidence_contract_snapshot") or {})
    items_in = list(snap.get("evidence_items") or [])
    kept: list[dict[str, Any]] = []
    dropped: list[str] = []
    for it in items_in:
        if not isinstance(it, dict):
            continue
        fid = _fact_id_from_evidence_item(it)
        if fid and not fact_id_in_allowed_pool(fid, allowed):
            dropped.append(fid)
            continue
        row = dict(it)
        row.setdefault("claim_support_allowed", True)
        kept.append(row)
    snap["evidence_items"] = kept
    snap["evidence_items_count"] = len(kept)
    out["final_evidence_contract_snapshot"] = snap
    out["evidence_items_count"] = len(kept)

    if isinstance(track_expansion, dict):
        te = dict(track_expansion)
        te["c03_selected_fact_ids"] = claimable_expansion
        te["c03_context_fact_ids"] = context_ids
        te["c03_filtered_out_fact_ids"] = filtered_out
        te.update(GRAPH_NON_PROOF_STAMP)
        track_expansion_out = te
    else:
        track_expansion_out = track_expansion

    receipt = {
        "allowlist_policy": "pool_wins",
        "allowed_fact_ids": sorted(allowed),
        "c03_context_fact_ids": context_ids,
        "c03_filtered_out_fact_ids": filtered_out,
        "promoted_fact_ids": [],
        "c03_selected_fact_ids_claimable": claimable_expansion,
        "allowlist_mismatch": False,
        "c03_expansion_surplus_fact_ids": filtered_out,
        "dropped_evidence_item_fact_ids": sorted(set(dropped)),
    }
    return out, receipt


def check_claimable_evidence_subset(
    evidence_items: list[dict[str, Any]],
    allowed_fact_ids: set[str],
) -> tuple[bool, list[str]]:
    """True when every claimable evidence item references an allowed fact_id."""
    violations: list[str] = []
    for it in evidence_items:
        if not isinstance(it, dict):
            continue
        if it.get("claim_support_allowed") is False:
            continue
        fid = _fact_id_from_evidence_item(it)
        if fid and not fact_id_in_allowed_pool(fid, allowed_fact_ids):
            violations.append(fid)
    return (len(violations) == 0, sorted(set(violations)))


def build_exec_summary_allowlist_receipt(
    *,
    allowed_fact_ids: set[str],
    allowlist_filter_receipt: dict[str, Any],
    track_expansion: dict[str, Any] | None,
    proof_pool_digest: str,
    jd_text: str = "",
) -> dict[str, Any]:
    from apps_rg.runtime.c0.c03_promotion_candidates import build_c03_promotion_candidates_receipt
    from apps_rg.runtime.validators.executive_summary_x2 import resolve_utilization_waived_fact_ids

    skill_ids: list[str] = []
    if isinstance(track_expansion, dict):
        skill_ids = sorted(
            {str(x).strip() for x in (track_expansion.get("c03_selected_skill_ids") or []) if str(x).strip()}
        )
    waived = sorted(resolve_utilization_waived_fact_ids(allowed_fact_ids))
    filtered_out = list(allowlist_filter_receipt.get("c03_filtered_out_fact_ids") or [])
    promotion = build_c03_promotion_candidates_receipt(
        filtered_out_fact_ids=filtered_out,
        allowed_fact_ids=allowed_fact_ids,
        track_expansion=track_expansion,
        jd_text=jd_text,
    )
    return {
        **allowlist_filter_receipt,
        "proof_pool_digest": proof_pool_digest,
        "graph_targeting_skill_ids": skill_ids,
        "dg1_decision": "A",
        "waived_fact_ids": waived,
        "utilization_policy": "fact_certs_waived_by_default",
        "c03_promotion_candidates": promotion,
    }


def assert_pre_l2_allowlist_coherence(
    *,
    allowed_fact_ids: set[str],
    c03_bound: dict[str, Any] | None,
    track_expansion: dict[str, Any] | None,
    runtime_payload: dict[str, Any] | None = None,
) -> str | None:
    """Return block reason when claimable evidence escapes the pool; else None."""
    items: list[dict[str, Any]] = []
    if isinstance(c03_bound, dict):
        snap = c03_bound.get("final_evidence_contract_snapshot")
        if isinstance(snap, dict):
            items.extend(list(snap.get("evidence_items") or []))
    if isinstance(runtime_payload, dict):
        plan = runtime_payload.get("selected_fact_plan") or {}
        for fact in plan.get("facts") or []:
            if isinstance(fact, dict):
                fid = str(fact.get("fact_id") or "").strip()
                if fid:
                    items.append(
                        {
                            "source_fact_id": fid,
                            "claim_support_allowed": True,
                        }
                    )
    ok, violations = check_claimable_evidence_subset(items, allowed_fact_ids)
    if ok:
        return None
    return (
        "exec_summary_allowlist_coherence:blocked:"
        f"claimable_fact_ids_outside_pool={violations}"
    )


__all__ = [
    "AUTHORITY_CLASS_GRAPH_TARGETING_NON_PROOF",
    "GRAPH_NON_PROOF_STAMP",
    "_fact_id_from_evidence_item",
    "assert_pre_l2_allowlist_coherence",
    "build_exec_summary_allowlist_receipt",
    "check_claimable_evidence_subset",
    "collect_expansion_fact_ids",
    "fact_id_base",
    "fact_id_in_allowed_pool",
    "filter_c03_evidence_to_allowed_pool",
    "stamp_graph_non_proof",
]
