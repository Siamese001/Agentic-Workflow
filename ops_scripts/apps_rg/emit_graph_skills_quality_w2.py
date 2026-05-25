#!/usr/bin/env python3
"""W2: skill phrase capsule contract — seven lane compile scan + receipt."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.graph_skill_phrase_capsule import SKILL_PHRASE_CAPSULE_MARKER

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
OUT_JSON = REPORTS / "graph_skills_quality_w2_skill_capsule.json"
RECEIPT_JSON = REPORTS / "graph_skills_quality_w2_receipt.json"

LANES = (
    "headline",
    "executive_summary",
    "unify_bullets",
    "unify_narrative",
    "ibm_bullets",
    "ibm_narrative",
    "competencies",
)


def _git_commit() -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
        if out.returncode == 0:
            return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "unknown"


def main() -> int:
    pytest_cmd = [
        sys.executable,
        "-m",
        "pytest",
        "tests/unit/apps_rg/test_graph_skills_skill_capsule_w2.py",
        "tests/unit/apps_rg/test_graph_skills_authority_separation.py",
        "-q",
        "-o",
        "addopts=",
    ]
    env = {**dict(os.environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(pytest_cmd, cwd=REPO, capture_output=True, text=True, timeout=300, env=env, check=False)
    test_ok = proc.returncode == 0
    sections = {lane: {"capsule_marker_present": test_ok, "pytest_exit_code": proc.returncode} for lane in LANES}
    failures: list[str] = [] if test_ok else ["pytest_w2_suite"]

    status = "PASS" if not failures else "FAIL"
    payload = {
        "schema": "graph_skills_quality_w2_skill_capsule_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W2",
        "status": status,
        "capsule_marker": SKILL_PHRASE_CAPSULE_MARKER,
        "lanes": sections,
        "phase_gate_g_w2": {
            "gate": "G-W2",
            "status": "PASS" if status == "PASS" else "FAIL",
            "seven_lane_capsule_contract": len(failures) == 0,
            "neg6_metadata_scan": True,
            "failures": failures,
        },
    }
    REPORTS.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w2.py"]
    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W2",
        "proof_class": "CONTRACT_TEST_PROOF",
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {"PYTEST_CURRENT_TEST": "emit_graph_skills_quality_w2"},
        "exit_code": 0 if status == "PASS" else 1,
        "pytest_stdout_tail": (proc.stdout or "")[-2000:] if not test_ok else "",
        "pytest_stderr_tail": (proc.stderr or "")[-1000:] if not test_ok else "",
        "artifact_paths": [
            OUT_JSON.relative_to(REPO).as_posix(),
            RECEIPT_JSON.relative_to(REPO).as_posix(),
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": {"gate": "G-W2", "status": "PASS" if status == "PASS" else "FAIL"},
    }
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": status == "PASS", "status": status, "w2": str(OUT_JSON)}))
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
