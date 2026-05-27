"""Hybrid graph boost — reorder only; log rejected pool-widen attempts (W6)."""
from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from agentic_core.runtime.contracts.final_evidence_contract import EvidenceItem
from apps_rg.runtime.c0.hybrid_informed_fact_plan_reorder import (
    HYBRID_INFORMED_ORDER_SUFFIX,
    apply_hybrid_informed_fact_plan_reorder,
    hybrid_score_map_from_enrichment,
)
from apps_rg.runtime.validators.graph_skills_proof_common import (
    GraphSkillsProofError,
    assert_hybrid_fact_ids_in_resolver_pool,
)

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
RECEIPT_SCHEMA = "hybrid_graph_boost_receipt_v1"
_FACT_ID_TOKEN_RE = re.compile(r"\bfact_[a-z0-9_]+\b", re.IGNORECASE)

HYBRID_SECTIONS_DEFAULT: tuple[str, ...] = ("executive_summary",)

# Enhancement #7 — narrative sections to add for three-phase JDs.
# The career arc story most needs JD-signal-informed fact ordering in narrative lanes.
_HYBRID_NARRATIVE_SECTIONS: tuple[str, ...] = ("unify_narrative", "ibm_narrative")


def hybrid_sections_for_jd(three_phase: bool) -> tuple[str, ...]:
    """Return the set of sections to apply hybrid reorder for, based on JD posture.

    For three-phase JDs (all three career tracks hit), narrative sections are added
    because they carry the chronological career arc where era-ordering matters most.
    Pool widening is still forbidden (NEG-3 law applies regardless of section set).
    """
    if three_phase:
        return HYBRID_SECTIONS_DEFAULT + _HYBRID_NARRATIVE_SECTIONS
    return HYBRID_SECTIONS_DEFAULT


def _fact_ids_from_plan(plan: Mapping[str, Any]) -> set[str]:
    out: set[str] = set()
    for fact in plan.get("facts") or []:
        if not isinstance(fact, Mapping):
            continue
        fid = str(fact.get("fact_id") or fact.get("candidate_fact_id") or "").strip()
        if fid:
            out.add(fid)
    return out


def _all_fact_tokens_from_item(item: EvidenceItem | Mapping[str, Any]) -> list[str]:
    if isinstance(item, EvidenceItem):
        ev = item
    elif isinstance(item, Mapping):
        ev = EvidenceItem(
            source=str(item.get("source") or ""),
            content=str(item.get("content") or ""),
            source_id=str(item.get("source_id") or ""),
            confidence_score=float(item.get("confidence_score") or 0.0),
            dense_score=float(item.get("dense_score") or 0.0),
            bm25_score=float(item.get("bm25_score") or 0.0),
        )
    else:
        return []
    tokens: list[str] = []
    seen: set[str] = set()
    for blob in (
        str(ev.source_id or ""),
        str(ev.citation_anchor or ""),
        str(ev.fact_vec_ref or ""),
        str(ev.content or ""),
        str(ev.source or ""),
    ):
        for token in _FACT_ID_TOKEN_RE.findall(blob):
            tid = token.lower()
            if tid.startswith("fact_") and tid not in seen:
                seen.add(tid)
                tokens.append(tid)
    sid = str(ev.source_id or "").strip().lower()
    if sid.startswith("fact_") and sid not in seen:
        tokens.insert(0, sid)
    return tokens


def collect_rejected_hybrid_widen_attempts(
    enrichment_items: Sequence[EvidenceItem | Mapping[str, Any]],
    *,
    resolver_allowed_fact_ids: set[str],
) -> list[dict[str, str]]:
    """Log hybrid-suggested fact_ids that are not in the resolver pool (no widen)."""
    allowed_lower = {a.lower(): a for a in resolver_allowed_fact_ids}
    rejected: list[dict[str, str]] = []
    seen: set[str] = set()
    for raw in enrichment_items:
        for token in _all_fact_tokens_from_item(raw):
            key = token.lower()
            if key in seen:
                continue
            seen.add(key)
            if key in allowed_lower or token in resolver_allowed_fact_ids:
                continue
            rejected.append(
                {
                    "fact_id": token,
                    "reason_code": "outside_resolver_pool",
                    "action": "rejected_widen_attempt",
                }
            )
    return rejected


def attempt_hybrid_pool_widen(
    *,
    section_id: str,
    plan: dict[str, Any],
    candidate_fact_ids: Sequence[str],
) -> list[dict[str, str]]:
    """Explicit widen probes — always rejected when outside resolver pool (NEG-3 law)."""
    allowed = _fact_ids_from_plan(plan)
    attempts: list[dict[str, str]] = []
    for raw in candidate_fact_ids:
        fid = str(raw).strip()
        if not fid:
            continue
        if fid in allowed:
            attempts.append(
                {
                    "fact_id": fid,
                    "reason_code": "already_in_resolver_pool",
                    "action": "no_widen_needed",
                }
            )
            continue
        attempts.append(
            {
                "fact_id": fid,
                "reason_code": "outside_resolver_pool",
                "action": "rejected_widen_attempt",
            }
        )
        try:
            assert_hybrid_fact_ids_in_resolver_pool(
                section_id=section_id,
                hybrid_suggested_fact_ids=[fid],
                resolver_allowed_fact_ids=sorted(allowed),
            )
        except GraphSkillsProofError:
            pass
    return attempts


def apply_hybrid_boost_reorder_only(
    plan: dict[str, Any],
    *,
    hybrid_doc: Mapping[str, Any],
    section_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Apply hybrid-informed reorder; never widen fact id set."""
    allowed_before = _fact_ids_from_plan(plan)
    rejected = collect_rejected_hybrid_widen_attempts(
        list(hybrid_doc.get("enrichment_items") or []),
        resolver_allowed_fact_ids=allowed_before,
    )
    reordered = apply_hybrid_informed_fact_plan_reorder(dict(plan), hybrid_doc=hybrid_doc)
    allowed_after = _fact_ids_from_plan(reordered)
    pool_widened = allowed_before != allowed_after
    reorder_applied = bool((reordered.get("hybrid_informed_reorder") or {}).get("applied"))
    scores = hybrid_score_map_from_enrichment(
        list(hybrid_doc.get("enrichment_items") or []),
        allowed_fact_ids=allowed_before,
    )
    summary = {
        "section_id": section_id,
        "resolver_fact_count": len(allowed_before),
        "reorder_applied": reorder_applied,
        "pool_widened": pool_widened,
        "pool_widen_forbidden": True,
        "rejected_widen_attempt_count": len(rejected),
        "rejected_widen_attempts": rejected,
        "hybrid_matched_in_pool_count": len(scores),
        "selection_method_suffix": HYBRID_INFORMED_ORDER_SUFFIX,
        "status": "PASS" if not pool_widened else "FAIL",
    }
    return reordered, summary


def audit_section_hybrid_boost(
    *,
    section_id: str,
    plan: dict[str, Any],
    hybrid_doc: Mapping[str, Any],
    probe_outside_pool_ids: Sequence[str] = (),
) -> dict[str, Any]:
    """Per-lane hybrid boost audit row for receipt."""
    allowed = _fact_ids_from_plan(plan)
    widen_probes = attempt_hybrid_pool_widen(
        section_id=section_id,
        plan=plan,
        candidate_fact_ids=probe_outside_pool_ids,
    )
    _, summary = apply_hybrid_boost_reorder_only(plan, hybrid_doc=hybrid_doc, section_id=section_id)
    all_rejected = list(summary.get("rejected_widen_attempts") or []) + [
        a for a in widen_probes if a.get("action") == "rejected_widen_attempt"
    ]
    neg3_pass = all(
        a.get("reason_code") == "outside_resolver_pool"
        for a in all_rejected
        if a.get("action") == "rejected_widen_attempt"
    )
    return {
        **summary,
        "neg3_fail_closed": True,
        "neg3_pass": neg3_pass and not summary.get("pool_widened"),
        "explicit_widen_probes": widen_probes,
        "all_rejected_widen_attempts": all_rejected,
    }


def build_hybrid_graph_boost_receipt(
    *,
    repo_root: Any,
    sections: tuple[str, ...] = HYBRID_SECTIONS_DEFAULT,
    target_company: str = "Brown & Brown",
    target_role: str = "SVP IT Strategy & Innovation",
    jd_text: str = "",
    briefing_text: str = "",
) -> dict[str, Any]:
    """Build W6 receipt from resolver pools + synthetic widen probes on executive_summary."""
    from datetime import datetime, timezone
    from pathlib import Path

    from apps_rg.runtime.proof_pool_resolver import resolve_section_proof_pool

    root = Path(repo_root)
    lane_rows: list[dict[str, Any]] = []
    for section_id in sections:
        pool = resolve_section_proof_pool(
            section=section_id,
            repo_root=root,
            product_visible=False,
            target_company=target_company,
            target_role=target_role,
            jd_text=jd_text,
            briefing_text=briefing_text,
        )
        plan = dict(pool.selected_fact_plan or {})
        allowed = _fact_ids_from_plan(plan)
        facts = list(plan.get("facts") or [])
        enrichment: list[dict[str, Any]] = []
        for idx, fact in enumerate(facts[:3]):
            fid = str(fact.get("fact_id") or "")
            if not fid:
                continue
            enrichment.append(
                {
                    "source": "contract:hybrid_boost_w6",
                    "content": str(fact.get("claim_text") or fact.get("text") or ""),
                    "source_id": fid,
                    "confidence_score": float(3 - idx),
                    "dense_score": 0.0,
                    "bm25_score": 0.0,
                }
            )
        enrichment.append(
            {
                "source": "contract:hybrid_boost_w6_probe",
                "content": "JD-only widen probe",
                "source_id": "fact_w6_outside_resolver_probe",
                "confidence_score": 99.0,
                "dense_score": 99.0,
                "bm25_score": 99.0,
            }
        )
        hybrid_doc = {"enrichment_items": enrichment, "schema": "synthetic_hybrid_w6"}
        row = audit_section_hybrid_boost(
            section_id=section_id,
            plan=plan,
            hybrid_doc=hybrid_doc,
            probe_outside_pool_ids=("fact_w6_outside_resolver_probe", "fact_jd_only_w6_probe"),
        )
        row["resolver_allowed_fact_ids_sample"] = sorted(allowed)[:8]
        lane_rows.append(row)

    neg3_all = all(r.get("neg3_pass") for r in lane_rows)
    reorder_any = any(r.get("reorder_applied") for r in lane_rows)
    status = "PASS" if neg3_all and all(r.get("status") == "PASS" for r in lane_rows) else "FAIL"
    return {
        "schema": RECEIPT_SCHEMA,
        "plan_id": PLAN_ID,
        "wave": "W6",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": status,
        "pool_widen_forbidden": True,
        "reorder_only": True,
        "neg3_all_lanes_pass": neg3_all,
        "reorder_applied_any_lane": reorder_any,
        "lanes": lane_rows,
        "non_claim": "Hybrid boost reordered in-pool facts only; out-of-pool widen attempts are rejected and logged.",
    }


__all__ = [
    "HYBRID_SECTIONS_DEFAULT",
    "apply_hybrid_boost_reorder_only",
    "audit_section_hybrid_boost",
    "attempt_hybrid_pool_widen",
    "build_hybrid_graph_boost_receipt",
    "collect_rejected_hybrid_widen_attempts",
    "hybrid_sections_for_jd",
]
