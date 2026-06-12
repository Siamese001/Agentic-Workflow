"""Graph evidence constraints for ibm_bullets — Phase 2 career track only (IBM 2017–2022)."""
from __future__ import annotations

from typing import Any

from apps_rg.fact_inventory.track_weighted_graph_expansion import _skill_rows_by_id

# Phase 2 (Data / tech / Cloud / ML) — IBM stint 2017-04..2022-10 lies entirely in this track.
IBM_PHASE2_CAREER_TRACK = "track_data_tech_cloud_ml"

# ---------------------------------------------------------------------------
# GRAPH_BULLET_EVIDENCE_PACK — IBM organic proof bundle (W1: Bullet Proof Bundle Redesign)
# ---------------------------------------------------------------------------

GRAPH_BULLET_EVIDENCE_PACK_MARKER = "GRAPH_BULLET_EVIDENCE_PACK"

IBM_BULLET_SLOT_IDS: tuple[str, ...] = (
    "bul_ibm_001",
    "bul_ibm_002",
    "bul_ibm_003",
    "bul_ibm_004",
    "bul_ibm_005",
)

# Static engineering skill assignments per IBM bullet slot.
# References arsenal skill nodes tracing through cloud/platform/data-engineering pillars.
# Phrase labels come from master_skills_arsenal_ledger.json skill_rows.
IBM_BULLET_SLOT_SKILL_MAP: dict[str, list[dict[str, str]]] = {
    "bul_ibm_001": [
        {"skill_id": "skill_sr_cloud_data_platform_engineering",
         "allowed_phrases": "cloud-native, platform engineering"},
        {"skill_id": "skill_p2_tech_ibm_cloud_portfolio_anchor",
         "allowed_phrases": "$30M cloud and AI transformation portfolio, systems architect"},
    ],
    "bul_ibm_002": [
        {"skill_id": "skill_sr_cloud_data_platform_engineering",
         "allowed_phrases": "cloud-native, platform engineering"},
        {"skill_id": "skill_sr_microservices_integration_platform",
         "allowed_phrases": "microservices, cloud-native, integration"},
    ],
    "bul_ibm_003": [
        {"skill_id": "skill_p2_tech_ibm_cloud_portfolio_anchor",
         "allowed_phrases": "$30M cloud and AI transformation portfolio"},
        {"skill_id": "skill_ai_platform_commercialization",
         "allowed_phrases": "ai platform commercialization"},
    ],
    "bul_ibm_004": [
        {"skill_id": "skill_sr_basel_ccar_lineage_regulatory",
         "allowed_phrases": "Basel, CCAR, data lineage, regulatory reporting"},
        {"skill_id": "skill_audit_grade_observability",
         "allowed_phrases": "audit grade observability"},
    ],
    "bul_ibm_005": [
        {"skill_id": "skill_partner_cloud_partner_ecosystem",
         "allowed_phrases": "IBM-AWS alliance, cloud transformations"},
        {"skill_id": "skill_partner_ibm_aws_alliance_joint_revenue",
         "allowed_phrases": "IBM-AWS alliance, 20% joint revenue, AI-driven sales frameworks"},
    ],
}

# Mechanism vocabulary per slot extracted from base resume IBM fact structured fields.
# Source: amit_ayer_base_resume_v1.json → facts.employment[exp_ibm_001].bullets[*].technologies
# Constraint: claim_text prose is EXCLUDED. Only the `technologies` list is used here.
IBM_BULLET_MECHANISM_VOCAB: dict[str, list[str]] = {
    "bul_ibm_001": ["AI platforms", "analytics", "cloud-native"],
    "bul_ibm_002": ["cloud migration", "modernization", "analytics", "ML"],
    "bul_ibm_003": ["SaaS platforms", "regulatory workflows", "shared services"],
    "bul_ibm_004": ["data lineage", "observability", "real-time ingestion"],
    "bul_ibm_005": ["hyperscaler alliances", "co-sell"],
}

# Legacy locked metrics retired — HOLD/DO_NOT_PROMOTE base-resume tokens must not drive C0.
# Metric claims bind only to allowed_metric_outcome_ids from role episode bundles.
IBM_BULLET_LOCKED_METRICS: dict[str, str] = {}

# Domain context per slot (structural field — not claim prose).
IBM_BULLET_SLOT_DOMAIN: dict[str, str] = {
    "bul_ibm_001": "AI infrastructure",
    "bul_ibm_002": "cloud infrastructure",
    "bul_ibm_003": "platform engineering",
    "bul_ibm_004": "data engineering",
    "bul_ibm_005": "business partnerships",
}

# Strings whose presence in the C0 pack would indicate base-resume prose leakage.
IBM_FORBIDDEN_C0_PROMPT_SUBSTRINGS: tuple[str, ...] = (
    "CANONICAL IBM FACTS",
    "REWRITE_FROM_FACT_POOL",
    "rewrite from these",
    "archive_reference_only",
)


def assert_ibm_c0_pack_has_no_forbidden_template_leaks(pack_text: str) -> None:
    blob = str(pack_text or "")
    hits = [s for s in IBM_FORBIDDEN_C0_PROMPT_SUBSTRINGS if s in blob]
    if hits:
        raise ValueError(
            f"IBM GRAPH_BULLET_EVIDENCE_PACK contains forbidden template leakage: {hits}"
        )


def format_ibm_graph_bullet_evidence_pack(
    runtime_payload: dict[str, Any],
) -> str:
    """C0 body: IBM role episode bundles per bul_ibm_* slot (not flat skill lists).

    Delegates to ibm_role_episode_evidence — proof authority is role_episode_bundle_id +
    bound_skills + linked_source_fact_ids. Base resume claim_text is excluded.
    """
    from apps_rg.runtime.sections.ibm_role_episode_evidence import (
        format_ibm_role_episode_evidence_pack,
    )

    return format_ibm_role_episode_evidence_pack(runtime_payload, section_id="ibm_bullets")
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
    from apps_rg.runtime.sections.graph_evidence_contract import slice_row_to_plan_fact

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
        except ValueError:  # guardian: allow-silent-swallow -- P2 burndown: fail-soft optional boundary
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
    "assert_ibm_c0_pack_has_no_forbidden_template_leaks",
    "build_ibm_phase2_graph_plan_fact",
    "check_ibm_bullets_phase2_career_track_scope",
    "FORBIDDEN_IBM_BULLET_CAREER_TRACKS",
    "format_ibm_graph_bullet_evidence_pack",
    "GRAPH_BULLET_EVIDENCE_PACK_MARKER",
    "IBM_BULLET_LOCKED_METRICS",
    "IBM_BULLET_MECHANISM_VOCAB",
    "IBM_BULLET_SLOT_DOMAIN",
    "IBM_BULLET_SLOT_IDS",
    "IBM_BULLET_SLOT_SKILL_MAP",
    "IBM_BULLETS_MIN_PHASE2_FACTS",
    "IBM_EMPLOYMENT_END",
    "IBM_EMPLOYMENT_START",
    "IBM_EMPLOYMENT_WINDOW_LABEL",
    "IBM_FORBIDDEN_C0_PROMPT_SUBSTRINGS",
    "IBM_PHASE2_CAREER_TRACK",
    "IBM_PHASE2_CAREER_TRACK_ID",
    "IBM_PHASE2_TRACK_WEIGHT_OVERRIDE",
    "IBM_TRACK_RANKED_SELECTION_METHOD",
]
