"""Apply CRO composite projection hardening to design JSON and rematerialize arsenal ledger."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.build_cro_projection_gap_analysis import (
    OUT_JSON,
    OUT_MD,
    PROFILE_ID,
    build_gap_payload,
    render_markdown,
)
from apps_rg.fact_inventory.materialize_arsenal_from_design import build_ledger_payload

ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json"
OUT_LEDGER = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
CANDIDATE_LEDGER_PATH = (
    ROOT / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
)

PILLAR_REVOPS = "pillar_revenue_operations"

REVOPS_MATRIX: list[dict[str, Any]] = [
    {
        "skill": "salesforce_pipeline_analytics",
        "description": "Salesforce analytics prioritizing high-potential deals",
        "source_resume_file": "Revenue_Operations_-_Amit_Ayer.txt",
        "source_evidence": (
            "Designed analytics in Salesforce to prioritize high-potential deals, "
            "generating $10M in new annual recurring revenue"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["$10M new ARR", "Salesforce analytics", "prioritize high-potential deals"],
        "role_relevance": ["REVENUE_OPERATIONS", "SALES_STRATEGIC_ACCOUNTS", "STRATEGIC_FINANCE"],
        "where_to_use": ["executive_summary", "competencies", "unify_bullets"],
        "risk_notes": "MEDIUM candidate fact; metrics bound to fact_revenue_ops_001.",
        "linked_fact_id": "fact_revenue_ops_001",
        "skill_id": "skill_revops_salesforce_pipeline_analytics",
    },
    {
        "skill": "salesforce_forecast_pipeline",
        "description": "Salesforce forecast pipeline for net-new revenue",
        "source_resume_file": "Amit_Ayer_Resume_-_VP_Finance_Sales_Marketing.txt",
        "source_evidence": (
            "maintaining a forecast pipeline in Salesforce that drove $10M in net-new revenue"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["$10M net-new revenue", "Salesforce forecast pipeline"],
        "role_relevance": ["REVENUE_OPERATIONS", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["executive_summary", "unify_narrative"],
        "risk_notes": "MEDIUM candidate fact; metrics bound to fact_revenue_ops_002.",
        "linked_fact_id": "fact_revenue_ops_002",
        "skill_id": "skill_revops_salesforce_forecast_pipeline",
    },
    {
        "skill": "usage_based_subscription_forecasting",
        "description": "Usage-based forecasting for subscription pricing and renewals",
        "source_resume_file": "Strategic Finance - Amit Ayer.txt",
        "source_evidence": (
            "Developed AI-enhanced usage-based forecasting models to optimize subscription "
            "pricing and renewals, adding $5M in recurring revenue"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["usage-based forecasting", "$5M recurring revenue", "subscription pricing"],
        "role_relevance": ["REVENUE_OPERATIONS", "STRATEGIC_FINANCE", "PRODUCT_TECHNICAL_STRATEGY"],
        "where_to_use": ["executive_summary", "unify_bullets"],
        "risk_notes": "MEDIUM candidate fact; metrics bound to fact_revenue_ops_003.",
        "linked_fact_id": "fact_revenue_ops_003",
        "skill_id": "skill_revops_usage_based_subscription_forecasting",
    },
    {
        "skill": "sales_forecasting_frameworks",
        "description": "CRM-harmonized sales forecasting frameworks",
        "source_resume_file": "Revenue_Operations_-_Amit_Ayer.txt",
        "source_evidence": (
            "Implemented robust sales forecasting frameworks, harmonizing CRM data with "
            "executive insights to drive accurate revenue projections"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["sales forecasting frameworks", "CRM data", "revenue projections"],
        "role_relevance": ["REVENUE_OPERATIONS", "STRATEGIC_FINANCE"],
        "where_to_use": ["competencies"],
        "risk_notes": "Archive-backed; no standalone candidate fact id.",
        "linked_fact_id": None,
        "skill_id": "skill_revops_sales_forecasting_frameworks",
    },
    {
        "skill": "multi_channel_gtm_alignment",
        "description": "Multi-channel GTM aligning marketing, product, and sales",
        "source_resume_file": "Revenue_Operations_-_Amit_Ayer.txt",
        "source_evidence": (
            "Architected multi-channel GTM strategies, aligning marketing, product, and sales "
            "to expand market share and increase ARR"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["multi-channel GTM", "aligning marketing, product, and sales"],
        "role_relevance": ["REVENUE_OPERATIONS", "PARTNERSHIPS_GTM", "PRODUCT_TECHNICAL_STRATEGY"],
        "where_to_use": ["executive_summary", "competencies"],
        "risk_notes": "Archive GTM alignment only; not full marketing-org leadership proof.",
        "linked_fact_id": None,
        "skill_id": "skill_revops_multi_channel_gtm_alignment",
    },
]

CRO_PROFILE: dict[str, Any] = {
    "label": "Chief Revenue Officer (composite projection)",
    "profile_kind": "composite_role_family_projection",
    "taxonomy_ids": [
        "REVENUE_OPERATIONS",
        "SALES_STRATEGIC_ACCOUNTS",
        "PARTNERSHIPS_GTM",
        "CUSTOMER_SUCCESS",
        "STRATEGIC_FINANCE",
        "EXECUTIVE_LEADERSHIP",
        "PRODUCT_TECHNICAL_STRATEGY",
    ],
    "role_family_weights": {
        "REVENUE_OPERATIONS": 1.0,
        "SALES_STRATEGIC_ACCOUNTS": 0.95,
        "PARTNERSHIPS_GTM": 0.9,
        "CUSTOMER_SUCCESS": 0.85,
        "STRATEGIC_FINANCE": 0.8,
        "EXECUTIVE_LEADERSHIP": 0.75,
        "PRODUCT_TECHNICAL_STRATEGY": 0.7,
    },
    "top_weighted_pillars": [
        {"pillar_id": PILLAR_REVOPS, "weight": 1.0},
        {"pillar_id": "pillar_revenue_commercialization", "weight": 0.95},
        {"pillar_id": "pillar_partner_gtm_alliances", "weight": 0.9},
        {"pillar_id": "pillar_presales_solutioning", "weight": 0.85},
        {"pillar_id": "pillar_customer_stakeholder", "weight": 0.8},
        {"pillar_id": "pillar_strategic_finance_saas", "weight": 0.75},
        {"pillar_id": "pillar_executive_leadership", "weight": 0.7},
    ],
    "deprioritize_pillars": [
        "pillar_derivatives_structured",
        "pillar_greeks_hedging",
        "pillar_actuarial_foundation",
        "pillar_embedded_options_insurance",
        "pillar_trading_hpc",
        "pillar_agentic_ai_platforms",
    ],
    "executive_summary_skill_budget": {
        "pipeline_revops": 2,
        "commercialization": 2,
        "partnerships_gtm": 2,
        "customer_lifecycle": 1,
        "executive_operating_model": 1,
    },
    "notes": "Composite projection only; not a canonical role_families taxonomy id.",
}

REJECTED_FACTS: list[dict[str, str]] = [
    {
        "candidate_fact_id": "fact_customer_success_001",
        "reason": "LOW confidence; not promoted to authoritative skill rows",
    },
    {
        "candidate_fact_id": "fact_sales_accounts_004",
        "reason": "NEEDS_VERIFICATION; renewal rate not wired to new RevOps skills",
    },
    {
        "candidate_fact_id": "fact_sales_accounts_005",
        "reason": "NEEDS_VERIFICATION; CRM forecasting uplift not wired without confirmation",
    },
]

WIRED_FACT_TARGETS: dict[str, list[str]] = {
    PILLAR_REVOPS: ["fact_revenue_ops_001", "fact_revenue_ops_002", "fact_revenue_ops_003"],
    "pillar_strategic_finance_saas": ["fact_revenue_ops_001", "fact_revenue_ops_002", "fact_revenue_ops_004"],
    "pillar_revenue_commercialization": ["fact_sales_accounts_002"],
}


def _merge_unique(existing: list[str], add: list[str]) -> tuple[list[str], list[str]]:
    seen = set(existing)
    newly: list[str] = []
    for fid in add:
        if fid not in seen:
            existing.append(fid)
            seen.add(fid)
            newly.append(fid)
    return existing, newly


def _ensure_revops_pillar(taxonomy: list[dict[str, Any]]) -> bool:
    if any(p.get("pillar_id") == PILLAR_REVOPS for p in taxonomy):
        return False
    pillar = {
        "pillar_id": PILLAR_REVOPS,
        "name": "Revenue Operations / Pipeline Governance",
        "description": (
            "Pipeline instrumentation, Salesforce analytics, forecasting rigor, "
            "and revenue process design across sales and finance."
        ),
        "subskills": [
            "salesforce_pipeline_analytics",
            "salesforce_forecast_pipeline",
            "usage_based_subscription_forecasting",
            "sales_forecasting_frameworks",
            "multi_channel_gtm_alignment",
            "cpq_automation",
        ],
        "evidence_sources": [
            "Revenue_Operations_-_Amit_Ayer.txt",
            "Amit_Ayer_Resume_-_VP_Finance_Sales_Marketing.txt",
            "Strategic Finance - Amit Ayer.txt",
        ],
        "archive_snippets": [
            "Designed analytics in Salesforce to prioritize high-potential deals",
            "forecast pipeline in Salesforce that drove $10M in net-new revenue",
            "Implemented robust sales forecasting frameworks, harmonizing CRM data",
        ],
        "user_confirmed_pending_source": [],
        "linked_fact_ids": [
            "fact_revenue_ops_001",
            "fact_revenue_ops_002",
            "fact_revenue_ops_003",
        ],
        "allowed_phrases": [
            "$10M new ARR",
            "$10M net-new revenue",
            "Salesforce analytics",
            "forecast pipeline",
            "usage-based forecasting",
        ],
        "forbidden_phrases_without_stronger_support": [
            "personally carried $100M quota every year"
        ],
        "role_family_weights": {
            "REVENUE_OPERATIONS": 1.0,
            "SALES_STRATEGIC_ACCOUNTS": 0.85,
            "STRATEGIC_FINANCE": 0.8,
        },
        "section_fit": {
            "headline": False,
            "executive_summary": True,
            "competencies": True,
            "unify_bullets": True,
            "unify_narrative": True,
            "ibm_bullets": False,
            "ibm_narrative": False,
            "early_career": False,
        },
    }
    insert_at = next(
        (i + 1 for i, p in enumerate(taxonomy) if p.get("pillar_id") == "pillar_revenue_commercialization"),
        len(taxonomy),
    )
    taxonomy.insert(insert_at, pillar)
    return True


def apply_design_patch(design: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    wired_rows: list[dict[str, Any]] = []
    taxonomy = design.setdefault("capability_taxonomy", [])
    _ensure_revops_pillar(taxonomy)

    for pillar in taxonomy:
        pid = str(pillar.get("pillar_id") or "")
        if pid not in WIRED_FACT_TARGETS:
            continue
        links = list(pillar.get("linked_fact_ids") or [])
        merged, newly = _merge_unique(links, WIRED_FACT_TARGETS[pid])
        pillar["linked_fact_ids"] = merged
        for fid in newly:
            wired_rows.append({"candidate_fact_id": fid, "pillar_id": pid, "confidence": "MEDIUM"})

    design["revenue_operations_matrix"] = REVOPS_MATRIX
    profiles = design.setdefault("role_family_projection_map", {})
    profiles[PROFILE_ID] = CRO_PROFILE

    stats = design.setdefault("stats", {})
    stats["pillar_count"] = len(taxonomy)
    stats["revenue_operations_matrix_rows"] = len(REVOPS_MATRIX)
    stats["role_family_projection_profile_count"] = len(profiles)

    new_skill_ids = [str(r["skill_id"]) for r in REVOPS_MATRIX]
    return wired_rows, new_skill_ids


def main() -> int:
    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    wired_rows, new_skill_ids = apply_design_patch(design)
    DESIGN_PATH.write_text(json.dumps(design, indent=2) + "\n", encoding="utf-8")

    payload = build_ledger_payload(design)
    prior_ids = {
        str(r["skill_id"])
        for r in json.loads(OUT_LEDGER.read_text(encoding="utf-8")).get("skill_rows") or []
        if isinstance(r, dict)
    }
    minted = [sid for sid in new_skill_ids if sid not in prior_ids]

    OUT_LEDGER.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    candidate = json.loads(CANDIDATE_LEDGER_PATH.read_text(encoding="utf-8"))
    gap = build_gap_payload(
        ledger=payload,
        design=design,
        candidate=candidate,
        wired_facts=wired_rows,
        new_skills=minted,
        rejected=REJECTED_FACTS,
    )
    OUT_JSON.write_text(json.dumps(gap, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(render_markdown(gap), encoding="utf-8")

    print(
        f"DESIGN patched; LEDGER skill_rows={len(payload['skill_rows'])} "
        f"profiles={len(payload['role_family_projection_profiles'])} "
        f"new_revops_skills={len(minted)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
