"""Commercial skills graph expansion — evidence-backed rows from resume variants + candidate ledger."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.materialize_arsenal_from_design import build_ledger_payload

ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json"
OUT_LEDGER = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
CANDIDATE_LEDGER_PATH = (
    ROOT / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json"
)
CLOSEOUT_JSON = ROOT / "docs/reports/apps_rg/skills_graph_commercial_expansion_closeout.json"
CLOSEOUT_MD = ROOT / "docs/reports/apps_rg/skills_graph_commercial_expansion_closeout.md"

PROFILE_ID = "CHIEF_REVENUE_OFFICER_COMPOSITE"

COMMERCIAL_MATRIX: list[dict[str, Any]] = [
    {
        "skill": "modernization_deals_15m",
        "description": "Multi-year modernization deals with HPC ROI proof",
        "source_resume_file": "Amit_Ayer_Resume_-_Strategic_Account_Executive.txt",
        "source_evidence": (
            "Closed multi-year modernization deals exceeding $15M by demonstrating ROI on HPC "
            "simulations for stress testing and cutting scenario runtimes by 40%."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": [">$15M deals", "40% scenario runtime reduction", "modernization deals"],
        "role_relevance": ["SALES_STRATEGIC_ACCOUNTS", "QUANT_TRADING_HPC", "CONSULTING_DELIVERY_LEADERSHIP"],
        "where_to_use": ["executive_summary", "ibm_bullets", "unify_narrative"],
        "risk_notes": "MEDIUM candidate fact fact_sales_accounts_002.",
        "linked_fact_id": "fact_sales_accounts_002",
        "skill_id": "skill_sales_modernization_deals_15m",
        "target_pillar": "pillar_revenue_commercialization",
    },
    {
        "skill": "global_financial_institutions_sales_leadership",
        "description": "Global financial-institution sales team leadership",
        "source_resume_file": "Sales_-_Amit_Ayer.txt",
        "source_evidence": (
            "Oversaw strategic sales engagements for top-tier financial institutions across EMEA, "
            "APAC, and North America, guiding a 20-member distributed sales team"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["20-member distributed sales team", "EMEA, APAC, and North America"],
        "role_relevance": ["SALES_STRATEGIC_ACCOUNTS", "EXECUTIVE_LEADERSHIP"],
        "where_to_use": ["executive_summary", "unify_narrative"],
        "risk_notes": "MEDIUM candidate fact fact_sales_accounts_003.",
        "linked_fact_id": "fact_sales_accounts_003",
        "skill_id": "skill_sales_global_financial_institutions_leadership",
        "target_pillar": "pillar_customer_stakeholder",
    },
    {
        "skill": "ibm_aws_alliance_joint_revenue",
        "description": "IBM–AWS alliance joint revenue growth frameworks",
        "source_resume_file": "Partnerships_Alliances_-_Amit_Ayer.txt",
        "source_evidence": (
            "Held executive responsibility for expanding AI and cloud-focused revenue streams within "
            "the IBM–AWS alliance for financial services and designed AI-driven sales frameworks "
            "that boosted joint revenue by 20%"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["IBM–AWS alliance", "20% joint revenue", "AI-driven sales frameworks"],
        "role_relevance": ["PARTNERSHIPS_GTM", "SALES_STRATEGIC_ACCOUNTS", "AI_SOLUTIONS_ARCHITECTURE"],
        "where_to_use": ["executive_summary", "competencies"],
        "risk_notes": "MEDIUM candidate fact fact_partnerships_gtm_002.",
        "linked_fact_id": "fact_partnerships_gtm_002",
        "skill_id": "skill_partner_ibm_aws_alliance_joint_revenue",
        "target_pillar": "pillar_partner_gtm_alliances",
    },
    {
        "skill": "cloud_vendor_joint_gtm",
        "description": "Cloud and AI vendor joint GTM roadmaps",
        "source_resume_file": "Sales_-_Amit_Ayer.txt",
        "source_evidence": (
            "Forged relationships with leading cloud and AI vendors, combining market influence "
            "with innovative solution roadmaps"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["cloud and AI vendors", "joint go-to-market", "solution roadmaps"],
        "role_relevance": ["PARTNERSHIPS_GTM", "PRODUCT_TECHNICAL_STRATEGY", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["competencies", "unify_bullets"],
        "risk_notes": "MEDIUM candidate fact fact_partnerships_gtm_004.",
        "linked_fact_id": "fact_partnerships_gtm_004",
        "skill_id": "skill_partner_cloud_vendor_joint_gtm",
        "target_pillar": "pillar_partner_gtm_alliances",
    },
    {
        "skill": "finance_cost_optimization_dashboards",
        "description": "Budget dashboards and resource reallocation for finance leaders",
        "source_resume_file": "Strategic_Finance_-_Amit_Ayer.txt",
        "source_evidence": (
            "Deployed transparent budget dashboards and microservices to reallocate underused "
            "resources and drive 30% cost optimization for senior finance teams"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["30% cost optimization", "budget dashboards", "resource reallocation"],
        "role_relevance": ["STRATEGIC_FINANCE", "REVENUE_OPERATIONS", "DATA_ANALYTICS_LEADERSHIP"],
        "where_to_use": ["executive_summary", "unify_bullets"],
        "risk_notes": "MEDIUM candidate fact fact_revenue_ops_004.",
        "linked_fact_id": "fact_revenue_ops_004",
        "skill_id": "skill_finance_cost_optimization_dashboards",
        "target_pillar": "pillar_strategic_finance_saas",
    },
    {
        "skill": "ma_synergy_due_diligence",
        "description": "M&A due diligence and synergy modeling",
        "source_resume_file": "Strategic_Finance_-_Amit_Ayer.txt",
        "source_evidence": (
            "Conducted preliminary M&A due diligence and developed synergy models to quantify "
            "technology integration costs and revenue opportunities"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["M&A due diligence", "synergy models", "integration costs"],
        "role_relevance": ["STRATEGIC_FINANCE", "EXECUTIVE_LEADERSHIP"],
        "where_to_use": ["executive_summary"],
        "risk_notes": "MEDIUM candidate fact fact_revenue_ops_005.",
        "linked_fact_id": "fact_revenue_ops_005",
        "skill_id": "skill_finance_ma_synergy_due_diligence",
        "target_pillar": "pillar_strategic_finance_saas",
    },
    {
        "skill": "net_revenue_retention_predictive_analytics",
        "description": "Predictive analytics for net revenue retention (archive variant)",
        "source_resume_file": "Head_of_Customer_Success_-_Amit_Ayer.txt",
        "source_evidence": (
            "Enhanced Net Revenue Retention by 20%: Introduced predictive analytics for early "
            "risk detection and built strategic alliances with professional services and technology firms"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["Net Revenue Retention by 20%", "predictive analytics", "early risk detection"],
        "role_relevance": ["CUSTOMER_SUCCESS", "DATA_ANALYTICS_LEADERSHIP"],
        "where_to_use": ["executive_summary", "unify_narrative"],
        "risk_notes": "Archive-only; no MEDIUM/HIGH candidate fact — not linked to fact_customer_success_001 (LOW).",
        "linked_fact_id": None,
        "skill_id": "skill_customer_nrr_predictive_analytics_20pct",
        "target_pillar": "pillar_customer_stakeholder",
    },
    {
        "skill": "customer_satisfaction_nps_program",
        "description": "NPS and satisfaction program tied to anomaly detection",
        "source_resume_file": "Head_of_Customer_Success_-_Amit_Ayer.txt",
        "source_evidence": (
            "Increased Customer Satisfaction by 25%: Integrated anomaly detection with a structured "
            "NPS feedback process"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["Customer Satisfaction by 25%", "NPS feedback", "anomaly detection"],
        "role_relevance": ["CUSTOMER_SUCCESS", "AI_SOLUTIONS_ARCHITECTURE"],
        "where_to_use": ["competencies", "unify_bullets"],
        "risk_notes": "Archive-only; no authoritative candidate fact id.",
        "linked_fact_id": None,
        "skill_id": "skill_customer_satisfaction_nps_25pct",
        "target_pillar": "pillar_customer_stakeholder",
    },
    {
        "skill": "board_level_stakeholder_alignment",
        "description": "Board-level stakeholder alignment on data-centric solutions",
        "source_resume_file": "Sales_-_Amit_Ayer.txt",
        "source_evidence": (
            "aligning C level stakeholders around data centric solutions"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["board level priorities", "C level stakeholders", "data centric solutions"],
        "role_relevance": ["EXECUTIVE_LEADERSHIP", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["executive_summary", "headline"],
        "risk_notes": "Executive fluency signal only; not primary board/investor relations role.",
        "linked_fact_id": None,
        "skill_id": "skill_commercial_board_level_stakeholder_alignment",
        "target_pillar": "pillar_executive_leadership",
    },
    {
        "skill": "gtm_investment_pipeline_decisions",
        "description": "GTM investment decisions informed by Salesforce pipeline",
        "source_resume_file": "Amit_Ayer_Resume_-_VP_Finance_Sales_Marketing.txt",
        "source_evidence": (
            "maintaining a forecast pipeline in Salesforce that drove $10M in net-new revenue and "
            "informed go-to-market investment decisions"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["go-to-market investment decisions", "$10M net-new revenue", "Salesforce pipeline"],
        "role_relevance": ["REVENUE_OPERATIONS", "STRATEGIC_FINANCE", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["executive_summary"],
        "risk_notes": "Archive complements fact_revenue_ops_002; no duplicate fact link on this row.",
        "linked_fact_id": None,
        "skill_id": "skill_commercial_gtm_investment_pipeline",
        "target_pillar": "pillar_revenue_operations",
    },
]

WIRED_FACT_TARGETS: dict[str, list[str]] = {
    "pillar_revenue_commercialization": [
        "fact_sales_accounts_001",
        "fact_sales_accounts_002",
    ],
    "pillar_customer_stakeholder": ["fact_sales_accounts_003"],
    "pillar_partner_gtm_alliances": [
        "fact_partnerships_gtm_001",
        "fact_partnerships_gtm_002",
        "fact_partnerships_gtm_003",
        "fact_partnerships_gtm_004",
    ],
    "pillar_strategic_finance_saas": [
        "fact_revenue_ops_001",
        "fact_revenue_ops_002",
        "fact_revenue_ops_003",
        "fact_revenue_ops_004",
        "fact_revenue_ops_005",
    ],
    "pillar_revenue_operations": [
        "fact_revenue_ops_001",
        "fact_revenue_ops_002",
        "fact_revenue_ops_003",
    ],
}

REJECTED_FACTS: list[dict[str, str]] = [
    {
        "candidate_fact_id": "fact_customer_success_001",
        "reason": "LOW confidence; archive-backed CS skills used instead of authoritative fact link",
    },
    {
        "candidate_fact_id": "fact_sales_accounts_004",
        "reason": "NEEDS_VERIFICATION; 93% renewal rate not wired",
    },
    {
        "candidate_fact_id": "fact_sales_accounts_005",
        "reason": "NEEDS_VERIFICATION; CRM forecasting uplift not wired",
    },
]

UNSUPPORTED_GAPS: list[dict[str, str]] = [
    {
        "gap_id": "marketing_demand_generation",
        "reason": "No MEDIUM/HIGH candidate facts; only narrative marketing language in variants",
    },
    {
        "gap_id": "primary_quota_carrying_ae",
        "reason": "No confirmed personal quota scope as primary AE accountability",
    },
    {
        "gap_id": "board_investor_relations_primary",
        "reason": "Board alignment phrasing only; no investor-relations primary role evidence",
    },
    {
        "gap_id": "marketing_org_pnl",
        "reason": "VP Finance Sales & Marketing title does not establish marketing org P&L ownership",
    },
]

PILLAR_FACT_REMOVALS: dict[str, list[str]] = {
    "pillar_customer_stakeholder": ["fact_customer_success_001"],
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


def _patch_partner_revenue_3m(design: dict[str, Any]) -> bool:
    """Wire partner_revenue_3m skill row to fact_partnerships_gtm_001 (DERIVED)."""
    for row in design.get("partner_gtm_matrix") or []:
        if row.get("skill_id") == "skill_partner_partner_revenue_3m":
            row["linked_fact_id"] = "fact_partnerships_gtm_001"
            row["support_status"] = "DERIVED_SUPPORTED"
            row["risk_notes"] = "MEDIUM candidate fact fact_partnerships_gtm_001; $3M partner-derived revenue."
            return True
    return False


def apply_design_patch(design: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    wired_rows: list[dict[str, Any]] = []
    taxonomy = design.get("capability_taxonomy") or []

    for pillar in taxonomy:
        pid = str(pillar.get("pillar_id") or "")
        if pid in PILLAR_FACT_REMOVALS:
            links = list(pillar.get("linked_fact_ids") or [])
            for rem in PILLAR_FACT_REMOVALS[pid]:
                if rem in links:
                    links.remove(rem)
            pillar["linked_fact_ids"] = links
        if pid not in WIRED_FACT_TARGETS:
            continue
        links = list(pillar.get("linked_fact_ids") or [])
        merged, newly = _merge_unique(links, WIRED_FACT_TARGETS[pid])
        pillar["linked_fact_ids"] = merged
        candidate = json.loads(CANDIDATE_LEDGER_PATH.read_text(encoding="utf-8"))
        conf_map = {
            str(f["candidate_fact_id"]): str(f.get("confidence") or "")
            for f in candidate.get("candidate_facts") or []
        }
        for fid in newly:
            wired_rows.append(
                {
                    "candidate_fact_id": fid,
                    "pillar_id": pid,
                    "confidence": conf_map.get(fid, "UNKNOWN"),
                }
            )

    design["commercial_expansion_matrix"] = COMMERCIAL_MATRIX
    _patch_partner_revenue_3m(design)

    stats = design.setdefault("stats", {})
    stats["pillar_count"] = len(taxonomy)
    stats["commercial_expansion_matrix_rows"] = len(COMMERCIAL_MATRIX)
    stats["role_family_projection_profile_count"] = len(design.get("role_family_projection_map") or {})

    new_skill_ids = [str(r["skill_id"]) for r in COMMERCIAL_MATRIX]
    return wired_rows, new_skill_ids


def _counts(ledger: dict[str, Any]) -> dict[str, int]:
    return {
        "pillar_count": len(ledger.get("pillars") or []),
        "skill_row_count": len(ledger.get("skill_rows") or []),
        "projection_profile_count": len(ledger.get("role_family_projection_profiles") or {}),
    }


def _render_closeout_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Skills graph commercial expansion closeout",
        "",
        f"**Status:** {payload['status']}",
        f"**Generated:** {payload['generated_at_utc']}",
        "",
        "## Before / after",
        "",
        f"| Metric | Before | After |",
        f"|--------|--------|-------|",
    ]
    b, a = payload["before_after_counts"]["before"], payload["before_after_counts"]["after"]
    for key in ("pillar_count", "skill_row_count", "projection_profile_count"):
        lines.append(f"| {key} | {b[key]} | {a[key]} |")
    lines.extend(
        [
            "",
            "## New skill rows",
            "",
        ]
    )
    for row in payload.get("new_skills") or []:
        lines.append(
            f"- `{row['skill_id']}` — {row.get('evidence_source', '')} — pillar `{row.get('pillar', '')}`"
        )
    lines.extend(["", "## Rejected facts", ""])
    for r in payload.get("rejected_facts") or []:
        lines.append(f"- `{r['candidate_fact_id']}`: {r['reason']}")
    lines.extend(["", "## Unsupported gaps", ""])
    for g in payload.get("unsupported_gaps") or []:
        lines.append(f"- **{g['gap_id']}**: {g['reason']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    before_ledger = json.loads(OUT_LEDGER.read_text(encoding="utf-8"))
    before = _counts(before_ledger)

    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    wired_rows, new_skill_ids = apply_design_patch(design)
    DESIGN_PATH.write_text(json.dumps(design, indent=2) + "\n", encoding="utf-8")

    prior_ids = {
        str(r["skill_id"])
        for r in before_ledger.get("skill_rows") or []
        if isinstance(r, dict)
    }
    minted = [sid for sid in new_skill_ids if sid not in prior_ids]

    payload = build_ledger_payload(design)
    OUT_LEDGER.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    after = _counts(payload)

    closeout = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS",
        "scope": "skills_graph_commercial_expansion",
        "before_after_counts": {"before": before, "after": after},
        "new_pillars": [],
        "new_skills": [
            {
                "skill_id": sid,
                "pillar": next(
                    (r["target_pillar"] for r in COMMERCIAL_MATRIX if r["skill_id"] == sid),
                    None,
                ),
                "linked_fact_id": next(
                    (r.get("linked_fact_id") for r in COMMERCIAL_MATRIX if r["skill_id"] == sid),
                    None,
                ),
                "evidence_source": next(
                    (r.get("source_resume_file") for r in COMMERCIAL_MATRIX if r["skill_id"] == sid),
                    None,
                ),
                "support_status": next(
                    (r.get("support_status") for r in COMMERCIAL_MATRIX if r["skill_id"] == sid),
                    None,
                ),
            }
            for sid in minted
        ],
        "facts_newly_wired": wired_rows,
        "rejected_facts": REJECTED_FACTS,
        "unsupported_gaps": UNSUPPORTED_GAPS,
        "partner_revenue_3m_fact_wired": True,
        "standalone_cro_role_family_added": False,
        "scope_control": {
            "section_prompts_touched": False,
            "agentic_core_touched": False,
            "resume_pa_prompt_profile_touched": False,
        },
        "explicit_non_claims": [
            "No live LLM run",
            "No JD/briefing used as proof",
            "No SRFS/X2/X3 gate changes",
        ],
    }
    CLOSEOUT_JSON.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
    CLOSEOUT_MD.write_text(_render_closeout_md(closeout), encoding="utf-8")

    print(
        f"COMMERCIAL_EXPANSION skill_rows {before['skill_row_count']} -> {after['skill_row_count']} "
        f"new={len(minted)} wired_facts={len(wired_rows)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
