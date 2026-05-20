"""Materialize Part 1 career tracks (P1-W1–W3) into master_skills_arsenal_ledger.json.

Operator taxonomy SSOT: docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json
Employment SSOT: apps_rg/resume/base/amit_ayer_base_resume_v1.json

Does not modify competencies runtime or agentic_core.
"""
from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    skill_row_eligible_for_external_claim,
)

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
TAXONOMY_PATH = ROOT / "docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json"
BASE_RESUME_PATH = ROOT / "apps_rg/resume/base/amit_ayer_base_resume_v1.json"
REPORTS_DIR = ROOT / "docs/reports/apps_rg"

TRACK_NODES = (
    {
        "node_id": "track_actuarial_risk_derivatives",
        "track_id": "TRACK_ACTUARIAL_RISK_DERIVATIVES",
        "start_year": 2002,
        "end_year": 2010,
        "end_year_present": False,
    },
    {
        "node_id": "track_data_tech_cloud_ml",
        "track_id": "TRACK_DATA_TECH_CLOUD_ML",
        "start_year": 2010,
        "end_year": 2022,
        "end_year_present": False,
    },
    {
        "node_id": "track_genai_agentic",
        "track_id": "TRACK_GENAI_AGENTIC",
        "start_year": 2022,
        "end_year": None,
        "end_year_present": True,
    },
)

EPOCH_TO_TRACK: dict[str, str] = {
    "epoch_actuarial_financial_engineering": "track_actuarial_risk_derivatives",
    "epoch_enterprise_risk_governance": "track_actuarial_risk_derivatives",
    "epoch_cloud_data_platform_engineering": "track_data_tech_cloud_ml",
    "epoch_ai_platform_commercialization": "track_data_tech_cloud_ml",
    "epoch_partner_gtm_revenue_leadership": "track_data_tech_cloud_ml",
    "epoch_agentic_ai_runtime_architecture": "track_genai_agentic",
}

PILLAR_TO_TRACK_OVERRIDE: dict[str, str] = {
    "pillar_trading_hpc": "track_data_tech_cloud_ml",
    "pillar_partner_gtm_alliances": "track_data_tech_cloud_ml",
    "pillar_cosell_partner_engineering": "track_data_tech_cloud_ml",
    "pillar_presales_solutioning": "track_data_tech_cloud_ml",
    "pillar_gtm_presales_motion": "track_data_tech_cloud_ml",
    "pillar_technical_presales_accelerators": "track_data_tech_cloud_ml",
    "pillar_agentic_ai_platforms": "track_genai_agentic",
    "pillar_insurance_carrier_transformation": "track_data_tech_cloud_ml",
    "pillar_underwriting_claims_ops_ai": "track_data_tech_cloud_ml",
    "pillar_insurer_it_strategy_ai_enablement": "track_data_tech_cloud_ml",
    "pillar_enterprise_portfolio_governance": "track_data_tech_cloud_ml",
    "pillar_banking_platform_responsible_ai": "track_actuarial_risk_derivatives",
    "pillar_interoperability_integration_ecosystem": "track_data_tech_cloud_ml",
    "pillar_hyperscaler_marketplace_partner_gtm": "track_data_tech_cloud_ml",
    "pillar_applied_ai_partner_architecture": "track_data_tech_cloud_ml",
}

SECTION_TO_EMPLOYMENT: dict[str, str] = {
    "unify_narrative": "exp_unify_001",
    "unify_bullets": "exp_unify_001",
    "ibm_narrative": "exp_ibm_001",
    "ibm_bullets": "exp_ibm_001",
}

EMPLOYER_SOURCE_TO_EMPLOYMENT: dict[str, str] = {
    "Early Career": "exp_early_career_001",
    "Towers Perrin / ING / Aetna": "exp_early_career_001",
}

CAREER_STAGE_TO_EMPLOYMENT: dict[str, str] = {
    "early_career": "exp_early_career_001",
    "ibm_partner": "exp_ibm_001",
    "insurtech": "exp_insurtech_001",
    "ey": "exp_ey_001",
    "unify": "exp_unify_001",
}


def _parse_ym(value: str) -> tuple[int, int]:
    if value in ("present", "", None):
        return 9999, 12
    year_s, month_s = str(value).split("-", 1)
    return int(year_s), int(month_s)


def _stint_months(start: str, end: str, *, is_current: bool) -> tuple[int, int, int]:
    sy, sm = _parse_ym(start)
    ey, em = _parse_ym("present" if is_current else end)
    start_m = sy * 12 + sm
    end_m = ey * 12 + em
    return start_m, end_m, end_m - start_m + 1


EMPLOYMENT_PRIMARY_TRACK: dict[str, tuple[str, list[dict[str, Any]]]] = {
    "exp_early_career_001": (
        "track_actuarial_risk_derivatives",
        [{"type": "stint_end_at_track1_track2_boundary", "end": "2009-09"}],
    ),
    "exp_ey_001": (
        "track_data_tech_cloud_ml",
        [
            {
                "type": "stint_start_before_track2_official_year",
                "start": "2009-10",
                "track2_start_year": 2010,
            }
        ],
    ),
    "exp_insurtech_001": ("track_data_tech_cloud_ml", []),
    "exp_ibm_001": (
        "track_data_tech_cloud_ml",
        [{"type": "stint_end_at_track2_track3_boundary", "end": "2022-10"}],
    ),
    "exp_unify_001": ("track_genai_agentic", []),
}


def primary_track_for_stint(
    start: str,
    end: str,
    *,
    is_current: bool,
    employment_fact_id: str = "",
) -> tuple[str, list[dict[str, Any]]]:
    """Return primary track node_id and boundary notes (base-resume stints only)."""
    if employment_fact_id in EMPLOYMENT_PRIMARY_TRACK:
        primary, notes = EMPLOYMENT_PRIMARY_TRACK[employment_fact_id]
        return primary, list(notes)

    notes: list[dict[str, Any]] = []
    sy, _ = _parse_ym(start)
    ey, _ = _parse_ym("present" if is_current else end)

    if is_current or end == "present":
        if sy >= 2022:
            return "track_genai_agentic", notes
    if ey <= 2010:
        return "track_actuarial_risk_derivatives", notes
    if sy >= 2022:
        return "track_genai_agentic", notes
    if sy >= 2010 and ey <= 2022:
        return "track_data_tech_cloud_ml", notes

    start_m, end_m, _ = _stint_months(start, end, is_current=is_current)
    track_months = {
        "track_actuarial_risk_derivatives": 0,
        "track_data_tech_cloud_ml": 0,
        "track_genai_agentic": 0,
    }
    for m in range(start_m, end_m + 1):
        y, mo = divmod(m, 12)
        if y < 2010 or (y == 2010 and mo == 0):
            track_months["track_actuarial_risk_derivatives"] += 1
        elif y < 2022:
            track_months["track_data_tech_cloud_ml"] += 1
        else:
            track_months["track_genai_agentic"] += 1
    primary = max(track_months, key=track_months.get)
    if sum(1 for v in track_months.values() if v > 0) > 1:
        notes.append(
            {
                "type": "multi_track_overlap",
                "start": start,
                "end": end,
                "track_months": track_months,
                "primary": primary,
            }
        )
    return primary, notes


def _graph_node_template(
    node_id: str,
    node_type: str,
    label: str,
    description: str,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    node: dict[str, Any] = {
        "node_id": node_id,
        "node_type": node_type,
        "label": label,
        "description": description,
        "support_level": "DERIVED_SUPPORTED",
        "visibility_rule": "role_family_match",
        "activation_status": "DRAFT",
        "evidence_risk": "low",
        "source_refs": [],
        "projection_behavior": "graph_structure",
        "external_claim_policy": "skill_projection_not_proof",
    }
    if extra:
        node.update(extra)
    return node


def _graph_edge_template(
    edge_id: str,
    edge_type: str,
    source: str,
    target: str,
    rationale: str,
    *,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    edge: dict[str, Any] = {
        "edge_id": edge_id,
        "edge_type": edge_type,
        "source_node_id": source,
        "target_node_id": target,
        "rationale": rationale,
        "projection_behavior": "graph_traversal",
        "external_claim_policy": "skill_projection_not_proof",
        "validation_status": "validated",
    }
    if extra:
        edge.update(extra)
    return edge


def _pillar_primary_track(pillar_id: str, edges: list[dict[str, Any]]) -> str:
    if pillar_id in PILLAR_TO_TRACK_OVERRIDE:
        return PILLAR_TO_TRACK_OVERRIDE[pillar_id]
    epoch_hits: Counter[str] = Counter()
    for edge in edges:
        if edge.get("edge_type") != "epoch_contains_pillar":
            continue
        if edge.get("target_node_id") != pillar_id:
            continue
        epoch = str(edge.get("source_node_id"))
        if epoch in EPOCH_TO_TRACK:
            epoch_hits[EPOCH_TO_TRACK[epoch]] += 1
    if not epoch_hits:
        return "track_data_tech_cloud_ml"
    return epoch_hits.most_common(1)[0][0]


def _remove_prior_p1_artifacts(ledger: dict[str, Any]) -> None:
    remove_node_types = {"career_track", "employment"}
    remove_edge_types = {
        "career_track_contains_epoch",
        "career_track_contains_pillar",
        "career_track_precedes_career_track",
        "employment_in_career_track",
        "employment_hosts_fact",
    }
    ledger["graph_nodes"] = [
        n
        for n in ledger.get("graph_nodes") or []
        if n.get("node_type") not in remove_node_types
    ]
    ledger["graph_edges"] = [
        e
        for e in ledger.get("graph_edges") or []
        if e.get("edge_type") not in remove_edge_types
    ]
    layers = ledger.get("graph_layers") or []
    ledger["graph_layers"] = [layer for layer in layers if layer.get("layer_id") != "career_track"]


def _ensure_career_track_layer(ledger: dict[str, Any]) -> None:
    layers = ledger.get("graph_layers") or []
    if any(layer.get("layer_id") == "career_track" for layer in layers):
        return
    new_layers: list[dict[str, Any]] = []
    for layer in layers:
        new_layers.append(layer)
        if layer.get("layer_id") == "career_epoch":
            new_layers.append({"layer_id": "career_track", "order": "2b"})
    ledger["graph_layers"] = new_layers


def materialize_p1_w1(ledger: dict[str, Any]) -> dict[str, Any]:
    _remove_prior_p1_artifacts(ledger)
    _ensure_career_track_layer(ledger)
    nodes = ledger["graph_nodes"]
    edges = ledger["graph_edges"]
    taxonomy = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))

    for spec in TRACK_NODES:
        end_label = "present" if spec["end_year_present"] else str(spec["end_year"])
        nodes.append(
            _graph_node_template(
                spec["node_id"],
                "career_track",
                spec["track_id"].replace("_", " ").title(),
                f"Career track {spec['track_id']} ({spec['start_year']}–{end_label})",
                extra={
                    "track_id": spec["track_id"],
                    "start_year": spec["start_year"],
                    "end_year": spec["end_year"],
                    "end_year_present": spec["end_year_present"],
                    "operator_confirmed": True,
                    "taxonomy_ref": taxonomy.get("schema"),
                },
            )
        )

    for epoch_id, track_node in EPOCH_TO_TRACK.items():
        edges.append(
            _graph_edge_template(
                f"edge_track_epoch_{track_node}_{epoch_id}",
                "career_track_contains_epoch",
                track_node,
                epoch_id,
                "Primary career track contains epoch (operator-confirmed taxonomy)",
                extra={"primary": True},
            )
        )

    pillar_ids = {
        n["node_id"]
        for n in nodes
        if n.get("node_type") == "domain_pillar"
    }
    for pillar_id in sorted(pillar_ids):
        track_node = _pillar_primary_track(pillar_id, edges)
        edges.append(
            _graph_edge_template(
                f"edge_track_pillar_{track_node}_{pillar_id}",
                "career_track_contains_pillar",
                track_node,
                pillar_id,
                "Career track contains domain pillar",
                extra={"primary": True},
            )
        )

    sequence = [
        "track_actuarial_risk_derivatives",
        "track_data_tech_cloud_ml",
        "track_genai_agentic",
    ]
    for src, tgt in zip(sequence, sequence[1:]):
        edges.append(
            _graph_edge_template(
                f"edge_track_precedes_{src}_{tgt}",
                "career_track_precedes_career_track",
                src,
                tgt,
                "Career sequence (non-causal); synthesis ordering only",
                extra={"causal": False, "relationship": "non_causal_sequence"},
            )
        )

    gm = ledger.setdefault("graph_metadata", {})
    gm["career_track_count"] = 3
    gm["career_track_materialized_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gm["node_count"] = len(nodes)
    gm["edge_count"] = len(edges)
    return {
        "career_track_count": 3,
        "epoch_primary_coverage": dict(EPOCH_TO_TRACK),
        "pillar_trading_hpc_track": _pillar_primary_track("pillar_trading_hpc", edges),
        "sequence_edges": len(sequence) - 1,
    }


def materialize_p1_w2(ledger: dict[str, Any]) -> dict[str, Any]:
    base = json.loads(BASE_RESUME_PATH.read_text(encoding="utf-8"))
    nodes = ledger["graph_nodes"]
    edges = ledger["graph_edges"]
    proven_skill_facts = {
        str(e["target_node_id"])
        for e in edges
        if e.get("edge_type") == "skill_supported_by_fact"
    }

    employment_hosts: list[dict[str, str]] = []
    boundary_cases: list[dict[str, Any]] = []
    employment_primary: dict[str, str] = {}

    for emp in base.get("facts", {}).get("employment") or []:
        if not isinstance(emp, dict):
            continue
        fact_id = str(emp.get("fact_id") or "")
        if not fact_id.startswith("exp_"):
            continue
        node_id = f"employment_{fact_id}"
        sy, sm = _parse_ym(str(emp.get("start_date") or ""))
        end_raw = str(emp.get("end_date") or "")
        is_current = bool(emp.get("is_current"))
        ey, em = _parse_ym("present" if is_current else end_raw)
        primary_track, notes = primary_track_for_stint(
            str(emp.get("start_date")),
            end_raw,
            is_current=is_current,
            employment_fact_id=fact_id,
        )
        employment_primary[fact_id] = primary_track
        if notes:
            boundary_cases.extend([{**n, "employment_fact_id": fact_id} for n in notes])

        label = f"{emp.get('employer')} — {emp.get('title')}"
        nodes.append(
            _graph_node_template(
                node_id,
                "employment",
                label,
                str(emp.get("role_narrative") or label)[:500],
                extra={
                    "source_fact_id": fact_id,
                    "employer": emp.get("employer"),
                    "title": emp.get("title"),
                    "location": emp.get("location"),
                    "start_date": emp.get("start_date"),
                    "end_date": end_raw,
                    "is_current": is_current,
                    "start_year": sy,
                    "end_year": None if is_current else ey,
                    "end_year_present": is_current,
                },
            )
        )
        edges.append(
            _graph_edge_template(
                f"edge_employment_track_{fact_id}_{primary_track}",
                "employment_in_career_track",
                node_id,
                primary_track,
                "Primary career track for employment stint (date overlap policy)",
                extra={"primary": True},
            )
        )

    # Proof-backed fact hosting: matrix linked_fact_id + skill_supported_by_fact
    fact_to_employment: dict[str, set[str]] = defaultdict(set)
    for matrix_name in ("actuarial_career_matrix", "partner_gtm_matrix"):
        for row in ledger.get(matrix_name) or []:
            if not isinstance(row, dict):
                continue
            linked = row.get("linked_fact_id")
            if not linked:
                continue
            fid = str(linked)
            employer_src = str(row.get("employer_source") or "")
            if employer_src in EMPLOYER_SOURCE_TO_EMPLOYMENT:
                fact_to_employment[fid].add(EMPLOYER_SOURCE_TO_EMPLOYMENT[employer_src])
            stage = str(row.get("career_stage") or "")
            if stage in CAREER_STAGE_TO_EMPLOYMENT:
                fact_to_employment[fid].add(CAREER_STAGE_TO_EMPLOYMENT[stage])

    audit_path = REPORTS_DIR / "apps_rg_post_section_aggregation_readiness_audit.json"
    if audit_path.is_file():
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        matrix = audit.get("source_fact_reuse_matrix") or {}
        for fid, meta in matrix.items():
            if not str(fid).startswith("fact_"):
                continue
            for section in meta.get("sections") or []:
                if section in SECTION_TO_EMPLOYMENT:
                    fact_to_employment[str(fid)].add(SECTION_TO_EMPLOYMENT[section])

    for fid, employments in sorted(fact_to_employment.items()):
        if fid not in proven_skill_facts:
            continue
        for exp_id in sorted(employments):
            emp_node = f"employment_{exp_id}"
            if not any(n.get("node_id") == emp_node for n in nodes):
                continue
            edge_id = f"edge_employment_hosts_fact_{exp_id}_{fid}"
            edges.append(
                _graph_edge_template(
                    edge_id,
                    "employment_hosts_fact",
                    emp_node,
                    fid,
                    "Employment hosts fact (proven via skill_supported_by_fact + source trace)",
                    extra={"proof_basis": "skill_supported_by_fact_and_source_trace"},
                )
            )
            employment_hosts.append({"employment": exp_id, "fact_id": fid, "edge_id": edge_id})

    gm = ledger.setdefault("graph_metadata", {})
    gm["employment_node_count"] = len(employment_primary)
    gm["node_count"] = len(nodes)
    gm["edge_count"] = len(edges)
    return {
        "employment_node_count": len(employment_primary),
        "employment_primary_track_coverage": employment_primary,
        "employment_hosts_fact_edges": len(employment_hosts),
        "employment_hosts_fact_sample": employment_hosts[:20],
        "boundary_cases": boundary_cases,
    }


def _skill_row_track(row: dict[str, Any], ledger: dict[str, Any]) -> str:
    pillar = str(row.get("pillar") or "")
    if pillar in PILLAR_TO_TRACK_OVERRIDE:
        return PILLAR_TO_TRACK_OVERRIDE[pillar]
    epoch = str(row.get("career_epoch") or "")
    if epoch in EPOCH_TO_TRACK:
        return EPOCH_TO_TRACK[epoch]
    stage = str(row.get("career_stage") or "")
    if stage == "early_career":
        return "track_actuarial_risk_derivatives"
    return "track_data_tech_cloud_ml"


def _may_activate_row(row: dict[str, Any]) -> tuple[bool, str]:
    support = str(row.get("support_level") or "")
    if support in ("BLOCKED", "TARGETING_ONLY", "STYLE_ONLY"):
        return False, f"support_level={support}"
    if support == "USER_CONFIRMED_PENDING_SOURCE":
        return False, "pending_source"
    links = row.get("fact_id_links") or []
    if not links:
        return False, "empty_fact_id_links"
    if support == "DIRECT_FROM_RESUME_ARCHIVE":
        if not (row.get("source_snippets") or []):
            return False, "archive_missing_snippets"
        return True, "direct_archive_confirmed"
    if support == "BUNDLE_SUPPORTED":
        return True, "bundle_supported"
    if support == "DERIVED_SUPPORTED":
        if not skill_row_eligible_for_external_claim(row):
            return False, "not_eligible_for_external_claim"
        return True, "derived_supported_with_facts"
    return False, f"unsupported_support={support}"


def materialize_p1_w3(ledger: dict[str, Any]) -> dict[str, Any]:
    before_empty = 0
    after_empty = 0
    activated: list[dict[str, str]] = []
    kept_draft: list[dict[str, str]] = []
    by_track: Counter[str] = Counter()
    confidence_upgrades: list[str] = []

    def process_row(row: dict[str, Any]) -> None:
        nonlocal before_empty, after_empty
        links = row.get("fact_id_links") or []
        if not links:
            before_empty += 1
        ok, reason = _may_activate_row(row)
        track = _skill_row_track(row, ledger)
        if ok:
            prior = str(row.get("activation_status"))
            if prior not in ("DRAFT",):
                return
            support = str(row.get("support_level"))
            row["activation_status"] = (
                "ACTIVE_CONFIRMED" if support == "DIRECT_FROM_RESUME_ARCHIVE" else "ACTIVE"
            )
            track_map = {
                "track_actuarial_risk_derivatives": "TRACK_ACTUARIAL_RISK_DERIVATIVES",
                "track_data_tech_cloud_ml": "TRACK_DATA_TECH_CLOUD_ML",
                "track_genai_agentic": "TRACK_GENAI_AGENTIC",
            }
            row["career_track_id"] = track_map.get(track, track)
            if str(row.get("support_level")) != support:
                confidence_upgrades.append(str(row.get("skill_id")))
            activated.append({"skill_id": str(row["skill_id"]), "track": track, "reason": reason})
            by_track[track] += 1
        else:
            if not links:
                after_empty += 1
            kept_draft.append({"skill_id": str(row.get("skill_id")), "track": track, "reason": reason})

    skill_by_id = {
        str(r["skill_id"]): r for r in ledger.get("skill_rows") or [] if isinstance(r, dict)
    }
    for row in ledger.get("skill_rows") or []:
        if isinstance(row, dict):
            process_row(row)

    for row in ledger.get("agentic_runtime_matrix") or []:
        if not isinstance(row, dict):
            continue
        sid = str(row.get("skill_id") or "")
        src = skill_by_id.get(sid)
        if src:
            row["activation_status"] = src.get("activation_status", row.get("activation_status"))
            if src.get("career_track_id"):
                row["career_track_id"] = src["career_track_id"]

    for node in ledger.get("graph_nodes") or []:
        if node.get("node_type") != "skill_row":
            continue
        sid = str(node.get("node_id"))
        src = skill_by_id.get(sid)
        if src:
            node["activation_status"] = src.get("activation_status", node.get("activation_status"))

    gm = ledger.setdefault("graph_metadata", {})
    gm["p1_w3_activation_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    gm["active_skills_by_track"] = dict(by_track)
    return {
        "empty_fact_id_links_before": before_empty,
        "empty_fact_id_links_after": after_empty,
        "activated_count": len(activated),
        "active_skills_by_track": dict(by_track),
        "unsupported_rows_remaining_draft": len(kept_draft),
        "confidence_upgrades": confidence_upgrades,
        "activated_sample": activated[:15],
        "draft_empty_links_sample": [r for r in kept_draft if r["reason"] == "empty_fact_id_links"][:10],
    }


def verify_p1_invariants(ledger: dict[str, Any]) -> dict[str, Any]:
    nodes = ledger.get("graph_nodes") or []
    edges = ledger.get("graph_edges") or []
    track_nodes = [n for n in nodes if n.get("node_type") == "career_track"]
    epoch_edges = [e for e in edges if e.get("edge_type") == "career_track_contains_epoch"]
    pillar_trading = [
        e
        for e in edges
        if e.get("edge_type") == "career_track_contains_pillar"
        and e.get("target_node_id") == "pillar_trading_hpc"
    ]
    seq_edges = [e for e in edges if e.get("edge_type") == "career_track_precedes_career_track"]
    epoch_primary: dict[str, list[str]] = defaultdict(list)
    for e in epoch_edges:
        epoch_primary[str(e["target_node_id"])].append(str(e["source_node_id"]))
    violations = []
    for epoch_id in EPOCH_TO_TRACK:
        primaries = epoch_primary.get(epoch_id, [])
        if len(primaries) != 1:
            violations.append(f"epoch {epoch_id} primary count {len(primaries)}")
    trading_ok = any(
        e.get("source_node_id") == "track_data_tech_cloud_ml" for e in pillar_trading
    )
    non_causal_ok = all(e.get("causal") is False for e in seq_edges)
    active_without_facts = [
        r["skill_id"]
        for r in ledger.get("skill_rows") or []
        if isinstance(r, dict)
        and str(r.get("activation_status", "")).startswith("ACTIVE")
        and not (r.get("fact_id_links") or [])
    ]
    return {
        "career_track_count": len(track_nodes),
        "epoch_primary_track_coverage": {k: v[0] if len(v) == 1 else v for k, v in epoch_primary.items()},
        "pillar_trading_hpc_track": pillar_trading[0]["source_node_id"] if pillar_trading else None,
        "non_causal_sequence_only": non_causal_ok and len(seq_edges) == 2,
        "violations": violations,
        "trading_hpc_ok": trading_ok,
        "active_without_facts": active_without_facts,
    }


def run_materialize(*, write: bool = True) -> dict[str, Any]:
    ledger = json.loads(LEDGER_PATH.read_text(encoding="utf-8"))
    w1 = materialize_p1_w1(ledger)
    w2 = materialize_p1_w2(ledger)
    w3 = materialize_p1_w3(ledger)
    verify = verify_p1_invariants(ledger)
    out = {"p1_w1": w1, "p1_w2": w2, "p1_w3": w3, "verify": verify}
    if write:
        LEDGER_PATH.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        (REPORTS_DIR / "career_track_materialization_receipt.json").write_text(
            json.dumps(
                {
                    "schema": "career_track_materialization_receipt_v1",
                    "plan_id": "graph-skills-hardening-f3a8c1",
                    "waves": ["P1-W1", "P1-W2", "P1-W3"],
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    **out,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (REPORTS_DIR / "career_track_p1_w2_employment_receipt.json").write_text(
            json.dumps(
                {
                    "schema": "career_track_p1_w2_employment_receipt_v1",
                    "plan_id": "graph-skills-hardening-f3a8c1",
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    **w2,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (REPORTS_DIR / "career_track_p1_w3_activation_receipt.json").write_text(
            json.dumps(
                {
                    "schema": "career_track_p1_w3_activation_receipt_v1",
                    "plan_id": "graph-skills-hardening-f3a8c1",
                    "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                    **w3,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Materialize P1-W1..W3 career tracks into arsenal graph")
    parser.add_argument("--dry-run", action="store_true", help="Compute receipts without writing ledger")
    args = parser.parse_args()
    result = run_materialize(write=not args.dry_run)
    print(json.dumps(result["verify"], indent=2))


if __name__ == "__main__":
    main()
