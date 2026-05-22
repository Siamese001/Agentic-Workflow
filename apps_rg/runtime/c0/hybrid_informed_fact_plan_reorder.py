"""W2B — hybrid-informed reorder of ledger-selected facts (ordering only, H4 law)."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem

HYBRID_INFORMED_ORDER_SUFFIX = "+hybrid_informed_order_v1"
_FACT_ID_TOKEN_RE = re.compile(r"\bfact_[a-z0-9_]+\b", re.IGNORECASE)


def _ledger_fact_ids_from_item(item: EvidenceItem) -> list[str]:
    """Resolve ledger ``fact_*`` ids from hybrid enrichment carriers."""
    seen: set[str] = set()
    ordered: list[str] = []
    blobs = (
        str(item.source_id or ""),
        str(item.citation_anchor or ""),
        str(item.fact_vec_ref or ""),
        str(item.content or ""),
        str(item.source or ""),
    )
    for blob in blobs:
        for token in _FACT_ID_TOKEN_RE.findall(blob):
            tid = token.lower()
            if tid.startswith("fact_") and tid not in seen:
                seen.add(tid)
                ordered.append(tid)
    sid = str(item.source_id or "").strip()
    if sid.startswith("fact_") and sid not in seen:
        ordered.insert(0, sid)
    return ordered


def hybrid_score_map_from_enrichment(
    enrichment_items: Sequence[EvidenceItem | Mapping[str, Any]],
    *,
    allowed_fact_ids: set[str] | None = None,
) -> dict[str, float]:
    """Map fact/source ids to max hybrid score from non-authoritative enrichment hits."""
    scores: dict[str, float] = {}
    for raw in enrichment_items:
        if isinstance(raw, EvidenceItem):
            item = raw
        elif isinstance(raw, Mapping):
            item = EvidenceItem(
                source=str(raw.get("source") or ""),
                content=str(raw.get("content") or ""),
                source_id=str(raw.get("source_id") or ""),
                confidence_score=float(raw.get("confidence_score") or 0.0),
                dense_score=float(raw.get("dense_score") or 0.0),
                bm25_score=float(raw.get("bm25_score") or 0.0),
            )
        else:
            continue
        score = max(
            float(item.confidence_score or 0.0),
            float(item.dense_score or 0.0),
            float(item.bm25_score or 0.0),
        )
        fact_ids = _ledger_fact_ids_from_item(item)
        if not fact_ids:
            sid = str(item.source_id or "").strip()
            if sid:
                fact_ids = [sid]
        for fid in fact_ids:
            key = fid
            if allowed_fact_ids is not None:
                if fid not in allowed_fact_ids:
                    by_lower = {a.lower(): a for a in allowed_fact_ids}
                    key = by_lower.get(fid.lower())
                    if not key:
                        continue
                else:
                    key = fid
            scores[key] = max(scores.get(key, 0.0), score)
    return scores


def _fact_ids_from_plan(plan: Mapping[str, Any]) -> set[str]:
    out: set[str] = set()
    for fact in plan.get("facts") or []:
        if not isinstance(fact, Mapping):
            continue
        fid = str(fact.get("fact_id") or fact.get("candidate_fact_id") or "").strip()
        if fid:
            out.add(fid)
    return out


def reorder_selected_fact_plan_by_hybrid_scores(
    plan: dict[str, Any],
    *,
    score_by_fact_id: Mapping[str, float],
) -> dict[str, Any]:
    """Reorder ``facts`` by hybrid score; preserve id set and per-fact fields (H4)."""
    facts = list(plan.get("facts") or [])
    if not facts or not score_by_fact_id:
        return plan

    id_set_before = _fact_ids_from_plan(plan)
    if not id_set_before:
        return plan

    def _score_for(fact: Mapping[str, Any]) -> float:
        fid = str(fact.get("fact_id") or fact.get("candidate_fact_id") or "").strip()
        return float(score_by_fact_id.get(fid, 0.0))

    sorted_facts = sorted(
        facts,
        key=lambda f: (-_score_for(f), str(f.get("fact_id") or "")),
    )
    id_set_after = _fact_ids_from_plan({"facts": sorted_facts})
    if id_set_before != id_set_after:
        raise ValueError("hybrid_informed_reorder: allowed_fact_ids set changed")

    method = str(plan.get("selection_method") or "").strip()
    if HYBRID_INFORMED_ORDER_SUFFIX not in method:
        method = f"{method}{HYBRID_INFORMED_ORDER_SUFFIX}" if method else HYBRID_INFORMED_ORDER_SUFFIX.lstrip("+")

    new_plan = dict(plan)
    new_plan["facts"] = sorted_facts
    new_plan["required_fact_ids"] = [
        str(f.get("fact_id") or "") for f in sorted_facts if f.get("fact_id")
    ]
    new_plan["selection_method"] = method
    new_plan["hybrid_informed_reorder"] = {
        "applied": True,
        "scored_fact_count": len(score_by_fact_id),
        "fact_count": len(sorted_facts),
    }
    return new_plan


def apply_hybrid_informed_fact_plan_reorder(
    plan: dict[str, Any],
    *,
    hybrid_doc: Mapping[str, Any],
) -> dict[str, Any]:
    """Apply W2B reorder from ``perform_product_hybrid_retrieval`` output document."""
    items = list(hybrid_doc.get("enrichment_items") or [])
    allowed = _fact_ids_from_plan(plan)
    scores = hybrid_score_map_from_enrichment(items, allowed_fact_ids=allowed or None)
    if not scores:
        return plan
    reordered = reorder_selected_fact_plan_by_hybrid_scores(plan, score_by_fact_id=scores)
    matched = [fid for fid in allowed if fid in scores]
    reordered.setdefault("hybrid_informed_reorder", {})
    if isinstance(reordered.get("hybrid_informed_reorder"), dict):
        reordered["hybrid_informed_reorder"]["matched_fact_ids"] = matched
    return reordered


__all__ = [
    "apply_hybrid_informed_fact_plan_reorder",
    "hybrid_score_map_from_enrichment",
    "reorder_selected_fact_plan_by_hybrid_scores",
]
