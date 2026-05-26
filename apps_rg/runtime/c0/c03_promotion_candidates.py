"""Read-only C0.3 promotion transparency (DG-1=A pool-wins; no auto-promote)."""
from __future__ import annotations

from typing import Any

from apps_rg.runtime.c0.c03_allowlist_coherence import fact_id_base
from apps_rg.runtime.graph_selection_rationale import extract_jd_keyword_hits

SCHEMA = "c03_promotion_candidates_v1"
REASON_POOL_WINS_DG1_A = "pool_wins_dg1_a"
PROMOTION_ELIGIBLE_DEFAULT = False


def _index_expansion_facts(track_expansion: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    if not isinstance(track_expansion, dict):
        return out
    for entry in track_expansion.get("selected_facts") or []:
        if not isinstance(entry, dict):
            continue
        fid = str(entry.get("fact_id") or "").strip()
        if not fid:
            continue
        out[fid] = entry
        base = fact_id_base(fid)
        if base not in out:
            out[base] = entry
    return out


def _hop_edge_distance(hop_path: list[Any] | None) -> int | None:
    if not hop_path:
        return None
    return max(0, len(hop_path) - 1)


def jd_keyword_overlap_for_fact(
    *,
    fact_id: str,
    career_track: str | None,
    jd_text: str,
) -> dict[str, Any]:
    """Score JD relevance for operator transparency (not promotion authority)."""
    jd = jd_text.strip()
    if not jd:
        return {
            "score": 0.0,
            "career_track": career_track,
            "keywords_matched": [],
            "fact_tokens_in_jd": [],
        }
    hits = extract_jd_keyword_hits(jd)
    track_keywords: list[str] = []
    if career_track:
        for hit in hits:
            if str(hit.get("track_id") or "") == career_track:
                track_keywords.extend(str(k) for k in (hit.get("keywords_matched") or []))
    jd_lower = jd.lower()
    fact_tokens = [
        t
        for t in fact_id.replace("fact_", "").split("_")
        if len(t) >= 4 and t.lower() in jd_lower
    ]
    keywords = sorted({k.lower() for k in track_keywords + fact_tokens})
    score = min(1.0, 0.35 * bool(track_keywords) + 0.15 * len(keywords))
    if track_keywords and fact_tokens:
        score = min(1.0, score + 0.1)
    return {
        "score": round(score, 4),
        "career_track": career_track,
        "keywords_matched": keywords,
        "fact_tokens_in_jd": sorted(set(fact_tokens)),
    }


def build_c03_promotion_candidate_row(
    *,
    fact_id: str,
    track_expansion: dict[str, Any] | None,
    track_weights: dict[str, float] | None,
    jd_text: str,
    promotion_eligible: bool = PROMOTION_ELIGIBLE_DEFAULT,
    reason: str = REASON_POOL_WINS_DG1_A,
) -> dict[str, Any]:
    idx = _index_expansion_facts(track_expansion)
    entry = idx.get(fact_id) or idx.get(fact_id_base(fact_id)) or {}
    career_track = str(entry.get("career_track") or "").strip() or None
    hop = entry.get("graph_hop_path")
    hop_list = hop if isinstance(hop, list) else None
    weights = track_weights if isinstance(track_weights, dict) else {}
    tw = float(weights.get(career_track or "", 0.0)) if career_track else 0.0
    overlap = jd_keyword_overlap_for_fact(
        fact_id=fact_id,
        career_track=career_track,
        jd_text=jd_text,
    )
    return {
        "fact_id": fact_id,
        "career_track": career_track,
        "track_weight": round(tw, 6),
        "jd_keyword_overlap": overlap,
        "edge_distance": _hop_edge_distance(hop_list),
        "graph_hop_steps": len(hop_list) if hop_list else 0,
        "skill_id": str(entry.get("skill_id") or "").strip() or None,
        "promotion_eligible": promotion_eligible,
        "reason": reason,
    }


def build_c03_promotion_candidates_receipt(
    *,
    filtered_out_fact_ids: list[str],
    allowed_fact_ids: set[str] | list[str],
    track_expansion: dict[str, Any] | None = None,
    jd_text: str = "",
    dg1_decision: str = "A",
    allowlist_policy: str = "pool_wins",
) -> dict[str, Any]:
    """Build read-only promotion transparency receipt (never mutates allowed pool)."""
    allowed = sorted({str(x).strip() for x in allowed_fact_ids if str(x).strip()})
    filtered = sorted({str(x).strip() for x in filtered_out_fact_ids if str(x).strip()})
    weights: dict[str, float] | None = None
    role_family_key: str | None = None
    if isinstance(track_expansion, dict):
        raw_w = track_expansion.get("track_weights")
        if isinstance(raw_w, dict):
            weights = {str(k): float(v) for k, v in raw_w.items()}
        role_family_key = str(track_expansion.get("role_family_key") or "").strip() or None

    candidates = [
        build_c03_promotion_candidate_row(
            fact_id=fid,
            track_expansion=track_expansion,
            track_weights=weights,
            jd_text=jd_text,
        )
        for fid in filtered
    ]
    return {
        "schema": SCHEMA,
        "dg1_decision": dg1_decision,
        "allowlist_policy": allowlist_policy,
        "promoted_fact_ids": [],
        "allowed_fact_ids": allowed,
        "c03_filtered_out_fact_ids": filtered,
        "c03_context_fact_ids": filtered,
        "candidate_count": len(candidates),
        "candidates": candidates,
        "auto_promote_enabled": False,
        "promotion_eligible_default": PROMOTION_ELIGIBLE_DEFAULT,
        "default_reason": REASON_POOL_WINS_DG1_A,
        "role_family_key": role_family_key,
        "operator_note": (
            "Filtered neighbors remain graph context only under DG-1=A; "
            "promotion requires separate Author-Gate plan."
        ),
    }


__all__ = [
    "REASON_POOL_WINS_DG1_A",
    "SCHEMA",
    "build_c03_promotion_candidate_row",
    "build_c03_promotion_candidates_receipt",
    "jd_keyword_overlap_for_fact",
]
