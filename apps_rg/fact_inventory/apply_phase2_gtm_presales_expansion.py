"""Phase 2 (TRACK_DATA_TECH_CLOUD_ML) GTM / pre-sales / technical-presales graph expansion.

Grounds new nodes in resume archive refs, base resume facts, and candidate-fact ledger.
Does not modify Phase 1 actuarial track or Phase 3 genai track semantics.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.utils import write_gateway as _wg

from apps_rg.fact_inventory.materialize_arsenal_from_design import build_ledger_payload
from apps_rg.fact_inventory.materialize_career_tracks_p1 import run_materialize as rematerialize_career_tracks

ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json"
OUT_LEDGER = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
TAXONOMY_PATH = ROOT / "docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json"
BASE_RESUME_PATH = ROOT / "apps_rg/resume/base/amit_ayer_base_resume_v1.json"
CLOSEOUT_JSON = ROOT / "docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json"
CLOSEOUT_MD = ROOT / "docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.md"

PILLAR_GTM = "pillar_gtm_presales_motion"
PILLAR_TECH = "pillar_technical_presales_accelerators"

NEW_PILLARS: list[dict[str, Any]] = [
    {
        "pillar_id": PILLAR_GTM,
        "name": "Go-to-Market / Pre-Sales Motion",
        "description": (
            "Discovery through pursuit: qualification, solution mapping, stakeholder and "
            "executive-buyer alignment, commercial validation, deal support, and delivery handoff."
        ),
        "subskills": [
            "discovery_qualification",
            "solution_mapping",
            "stakeholder_alignment",
            "executive_buyer_alignment",
            "commercial_validation",
            "deal_support",
            "presales_to_delivery_handoff",
            "joint_gtm_roadmaps",
        ],
        "evidence_sources": [
            "Sales - Amit Ayer.txt",
            "Partnerships & Alliances - Amit Ayer.docx",
            "Field CTO - Amit Ayer.docx",
            "Amit Ayer Resume - VP Finance Sales & Marketing.txt",
        ],
        "archive_snippets": [
            "aligning C level stakeholders around data centric solutions",
            "executive workshops, leading to faster adoption",
            "validating measurable ROI for clients through pilot engagements",
        ],
        "user_confirmed_pending_source": [
            "primary_quota_carrying_ae",
            "major_airline_client_naming",
            "engagement_100m_scope_ownership",
        ],
        "linked_fact_ids": [
            "fact_sales_accounts_001",
            "fact_revenue_ops_001",
            "fact_partnerships_gtm_004",
            "fact_partnerships_gtm_005",
            "fact_solutions_001",
        ],
        "allowed_phrases": [
            "discovery",
            "qualification",
            "solution mapping",
            "stakeholder alignment",
            "executive workshops",
            "pilot engagements",
            "measurable ROI",
            "deal support",
            "go-to-market",
        ],
        "forbidden_phrases_without_stronger_support": [
            "carried $100M presales quota",
            "owned $100M engagement",
            "major airline client",
            "primary customer-success owner",
        ],
        "role_family_weights": {
            "SALES_STRATEGIC_ACCOUNTS": 1.0,
            "AI_SOLUTIONS_ARCHITECTURE": 0.9,
            "PARTNERSHIPS_GTM": 0.85,
            "REVENUE_OPERATIONS": 0.75,
        },
        "section_fit": {
            "headline": False,
            "executive_summary": True,
            "competencies": True,
            "unify_bullets": True,
            "unify_narrative": True,
            "ibm_bullets": True,
            "ibm_narrative": True,
            "early_career": False,
        },
    },
    {
        "pillar_id": PILLAR_TECH,
        "name": "Technical Pre-Sales Accelerators",
        "description": (
            "Reference architectures, repeatable DevOps/CI-CD blueprints, AWS modernization patterns, "
            "demoable accelerators, adoption de-risking, and reusable implementation assets for pursuits."
        ),
        "subskills": [
            "reference_architectures",
            "devops_pipeline_blueprints",
            "aws_modernization_patterns",
            "estimation_sizing_models",
            "demoable_end_to_end_flows",
            "adoption_derisking_patterns",
            "reusable_implementation_accelerators",
        ],
        "evidence_sources": [
            "Partnerships & Alliances - Amit Ayer.docx",
            "Industry Solutions - Amit Ayer.txt",
            "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        ],
        "archive_snippets": [
            "AWS Partner: Advanced Migration and Modernization Sales Training",
            "generative AI Solution Accelerator",
            "cloud-native architectures",
        ],
        "user_confirmed_pending_source": [
            "major_airline_devops_pipeline_engagement",
            "engagement_100m_technical_or_commercial_ownership",
            "formal_estimation_sizing_models",
        ],
        "linked_fact_ids": [
            "fact_solutions_002",
            "fact_engineering_platform_003",
            "fact_engineering_platform_005",
            "fact_engineering_platform_006",
            "fact_partnerships_gtm_002",
        ],
        "allowed_phrases": [
            "reference architecture",
            "AWS modernization",
            "cloud migration",
            "CI/CD",
            "Solution Accelerator",
            "reusable platform",
            "pilot engagements",
        ],
        "forbidden_phrases_without_stronger_support": [
            "$100M engagement owner",
            "major airline",
            "DevOps pipeline for major airline",
        ],
        "role_family_weights": {
            "AI_SOLUTIONS_ARCHITECTURE": 1.0,
            "ENGINEERING_PLATFORM": 0.95,
            "PARTNERSHIPS_GTM": 0.85,
            "CONSULTING_DELIVERY_LEADERSHIP": 0.8,
        },
        "section_fit": {
            "headline": False,
            "executive_summary": True,
            "competencies": True,
            "unify_bullets": True,
            "unify_narrative": True,
            "ibm_bullets": True,
            "ibm_narrative": True,
            "early_career": False,
        },
    },
]

PHASE2_GTM_MATRIX: list[dict[str, Any]] = [
    {
        "skill": "discovery_qualification",
        "description": "Discovery and qualification via pipeline analytics",
        "source_resume_file": "Strategic Finance - Amit Ayer.txt",
        "source_evidence": (
            "Designed analytics in Salesforce to prioritize high-potential deals, generating $10M "
            "in new annual recurring revenue and refining GTM strategies."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["prioritize high-potential deals", "GTM strategies"],
        "role_relevance": ["REVENUE_OPERATIONS", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["executive_summary", "competencies"],
        "risk_notes": "MEDIUM candidate fact fact_revenue_ops_001.",
        "linked_fact_id": "fact_revenue_ops_001",
        "skill_id": "skill_p2_gtm_discovery_qualification",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "solution_mapping_executive_value",
        "description": "Solution mapping to executive value and ROI",
        "source_resume_file": "Field CTO - Amit Ayer.txt",
        "source_evidence": (
            "Translated complex AI, data, and cloud architecture into executive value propositions "
            "and measurable ROI for senior stakeholders."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["executive value propositions", "measurable ROI"],
        "role_relevance": ["AI_SOLUTIONS_ARCHITECTURE", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["executive_summary", "competencies", "ibm_narrative"],
        "risk_notes": "MEDIUM; fact_solutions_001 BLOCKED in SRFS audit — graph skill anchor only.",
        "linked_fact_id": "fact_solutions_001",
        "skill_id": "skill_p2_gtm_solution_mapping",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "stakeholder_alignment_governance",
        "description": "Stakeholder alignment across partner and client governance",
        "source_resume_file": "AI and Data Governance - Amit Ayer.txt",
        "source_evidence": (
            "Facilitated an executive governance council with partner stakeholders to align solution "
            "architecture, data security protocols, and regulatory mandates."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["executive governance council", "stakeholder alignment"],
        "role_relevance": ["PARTNERSHIPS_GTM", "AI_GOVERNANCE_RISK", "EXECUTIVE_LEADERSHIP"],
        "where_to_use": ["executive_summary", "unify_narrative"],
        "risk_notes": "MEDIUM candidate fact fact_partnerships_gtm_005.",
        "linked_fact_id": "fact_partnerships_gtm_005",
        "skill_id": "skill_p2_gtm_stakeholder_alignment",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "executive_buyer_alignment",
        "description": "Executive / CFO buyer alignment on data-centric solutions",
        "source_resume_file": "Sales - Amit Ayer.txt",
        "source_evidence": (
            "Drove $5M in annual contract value by aligning generative AI workflows with CFO priorities "
            "and facilitating enterprise-wide adoption of data-driven decision-making."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["CFO priorities", "enterprise-wide adoption", "$5M ACV"],
        "role_relevance": ["SALES_STRATEGIC_ACCOUNTS", "EXECUTIVE_LEADERSHIP"],
        "where_to_use": ["executive_summary", "headline"],
        "risk_notes": "MEDIUM candidate fact fact_sales_accounts_001.",
        "linked_fact_id": "fact_sales_accounts_001",
        "skill_id": "skill_p2_gtm_executive_buyer_alignment",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "commercial_validation_pilots",
        "description": "Commercial validation through pilots and measurable ROI",
        "source_resume_file": "Partnerships & Alliances - Amit Ayer.docx",
        "source_evidence": "validating measurable ROI for clients through pilot engagements",
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["pilot engagements", "measurable ROI"],
        "role_relevance": ["AI_SOLUTIONS_ARCHITECTURE", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["ibm_bullets", "competencies"],
        "risk_notes": "Archive-backed; complements existing skill_partner_pre_sales.",
        "linked_fact_id": None,
        "skill_id": "skill_p2_gtm_commercial_validation_pilots",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "enterprise_deal_support",
        "description": "Enterprise deal support and ACV pursuit",
        "source_resume_file": "Sales - Amit Ayer.txt",
        "source_evidence": "Drove $5 Million in Annual Contract Value",
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["Annual Contract Value", "enterprise-wide adoption"],
        "role_relevance": ["SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["unify_narrative", "executive_summary"],
        "risk_notes": "Same fact as skill_partner_customer_deal_support; Phase-2 pillar placement.",
        "linked_fact_id": "fact_sales_accounts_001",
        "skill_id": "skill_p2_gtm_enterprise_deal_support",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "presales_to_delivery_handoff",
        "description": "Handoff from pursuit to reusable delivery / platform IP",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "converting bespoke client delivery into reusable IP deployed across enterprise lines of business"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": [
            "reusable IP",
            "bespoke client delivery",
            "Solution Accelerator",
        ],
        "role_relevance": ["CONSULTING_DELIVERY_LEADERSHIP", "PRODUCT_TECHNICAL_STRATEGY"],
        "where_to_use": ["unify_narrative", "unify_bullets"],
        "risk_notes": "Base resume exp_unify_001 narrative; not a named pre-sales title.",
        "linked_fact_id": None,
        "skill_id": "skill_p2_gtm_presales_delivery_handoff",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "joint_gtm_cloud_vendor_roadmaps",
        "description": "Joint GTM and solution roadmaps with cloud/AI vendors",
        "source_resume_file": "Sales - Amit Ayer.txt",
        "source_evidence": (
            "Forged relationships with leading cloud and AI vendors, combining market influence "
            "with innovative solution roadmaps"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["joint go-to-market", "solution roadmaps", "cloud and AI vendors"],
        "role_relevance": ["PARTNERSHIPS_GTM", "SALES_STRATEGIC_ACCOUNTS"],
        "where_to_use": ["competencies", "unify_bullets"],
        "risk_notes": "MEDIUM candidate fact fact_partnerships_gtm_004.",
        "linked_fact_id": "fact_partnerships_gtm_004",
        "skill_id": "skill_p2_gtm_joint_vendor_roadmaps",
        "target_pillar": PILLAR_GTM,
        "evidence_confidence": "MEDIUM",
    },
]

PHASE2_TECH_MATRIX: list[dict[str, Any]] = [
    {
        "skill": "reference_architecture_industry_solutions",
        "description": "Industry reference architectures for regulated modernization",
        "source_resume_file": "Industry Solutions - Amit Ayer.txt",
        "source_evidence": (
            "Developed industry-specific AI, analytics, and cloud modernization solutions across "
            "financial-services risk, compliance, fraud, and regulatory use cases."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["industry-specific", "cloud modernization solutions", "reference architecture"],
        "role_relevance": ["AI_SOLUTIONS_ARCHITECTURE", "CONSULTING_DELIVERY_LEADERSHIP"],
        "where_to_use": ["competencies", "ibm_bullets"],
        "risk_notes": "MEDIUM; fact_solutions_002 BLOCKED in SRFS audit — graph anchor only.",
        "linked_fact_id": "fact_solutions_002",
        "skill_id": "skill_p2_tech_reference_architecture",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "aws_migration_modernization_patterns",
        "description": "AWS migration and modernization patterns (partner + delivery)",
        "source_resume_file": "Partnerships & Alliances - Amit Ayer.docx",
        "source_evidence": "AWS Partner: Advanced Migration and Modernization Sales Training",
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["AWS Partner", "Migration and Modernization", "cloud migration"],
        "role_relevance": ["PARTNERSHIPS_GTM", "ENGINEERING_PLATFORM"],
        "where_to_use": ["competencies", "ibm_bullets"],
        "risk_notes": "Complements skill_partner_aws_ecosystem; verify accreditations against portal.",
        "linked_fact_id": "fact_partnerships_gtm_002",
        "skill_id": "skill_p2_tech_aws_modernization_patterns",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "devops_pipeline_cicd_blueprint",
        "description": "Repeatable DevOps / AI CI-CD pipeline blueprint",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Strengthened enterprise retrieval quality, context assembly, evaluation gates, telemetry "
            "instrumentation, rollback controls, and AI CI/CD standards"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["AI CI/CD standards", "evaluation gates", "rollback controls"],
        "role_relevance": ["ENGINEERING_PLATFORM", "AI_SOLUTIONS_ARCHITECTURE"],
        "where_to_use": ["unify_bullets", "competencies"],
        "risk_notes": "HIGH base resume bul_unify_003 + candidate fact_engineering_platform_003.",
        "linked_fact_id": "fact_engineering_platform_003",
        "skill_id": "skill_p2_tech_devops_pipeline_blueprint",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "demoable_solution_accelerator",
        "description": "Demoable end-to-end Solution Accelerator flows",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "commercialization of a production-grade generative AI Solution Accelerator within a consulting firm"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["Solution Accelerator", "production-grade generative AI"],
        "role_relevance": ["PRODUCT_TECHNICAL_STRATEGY", "AI_SOLUTIONS_ARCHITECTURE"],
        "where_to_use": ["unify_narrative", "executive_summary"],
        "risk_notes": "Base resume exp_unify_001 role_narrative.",
        "linked_fact_id": None,
        "skill_id": "skill_p2_tech_demoable_accelerator",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "reusable_implementation_accelerators",
        "description": "Reusable implementation accelerators and platform IP",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Productized core agentic AI primitives into reusable platform services, generating $22M in IP-led revenue"
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["reusable platform services", "$22M IP-led revenue"],
        "role_relevance": ["ENGINEERING_PLATFORM", "PRODUCT_TECHNICAL_STRATEGY"],
        "where_to_use": ["unify_bullets", "executive_summary"],
        "risk_notes": "HIGH candidate fact fact_engineering_platform_006.",
        "linked_fact_id": "fact_engineering_platform_006",
        "skill_id": "skill_p2_tech_reusable_accelerators",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "adoption_derisking_pilots",
        "description": "Adoption de-risking via pilots, workshops, and governance",
        "source_resume_file": "Partnerships & Alliances - Amit Ayer.docx",
        "source_evidence": (
            "executive workshops, leading to faster adoption across major financial accounts"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["executive workshops", "faster adoption"],
        "role_relevance": ["AI_SOLUTIONS_ARCHITECTURE", "PARTNERSHIPS_GTM"],
        "where_to_use": ["ibm_narrative", "competencies"],
        "risk_notes": "Financial-institution accounts only in archive; not airline-specific.",
        "linked_fact_id": None,
        "skill_id": "skill_p2_tech_adoption_derisking",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "ibm_cloud_portfolio_architecture_anchor",
        "description": "Large cloud/AI portfolio technical architecture (IBM Partner)",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Led architecture and commercial ownership of a $30M cloud and AI transformation portfolio"
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["$30M cloud and AI transformation portfolio", "systems architect"],
        "role_relevance": ["AI_SOLUTIONS_ARCHITECTURE", "CONSULTING_DELIVERY_LEADERSHIP"],
        "where_to_use": ["ibm_narrative", "executive_summary"],
        "risk_notes": "NOT airline/$100M; scoped to IBM base-resume portfolio claim only.",
        "linked_fact_id": None,
        "skill_id": "skill_p2_tech_ibm_cloud_portfolio_anchor",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "estimation_sizing_directional",
        "description": "Estimation and sizing models (directional — no metric anchor)",
        "source_resume_file": None,
        "source_evidence": None,
        "support_status": "INTERNAL_ONLY",
        "allowed_phrases": [],
        "role_relevance": ["AI_SOLUTIONS_ARCHITECTURE", "CONSULTING_DELIVERY_LEADERSHIP"],
        "where_to_use": [],
        "risk_notes": "INFERENCE_ONLY: no resume-archive or candidate-fact sizing/estimation proof located.",
        "linked_fact_id": None,
        "skill_id": "skill_p2_tech_estimation_sizing_directional",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "LOW",
    },
    {
        "skill": "anchor_major_airline_devops_aws_directional",
        "description": "Major-airline DevOps/AWS modernization engagement (directional anchor)",
        "source_resume_file": None,
        "source_evidence": None,
        "support_status": "INTERNAL_ONLY",
        "allowed_phrases": [],
        "role_relevance": ["AI_SOLUTIONS_ARCHITECTURE", "CONSULTING_DELIVERY_LEADERSHIP"],
        "where_to_use": [],
        "risk_notes": (
            "INFERENCE_ONLY_PENDING_OPERATOR_SOURCE: operator requested major-airline ~$100M "
            "DevOps/AWS engagement anchor; no matching text in repo resume archive or candidate ledger."
        ),
        "linked_fact_id": None,
        "skill_id": "skill_p2_anchor_major_airline_devops_aws",
        "target_pillar": PILLAR_TECH,
        "evidence_confidence": "LOW",
    },
]

EXPLICIT_NON_CLAIMS: list[str] = [
    "No repo evidence for major-airline client naming or ~$100M engagement scope.",
    "No claim of personal ownership of a $100M presales quota (forbidden on pillar_presales_solutioning).",
    "No claim of full $100M engagement ownership (operator anchor is directional only).",
    "IBM $30M cloud/AI portfolio (base resume) is not the airline engagement and must not be conflated.",
    "No customer-success-primary claims added (per guardrail).",
    "fact_solutions_001/002 remain SRFS-blocked; graph skills are anchors pending human confirm.",
    "Delivery execution at Unify/IBM does not imply named pre-sales quota carrying without archive proof.",
]

EVIDENCE_GAPS: list[dict[str, str]] = [
    {
        "gap_id": "major_airline_client_context",
        "reason": "No airline/aviation/travel carrier string in resume archive, base resume, or candidate ledger.",
        "promotion_requires": "Phase I resume variant or SOW naming airline + role scope.",
    },
    {
        "gap_id": "engagement_100m_scope",
        "reason": "Only $100M strings in graph are forbidden presales-quota phrases, not engagement proof.",
        "promotion_requires": "Signed SOW/CRM export or resume bullet with engagement TCV and role (not personal quota).",
    },
    {
        "gap_id": "devops_pipeline_major_airline",
        "reason": "DevOps/CI-CD evidence is Unify platform engineering, not airline-client-specific.",
        "promotion_requires": "Client-named delivery receipt or resume bullet tying pipeline work to airline program.",
    },
    {
        "gap_id": "presales_contribution_airline",
        "reason": "Pre-sales workshop/pilot evidence is financial-institution phrasing in archive.",
        "promotion_requires": "Archive line naming airline + solutioning/pursuit role.",
    },
    {
        "gap_id": "commercial_outcome_airline",
        "reason": "No closed-won / TCV outcome linked to airline in candidate facts.",
        "promotion_requires": "fact_sales_accounts_* or partnerships fact with airline + metric.",
    },
    {
        "gap_id": "estimation_sizing_models",
        "reason": "No estimation/sizing model evidence in ledger.",
        "promotion_requires": "Resume or artifact describing sizing methodology used in pursuits.",
    },
]


def _upsert_pillars(taxonomy: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[str]]:
    by_id = {str(p["pillar_id"]): p for p in taxonomy}
    added: list[str] = []
    for pillar in NEW_PILLARS:
        pid = pillar["pillar_id"]
        if pid in by_id:
            by_id[pid] = {**by_id[pid], **pillar}
        else:
            by_id[pid] = pillar
            added.append(pid)
    return list(by_id.values()), added


def _merge_matrix(design: dict[str, Any], key: str, rows: list[dict[str, Any]]) -> list[str]:
    existing = {str(r["skill_id"]): r for r in design.get(key) or [] if r.get("skill_id")}
    new_ids: list[str] = []
    for row in rows:
        sid = str(row["skill_id"])
        if sid not in existing:
            new_ids.append(sid)
        existing[sid] = row
    design[key] = list(existing.values())
    return new_ids


def _patch_taxonomy_ssot() -> None:
    tax = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    track2 = next(t for t in tax["tracks"] if t["track_id"] == "TRACK_DATA_TECH_CLOUD_ML")
    inc = list(track2.get("pillars_include_confirmed") or [])
    for pid in (PILLAR_GTM, PILLAR_TECH):
        if pid not in inc:
            inc.append(pid)
    track2["pillars_include_confirmed"] = inc
    _wg.write_text(TAXONOMY_PATH, json.dumps(tax, indent=2) + "\n", encoding="utf-8")


def _counts(ledger: dict[str, Any]) -> dict[str, int]:
    return {
        "pillar_count": len(ledger.get("pillars") or []),
        "skill_row_count": len(ledger.get("skill_rows") or []),
        "graph_node_count": len(ledger.get("graph_nodes") or []),
        "graph_edge_count": len(ledger.get("graph_edges") or []),
    }


def _node_evidence_manifest(matrix_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for row in matrix_rows:
        out.append(
            {
                "skill_id": row["skill_id"],
                "pillar": row.get("target_pillar"),
                "confidence": row.get("evidence_confidence", "UNKNOWN"),
                "support_status": row.get("support_status"),
                "linked_fact_id": row.get("linked_fact_id"),
                "source_resume_file": row.get("source_resume_file"),
                "source_evidence": row.get("source_evidence"),
                "inference_only": row.get("support_status") == "INTERNAL_ONLY",
            }
        )
    return out


def _render_closeout_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Skills graph Phase 2 GTM / pre-sales expansion closeout",
        "",
        f"**Status:** {payload['status']}",
        f"**Generated:** {payload['generated_at_utc']}",
        f"**Career track:** TRACK_DATA_TECH_CLOUD_ML (Phase 2)",
        "",
        "## New pillars",
        "",
    ]
    for p in payload.get("new_pillars") or []:
        lines.append(f"- `{p}`")
    lines.extend(["", "## New skill nodes", ""])
    for row in payload.get("new_skills") or []:
        lines.append(
            f"- `{row['skill_id']}` — confidence **{row.get('confidence')}** — "
            f"{row.get('source_resume_file') or 'INFERENCE_ONLY'}"
        )
    lines.extend(["", "## Explicit non-claims", ""])
    for claim in payload.get("explicit_non_claims") or []:
        lines.append(f"- {claim}")
    lines.extend(["", "## Evidence gaps", ""])
    for gap in payload.get("evidence_gaps") or []:
        lines.append(f"- **{gap['gap_id']}**: {gap['reason']}")
    return "\n".join(lines) + "\n"


def main() -> int:
    before_ledger = json.loads(OUT_LEDGER.read_text(encoding="utf-8"))
    before = _counts(before_ledger)

    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    taxonomy, pillars_added = _upsert_pillars(design.get("capability_taxonomy") or [])
    design["capability_taxonomy"] = taxonomy
    gtm_new = _merge_matrix(design, "phase2_gtm_presales_matrix", PHASE2_GTM_MATRIX)
    tech_new = _merge_matrix(design, "phase2_technical_presales_matrix", PHASE2_TECH_MATRIX)
    stats = design.setdefault("stats", {})
    stats["phase2_gtm_presales_matrix_rows"] = len(design.get("phase2_gtm_presales_matrix") or [])
    stats["phase2_technical_presales_matrix_rows"] = len(
        design.get("phase2_technical_presales_matrix") or []
    )
    stats["pillar_count"] = len(taxonomy)
    _wg.write_text(DESIGN_PATH, json.dumps(design, indent=2) + "\n", encoding="utf-8")
    _patch_taxonomy_ssot()

    payload = build_ledger_payload(design)
    _wg.write_text(OUT_LEDGER, json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    rematerialize_career_tracks(write=True)

    after_ledger = json.loads(OUT_LEDGER.read_text(encoding="utf-8"))
    after = _counts(after_ledger)

    all_rows = PHASE2_GTM_MATRIX + PHASE2_TECH_MATRIX
    closeout = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS",
        "scope": "skills_graph_phase2_gtm_presales",
        "career_track": "TRACK_DATA_TECH_CLOUD_ML",
        "before_after_counts": {"before": before, "after": after},
        "new_pillars": pillars_added,
        "new_skills": [
            {
                "skill_id": sid,
                "pillar": next((r["target_pillar"] for r in all_rows if r["skill_id"] == sid), None),
                "confidence": next(
                    (r.get("evidence_confidence") for r in all_rows if r["skill_id"] == sid),
                    "UNKNOWN",
                ),
                "linked_fact_id": next(
                    (r.get("linked_fact_id") for r in all_rows if r["skill_id"] == sid),
                    None,
                ),
                "source_resume_file": next(
                    (r.get("source_resume_file") for r in all_rows if r["skill_id"] == sid),
                    None,
                ),
                "support_status": next(
                    (r.get("support_status") for r in all_rows if r["skill_id"] == sid),
                    None,
                ),
            }
            for sid in gtm_new + tech_new
        ],
        "node_evidence_manifest": _node_evidence_manifest(all_rows),
        "explicit_non_claims": EXPLICIT_NON_CLAIMS,
        "evidence_gaps": EVIDENCE_GAPS,
        "related_high_evidence_anchors_not_airline": [
            {
                "skill_id": "skill_p2_tech_ibm_cloud_portfolio_anchor",
                "claim": "$30M cloud and AI transformation portfolio (IBM Partner, base resume)",
                "confidence": "HIGH",
            },
            {
                "skill_id": "skill_sales_modernization_deals_15m",
                "claim": ">$15M modernization deals (Strategic Account Executive archive)",
                "confidence": "MEDIUM",
            },
            {
                "skill_id": "skill_p2_tech_aws_modernization_patterns",
                "claim": "AWS Migration and Modernization partner training",
                "confidence": "HIGH",
            },
        ],
        "scope_control": {
            "phase1_actuarial_track_touched": False,
            "phase3_genai_track_touched": False,
            "section_prompts_touched": False,
            "agentic_core_touched": False,
        },
    }
    _wg.write_text(CLOSEOUT_JSON, json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
    _wg.write_text(CLOSEOUT_MD, _render_closeout_md(closeout), encoding="utf-8")

    print(
        f"PHASE2_GTM_PRE_SALES pillars_added={len(pillars_added)} "
        f"skills_new={len(gtm_new) + len(tech_new)} "
        f"skill_rows {before['skill_row_count']} -> {after['skill_row_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
