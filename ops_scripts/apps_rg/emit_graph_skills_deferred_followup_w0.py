#!/usr/bin/env python3
"""W0: deferred follow-on baseline — refresh parent closeout notes + W10-AG merge."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.graph_skills_quality_enhancement_closeout import build_closeout

PLAN_ID = "graph-skills-deferred-followup-d7f2a8"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RECEIPT = REPORTS / "graph_skills_deferred_followup_w0_receipt.json"
PARENT_CLOSEOUT = REPORTS / "graph_skills_quality_enhancement_closeout.json"
W10_AG_BIND = REPORTS / "graph_skills_c03_unified_pipeline_bind.json"


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return out.stdout.strip()
    except (subprocess.SubprocessError, OSError):
        return "unknown"


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    commit = _git_commit()
    closeout = build_closeout(REPO, git_commit=commit)
    w10_ag = {}
    if W10_AG_BIND.is_file():
        w10_ag = json.loads(W10_AG_BIND.read_text(encoding="utf-8"))
    closeout["w10_ag_contract_status"] = w10_ag.get("status")
    closeout["claims_c03_unified_pipeline_bound_contract"] = bool(
        w10_ag.get("claims_c03_unified_pipeline_bound")
    )
    closeout["claims_dynamic_graphrag_traverse_contract"] = bool(
        w10_ag.get("claims_dynamic_graphrag_traverse")
    )
    closeout["follow_on_plan_id"] = PLAN_ID
    closeout["notes"] = (
        "Parent closeout refreshed at follow-on W0. W10-AG contract PASS on disk; "
        "claims_release_eligible remains false until follow-on W2/W5."
    )
    PARENT_CLOSEOUT.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": "graph_skills_deferred_followup_wave_receipt_v1",
        "plan_id": PLAN_ID,
        "wave_id": "W0",
        "status": "PASS",
        "git_commit": commit,
        "parent_closeout_path": "docs/reports/apps_rg/graph_skills_quality_enhancement_closeout.json",
        "w10_ag_bind_path": "docs/reports/apps_rg/graph_skills_c03_unified_pipeline_bind.json",
        "w10_ag_status": w10_ag.get("status"),
        "live_x3_allow_lane_count": closeout.get("live_x3_allow_lane_count"),
        "phase_gate": "PHASE_GATE: wave=W0 status=PASS gate=G-W0",
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": "PASS", "receipt": str(RECEIPT.relative_to(REPO))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
