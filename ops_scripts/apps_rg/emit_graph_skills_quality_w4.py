#!/usr/bin/env python3
"""W4: X1D rubric port diff + authority negative tests + X2 contract subset."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from apps_rg.runtime.judges.graph_skills_x1d_rubric_contract import (
    NON_CLAIM_NO_MASKING,
    build_rubric_port_diff,
)

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RUBRIC_DIFF_JSON = REPORTS / "graph_skills_x1d_rubric_port_diff.json"
W4_JSON = REPORTS / "graph_skills_quality_w4_quality_port.json"
RECEIPT_W4 = REPORTS / "graph_skills_quality_w4_receipt.json"

PYTEST_TARGETS = [
    "tests/unit/apps_rg/test_graph_skills_authority_separation.py",
    "tests/unit/apps_rg/test_graph_skills_authority_separation_w1.py",
    "tests/unit/apps_rg/test_graph_skills_x1d_rubric_w4.py",
    "tests/unit/apps_rg/validators/test_headline_x2_fixed_prefix_contract.py",
    "tests/unit/apps_rg/test_executive_summary_composition_x2.py",
]


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
    rubric_diff = build_rubric_port_diff(repo_root=REPO)
    REPORTS.mkdir(parents=True, exist_ok=True)
    RUBRIC_DIFF_JSON.write_text(json.dumps(rubric_diff, indent=2) + "\n", encoding="utf-8")

    pytest_cmd = [sys.executable, "-m", "pytest", *PYTEST_TARGETS, "-q", "-o", "addopts="]
    env = {**dict(os.environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(pytest_cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=env, check=False)
    tests_ok = proc.returncode == 0

    status = "PASS" if rubric_diff.get("status") == "PASS" and tests_ok else "FAIL"
    payload = {
        "schema": "graph_skills_quality_w4_quality_port_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W4",
        "status": status,
        "non_claim": NON_CLAIM_NO_MASKING,
        "rubric_port_diff": RUBRIC_DIFF_JSON.relative_to(REPO).as_posix(),
        "any_masking_relaxed": rubric_diff.get("any_masking_relaxed"),
        "invariant_failures": rubric_diff.get("invariant_failures"),
        "pytest_exit_code": proc.returncode,
        "pytest_targets": PYTEST_TARGETS,
        "phase_gate_g_w4": {
            "gate": "G-W4",
            "status": "PASS" if status == "PASS" else "FAIL",
            "rubric_diff_pass": rubric_diff.get("status") == "PASS",
            "negative_authority_tests_pass": tests_ok,
            "x2_contract_subset_pass": tests_ok,
        },
    }
    W4_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w4.py"]
    code = 0 if status == "PASS" else 1
    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W4",
        "proof_class": "CONTRACT_TEST_PROOF",
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        "exit_code": code,
        "non_claim": NON_CLAIM_NO_MASKING,
        "pytest_stdout_tail": (proc.stdout or "")[-2500:] if not tests_ok else "",
        "pytest_stderr_tail": (proc.stderr or "")[-1500:] if not tests_ok else "",
        "artifact_paths": [
            RUBRIC_DIFF_JSON.relative_to(REPO).as_posix(),
            W4_JSON.relative_to(REPO).as_posix(),
            RECEIPT_W4.relative_to(REPO).as_posix(),
            rubric_diff.get("baseline_path"),
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": {"gate": "G-W4", "status": "PASS" if code == 0 else "FAIL"},
    }
    RECEIPT_W4.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": code == 0, "status": status, "rubric_diff": str(RUBRIC_DIFF_JSON)}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
