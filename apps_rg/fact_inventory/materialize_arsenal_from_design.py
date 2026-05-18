"""Materializer: design JSON + W4A graph -> master_skills_arsenal_ledger.json."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.arsenal_graph_w4a_builder import build_w4a_graph_package

ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json"
OUT_PATH = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"

DOMAIN_TO_PILLAR: dict[str, str] = {
    "derivatives": "pillar_derivatives_structured",
    "greeks": "pillar_greeks_hedging",
    "greeks_hedging": "pillar_greeks_hedging",
    "actuarial": "pillar_actuarial_foundation",
    "capital": "pillar_capital_modeling",
    "risk": "pillar_risk_management",
    "insurance_liabilities": "pillar_embedded_options_insurance",
}

PARTNER_SKILL_TO_PILLAR: dict[str, str] = {
    "aws_ecosystem": "pillar_cloud_data_aws",
    "cloud_partner_ecosystem": "pillar_cloud_data_aws",
    "partner_motions": "pillar_partner_gtm_alliances",
    "co_selling": "pillar_cosell_partner_engineering",
    "partner_engineering": "pillar_cosell_partner_engineering",
    "pre_sales": "pillar_presales_solutioning",
    "solution_architecture": "pillar_presales_solutioning",
    "workshops": "pillar_presales_solutioning",
    "customer_deal_support": "pillar_customer_stakeholder",
    "enterprise_negotiations": "pillar_customer_stakeholder",
    "sales_revenue_targets": "pillar_revenue_commercialization",
    "gtm_enablement": "pillar_partner_gtm_alliances",
    "partner_led_ai_solutions": "pillar_partner_gtm_alliances",
    "product_feedback_loops": "pillar_partner_gtm_alliances",
    "pnl_oversight": "pillar_revenue_commercialization",
    "partner_revenue_3m": "pillar_partner_gtm_alliances",
}

RISK_MAP = {"low": "low", "medium": "medium", "high": "high"}


def _role_weights(role_relevance: list[str]) -> dict[str, float]:
    return {rf: 1.0 for rf in role_relevance}


def _activation_and_visibility(support_level: str, user_confirmed: bool) -> tuple[str, str, bool]:
    if support_level == "USER_CONFIRMED_PENDING_SOURCE":
        return "DRAFT", "human_confirm", True
    if support_level == "BLOCKED":
        return "RETIRED", "never_external", True
    if support_level in ("TARGETING_ONLY", "STYLE_ONLY"):
        return "DRAFT", "never_external", False
    return "DRAFT", "role_family_match", False


def _matrix_actuarial_row(row: dict[str, Any]) -> dict[str, Any]:
    support = str(row["support_status"])
    user_confirmed = support == "USER_CONFIRMED_PENDING_SOURCE"
    activation, visibility, human_req = _activation_and_visibility(support, user_confirmed)
    domain = str(row.get("domain") or "")
    fact_links: list[str] = []
    if row.get("linked_fact_id"):
        fact_links.append(str(row["linked_fact_id"]))
    src_files = [str(row["source_resume_file"])] if row.get("source_resume_file") else []
    snippets = [str(row["source_evidence"])] if row.get("source_evidence") else []
    sections = list(row.get("where_to_use_in_resume") or [])
    return {
        "skill_id": row["skill_id"],
        "fact_id_links": fact_links,
        "pillar": DOMAIN_TO_PILLAR.get(domain, "pillar_actuarial_foundation"),
        "subpillar": str(row.get("skill") or domain),
        "career_stage": str(row.get("career_stage") or "early_career"),
        "source_resume_files": src_files,
        "source_snippets": snippets,
        "user_confirmed": user_confirmed,
        "support_level": support,
        "role_family_weights": _role_weights(list(row.get("role_relevance") or [])),
        "allowed_phrases": list(row.get("allowed_output_phrases") or []),
        "forbidden_phrases": [],
        "allowed_sections": sections,
        "visibility_rule": visibility,
        "evidence_risk": RISK_MAP.get(str(row.get("risk_of_overclaim") or "low"), "low"),
        "activation_status": activation,
        "human_confirmation_required": human_req,
    }


def _matrix_partner_row(row: dict[str, Any]) -> dict[str, Any]:
    support = str(row["support_status"])
    user_confirmed = support == "USER_CONFIRMED_PENDING_SOURCE"
    activation, visibility, human_req = _activation_and_visibility(support, user_confirmed)
    skill_key = str(row.get("skill") or "")
    src_files = [str(row["source_resume_file"])] if row.get("source_resume_file") else []
    snippets = [str(row["source_evidence"])] if row.get("source_evidence") else []
    fact_links: list[str] = []
    if row.get("linked_fact_id"):
        fact_links.append(str(row["linked_fact_id"]))
    risk_raw = str(row.get("risk_notes") or "low").lower()
    evidence_risk = "medium" if "medium" in risk_raw else ("high" if "high" in risk_raw else "low")
    return {
        "skill_id": row["skill_id"],
        "fact_id_links": fact_links,
        "pillar": PARTNER_SKILL_TO_PILLAR.get(skill_key, "pillar_partner_gtm_alliances"),
        "subpillar": skill_key,
        "career_stage": "cross_career",
        "source_resume_files": src_files,
        "source_snippets": snippets,
        "user_confirmed": user_confirmed,
        "support_level": support,
        "role_family_weights": _role_weights(list(row.get("role_relevance") or [])),
        "allowed_phrases": list(row.get("allowed_phrases") or []),
        "forbidden_phrases": [],
        "allowed_sections": list(row.get("where_to_use") or []),
        "visibility_rule": visibility,
        "evidence_risk": evidence_risk,
        "activation_status": activation,
        "human_confirmation_required": human_req,
    }


def _normalize_pillars(pillars: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in pillars:
        out.append(
            {
                "pillar_id": p["pillar_id"],
                "name": p["name"],
                "description": p["description"],
                "subskills": p.get("subskills") or [],
                "linked_fact_ids": p.get("linked_fact_ids") or [],
                "allowed_phrases": p.get("allowed_phrases") or [],
                "forbidden_phrases_without_stronger_support": p.get("forbidden_phrases_without_stronger_support") or [],
                "role_family_weights": p.get("role_family_weights") or {},
                "section_fit": p.get("section_fit") or {},
                "archive_snippets": p.get("archive_snippets") or [],
                "evidence_sources": p.get("evidence_sources") or [],
                "user_confirmed_pending_source": p.get("user_confirmed_pending_source") or [],
            }
        )
    return out


def build_ledger_payload(design: dict[str, Any]) -> dict[str, Any]:
    actuarial_rows = [_matrix_actuarial_row(r) for r in design.get("actuarial_career_matrix") or []]
    partner_rows = [_matrix_partner_row(r) for r in design.get("partner_gtm_matrix") or []]
    legacy_matrix = actuarial_rows + partner_rows
    pillars = _normalize_pillars(design.get("capability_taxonomy") or [])

    w4a = build_w4a_graph_package(pillars=pillars, legacy_skill_rows=legacy_matrix)
    skill_rows = w4a["skill_rows"]

    schema = design.get("schema_extension") or {}
    agentic_count = w4a["graph_metadata"]["deep_agentic_row_count"]
    return {
        "metadata": {
            "schema_version": "master_skills_arsenal_graph_v1",
            "extends": "master_candidate_skills_fact_ledger",
            "design_source": "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json",
            "materialized_from": "apps_rg/fact_inventory/materialize_arsenal_from_design.py",
            "status": "arsenal_ledger_requires_human_confirmation",
            "candidate_fact_ledger_ref": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
            "w4a_hardened": True,
            "pillar_count": len(pillars),
            "skill_row_count": len(skill_rows),
            "deep_agentic_row_count": agentic_count,
            "capability_domain_count": len(w4a.get("agentic_capability_domains") or []),
        },
        "graph_metadata": w4a["graph_metadata"],
        "graph_layers": w4a["graph_layers"],
        "graph_nodes": w4a["graph_nodes"],
        "graph_edges": w4a["graph_edges"],
        "external_claim_policies": w4a["external_claim_policies"],
        "agentic_runtime_matrix": w4a["agentic_runtime_matrix"],
        "agentic_capability_domains": w4a["agentic_capability_domains"],
        "graph_validation_rules": w4a["graph_validation_rules"],
        "resume_generation_policy": w4a["resume_generation_policy"],
        "support_levels": [
            "DIRECT_FROM_RESUME_ARCHIVE",
            "BUNDLE_SUPPORTED",
            "DERIVED_SUPPORTED",
            "METRIC_DIRECT",
            "TARGETING_ONLY",
            "STYLE_ONLY",
            "USER_CONFIRMED_PENDING_SOURCE",
            "REPO_EVIDENCE_PORTFOLIO",
            "INTERNAL_ONLY",
            "BLOCKED",
        ],
        "visibility_rules": schema.get("visibility_rules_catalog") or {
            "always": "Eligible when support_level is DIRECT and evidence present",
            "role_family_match": "Surface when role_family weight >= 0.7",
            "human_confirm": "Blocked from external until confirmation",
            "never_external": "Internal arsenal only",
        },
        "activation_statuses": ["DRAFT", "ACTIVE", "ACTIVE_CONFIRMED", "RETIRED"],
        "pillars": pillars,
        "skill_rows": skill_rows,
        "actuarial_career_matrix": design.get("actuarial_career_matrix") or [],
        "partner_gtm_matrix": design.get("partner_gtm_matrix") or [],
        "role_family_projection_profiles": design.get("role_family_projection_map") or {},
        "validation_rules": {
            "jd_briefing_never_proof": True,
            "targeting_only_never_proof": True,
            "style_only_never_proof": True,
            "blocked_never_external": True,
            "pending_source_requires_active_confirmed": True,
            "derived_requires_fact_id_links": True,
            "external_claim_requires_snippet_or_fact_link": True,
            "no_fact_links_internal_ranking_only_for_external_claims": True,
            "forbidden_phrase_cannot_appear_in_allowed_phrases": True,
            "capability_domain_primary_taxonomy": True,
            "skill_id_never_source_fact_id": True,
            "repo_portfolio_not_resume_default": True,
            "weak_snippet_internal_only": True,
            "ats_keywords_not_claims": True,
        },
    }


def main() -> int:
    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    payload = build_ledger_payload(design)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"WROTE {OUT_PATH} skill_rows={len(payload['skill_rows'])} "
        f"agentic={payload['metadata']['deep_agentic_row_count']} "
        f"edges={payload['graph_metadata']['edge_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
