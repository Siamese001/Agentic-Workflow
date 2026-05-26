#!/usr/bin/env python3
"""W4: CI GHA ratchet status — BLOCKED locally without gh."""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
PLAN_ID = "graph-skills-deferred-followup-d7f2a8"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RECEIPT = REPORTS / "graph_skills_deferred_followup_w4_receipt.json"
WORKFLOW = ".github/workflows/graph-skills-authority-ratchet.yml"


def main() -> int:
    gh = shutil.which("gh")
    gha_url = ""
    ci_ok = False
    if gh:
        proc = subprocess.run(
            [gh, "run", "list", f"--workflow={Path(WORKFLOW).name}", "--limit", "1", "--json", "url,conclusion"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if proc.returncode == 0 and proc.stdout.strip():
            try:
                rows = json.loads(proc.stdout)
                if rows:
                    gha_url = str(rows[0].get("url") or "")
                    ci_ok = str(rows[0].get("conclusion") or "") == "success"
            except json.JSONDecodeError:
                pass
    status = "PASS" if ci_ok and gha_url else "BLOCKED" if not gh else "PARTIAL"
    receipt = {
        "schema": "graph_skills_deferred_followup_wave_receipt_v1",
        "plan_id": PLAN_ID,
        "wave_id": "W4",
        "status": status,
        "ci_gha_executed": ci_ok,
        "gha_run_url": gha_url,
        "workflow_path": WORKFLOW,
        "phase_gate": f"PHASE_GATE: wave=W4 status={status} gate=G-W4",
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(receipt, indent=0))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
