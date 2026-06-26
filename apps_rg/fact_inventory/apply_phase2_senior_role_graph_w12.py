"""W12 partner/hyperscaler graph — evidence-gated pillars, skills, activation criteria, bridges.

Activates only source-backed partner/hyperscaler surfaces. Preserves DO_NOT_PROMOTE on pending-source skills.
Does not run W13 fixtures, runtime proof, track-weight code, or W12 marketplace/Snowflake claims without evidence.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agentic_core.L2_execution.utils import write_gateway as _wg

from apps_rg.fact_inventory.augmented_skills_graph import assert_skills_not_broad_ledger_authority
from apps_rg.fact_inventory.materialize_arsenal_from_design import build_ledger_payload
from apps_rg.fact_inventory.materialize_career_tracks_p1 import run_materialize as rematerialize_career_tracks
from apps_rg.fact_inventory.master_skills_arsenal_ledger import (
    load_master_skills_arsenal_ledger,
    skill_row_eligible_for_external_claim,
    validate_arsenal_ledger_shape,
)

ROOT = Path(__file__).resolve().parents[2]
DESIGN_PATH = ROOT / "docs/reports/apps_rg/master_skills_arsenal_ledger_design.json"
OUT_LEDGER = ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json"
TAXONOMY_PATH = ROOT / "docs/reports/apps_rg/career_track_taxonomy_operator_confirmed.json"
RECEIPT_JSON = ROOT / "docs/reports/apps_rg/phase2_w12_partner_hyperscaler_graph_receipt.json"
RECEIPT_MD = ROOT / "docs/reports/apps_rg/phase2_w12_partner_hyperscaler_graph_receipt.md"

P_HYPERSCALER = "pillar_hyperscaler_marketplace_partner_gtm"
P_APPLIED_AI = "pillar_applied_ai_partner_architecture"
P_PARTNER_GTM = "pillar_partner_gtm_alliances"
P_COSELL = "pillar_cosell_partner_engineering"
P_PRESALES = "pillar_presales_solutioning"
P_AGENTIC = "pillar_agentic_ai_platforms"

EXPLICIT_NON_CLAIMS: list[str] = [
    "No cloud marketplace listing / marketplace co-sell claim (no marketplace string in approved sources).",
    "No Snowflake partner or platform claim (ABSENT_EVIDENCE in archive).",
    "No GCP or Azure partner exclusivity or sole-hyperscaler mandate.",
    "No partner engineering or product feedback loops in external claims until operator source.",
    "No GSI enablement claim (ABSENT_EVIDENCE).",
    "No indirect revenue ownership beyond archive-scoped partner-derived / alliance metrics.",
    "Do not conflate IBM/AWS alliance co-sell with hyperscaler marketplace GTM.",
    "broad_skills_ledger remains non-authority.",
]

# Pre-edit classification manifest (written to design + receipt).
W12_ACTIVATION_CRITERIA: list[dict[str, Any]] = [
    {
        "item_id": "skill_partner_aws_ecosystem",
        "topic": "AWS partner ecosystem",
        "evidence_class": "DIRECT_EVIDENCE",
        "activation_decision": "DRAFT",
        "notes": "Archive AWS Partner training; existing partner_gtm_matrix row; external via gate not AUTO MEDIUM.",
    },
    {
        "item_id": "skill_partner_cloud_partner_ecosystem",
        "topic": "IBM–AWS alliance",
        "evidence_class": "DIRECT_EVIDENCE",
        "activation_decision": "DRAFT",
        "notes": "Partnerships archive IBM–AWS alliance line.",
    },
    {
        "item_id": "skill_partner_co_selling",
        "topic": "Co-sell with SI/ISV",
        "evidence_class": "DIRECT_EVIDENCE",
        "activation_decision": "DRAFT",
        "notes": "Archive co-selling frameworks; fact_partnerships_gtm_003 MEDIUM — not marketplace co-sell.",
    },
    {
        "item_id": "skill_partner_partner_engineering",
        "topic": "Partner engineering",
        "evidence_class": "ABSENT_EVIDENCE",
        "activation_decision": "DO_NOT_PROMOTE",
        "notes": "USER_CONFIRMED_PENDING_SOURCE; no archive snippet.",
    },
    {
        "item_id": "skill_partner_product_feedback_loops",
        "topic": "Product feedback loops",
        "evidence_class": "ABSENT_EVIDENCE",
        "activation_decision": "DO_NOT_PROMOTE",
        "notes": "USER_CONFIRMED_PENDING_SOURCE; trading-desk feedback loops in archive are not partner-product scope.",
    },
    {
        "item_id": "skill_sr_w12_databricks_lakehouse_fundamentals",
        "topic": "Databricks Lakehouse",
        "evidence_class": "DIRECT_EVIDENCE",
        "activation_decision": "DRAFT",
        "notes": "cert_databricks_lakehouse_001 + fact_engineering_platform_005; accreditation not marketplace.",
    },
    {
        "item_id": "skill_sr_w12_hyperscaler_alliance_co_sell",
        "topic": "Hyperscaler alliance co-sell",
        "evidence_class": "DIRECT_EVIDENCE",
        "activation_decision": "DRAFT",
        "notes": "bul_ibm_005 base resume; co-sell/alliance — forbidden: marketplace listing.",
    },
    {
        "item_id": "skill_sr_w12_joint_ai_solution_development",
        "topic": "Joint AI solution development",
        "evidence_class": "MEDIUM_NEEDS_HUMAN_CONFIRMATION",
        "activation_decision": "DRAFT",
        "notes": "fact_partnerships_gtm_001 partner-led co-development; human confirm before MEDIUM external.",
    },
    {
        "item_id": "skill_sr_w12_industry_reference_architecture",
        "topic": "Reference architectures (partner applied AI)",
        "evidence_class": "DIRECT_EVIDENCE",
        "activation_decision": "DRAFT",
        "notes": "Phase I Industry Solutions + skill_p2_tech_reference_architecture archive lines.",
    },
    {
        "item_id": "snowflake_partner",
        "topic": "Snowflake",
        "evidence_class": "ABSENT_EVIDENCE",
        "activation_decision": "DO_NOT_PROMOTE",
        "notes": "No Snowflake string in Phase I archive grep.",
    },
    {
        "item_id": "cloud_marketplace_listing",
        "topic": "Cloud marketplace GTM",
        "evidence_class": "ABSENT_EVIDENCE",
        "activation_decision": "DO_NOT_PROMOTE",
        "notes": "Pillar id retains taxonomy label; external claims block marketplace/co-sell listing phrases.",
    },
    {
        "item_id": "gsi_enablement",
        "topic": "GSI enablement",
        "evidence_class": "ABSENT_EVIDENCE",
        "activation_decision": "DO_NOT_PROMOTE",
        "notes": "No GSI string in archive.",
    },
]

NEW_PILLARS: list[dict[str, Any]] = [
    {
        "pillar_id": P_HYPERSCALER,
        "name": "Hyperscaler Alliance & Co-Sell GTM",
        "description": (
            "Hyperscaler alliances (IBM/AWS), AWS partner accreditations, alliance co-sell motions, "
            "and partner-derived revenue — not cloud marketplace listing GTM (no marketplace evidence)."
        ),
        "subskills": [
            "aws_partner_accreditation",
            "hyperscaler_alliance_co_sell",
            "partner_co_sell_frameworks",
            "databricks_accreditation",
        ],
        "evidence_sources": [
            "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
            "Partnerships & Alliances - Amit Ayer.docx",
            "Amit Ayer Resume - Strategic Account Executive.txt",
        ],
        "archive_snippets": [
            "AWS Partner: Advanced Migration and Modernization Sales Training",
            "Structured multi-year hyperscaler alliances generating $15M in incremental revenue through co-sell motions",
            "Forged co-selling frameworks with SIs and ISVs",
            "Databricks Lakehouse Fundamentals Accreditation",
        ],
        "linked_fact_ids": [
            "bul_ibm_005",
            "cert_databricks_lakehouse_001",
            "fact_partnerships_gtm_001",
            "fact_partnerships_gtm_003",
        ],
        "user_confirmed_pending_source": [
            "cloud_marketplace_listing",
            "snowflake_partner_platform",
            "gsi_enablement",
            "exclusive_hyperscaler_mandate",
        ],
        "allowed_phrases": [
            "AWS Partner",
            "hyperscaler alliances",
            "co-sell",
            "co-selling",
            "IBM–AWS alliance",
            "partner-derived revenue",
            "Databricks Lakehouse Fundamentals",
        ],
        "forbidden_phrases_without_stronger_support": [
            "cloud marketplace",
            "marketplace co-sell",
            "Snowflake",
            "GCP partner",
            "Azure exclusivity",
            "GSI enablement",
            "partner engineering",
            "product feedback loops",
        ],
        "role_family_weights": {
            "HYPERSCALER_MARKETPLACE_GTM": 1.0,
            "PARTNER_APPLIED_AI_ARCHITECTURE": 0.85,
            "PARTNERSHIPS_GTM": 0.9,
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
        "pillar_id": P_APPLIED_AI,
        "name": "Applied AI Partner Architecture",
        "description": (
            "Partner-applied reference architectures, joint AI solution development, solution accelerators, "
            "and presales solution architecture — distinct from generic quota-carrying partner sales."
        ),
        "subskills": [
            "reference_architectures",
            "joint_ai_solutions",
            "solution_accelerators",
            "solution_architecture",
        ],
        "evidence_sources": [
            "Industry Solutions - Amit Ayer.docx",
            "Field CTO - Amit Ayer.docx",
            "Partnerships & Alliances - Amit Ayer.docx",
        ],
        "linked_fact_ids": ["fact_partnerships_gtm_001", "fact_solutions_001", "fact_solutions_002"],
        "user_confirmed_pending_source": ["partner_engineering_delivery_receipts"],
        "allowed_phrases": [
            "reference architecture",
            "Solution Accelerator",
            "co-developing",
            "partner-led",
            "solution architecture",
            "executive workshops",
        ],
        "forbidden_phrases_without_stronger_support": [
            "partner engineering owner",
            "product feedback loops",
            "partner sales quota owner",
        ],
        "role_family_weights": {
            "PARTNER_APPLIED_AI_ARCHITECTURE": 1.0,
            "AI_SOLUTIONS_ARCHITECTURE": 0.95,
            "PARTNERSHIPS_GTM": 0.85,
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

SENIOR_ROLE_W12_MATRIX: list[dict[str, Any]] = [
    {
        "skill": "databricks_lakehouse_fundamentals",
        "skill_id": "skill_sr_w12_databricks_lakehouse_fundamentals",
        "target_pillar": P_HYPERSCALER,
        "career_epoch": "epoch_partner_gtm_revenue_leadership",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": "Databricks Lakehouse Fundamentals Accreditation (2023); AWS/Databricks lakehouse architecture in platform engineering.",
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["Databricks Lakehouse Fundamentals", "Databricks Lakehouse", "AWS and Databricks"],
        "role_relevance": ["HYPERSCALER_MARKETPLACE_GTM", "ENGINEERING_PLATFORM", "PARTNERSHIPS_GTM"],
        "where_to_use": ["competencies"],
        "risk_notes": "Accreditation + engineering fact; not Snowflake; not marketplace listing.",
        "linked_fact_id": "cert_databricks_lakehouse_001",
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "hyperscaler_alliance_co_sell",
        "skill_id": "skill_sr_w12_hyperscaler_alliance_co_sell",
        "target_pillar": P_HYPERSCALER,
        "career_epoch": "epoch_partner_gtm_revenue_leadership",
        "source_resume_file": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_evidence": (
            "Structured multi-year hyperscaler alliances generating $15M in incremental revenue through "
            "co-sell motions aligned to platform modernization and AI growth."
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": [
            "hyperscaler alliances",
            "co-sell motions",
            "incremental revenue",
            "platform modernization",
        ],
        "role_relevance": ["HYPERSCALER_MARKETPLACE_GTM", "PARTNERSHIPS_GTM"],
        "where_to_use": ["executive_summary", "ibm_bullets", "unify_bullets"],
        "risk_notes": "IBM Partner stint bullet; do not upgrade to marketplace or personal quota carry.",
        "linked_fact_id": "bul_ibm_005",
        "evidence_confidence": "HIGH",
    },
    {
        "skill": "joint_ai_solution_development",
        "skill_id": "skill_sr_w12_joint_ai_solution_development",
        "target_pillar": P_APPLIED_AI,
        "career_epoch": "epoch_partner_gtm_revenue_leadership",
        "source_resume_file": "Partnerships & Alliances - Amit Ayer.docx",
        "source_evidence": "Co-developing advanced analytics frameworks with strategic partners.",
        "support_status": "DERIVED_SUPPORTED",
        "allowed_phrases": ["co-developing", "partner-led", "advanced analytics frameworks"],
        "role_relevance": ["PARTNER_APPLIED_AI_ARCHITECTURE", "PARTNERSHIPS_GTM"],
        "where_to_use": ["unify_bullets", "competencies"],
        "risk_notes": "fact_partnerships_gtm_001 MEDIUM — human confirmation before external MEDIUM claim.",
        "linked_fact_id": "fact_partnerships_gtm_001",
        "evidence_confidence": "MEDIUM",
    },
    {
        "skill": "industry_reference_architecture_partner",
        "skill_id": "skill_sr_w12_industry_reference_architecture",
        "target_pillar": P_APPLIED_AI,
        "career_epoch": "epoch_partner_gtm_revenue_leadership",
        "source_resume_file": "Industry Solutions - Amit Ayer.docx",
        "source_evidence": (
            "Industry Solutions archive: reference architectures and regulated modernization patterns "
            "(complements skill_p2_tech_reference_architecture)."
        ),
        "support_status": "DIRECT_FROM_RESUME_ARCHIVE",
        "allowed_phrases": ["reference architecture", "regulated modernization", "Solution Accelerator"],
        "role_relevance": ["PARTNER_APPLIED_AI_ARCHITECTURE", "AI_SOLUTIONS_ARCHITECTURE"],
        "where_to_use": ["competencies", "ibm_bullets"],
        "risk_notes": "Not partner-engineering-specific; presales/solutioning surface.",
        "linked_fact_id": "fact_solutions_002",
        "evidence_confidence": "HIGH",
    },
]

W12_BRIDGE_EDGES: list[dict[str, Any]] = [
    {
        "bridge_edge_family": "hyperscaler_to_applied_ai_architecture",
        "source_pillar_id": P_HYPERSCALER,
        "target_pillar_id": P_APPLIED_AI,
        "direction": "forward",
        "evidence_fact_ids": ["bul_ibm_005", "fact_partnerships_gtm_001"],
        "rationale": "Alliance co-sell and joint solution development bridge hyperscaler GTM to applied AI architecture.",
    },
    {
        "bridge_edge_family": "marketplace_to_partner_gtm",
        "source_pillar_id": P_HYPERSCALER,
        "target_pillar_id": P_PARTNER_GTM,
        "direction": "forward",
        "evidence_fact_ids": ["fact_partnerships_gtm_003"],
        "rationale": (
            "Co-sell/alliance traversal to partner GTM pillar — not cloud marketplace listing "
            "(marketplace phrase blocked on pillar)."
        ),
        "external_claim_policy": "internal_traversal_only",
    },
    {
        "bridge_edge_family": "partner_engineering_to_reference_architecture",
        "source_pillar_id": P_COSELL,
        "target_pillar_id": P_APPLIED_AI,
        "direction": "forward",
        "evidence_fact_ids": ["fact_solutions_002"],
        "evidence_sources": ["skill_partner_pre_sales", "skill_partner_solution_architecture"],
        "rationale": (
            "Co-sell/presales engineering surface bridges to reference architecture; "
            "skill_partner_partner_engineering remains DO_NOT_PROMOTE."
        ),
    },
    {
        "bridge_edge_family": "partner_ecosystem_to_ai_adoption",
        "source_pillar_id": P_PARTNER_GTM,
        "target_pillar_id": P_AGENTIC,
        "direction": "forward",
        "evidence_fact_ids": ["fact_partnerships_gtm_001", "fact_engineering_platform_001"],
        "rationale": "Partner GTM ecosystem bridges to agentic AI platform adoption (traversal only).",
    },
    {
        "bridge_edge_family": "domain_expertise_to_section_eligibility",
        "source_pillar_id": P_HYPERSCALER,
        "target_pillar_id": "section_executive_summary",
        "direction": "forward",
        "edge_type": "pillar_section_eligibility",
        "evidence_fact_ids": ["bul_ibm_005"],
        "rationale": "Hyperscaler alliance pillar eligible for executive_summary when facts active.",
    },
    {
        "bridge_edge_family": "domain_expertise_to_section_eligibility",
        "source_pillar_id": P_APPLIED_AI,
        "target_pillar_id": "section_competencies",
        "direction": "forward",
        "edge_type": "pillar_section_eligibility",
        "evidence_fact_ids": ["fact_solutions_002"],
        "rationale": "Applied AI partner architecture eligible for competencies projection.",
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
        if pid in (P_HYPERSCALER, P_APPLIED_AI) and pid not in inc:
            inc.append(pid)
    track2["pillars_include_confirmed"] = inc
    _wg.write_text(TAXONOMY_PATH, json.dumps(tax, indent=2) + "\n", encoding="utf-8")


def _counts(ledger: dict[str, Any]) -> dict[str, int]:
    rows = ledger.get("skill_rows") or []
    bridge_edges = [
        e
        for e in ledger.get("graph_edges") or []
        if str(e.get("edge_type")) in ("pillar_phase_bridge", "pillar_section_eligibility")
    ]
    w12_bridges = [e for e in bridge_edges if e.get("bridge_edge_family") in {
        "hyperscaler_to_applied_ai_architecture",
        "marketplace_to_partner_gtm",
        "partner_engineering_to_reference_architecture",
        "partner_ecosystem_to_ai_adoption",
    } or str(e.get("source_node_id", "")).startswith("pillar_hyperscaler")]
    return {
        "pillar_count": len(ledger.get("pillars") or []),
        "skill_row_count": len(rows),
        "graph_edge_count": len(ledger.get("graph_edges") or []),
        "bridge_edge_count": len(bridge_edges),
        "w12_bridge_edge_count": len(w12_bridges),
        "activation_active": sum(1 for r in rows if str(r.get("activation_status")) == "ACTIVE"),
        "activation_active_confirmed": sum(
            1 for r in rows if str(r.get("activation_status")) == "ACTIVE_CONFIRMED"
        ),
        "activation_draft": sum(1 for r in rows if str(r.get("activation_status")) == "DRAFT"),
        "internal_only_skill_rows": sum(
            1 for r in rows if str(r.get("support_level")) == "INTERNAL_ONLY"
        ),
        "user_confirmed_pending": sum(
            1 for r in rows if str(r.get("support_level")) == "USER_CONFIRMED_PENDING_SOURCE"
        ),
    }


def _verify_w8_intact(ledger: dict[str, Any]) -> None:
    pids = {p["pillar_id"] for p in ledger.get("pillars") or []}
    required = {
        "pillar_insurance_carrier_transformation",
        "pillar_insurer_it_strategy_ai_enablement",
        "pillar_banking_platform_responsible_ai",
    }
    missing = required - pids
    if missing:
        raise ValueError(f"W8–W11 pillars missing after W12 apply: {sorted(missing)}")
    sr = [r["skill_id"] for r in ledger.get("skill_rows") or [] if str(r["skill_id"]).startswith("skill_sr_")]
    if len([s for s in sr if not s.startswith("skill_sr_w12_")]) < 10:
        raise ValueError("W8–W11 skill_sr rows count dropped unexpectedly")


def main() -> int:
    before_ledger = json.loads(OUT_LEDGER.read_text(encoding="utf-8"))
    assert_skills_not_broad_ledger_authority(before_ledger.get("metadata"))
    before = _counts(before_ledger)

    design = json.loads(DESIGN_PATH.read_text(encoding="utf-8"))
    taxonomy, pillars_added = _upsert_pillars(design.get("capability_taxonomy") or [])
    design["capability_taxonomy"] = taxonomy
    skills_new = _merge_matrix(design, "senior_role_w12_partner_matrix", SENIOR_ROLE_W12_MATRIX)
    bridges_new = _merge_bridges(design, W12_BRIDGE_EDGES)
    design["w12_partner_activation_criteria"] = W12_ACTIVATION_CRITERIA
    design.setdefault("stats", {})["senior_role_w12_partner_matrix_rows"] = len(
        design.get("senior_role_w12_partner_matrix") or []
    )
    design["stats"]["w12_partner_activation_criteria_rows"] = len(W12_ACTIVATION_CRITERIA)
    _wg.write_text(DESIGN_PATH, json.dumps(design, indent=2) + "\n", encoding="utf-8")
    _patch_career_taxonomy(pillars_added)

    payload = build_ledger_payload(design)
    _wg.write_text(OUT_LEDGER, json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    rematerialize_career_tracks(write=True)

    ledger = load_master_skills_arsenal_ledger(path=OUT_LEDGER)
    validate_arsenal_ledger_shape(ledger)
    _verify_w8_intact(ledger)
    after = _counts(ledger)

    w12_skills = [r for r in ledger.get("skill_rows") or [] if str(r.get("skill_id", "")).startswith("skill_sr_w12_")]
    pending = [
        r["skill_id"]
        for r in ledger.get("skill_rows") or []
        if str(r.get("support_level")) == "USER_CONFIRMED_PENDING_SOURCE"
    ]
    do_not_promote_external = [
        sid
        for sid in ("skill_partner_partner_engineering", "skill_partner_product_feedback_loops")
        if not skill_row_eligible_for_external_claim(
            next(r for r in ledger["skill_rows"] if r["skill_id"] == sid)
        )
    ]

    receipt = {
        "schema": "phase2_w12_partner_hyperscaler_graph_receipt_v1",
        "status": "PASS",
        "plan_id": "phase2-gtm-presales-remaining-f7a2c9",
        "wave": "W12-graph",
        "audit_id": "senior_role_graph_gap_analysis_20260520",
        "scope_match": True,
        "proof_classification": "graph_materialization_receipt_only",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pillar_count_before_after": {"before": before["pillar_count"], "after": after["pillar_count"]},
        "skill_count_before_after": {"before": before["skill_row_count"], "after": after["skill_row_count"]},
        "edge_count_before_after": {
            "before": before["graph_edge_count"],
            "after": after["graph_edge_count"],
        },
        "bridge_edge_count_before_after": {
            "before": before["bridge_edge_count"],
            "after": after["bridge_edge_count"],
        },
        "active_vs_draft_counts": {
            "activation_active": after["activation_active"],
            "activation_active_confirmed": after["activation_active_confirmed"],
            "activation_draft": after["activation_draft"],
            "internal_only_skill_rows": after["internal_only_skill_rows"],
            "user_confirmed_pending_source": after["user_confirmed_pending"],
        },
        "pillars_added": pillars_added,
        "skills_added": skills_new,
        "bridge_edges_added": bridges_new,
        "w12_partner_activation_criteria": W12_ACTIVATION_CRITERIA,
        "direct_evidence_items": [
            c["item_id"] for c in W12_ACTIVATION_CRITERIA if c["evidence_class"] == "DIRECT_EVIDENCE"
        ],
        "human_confirmation_required": [
            c["item_id"] for c in W12_ACTIVATION_CRITERIA
            if c["evidence_class"] == "MEDIUM_NEEDS_HUMAN_CONFIRMATION"
        ],
        "draft_internal_only_items": [
            c["item_id"] for c in W12_ACTIVATION_CRITERIA
            if c["activation_decision"] in ("DO_NOT_PROMOTE", "INTERNAL_ONLY_DIRECTIONAL")
        ],
        "do_not_promote_external_blocked": do_not_promote_external,
        "explicit_non_claims": EXPLICIT_NON_CLAIMS,
        "w8_w11_integrity_check": "PASS",
    }
    _wg.write_text(RECEIPT_JSON, json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    _wg.write_text(
        RECEIPT_MD,
        "\n".join(
            [
                "# W12 partner / hyperscaler graph receipt",
                "",
                f"**STATUS:** {receipt['status']}",
                f"**PLAN_ID:** `{receipt['plan_id']}`",
                f"**WAVE:** {receipt['wave']}",
                "",
                f"Pillars {before['pillar_count']} → {after['pillar_count']}; "
                f"skills {before['skill_row_count']} → {after['skill_row_count']}; "
                f"edges {before['graph_edge_count']} → {after['graph_edge_count']}; "
                f"phase bridges {before['bridge_edge_count']} → {after['bridge_edge_count']}.",
                "",
                "## Pillars added",
                *[f"- `{p}`" for p in pillars_added],
                "",
                "## Skills added",
                *[f"- `{s}`" for s in skills_new],
                "",
                "## DO_NOT_PROMOTE (external blocked)",
                *[f"- `{s}`" for s in do_not_promote_external],
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(
        f"W12 pillars_added={len(pillars_added)} skills_new={len(skills_new)} "
        f"bridges_new_families={len(bridges_new)} "
        f"skill_rows {before['skill_row_count']}->{after['skill_row_count']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
