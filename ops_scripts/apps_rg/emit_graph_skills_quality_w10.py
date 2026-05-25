#!/usr/bin/env python3
"""W10: graph-skills quality enhancement closeout (D1–D16 matrix + D6 inventory)."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.fact_inventory.graph_skills_quality_enhancement_closeout import (
    PLAN_ID,
    build_closeout,
)

REPORTS = REPO / "docs" / "reports" / "apps_rg"
CLOSEOUT_JSON = REPORTS / "graph_skills_quality_enhancement_closeout.json"
RECEIPT_W10 = REPORTS / "graph_skills_quality_w10_receipt.json"
PYTEST_TARGET = "tests/unit/apps_rg/test_graph_skills_closeout_w10.py"


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


def _run_pytest() -> tuple[bool, str]:
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", PYTEST_TARGET, "-q", "-o", "addopts="],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
        env=env,
    )
    tail = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode == 0, tail[-2000:]


def main() -> int:
    REPORTS.mkdir(parents=True, exist_ok=True)
    pytest_ok, pytest_tail = _run_pytest()
    closeout = build_closeout(REPO, git_commit=_git_commit())
    closeout["contract_test_pass"] = pytest_ok
    compiler_status = str(closeout.get("status") or "PARTIAL")
    if not pytest_ok:
        closeout["status"] = "FAIL"
        compiler_status = "FAIL"
    CLOSEOUT_JSON.write_text(json.dumps(closeout, indent=2) + "\n", encoding="utf-8")

    status = compiler_status
    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "plan_id": PLAN_ID,
        "wave_id": "W10",
        "proof_class": "LIVE_X3_ALLOW_PROOF",
        "command": "python ops_scripts/apps_rg/emit_graph_skills_quality_w10.py",
        "command_argv": [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w10.py"],
        "cwd": str(REPO),
        "env_vars": {},
        "exit_code": 0 if pytest_ok and status != "FAIL" else 1,
        "artifact_paths": [
            "docs/reports/apps_rg/graph_skills_quality_enhancement_closeout.json",
            "docs/reports/apps_rg/graph_skills_quality_w10_receipt.json",
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": closeout.get("git_commit"),
        "phase_gate": {
            "gate": "G-W10",
            "status": status,
            "live_x3_allow_count": closeout.get("live_x3_allow_lane_count"),
        },
        "proof_classes": {
            "closeout_compiler": "PASS" if pytest_ok else "FAIL",
            "live_x3_matrix": status,
        },
        "claims": {
            "claims_release_eligible": closeout.get("claims_release_eligible"),
            "claims_live_x3_7_of_7": closeout.get("claims_live_x3_7_of_7"),
            "claims_dynamic_graphrag_traverse": closeout.get("claims_dynamic_graphrag_traverse"),
            "claims_c03_unified_pipeline_bound": closeout.get("claims_c03_unified_pipeline_bound"),
        },
        "pytest_tail": pytest_tail,
        "notes": "W10 does not complete plan — mandatory W10-AG follows.",
    }
    RECEIPT_W10.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    print(f"STATUS: {status}")
    print(f"CLOSEOUT: {CLOSEOUT_JSON}")
    print(f"LIVE_X3: {closeout.get('live_x3_allow_lane_count')}/{len(closeout.get('d6_lane_matrix') or [])}")
    return 0 if pytest_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
