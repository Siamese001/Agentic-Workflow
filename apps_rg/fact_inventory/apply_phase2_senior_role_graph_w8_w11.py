"""W8–W11 senior-role graph: evidence-gated pillars, skills, and phase bridge edges.

Grounds nodes in base resume (exp_insurtech_001), Phase I archive snippets, and candidate facts.
Does not activate W12 partner/hyperscaler pillars, W13 fixtures, runtime, or track-weight code.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.augmented_skills_graph import assert_skills_not_broad_ledger_authority
from apps_rg.fact_inventory.materialize_arsenal_from_design import build_ledger_payload
from apps_rg.fact_inventory.materialize_career_tracks_p1 import run_materialize as rematerialize_career_tracks
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
    validate_arsenal_ledger_shape,
)

ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json"
OUT_LEDGER = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
TAXONOMY_PATH = ROOT / "docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json"
CLOSEOUT_JSON = ROOT / "docs/reports/apps_rg/phase2_w8_w11_senior_role_graph_closeout.json"
CLOSEOUT_MD = ROOT / "docs/reports/apps_rg/phase2_w8_w11_senior_role_graph_closeout.md"

P_INS_CARRIER = "pillar_insurance_carrier_transformation"
P_UW_CLAIMS = "pillar_underwriting_claims_ops_ai"
P_INS_IT = "pillar_insurer_it_strategy_ai_enablement"
P_ENT_GOV = "pillar_enterprise_portfolio_governance"
P_BANK_AI = "pillar_banking_platform_responsible_ai"
P_INTEROP = "pillar_interoperability_integration_ecosystem"
P_BROKERAGE = "pillar_insurance_brokerage_distribution"

EXPLICIT_NON_CLAIMS: list[str] = [
    "No underwriting, claims, policy administration, or billing ownership claims.",
    "No brokerage distribution ownership or broker-channel product claims.",
    "No transaction banking, payments, liquidity, trade, investor/issuer services, or fraud operations.",
    "No Fed/regulator-facing work, marketplace co-sell, or hyperscaler exclusivity.",
    "No airline ~$100M engagement or technical estimation/sizing without evidence.",
    "JD/briefing and taxonomy keywords are targeting-only, not proof.",
    "broad_skills_ledger remains non-authority.",
]

NEW_PILLARS: list[dict[str, Any]] = [
    {
        "pillar_id": P_INS_CARRIER,
        "name": "Insurance Carrier Technology Transformation",
        "description": (
            "Legacy insurance technology modernization and regulated insurer cloud adoption — "
            "middle-market carrier fluency from InsurTech employment; not carrier underwriting/claims ownership."
        ),
        "subskills": ["legacy_cloud_modernization", "regulated_insurer_controls", "carrier_technology_fluency"],
        "evidence_sources": ["apps_rg/resume/base/amit_ayer_base_resume_v1.json"],
        "archive_snippets": [
            "modernizing legacy insurance technology stacks for middle-market insurers",
            "AWS-based architectures, reducing total cost of ownership",
            "SOC 2-aligned cloud control frameworks for regulated insurers",
        ],
        "linked_fact_ids": ["exp_insurtech_001", "bul_insurtech_001", "bul_insurtech_002"],
        "user_confirmed_pending_source": [],
        "allowed_phrases": [
            "middle-market insurers",
            "legacy insurance technology",
            "cloud modernization",
            "regulated insurers",
            "SOC 2",
            "auditability",
        ],
        "forbidden_phrases_without_stronger_support": [
            "underwriting operations owner",
            "claims operations owner",
            "policy administration owner",
            "billing owner",
            "brokerage distribution",
        ],
        "role_family_weights": {
            "INSURANCE_CARRIER_TRANSFORMATION": 1.0,
            "INSURER_IT_AI_ENABLEMENT": 0.85,
            "REGULATED_AI_GOVERNANCE": 0.7,
        },
        "section_fit": {
            "headline": False,
            "executive_summary": True,
            "competencies": True,
            "unify_bullets": True,
            "unify_narrative": False,
            "ibm_bullets": True,
            "ibm_narrative": True,
            "early_career": False,
        },
    },
    {
        "pillar_id": P_UW_CLAIMS,
        "name": "Insurance Systems Resilience (Internal Traversal)",
        "description": (
            "Internal-only traversal pillar for legacy insurance platform resilience signals — "
            "does not assert underwriting/claims/policy-admin AI product ownership."
        ),
        "subskills": ["platform_resilience_internal"],
        "evidence_sources": ["apps_rg/resume/base/amit_ayer_base_resume_v1.json"],
        "archive_snippets": [],
        "linked_fact_ids": ["bul_insurtech_003"],
        "user_confirmed_pending_source": ["underwriting_claims_ops_ai_product_ownership"],
        "allowed_phrases": ["high availability", "platform resilience", "real-time ingestion"],
        "forbidden_phrases_without_stronger_support": [
            "underwriting AI",
            "claims AI",
            "policy administration",
            "claims operations",
            "underwriting operations",
        ],
        "role_family_weights": {"INSURANCE_CARRIER_TRANSFORMATION": 0.5},
        "section_fit": {
            "headline": False,
            "executive_summary": False,
            "competencies": False,
            "unify_bullets": False,
            "unify_narrative": False,
            "ibm_bullets": False,
            "ibm_narrative": False,
            "early_career": False,
        },
    },
    {
        "pillar_id": P_INS_IT,
        "name": "Insurer IT Strategy & AI Enablement",
        "description": (
            "Insurer IT strategy, cloud data platforms, and AI enablement from InsurTech CTO "
            "and engineering platform facts — not brokerage distribution."
        ),
        "subskills": ["it_strategy", "cloud_enablement", "ai_enablement"],
        "evidence_sources": [
            "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
            "Industry Solutions - Amit Ayer.txt",
        ],
        "archive_snippets": [
            "Founded and led a cloud-native engineering firm",
            "cloud-native architectures",
        ],
        "linked_fact_ids": ["exp_insurtech_001", "fact_engineering_platform_001", "fact_engineering_platform_003"],
        "allowed_phrases": ["cloud-native", "IT strategy", "data platform", "AI enablement"],
        "forbidden_phrases_without_stronger_support": ["brokerage", "distribution technology owner"],
        "role_family_weights": {
            "INSURER_IT_AI_ENABLEMENT": 1.0,
            "ENGINEERING_PLATFORM": 0.9,
            "INSURANCE_CARRIER_TRANSFORMATION": 0.8,
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
        "pillar_id": P_ENT_GOV,
        "name": "Enterprise Portfolio & Data Governance",
        "description": (
            "Enterprise portfolio governance, data catalogs, and executive alignment — "
            "EY/regulatory program and governance facts."
        ),
        "subskills": ["portfolio_governance", "data_catalogs", "executive_alignment"],
        "evidence_sources": [
            "AI and Data Governance - Amit Ayer.txt",
            "Chief Technology Officer - Amit Ayer.txt",
        ],
        "linked_fact_ids": ["fact_governance_004", "fact_engineering_platform_004"],
        "allowed_phrases": ["data catalogs", "governance", "executive alignment", "portfolio"],
        "forbidden_phrases_without_stronger_support": [],
        "role_family_weights": {
            "INSURER_IT_AI_ENABLEMENT": 0.85,
            "REGULATED_AI_GOVERNANCE": 0.9,
            "EXECUTIVE_LEADERSHIP": 0.8,
        },
        "section_fit": {
            "headline": False,
            "executive_summary": True,
            "competencies": True,
            "unify_bullets": False,
            "unify_narrative": True,
            "ibm_bullets": False,
            "ibm_narrative": True,
            "early_career": False,
        },
    },
    {
        "pillar_id": P_BANK_AI,
        "name": "Banking Platform & Responsible AI (Regulated)",
        "description": (
            "Regulated financial-institutions platform fluency, Basel/CCAR lineage, and responsible AI "
            "governance — not transaction banking product lines."
        ),
        "subskills": ["basel_ccar_lineage", "responsible_ai_governance", "financial_institutions_fluency"],
        "evidence_sources": [
            "AI and Data Governance - Amit Ayer.txt",
            "Amit Ayer Resume - Strategic Account Executive.txt",
            "Sales - Amit Ayer.txt",
        ],
        "linked_fact_ids": ["fact_governance_001", "fact_governance_003"],
        "allowed_phrases": [
            "Basel",
            "CCAR",
            "data lineage",
            "regulatory reporting",
            "financial institutions",
            "responsible AI",
        ],
        "forbidden_phrases_without_stronger_support": [
            "payments",
            "liquidity",
            "trade operations",
            "transaction banking owner",
            "fraud operations",
            "investor services",
        ],
        "role_family_weights": {
            "BANKING_PLATFORM_AI": 1.0,
            "REGULATED_AI_GOVERNANCE": 0.95,
            "AI_GOVERNANCE_RISK": 0.85,
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
        "pillar_id": P_INTEROP,
        "name": "Interoperability & Integration Platform",
        "description": (
            "Microservices and integration-platform patterns for regulated enterprises — "
            "not insurance brokerage distribution."
        ),
        "subskills": ["microservices_integration", "cloud_native_integration"],
        "evidence_sources": ["Industry Solutions - Amit Ayer.txt", "Revenue Operations - Amit Ayer.txt"],
        "archive_snippets": [
            "microservices architecture",
            "cloud-native microservices",
        ],
        "linked_fact_ids": ["fact_engineering_platform_002"],
        "allowed_phrases": ["microservices", "cloud-native", "integration"],
        "forbidden_phrases_without_stronger_support": ["brokerage", "insurance distribution owner"],
        "role_family_weights": {
            "INSURANCE_BROKERAGE_IT_INNOVATION": 0.4,
            "INSURER_IT_AI_ENABLEMENT": 0.85,
            "ENGINEERING_PLATFORM": 0.9,
        },
        "section_fit": {
            "headline": False,
            "executive_summary": True,
            "competencies": True,
            "unify_bullets": True,
            "unify_narrative": False,
            "ibm_bullets": True,
            "ibm_narrative": False,
            "early_career": False,
        },
    },
]

SENIOR_ROLE_W811_MATRIX: list[dict[str, Any]] = [
    {
        "skill": "insurtech_legacy_cloud_modernization",
        "skill_id": "skill_sr_insurtech_legacy_cloud_modernization",
        "target_pillar": P_INS_CARRIER,
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Led end-to-end modernization of monolithic policy administration systems into AWS-based "
            "architectures for middle-market insurers (InsurTech CTO)."
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["middle-market insurers", "AWS", "legacy modernization", "TCO"],
        "role_relevance": ["INSURANCE_CARRIER_TRANSFORMATION", "INSURER_IT_AI_ENABLEMENT"],
        "where_to_use": ["executive_summary", "competencies", "ibm_bullets"],
        "risk_notes": "Policy-admin systems mentioned as legacy modernization target only — not ownership of policy-admin product.",
        "linked_fact_id": "bul_insurtech_001",
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "insurtech_regulated_insurer_controls",
        "skill_id": "skill_sr_insurtech_regulated_insurer_controls",
        "target_pillar": P_INS_CARRIER,
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Designed SOC 2-aligned cloud control frameworks enabling regulated insurers to adopt "
            "modern analytics and ML with auditability."
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["SOC 2", "regulated insurers", "auditability", "ML capabilities"],
        "role_relevance": ["INSURANCE_CARRIER_TRANSFORMATION", "REGULATED_AI_GOVERNANCE"],
        "where_to_use": ["competencies", "ibm_bullets"],
        "risk_notes": "Carrier/regulated-insurer fluency only.",
        "linked_fact_id": "bul_insurtech_002",
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "insurance_systems_resilience_internal",
        "skill_id": "skill_sr_insurance_systems_resilience_internal",
        "target_pillar": P_UW_CLAIMS,
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Re-architected systems for high availability (99.99% uptime) and real-time ingestion — "
            "internal traversal only; no underwriting/claims ops AI ownership."
        ),
        "support_status": "INTERNAL_ONLY",
        "allowed_phrases": [],
        "role_relevance": ["INSURANCE_CARRIER_TRANSFORMATION"],
        "where_to_use": [],
        "risk_notes": "Source bullet references underwriting systems — forbidden for external claims; INTERNAL_ONLY.",
        "linked_fact_id": "bul_insurtech_003",
        "evidence_confidence": "LOW",
    },
    {
        "skill": "insurtech_cto_it_enablement",
        "skill_id": "skill_sr_insurtech_cto_it_enablement",
        "target_pillar": P_INS_IT,
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Founded and led a cloud-native engineering firm modernizing legacy insurance technology "
            "stacks for middle-market insurers."
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["cloud-native engineering", "insurance technology", "middle-market insurers"],
        "role_relevance": ["INSURER_IT_AI_ENABLEMENT", "INSURANCE_CARRIER_TRANSFORMATION"],
        "where_to_use": ["executive_summary", "competencies", "ibm_narrative"],
        "risk_notes": "InsurTech employment spine — exp_insurtech_001.",
        "linked_fact_id": "exp_insurtech_001",
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "cloud_data_platform_engineering",
        "skill_id": "skill_sr_cloud_data_platform_engineering",
        "target_pillar": P_INS_IT,
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "source_resume_file": "Industry Solutions - Amit Ayer.txt",
        "source_evidence": "Cloud-native architectures and platform engineering for regulated financial services clients.",
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["cloud-native", "platform engineering"],
        "role_relevance": ["INSURER_IT_AI_ENABLEMENT", "ENGINEERING_PLATFORM"],
        "where_to_use": ["competencies", "unify_bullets"],
        "risk_notes": "Linked fact_engineering_platform_001.",
        "linked_fact_id": "fact_engineering_platform_001",
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "enterprise_portfolio_data_governance",
        "skill_id": "skill_sr_enterprise_portfolio_data_governance",
        "target_pillar": P_ENT_GOV,
        "career_epoch": "epoch_enterprise_risk_governance",
        "source_resume_file": "AI and Data Governance - Amit Ayer.txt",
        "source_evidence": (
            "Defined documentation standards and centralized data catalogs that expedited audits."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["data catalogs", "documentation standards", "audits"],
        "role_relevance": ["REGULATED_AI_GOVERNANCE", "INSURER_IT_AI_ENABLEMENT"],
        "where_to_use": ["executive_summary", "competencies"],
        "risk_notes": "fact_governance_004 MEDIUM — DRAFT until human confirm.",
        "linked_fact_id": "fact_governance_004",
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "basel_ccar_lineage_regulatory",
        "skill_id": "skill_sr_basel_ccar_lineage_regulatory",
        "target_pillar": P_BANK_AI,
        "career_epoch": "epoch_enterprise_risk_governance",
        "source_resume_file": "AI and Data Governance - Amit Ayer.txt",
        "source_evidence": (
            "Implemented Basel III / CCAR data lineage, cataloging, and automated validation frameworks."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["Basel", "CCAR", "data lineage", "regulatory reporting"],
        "role_relevance": ["REGULATED_AI_GOVERNANCE", "BANKING_PLATFORM_AI"],
        "where_to_use": ["executive_summary", "competencies", "unify_bullets"],
        "risk_notes": "fact_governance_003 HIGH candidate — human_confirm per ledger policy.",
        "linked_fact_id": "fact_governance_003",
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "banking_ai_governance_controls",
        "skill_id": "skill_sr_banking_ai_governance_controls",
        "target_pillar": P_BANK_AI,
        "career_epoch": "epoch_enterprise_risk_governance",
        "source_resume_file": "AI and Data Governance - Amit Ayer.txt",
        "source_evidence": (
            "Enterprise AI rollout for a major banking client with data usage controls and compliance checkpoints."
        ),
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["banking client", "compliance checkpoints", "data usage controls"],
        "role_relevance": ["BANKING_PLATFORM_AI", "AI_GOVERNANCE_RISK"],
        "where_to_use": ["executive_summary"],
        "risk_notes": "fact_governance_001 MEDIUM — not transaction-banking product scope.",
        "linked_fact_id": "fact_governance_001",
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "regulated_financial_institutions_fluency",
        "skill_id": "skill_sr_regulated_financial_institutions_fluency",
        "target_pillar": P_BANK_AI,
        "career_epoch": "epoch_enterprise_risk_governance",
        "source_resume_file": "Amit Ayer Resume - Strategic Account Executive.txt",
        "source_evidence": (
            "Regulatory IT transformations for top banks and insurers with Basel and CCAR compliance emphasis."
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["financial institutions", "Basel", "CCAR", "regulatory IT"],
        "role_relevance": ["BANKING_PLATFORM_AI", "REGULATED_AI_GOVERNANCE"],
        "where_to_use": ["competencies", "ibm_narrative"],
        "risk_notes": "Broad regulated-enterprise fluency — not payments/liquidity/trade claims.",
        "linked_fact_id": None,
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "microservices_integration_platform",
        "skill_id": "skill_sr_microservices_integration_platform",
        "target_pillar": P_INTEROP,
        "career_epoch": "epoch_cloud_data_platform_engineering",
        "source_resume_file": "Industry Solutions - Amit Ayer.txt",
        "source_evidence": "Migrated monolithic systems to cloud-native microservices for high availability and integration.",
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["microservices", "cloud-native", "integration"],
        "role_relevance": ["INSURER_IT_AI_ENABLEMENT", "ENGINEERING_PLATFORM"],
        "where_to_use": ["competencies", "unify_bullets"],
        "risk_notes": "W11 interoperability via platform integration evidence — not brokerage distribution.",
        "linked_fact_id": "fact_engineering_platform_002",
        "evidence_confidence": "MEDIUM",
    },
]

SENIOR_ROLE_BRIDGE_EDGES: list[dict[str, Any]] = [
    {
        "bridge_edge_family": "actuarial_to_insurer_ai_strategy",
        "source_pillar_id": "pillar_actuarial_foundation",
        "target_pillar_id": P_INS_IT,
        "direction": "forward",
        "evidence_fact_ids": ["exp_insurtech_001"],
        "evidence_sources": ["career_arc_actuarial_to_insurtech_cto"],
        "rationale": "Actuarial foundation epoch precedes InsurTech CTO cloud/IT enablement (employment spine).",
    },
    {
        "bridge_edge_family": "actuarial_to_agentic_transformation",
        "source_pillar_id": "pillar_actuarial_foundation",
        "target_pillar_id": P_INS_CARRIER,
        "direction": "forward",
        "evidence_fact_ids": ["exp_insurtech_001"],
        "evidence_sources": ["insurtech_carrier_modernization_to_agentic_epoch"],
        "rationale": "Actuarial/insurance domain fluency bridges to carrier transformation pillar for agentic targeting.",
    },
    {
        "bridge_edge_family": "actuarial_to_agentic_transformation",
        "source_pillar_id": "pillar_actuarial_foundation",
        "target_pillar_id": "pillar_agentic_ai_platforms",
        "direction": "forward",
        "evidence_fact_ids": ["fact_engineering_platform_001"],
        "evidence_sources": ["regulated_enterprise_agentic_platform"],
        "rationale": "Forward bridge from actuarial/regulatory domain to agentic runtime pillar (traversal only).",
    },
    {
        "bridge_edge_family": "insurance_to_underwriting_claims_ops",
        "source_pillar_id": P_INS_CARRIER,
        "target_pillar_id": P_UW_CLAIMS,
        "direction": "forward",
        "evidence_fact_ids": ["bul_insurtech_003"],
        "evidence_sources": ["internal_only_resilience_signal"],
        "rationale": "Directional internal bridge to resilience pillar — external claims blocked.",
        "external_claim_policy": "internal_traversal_only",
    },
    {
        "bridge_edge_family": "insurtech_to_insurer_it_strategy",
        "source_pillar_id": P_INS_CARRIER,
        "target_pillar_id": P_INS_IT,
        "direction": "forward",
        "evidence_fact_ids": ["exp_insurtech_001"],
        "evidence_sources": ["same_employment_insurtech_spine"],
        "rationale": "InsurTech employment links carrier transformation to IT/AI enablement.",
    },
    {
        "bridge_edge_family": "basel_ccar_to_ai_auditability",
        "source_pillar_id": "pillar_regulatory_governance",
        "target_pillar_id": P_BANK_AI,
        "direction": "forward",
        "evidence_fact_ids": ["fact_governance_003"],
        "evidence_sources": ["AI and Data Governance - Amit Ayer.txt"],
        "rationale": "Basel/CCAR lineage evidence bridges regulatory governance to banking responsible-AI pillar.",
    },
    {
        "bridge_edge_family": "regulatory_governance_to_responsible_ai",
        "source_pillar_id": "pillar_regulatory_governance",
        "target_pillar_id": P_BANK_AI,
        "direction": "forward",
        "evidence_fact_ids": ["fact_governance_001", "fact_governance_003"],
        "rationale": "Regulatory governance pillar forward to banking platform responsible AI.",
    },
    {
        "bridge_edge_family": "data_lineage_to_ai_traceability",
        "source_pillar_id": "pillar_regulatory_governance",
        "target_pillar_id": "pillar_agentic_ai_platforms",
        "direction": "forward",
        "evidence_fact_ids": ["fact_governance_003"],
        "evidence_sources": ["skill_contradiction_and_lineage_handling"],
        "rationale": "Data lineage / regulatory reporting bridges to agentic auditability and traceability skills.",
    },
    {
        "bridge_edge_family": "domain_expertise_to_section_eligibility",
        "source_pillar_id": P_INS_CARRIER,
        "target_pillar_id": "section_executive_summary",
        "direction": "forward",
        "edge_type": "pillar_section_eligibility",
        "evidence_fact_ids": ["exp_insurtech_001"],
        "rationale": "Carrier transformation pillar eligible for executive_summary when facts active.",
    },
    {
        "bridge_edge_family": "domain_expertise_to_section_eligibility",
        "source_pillar_id": P_BANK_AI,
        "target_pillar_id": "section_competencies",
        "direction": "forward",
        "edge_type": "pillar_section_eligibility",
        "evidence_fact_ids": ["fact_governance_003"],
        "rationale": "Banking/regulatory pillar eligible for competencies section projection.",
    },
]

DEFERRED_PILLARS: list[dict[str, str]] = [
    {
        "pillar_id": P_BROKERAGE,
        "reason": "No brokerage/distribution/interoperability-for-brokers evidence in resume archive or candidate ledger.",
        "wave": "W11-deferred",
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


def _merge_bridges(design: dict[str, Any], bridges: list[dict[str, Any]]) -> list[str]:
    existing = {str(e.get("edge_id") or ""): e for e in design.get("senior_role_bridge_edges") or []}
    new_families: list[str] = []
    for spec in bridges:
        src = spec["source_pillar_id"]
        tgt = spec["target_pillar_id"]
        fam = spec["bridge_edge_family"]
        eid = f"edge_bridge_{fam}_{src}_to_{tgt}"
        spec = {**spec, "edge_id": eid}
        if eid not in existing:
            new_families.append(fam)
        existing[eid] = spec
    design["senior_role_bridge_edges"] = list(existing.values())
    return new_families


def _patch_career_taxonomy(pillar_ids: list[str]) -> None:
    tax = json.loads(TAXONOMY_PATH.read_text(encoding="utf-8"))
    track2 = next(t for t in tax["tracks"] if t["track_id"] == "TRACK_DATA_TECH_CLOUD_ML")
    inc = list(track2.get("pillars_include_confirmed") or [])
    for pid in pillar_ids:
        if pid in (
            P_INS_CARRIER,
            P_UW_CLAIMS,
            P_INS_IT,
            P_ENT_GOV,
            P_INTEROP,
        ) and pid not in inc:
            inc.append(pid)
    track2["pillars_include_confirmed"] = inc
    TAXONOMY_PATH.write_text(json.dumps(tax, indent=2) + "\n", encoding="utf-8")


def _counts(ledger: dict[str, Any]) -> dict[str, int]:
    rows = ledger.get("skill_rows") or []
    active = sum(1 for r in rows if str(r.get("activation_status")) == "ACTIVE")
    active_conf = sum(1 for r in rows if str(r.get("activation_status")) == "ACTIVE_CONFIRMED")
    draft = sum(1 for r in rows if str(r.get("activation_status")) == "DRAFT")
    internal = sum(
        1 for r in rows if str(r.get("support_level")) == "INTERNAL_ONLY" or r.get("skill_id", "").startswith("skill_sr_")
        and str(r.get("support_level")) == "INTERNAL_ONLY"
    )
    bridge_edges = [
        e
        for e in ledger.get("graph_edges") or []
        if str(e.get("edge_type")) in ("pillar_phase_bridge", "pillar_section_eligibility")
    ]
    return {
        "pillar_count": len(ledger.get("pillars") or []),
        "skill_row_count": len(rows),
        "graph_node_count": len(ledger.get("graph_nodes") or []),
        "graph_edge_count": len(ledger.get("graph_edges") or []),
        "bridge_edge_count": len(bridge_edges),
        "activation_active": active,
        "activation_active_confirmed": active_conf,
        "activation_draft": draft,
        "internal_only_skill_rows": sum(1 for r in rows if str(r.get("support_level")) == "INTERNAL_ONLY"),
    }


def main() -> int:
    before_ledger = json.loads(OUT_LEDGER.read_text(encoding="utf-8"))
    assert_skills_not_broad_ledger_authority(before_ledger.get("metadata"))
    before = _counts(before_ledger)

    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    taxonomy, pillars_added = _upsert_pillars(design.get("capability_taxonomy") or [])
    design["capability_taxonomy"] = taxonomy
    skills_new = _merge_matrix(design, "senior_role_w8_w11_matrix", SENIOR_ROLE_W811_MATRIX)
    bridges_new = _merge_bridges(design, SENIOR_ROLE_BRIDGE_EDGES)
    design.setdefault("stats", {})["senior_role_w8_w11_matrix_rows"] = len(
        design.get("senior_role_w8_w11_matrix") or []
    )
    design["stats"]["senior_role_bridge_edges"] = len(design.get("senior_role_bridge_edges") or [])
    DESIGN_PATH.write_text(json.dumps(design, indent=2) + "\n", encoding="utf-8")
    _patch_career_taxonomy(pillars_added)

    payload = build_ledger_payload(design)
    OUT_LEDGER.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    rematerialize_career_tracks(write=True)

    ledger = load_master_skills_arsenal_ledger(path=OUT_LEDGER)
    validate_arsenal_ledger_shape(ledger)
    after = _counts(ledger)

    sr_rows = [r for r in ledger.get("skill_rows") or [] if str(r.get("skill_id", "")).startswith("skill_sr_")]
    evidence_backed = sum(
        1
        for r in sr_rows
        if (r.get("fact_id_links") or r.get("source_snippets"))
        and str(r.get("support_level")) != "INTERNAL_ONLY"
    )

    closeout = {
        "schema": "phase2_w8_w11_senior_role_graph_closeout_v1",
        "status": "PASS",
        "plan_id": "phase2-gtm-presales-remaining-f7a2c9",
        "wave": "W8-W11-graph",
        "audit_id": "senior_role_graph_gap_analysis_20260520",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "proof_classification": "graph_materialization_receipt_only",
        "before_after_counts": {"before": before, "after": after},
        "pillars_added": pillars_added,
        "pillars_deferred": DEFERRED_PILLARS,
        "skills_added": skills_new,
        "bridge_edge_families_added": list(dict.fromkeys(bridges_new)),
        "explicit_non_claims": EXPLICIT_NON_CLAIMS,
        "scope_control": {
            "w12_partner_hyperscaler": False,
            "w13_fixtures": False,
            "runtime_proof": False,
            "track_weight_code": False,
            "agentic_core": False,
            "prompts": False,
            "broad_skills_ledger_authority": False,
        },
    }
    CLOSEOUT_JSON.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")
    CLOSEOUT_MD.write_text(
        "\n".join(
            [
                "# W8–W11 senior-role graph closeout",
                "",
                f"**STATUS:** {closeout['status']}",
                f"**PLAN_ID:** `{closeout['plan_id']}`",
                f"**WAVE:** {closeout['wave']}",
                "",
                "## Pillars added",
                "",
                *[f"- `{p}`" for p in pillars_added],
                "",
                "## Pillars deferred",
                "",
                *[f"- `{d['pillar_id']}` — {d['reason']}" for d in DEFERRED_PILLARS],
                "",
                "## Skills added",
                "",
                *[f"- `{s}`" for s in skills_new],
                "",
                f"## Counts: pillars {before['pillar_count']}→{after['pillar_count']}, "
                f"skills {before['skill_row_count']}→{after['skill_row_count']}, "
                f"edges {before['graph_edge_count']}→{after['graph_edge_count']}, "
                f"bridge_edges {after['bridge_edge_count']}",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"W8_W11 pillars_added={len(pillars_added)} skills_new={len(skills_new)} "
        f"bridges={after['bridge_edge_count']} "
        f"skill_rows {before['skill_row_count']}->{after['skill_row_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
