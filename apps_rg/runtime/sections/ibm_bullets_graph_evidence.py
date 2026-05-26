"""Graph evidence constraints for ibm_bullets — Phase 2 career track only (IBM 2017–2022)."""
from __future__ import annotations

from typing import Any

from apps_rg.fact_inventory.track_weighted_graph_expansion import _skill_rows_by_id

# Phase 2 (Data / tech / Cloud / ML) — IBM stint 2017-04..2022-10 lies entirely in this track.
IBM_PHASE2_CAREER_TRACK = "track_data_tech_cloud_ml"
IBM_PHASE2_CAREER_TRACK_ID = "TRACK_DATA_TECH_CLOUD_ML"

IBM_EMPLOYMENT_START = "2017-04"
IBM_EMPLOYMENT_END = "2022-10"
IBM_EMPLOYMENT_WINDOW_LABEL = f"{IBM_EMPLOYMENT_START} to {IBM_EMPLOYMENT_END}"

IBM_PHASE2_TRACK_WEIGHT_OVERRIDE: dict[str, float] = {
    "track_actuarial_risk_derivatives": 0.0,
    "track_data_tech_cloud_ml": 1.0,
    "track_genai_agentic": 0.0,
}

IBM_TRACK_RANKED_SELECTION_METHOD = "augmented_skills_graph_ibm_bullets_phase2_track_ranked"

FORBIDDEN_IBM_BULLET_CAREER_TRACKS: frozenset[str] = frozenset(
    {
        "track_actuarial_risk_derivatives",
        "track_genai_agentic",
    }
)

IBM_BULLETS_MIN_PHASE2_FACTS = 5


def _claim_text_for_phase2_graph_fact(
    *,
    fact_id: str,
    ledger_row: dict[str, Any] | None,
    hop_entry: dict[str, Any] | None,
    graph: dict[str, Any],
) -> str:
    if ledger_row:
        claim = str(ledger_row.get("claim_text") or "").strip()
        if claim:
            return claim
    skill_id = str((hop_entry or {}).get("skill_id") or "").strip()
    if skill_id:
        skill = _skill_rows_by_id(graph).get(skill_id) or {}
        phrases = skill.get("allowed_phrases") or []
        if phrases:
            return str(phrases[0]).strip()
    return ""


def build_ibm_phase2_graph_plan_fact(
    *,
    fact_id: str,
    ledger_row: dict[str, Any] | None,
    hop_entry: dict[str, Any] | None,
    graph: dict[str, Any],
    section_id: str = "ibm_bullets",
) -> dict[str, Any] | None:
    """Plan fact from Phase 2 graph expansion (ledger row optional; graph hop required)."""
    from apps_rg.runtime.sections.selected_role_fact_set import slice_row_to_plan_fact

    hop = list((hop_entry or {}).get("graph_hop_path") or [])
    if not hop:
        return None
    claim = _claim_text_for_phase2_graph_fact(
        fact_id=fact_id,
        ledger_row=ledger_row,
        hop_entry=hop_entry,
        graph=graph,
    )
    if not claim:
        return None
    if ledger_row:
        conf = str(ledger_row.get("confidence") or "").strip().upper()
        vstat = str(ledger_row.get("verification_status") or "").strip()
        try:
            if conf == "HIGH" or (
                conf == "MEDIUM" and vstat == "eligible_medium_with_source_trace"
            ):
                fact = slice_row_to_plan_fact(ledger_row, section_id=section_id)
                fact["career_track"] = IBM_PHASE2_CAREER_TRACK
                fact["graph_hop_path"] = hop
                if hop_entry and hop_entry.get("skill_id"):
                    fact["skill_id"] = hop_entry.get("skill_id")
                fact["graph_phase2_track_proof"] = True
                return fact
        except ValueError:
            pass
    row = ledger_row or {}
    metrics = row.get("metric_values") or []
    metric_raw = str(metrics[0]).strip() if metrics else ""
    return {
        "fact_id": fact_id,
        "candidate_fact_id": fact_id,
        "claim_text": claim,
        "confidence": str(row.get("confidence") or "MEDIUM").strip().upper() or "MEDIUM",
        "verification_status": str(row.get("verification_status") or "graph_phase2_track"),
        "career_track": IBM_PHASE2_CAREER_TRACK,
        "graph_hop_path": hop,
        "skill_id": (hop_entry or {}).get("skill_id"),
        "graph_phase2_track_proof": True,
        "metric_values": list(metrics) if isinstance(metrics, list) else [],
        "metric_raw": metric_raw,
        "has_metric": bool(metric_raw),
        "technologies": list(row.get("technologies") or []) if isinstance(row.get("technologies"), list) else [],
        "domain": str(row.get("domain") or row.get("domain_family") or "").strip(),
        "source_employment": str(row.get("source_employment") or row.get("company_lane") or "").strip(),
    }


def check_ibm_bullets_phase2_career_track_scope(
    *,
    proof_pool_metadata: dict[str, Any] | None,
    selected_fact_plan: dict[str, Any] | None,
) -> tuple[bool, dict[str, Any]]:
    """X2 helper: proof pool and plan facts must be Phase 2 track only."""
    meta = dict(proof_pool_metadata or {})
    plan = dict(selected_fact_plan or {})
    observed: dict[str, Any] = {
        "selection_method": plan.get("selection_method") or meta.get("selection_method"),
        "career_track_scope_allowed": meta.get("career_track_scope_allowed")
        or plan.get("career_track_scope_allowed"),
        "employment_window": meta.get("employment_window") or plan.get("employment_window"),
        "selected_tracks": meta.get("selected_tracks") or meta.get("c03_selected_tracks"),
    }

    allowed = list(observed.get("career_track_scope_allowed") or [])
    if allowed != [IBM_PHASE2_CAREER_TRACK]:
        return False, {
            **observed,
            "reason": "career_track_scope_allowed_must_be_phase2_only",
            "expected": [IBM_PHASE2_CAREER_TRACK],
            "actual": allowed,
        }

    window = str(observed.get("employment_window") or "")
    if window != IBM_EMPLOYMENT_WINDOW_LABEL:
        return False, {
            **observed,
            "reason": "employment_window_mismatch",
            "expected": IBM_EMPLOYMENT_WINDOW_LABEL,
            "actual": window,
        }

    method = str(observed.get("selection_method") or "")
    if method != IBM_TRACK_RANKED_SELECTION_METHOD:
        return False, {
            **observed,
            "reason": "selection_method_not_phase2_ranked",
            "expected": IBM_TRACK_RANKED_SELECTION_METHOD,
            "actual": method,
        }

    tracks = {str(t) for t in (observed.get("selected_tracks") or []) if str(t).strip()}
    forbidden_hits = sorted(tracks & FORBIDDEN_IBM_BULLET_CAREER_TRACKS)
    if forbidden_hits:
        return False, {**observed, "reason": "forbidden_career_tracks_in_pool", "forbidden": forbidden_hits}

    bad_facts: list[dict[str, str]] = []
    missing_graph_proof: list[str] = []
    for row in plan.get("facts") or []:
        if not isinstance(row, dict):
            continue
        track = str(row.get("career_track") or "").strip()
        if track and track != IBM_PHASE2_CAREER_TRACK:
            bad_facts.append(
                {
                    "fact_id": str(row.get("fact_id") or ""),
                    "career_track": track,
                }
            )
        if not row.get("graph_phase2_track_proof"):
            missing_graph_proof.append(str(row.get("fact_id") or row.get("ledger_candidate_fact_id") or ""))
        if not row.get("graph_hop_path"):
            missing_graph_proof.append(str(row.get("fact_id") or ""))
    if bad_facts:
        return False, {**observed, "reason": "plan_fact_wrong_career_track", "violations": bad_facts}
    if missing_graph_proof:
        return False, {
            **observed,
            "reason": "plan_fact_missing_phase2_graph_hop",
            "fact_ids": sorted({x for x in missing_graph_proof if x}),
        }

    return True, observed


__all__ = [
    "build_ibm_phase2_graph_plan_fact",
    "FORBIDDEN_IBM_BULLET_CAREER_TRACKS",
    "IBM_BULLETS_MIN_PHASE2_FACTS",
    "IBM_EMPLOYMENT_END",
    "IBM_EMPLOYMENT_START",
    "IBM_EMPLOYMENT_WINDOW_LABEL",
    "IBM_PHASE2_CAREER_TRACK",
    "IBM_PHASE2_CAREER_TRACK_ID",
    "IBM_PHASE2_TRACK_WEIGHT_OVERRIDE",
    "IBM_TRACK_RANKED_SELECTION_METHOD",
    "check_ibm_bullets_phase2_career_track_scope",
]
