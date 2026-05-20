"""Evidence uplift audit for skill_p2_tech_estimation_sizing_directional — read-only."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CLOSEOUT_SSOT = ROOT / "docs/reports/apps_rg/skills_graph_phase2_gtm_presales_closeout.json"
OUT_JSON = ROOT / "docs/reports/apps_rg/skills_graph_phase2_estimation_sizing_evidence_uplift.json"
OUT_MD = ROOT / "docs/reports/apps_rg/skills_graph_phase2_estimation_sizing_evidence_uplift.md"

TARGET_SKILL = "skill_p2_tech_estimation_sizing_directional"

SEARCH_PATHS: tuple[Path, ...] = (
    ROOT / "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
    ROOT / "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
    ROOT / "docs/reports/apps_rg/exec_summary_fact_ledger_expansion_audit.json",
    ROOT / "docs/reports/apps_rg/master_experience_ledger_archive_audit.json",
    ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
)

TECH_SIZING_RE = re.compile(
    r"\b(architecture sizing|migration sizing|cloud workload estim|workload estim|"
    r"capacity planning|delivery effort estim|effort estim|sizing model|estimation model|"
    r"infrastructure sizing|compute sizing)\b",
    re.I,
)
MODELING_RE = re.compile(
    r"\b(synergy model|forecasting model|forecast model|usage-based forecasting|"
    r"capital model|pricing model|stochastic model|quantify.*integration cost)\b",
    re.I,
)
ROI_RE = re.compile(r"\b(measurable ROI|ROI on|business case|value proposition)\b", re.I)
COST_RE = re.compile(r"\b(TCO|cost optimization|budget dashboard|cost model)\b", re.I)

CANDIDATE_TABLE: list[dict[str, Any]] = [
    {
        "search_theme": "estimation_models",
        "evidence_type": "financial_modeling",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_revenue_ops_005",
        "existing_skill_id": "skill_finance_ma_synergy_due_diligence",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Conducted preliminary M&A due diligence and developed synergy models to quantify "
            "technology integration costs and revenue opportunities."
        ),
        "rationale": "Synergy/integration-cost models are M&A financial modeling — not technical pre-sales sizing.",
    },
    {
        "search_theme": "sizing_models",
        "evidence_type": "financial_modeling",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_revenue_ops_003",
        "existing_skill_id": "skill_revops_usage_based_subscription_forecasting",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Developed AI-enhanced usage-based forecasting models to optimize subscription pricing "
            "and renewals, adding $5M in recurring revenue."
        ),
        "rationale": "Subscription/revenue forecasting — commercial finance sizing, not cloud architecture workload sizing.",
    },
    {
        "search_theme": "architecture_sizing",
        "evidence_type": "delivery_estimation",
        "supports_target_skill": False,
        "confidence": "LOW",
        "linked_fact_id": None,
        "existing_skill_id": None,
        "source_path": "apps_rg/fact_inventory/master_skills_arsenal_ledger.json",
        "source_quote": "No architecture-sizing / workload-estimation methodology string in searchable sources.",
        "rationale": "Absence of technical sizing vocabulary in ledger inputs.",
    },
    {
        "search_theme": "capacity_planning",
        "evidence_type": "financial_modeling",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_quant_hpc_001",
        "existing_skill_id": None,
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Launched AWS streaming microservices / streaming analytics ecosystems to validate market data "
            "in near real time and increase decision capacity by about 25%."
        ),
        "rationale": "Operational/trading capacity outcome — not cloud migration capacity-planning methodology.",
    },
    {
        "search_theme": "cost_modeling",
        "evidence_type": "financial_modeling",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_revenue_ops_004",
        "existing_skill_id": "skill_finance_cost_optimization_dashboards",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Deployed transparent budget dashboards and microservices to reallocate underused resources "
            "and drive 30% cost optimization for senior finance teams."
        ),
        "rationale": "Finance cost-optimization dashboards — not pursuit-level technical cost/TCO sizing models.",
    },
    {
        "search_theme": "cost_modeling",
        "evidence_type": "financial_modeling",
        "supports_target_skill": False,
        "confidence": "HIGH",
        "linked_fact_id": "bul_insurtech_001",
        "existing_skill_id": None,
        "source_path": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_quote": (
            "Led end-to-end modernization of monolithic policy administration systems into AWS-based "
            "architectures, reducing total cost of ownership by 40%..."
        ),
        "rationale": "TCO reduction outcome — does not describe estimation/sizing methodology.",
    },
    {
        "search_theme": "migration_sizing",
        "evidence_type": "delivery_estimation",
        "supports_target_skill": False,
        "confidence": "HIGH",
        "linked_fact_id": "bul_ibm_002",
        "existing_skill_id": "skill_p2_tech_aws_modernization_patterns",
        "source_path": "apps_rg/resume/base/amit_ayer_base_resume_v1.json",
        "source_quote": (
            "Cloud Infrastructure Modernization: Led migration from legacy on-prem environments to scalable "
            "cloud-native architectures, reducing infrastructure overhead by 30%..."
        ),
        "rationale": "Migration delivery evidence without workload/effort sizing model.",
    },
    {
        "search_theme": "cloud_workload_estimation",
        "evidence_type": "delivery_estimation",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_engineering_platform_005",
        "existing_skill_id": "skill_p2_tech_devops_pipeline_blueprint",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Architected cloud-native microservices across AWS and Databricks Lakehouse, integrating enterprise "
            "data pipelines, vector services, API gateways, identity controls, and highly available execution layers."
        ),
        "rationale": "Architecture delivery — no workload-estimation or sizing-model claim.",
    },
    {
        "search_theme": "delivery_effort_estimation",
        "evidence_type": "delivery_estimation",
        "supports_target_skill": False,
        "confidence": "LOW",
        "linked_fact_id": None,
        "existing_skill_id": None,
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": "No person-month, effort-estimate, WBS, or delivery-sizing methodology in candidate ledger.",
        "rationale": "Gap remains for delivery effort estimation.",
    },
    {
        "search_theme": "commercial_pursuit_sizing",
        "evidence_type": "commercial_sizing",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_revenue_ops_001",
        "existing_skill_id": "skill_revops_salesforce_pipeline_analytics",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Designed analytics in Salesforce to prioritize high-potential deals, generating $10M in new annual "
            "recurring revenue and refining GTM strategies."
        ),
        "rationale": "Pipeline prioritization analytics — not technical/commercial sizing models for pursuits.",
    },
    {
        "search_theme": "roi_business_case_sizing",
        "evidence_type": "commercial_sizing",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_solutions_001",
        "existing_skill_id": "skill_p2_gtm_solution_mapping",
        "source_path": "docs/reports/apps_rg/exec_summary_fact_ledger_expansion_audit.json",
        "source_quote": (
            "Translated complex AI, data, and cloud architecture into executive value propositions and "
            "measurable ROI for senior stakeholders."
        ),
        "rationale": "ROI translation for executives — not estimation/sizing-model methodology.",
    },
    {
        "search_theme": "roi_business_case_sizing",
        "evidence_type": "commercial_sizing",
        "supports_target_skill": False,
        "confidence": "MEDIUM",
        "linked_fact_id": "fact_sales_accounts_002",
        "existing_skill_id": "skill_sales_modernization_deals_15m",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Closed multi-year modernization deals exceeding $15M by demonstrating ROI on HPC simulations for "
            "stress testing and cutting scenario runtimes by 40%."
        ),
        "rationale": "Deal-win ROI proof via HPC stress scenarios — adjacent to business case, not sizing models.",
    },
    {
        "search_theme": "estimation_models",
        "evidence_type": "financial_modeling",
        "supports_target_skill": False,
        "confidence": "HIGH",
        "linked_fact_id": "fact_ma_synergy_modeling_001",
        "existing_skill_id": None,
        "source_path": "docs/reports/apps_rg/master_experience_ledger_archive_audit.json",
        "source_quote": (
            "Conducted M&A readiness reviews, synergy modeling, and post-merger risk-model consolidation "
            "for executive stakeholders."
        ),
        "rationale": "Archive audit cites synergy modeling — already covered by strategic-finance skill row.",
    },
    {
        "search_theme": "sizing_models",
        "evidence_type": "financial_modeling",
        "supports_target_skill": False,
        "confidence": "HIGH",
        "linked_fact_id": None,
        "existing_skill_id": "skill_capital_capital_modeling",
        "source_path": "artifacts/apps_rg/fact_inventory/master_candidate_skills_fact_ledger_20260518T1100Z.json",
        "source_quote": (
            "Built advanced quantitative foundation through derivatives pricing, multi-Greek hedging, "
            "capital modeling, and FSA credential across Towers Perrin, ING, and Aetna."
        ),
        "rationale": "Actuarial capital modeling (Phase 1 track) — wrong domain for Phase 2 technical pre-sales sizing.",
    },
]


def _scan_file(path: Path) -> dict[str, Any]:
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    if not path.is_file():
        return {"path": rel, "exists": False}
    text = path.read_text(encoding="utf-8", errors="replace")
    tech, model, roi, cost = [], [], [], []
    for i, line in enumerate(text.splitlines(), 1):
        if TECH_SIZING_RE.search(line):
            tech.append(f"L{i}:{line.strip()[:220]}")
        if MODELING_RE.search(line):
            model.append(f"L{i}:{line.strip()[:220]}")
        if ROI_RE.search(line):
            roi.append(f"L{i}:{line.strip()[:220]}")
        if COST_RE.search(line):
            cost.append(f"L{i}:{line.strip()[:220]}")
    return {
        "path": rel,
        "exists": True,
        "technical_sizing_hits": tech[:15],
        "financial_modeling_hits": model[:15],
        "roi_business_case_hits": roi[:15],
        "cost_modeling_hits": cost[:15],
    }


def _skill_snapshot() -> dict[str, Any]:
    ledger = json.loads((ROOT / "apps_rg/fact_inventory/master_skills_arsenal_ledger.json").read_text(encoding="utf-8"))
    row = next(r for r in ledger.get("skill_rows") or [] if r.get("skill_id") == TARGET_SKILL)
    return {
        "skill_id": TARGET_SKILL,
        "support_level": row.get("support_level"),
        "visibility_rule": row.get("visibility_rule"),
        "fact_id_links": row.get("fact_id_links"),
        "source_snippets": row.get("source_snippets"),
    }


def _render_md(payload: dict[str, Any]) -> str:
    lines = [
        "# Phase 2 estimation/sizing — evidence uplift audit",
        "",
        f"**Promotion decision:** {payload['promotion_decision']}",
        f"**Proof classification:** {payload['proof_classification']}",
        "",
        "## Candidate evidence table",
        "",
        "| Theme | Evidence type | Supports target? | Confidence | linked_fact_id | Source |",
        "|-------|---------------|------------------|------------|----------------|--------|",
    ]
    for row in payload["candidate_evidence_table"]:
        src = Path(row["source_path"]).name
        lines.append(
            f"| {row['search_theme']} | {row['evidence_type']} | {row['supports_target_skill']} | "
            f"{row['confidence']} | `{row.get('linked_fact_id') or '—'}` | {src} |"
        )
    lines.extend(["", "## Promotion decision", "", payload["promotion_rationale"], "", "## Next blocker", "", payload["next_blocker"]])
    return "\n".join(lines) + "\n"


def main() -> int:
    closeout = json.loads(CLOSEOUT_SSOT.read_text(encoding="utf-8"))
    promotion_decision = "DO_NOT_PROMOTE"
    proof_classification = "NO_PROMOTION_ADJACENT_EVIDENCE_WRONG_DOMAIN"
    promotion_rationale = (
        "Repo contains financial/commercial modeling (synergy models, usage-based forecasting, ROI deal proof) "
        "and cost/TCO outcomes, but no source-backed technical pre-sales estimation or sizing methodology "
        "(architecture sizing, cloud workload estimation, migration sizing, delivery effort models). "
        "Adjacent evidence is already represented on other skill rows; bridging would over-claim."
    )
    next_blocker = (
        "Ingest resume/archive text naming sizing methodology (e.g., cloud workload estimates, migration effort "
        "models, pursuit sizing worksheets) with role scope — then re-run audit before promoting "
        f"{TARGET_SKILL}."
    )
    payload: dict[str, Any] = {
        "schema": "skills_graph_phase2_estimation_sizing_evidence_uplift_v1",
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "status": "PASS",
        "scope": "phase2_estimation_sizing_evidence_uplift_readonly",
        "closeout_ssot": str(CLOSEOUT_SSOT.relative_to(ROOT)).replace("\\", "/"),
        "target_skill_id": TARGET_SKILL,
        "skill_row_after_audit": _skill_snapshot(),
        "inference_only": True,
        "promotion_decision": promotion_decision,
        "proof_classification": proof_classification,
        "promotion_rationale": promotion_rationale,
        "repo_scan": [_scan_file(p) for p in SEARCH_PATHS],
        "candidate_evidence_table": CANDIDATE_TABLE,
        "related_skills_do_not_promote_target": [
            "skill_finance_ma_synergy_due_diligence",
            "skill_revops_usage_based_subscription_forecasting",
            "skill_revops_salesforce_pipeline_analytics",
            "skill_sales_modernization_deals_15m",
            "skill_p2_gtm_solution_mapping",
            "skill_finance_cost_optimization_dashboards",
        ],
        "explicit_non_claims": [
            "No technical pre-sales estimation or sizing methodology in repo sources.",
            "Synergy models (fact_revenue_ops_005) are M&A financial modeling — not architecture/cloud workload sizing.",
            "Usage-based forecasting models (fact_revenue_ops_003) are subscription/revenue finance — not technical sizing.",
            "ROI on HPC simulations (fact_sales_accounts_002) is deal-win proof — not sizing-model methodology.",
            "TCO/cost-optimization outcomes are results metrics — not estimation models.",
            "Actuarial capital modeling is Phase 1 domain — do not bridge to Phase 2 technical presales sizing.",
            "Do not fabricate pursuit sizing, migration sizing, or cloud workload estimation claims.",
        ],
        "evidence_gaps_remaining": [
            {
                "gap_id": "technical_architecture_sizing_methodology",
                "reason": "No architecture/cloud workload sizing model evidence.",
            },
            {
                "gap_id": "migration_effort_sizing",
                "reason": "Migration bullets lack effort/workload estimation methodology.",
            },
            {
                "gap_id": "delivery_effort_estimation",
                "reason": "No WBS/person-month/effort-estimate language in ledger.",
            },
            {
                "gap_id": "commercial_pursuit_sizing_models",
                "reason": "Pipeline analytics and ROI translation are not sizing models.",
            },
        ],
        "closeout_gap_note": (
            "Closeout gap 'estimation_sizing_models' is accurate for the target skill: modeling evidence exists "
            "but under financial/commercial domains on other skill rows — not technical pre-sales sizing."
        ),
        "next_blocker": next_blocker,
        "ledger_mutation": False,
    }
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    OUT_MD.write_text(_render_md(payload), encoding="utf-8")
    print(f"AUDIT promotion_decision={promotion_decision} candidates={len(CANDIDATE_TABLE)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
