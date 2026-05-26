"""Follow-on closeout compiler — graph-skills-deferred-followup-d7f2a8."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from apps_rg.fact_inventory.graph_skills_quality_enhancement_closeout import (
    LANES,
    build_closeout as build_parent_closeout,
    build_d6_lane_matrix,
)

PLAN_ID = "graph-skills-deferred-followup-d7f2a8"
PARENT_PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
SCHEMA = "graph_skills_deferred_followup_closeout_v1"


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return doc if isinstance(doc, dict) else {}


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_followup_closeout(repo_root: Path, *, git_commit: str = "unknown") -> dict[str, Any]:
    parent = build_parent_closeout(repo_root, git_commit=git_commit)
    d6 = build_d6_lane_matrix(repo_root)
    live_count = sum(1 for r in d6 if r.get("live_x3_allow_claimed"))
    w10_ag = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_c03_unified_pipeline_bind.json")
    w1 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_deferred_followup_w1_receipt.json")
    w2 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_deferred_followup_w2_receipt.json")
    w4 = _read_json(repo_root / "docs/reports/apps_rg/graph_skills_deferred_followup_w4_receipt.json")

    contract_bound = bool(w10_ag.get("claims_c03_unified_pipeline_bound"))
    real_llm_spine = bool(w1.get("d16_real_llm_pass"))
    live_7 = live_count == len(LANES) or bool(w2.get("live_x3_allow_count") == len(LANES))
    ci_gha = bool(w4.get("ci_gha_executed"))

    release = contract_bound and real_llm_spine and live_7 and ci_gha

    return {
        "schema": SCHEMA,
        "plan_id": PLAN_ID,
        "parent_plan_id": PARENT_PLAN_ID,
        "generated_at": _utc_now(),
        "git_commit": git_commit,
        "status": "PASS" if release else "PARTIAL",
        "parent_closeout_status": parent.get("status"),
        "live_x3_allow_lane_count": live_count,
        "live_x3_required": len(LANES),
        "claims_c03_unified_pipeline_bound": contract_bound,
        "claims_dynamic_graphrag_traverse_real_llm": real_llm_spine,
        "claims_live_x3_7_of_7": live_7,
        "claims_ci_ratchet_gha_executed": ci_gha,
        "claims_release_eligible": release,
        "w10_ag_bind_status": w10_ag.get("status"),
        "wave_receipts": {
            "w0": "docs/reports/apps_rg/graph_skills_deferred_followup_w0_receipt.json",
            "w1": "docs/reports/apps_rg/graph_skills_deferred_followup_w1_receipt.json",
            "w2": "docs/reports/apps_rg/graph_skills_deferred_followup_w2_receipt.json",
            "w3": "docs/reports/apps_rg/graph_skills_deferred_followup_w3_receipt.json",
            "w4": "docs/reports/apps_rg/graph_skills_deferred_followup_w4_receipt.json",
            "w5": "docs/reports/apps_rg/graph_skills_deferred_followup_closeout.json",
        },
        "d6_lane_matrix": d6,
        "notes": "Follow-on plan; parent remains Completed.",
    }


__all__ = ["PLAN_ID", "build_followup_closeout"]
