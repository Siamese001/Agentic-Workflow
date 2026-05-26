#!/usr/bin/env python3
"""W2: inventory LIVE_X3 + D6 checklist from latest Brown runtime proof dirs."""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.graph_skills_quality_enhancement_closeout import build_d6_lane_matrix

PLAN_ID = "graph-skills-deferred-followup-d7f2a8"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RECEIPT = REPORTS / "graph_skills_deferred_followup_w2_receipt.json"


def main() -> int:
    d6 = build_d6_lane_matrix(REPO)
    live = sum(1 for r in d6 if r.get("live_x3_allow_claimed"))
    checklist_ok = sum(1 for r in d6 if (r.get("d6_artifact_checklist") or {}).get("checklist_pass"))
    status = "PASS" if live == len(d6) and checklist_ok == len(d6) else "PARTIAL"
    receipt = {
        "schema": "graph_skills_deferred_followup_wave_receipt_v1",
        "plan_id": PLAN_ID,
        "wave_id": "W2",
        "status": status,
        "live_x3_allow_count": live,
        "live_x3_required": len(d6),
        "checklist_pass_count": checklist_ok,
        "d6_lane_matrix": d6,
        "phase_gate": f"PHASE_GATE: wave=W2 status={status} gate=G-W2",
        "notes": "Rerun Brown CLI per lane to reach 7/7; unify/ibm/competencies need fresh REAL_LLM runs.",
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "live": live, "required": len(d6)}, indent=2))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
