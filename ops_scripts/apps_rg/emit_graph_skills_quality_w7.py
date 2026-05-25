#!/usr/bin/env python3
"""W7: graph-skills authority CI ratchet (local mirror + GHA workflow SSOT)."""
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

from ops_scripts.ci.check_graph_skills_agentic_core_boundary import check_boundary

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
WORKFLOW_PATH = REPO / ".github/workflows/graph-skills-authority-ratchet.yml"
BOUNDARY_JSON = REPORTS / "graph_skills_agentic_core_boundary_w7.json"
W7_JSON = REPORTS / "graph_skills_quality_w7_ci_ratchet.json"
RECEIPT_W7 = REPORTS / "graph_skills_quality_w7_receipt.json"

PYTEST_TARGETS = [
    "tests/unit/apps_rg/test_graph_skills_authority_separation.py",
    "tests/unit/apps_rg/test_graph_skills_authority_separation_w1.py",
    "tests/unit/apps_rg/test_graph_skills_jd_subgraph_w1.py",
    "tests/unit/apps_rg/test_graph_skills_skill_capsule_w2.py",
    "tests/unit/apps_rg/fact_inventory/test_graph_skills_graph_v2_w3.py",
    "tests/unit/apps_rg/test_graph_skills_x1d_rubric_w4.py",
    "tests/unit/apps_rg/test_graph_skills_spine_fec_w5.py",
    "tests/unit/apps_rg/test_graph_skills_hybrid_boost_w6.py",
    "tests/unit/apps_rg/test_graph_skills_utilization_w8.py",
    "tests/unit/apps_rg/test_graph_skills_operator_guide_w9.py",
    "tests/unit/apps_rg/test_graph_skills_closeout_w10.py",
    "tests/unit/apps_rg/test_graph_skills_run_artifacts.py",
    "tests/unit/apps_rg/test_graph_skills_enhancement_hardening.py",
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


def _try_gh_workflow_url() -> dict[str, object]:
    """Best-effort GHA run lookup; absent locally → ci_gha_executed=false."""
    if not WORKFLOW_PATH.is_file():
        return {"ci_gha_executed": False, "workflow_file_exists": False, "run_url": None}
    try:
        proc = subprocess.run(
            [
                "gh",
                "run",
                "list",
                "--workflow",
                "graph-skills-authority-ratchet.yml",
                "--limit",
                "1",
                "--json",
                "databaseId,url,conclusion,status",
            ],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        if proc.returncode != 0 or not (proc.stdout or "").strip():
            return {
                "ci_gha_executed": False,
                "workflow_file_exists": True,
                "run_url": None,
                "gh_error": (proc.stderr or proc.stdout or "")[:500],
            }
        rows = json.loads(proc.stdout)
        if not rows:
            return {"ci_gha_executed": False, "workflow_file_exists": True, "run_url": None}
        row = rows[0]
        return {
            "ci_gha_executed": True,
            "workflow_file_exists": True,
            "run_url": row.get("url"),
            "run_conclusion": row.get("conclusion"),
            "run_status": row.get("status"),
        }
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        return {
            "ci_gha_executed": False,
            "workflow_file_exists": True,
            "run_url": None,
            "gh_error": str(exc)[:500],
        }


def main() -> int:
    boundary = check_boundary(repo_root=REPO)
    REPORTS.mkdir(parents=True, exist_ok=True)
    BOUNDARY_JSON.write_text(json.dumps(boundary, indent=2) + "\n", encoding="utf-8")

    pytest_cmd = [sys.executable, "-m", "pytest", *PYTEST_TARGETS, "-q", "-o", "addopts="]
    env = {**dict(os.environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(pytest_cmd, cwd=REPO, capture_output=True, text=True, timeout=900, env=env, check=False)
    tests_ok = proc.returncode == 0
    boundary_ok = boundary.get("status") == "PASS"
    workflow_exists = WORKFLOW_PATH.is_file()
    gha = _try_gh_workflow_url()

    # Local W7 PASS = boundary + pytest + workflow on disk. GHA URL is D10 supplemental.
    local_pass = boundary_ok and tests_ok and workflow_exists
    proof_class = "CI_RATCHET_PROOF" if gha.get("ci_gha_executed") and gha.get("run_conclusion") == "success" else (
        "CONTRACT_TEST_PROOF"
    )
    if local_pass and not gha.get("ci_gha_executed"):
        status = "PARTIAL"
    elif local_pass:
        status = "PASS"
    else:
        status = "FAIL"

    payload = {
        "schema": "graph_skills_quality_w7_ci_ratchet_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W7",
        "status": status,
        "primary_proof_class": proof_class,
        "workflow_path": WORKFLOW_PATH.relative_to(REPO).as_posix(),
        "agentic_core_boundary": BOUNDARY_JSON.relative_to(REPO).as_posix(),
        "agentic_core_changed_count": boundary.get("changed_count"),
        "pytest_exit_code": proc.returncode,
        "pytest_target_count": len(PYTEST_TARGETS),
        "d10_ci_ratchet": {
            "workflow": "graph-skills-authority-ratchet.yml",
            "local_mirror_pass": local_pass,
            "gha": gha,
        },
        "d13_nightly_soak": {
            "cron": "17 9 * * *",
            "note": "Scheduled on graph-skills-authority-ratchet.yml; verify green run on GHA for full CI_RATCHET_PROOF",
        },
        "phase_gate_g_w7": {
            "gate": "G-W7",
            "status": "PASS" if status == "PASS" else ("PARTIAL" if status == "PARTIAL" else "FAIL"),
            "agentic_core_boundary_pass": boundary_ok,
            "contract_pytest_pass": tests_ok,
            "workflow_file_exists": workflow_exists,
            "ci_gha_executed": gha.get("ci_gha_executed"),
        },
    }
    W7_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w7.py"]
    code = 0 if local_pass else 1
    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W7",
        "proof_class": proof_class,
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        "exit_code": code,
        "status": status,
        "pytest_stdout_tail": (proc.stdout or "")[-2500:] if not tests_ok else "",
        "pytest_stderr_tail": (proc.stderr or "")[-1500:] if not tests_ok else "",
        "artifact_paths": [
            BOUNDARY_JSON.relative_to(REPO).as_posix(),
            W7_JSON.relative_to(REPO).as_posix(),
            RECEIPT_W7.relative_to(REPO).as_posix(),
            WORKFLOW_PATH.relative_to(REPO).as_posix(),
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": payload["phase_gate_g_w7"],
    }
    RECEIPT_W7.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": code == 0,
                "status": status,
                "boundary": boundary.get("status"),
                "pytest": proc.returncode,
                "workflow": str(WORKFLOW_PATH),
            }
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
