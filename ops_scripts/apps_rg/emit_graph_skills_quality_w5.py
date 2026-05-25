#!/usr/bin/env python3
"""W5: resume spine skill bundle + D7 FEC/resolver set equality (6/6 lanes)."""
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

from apps_rg.runtime.spine.graph_skills_fec_set_equality import D7_SET_EQUALITY_LANES, audit_all_d7_lanes
from apps_rg.runtime.spine.resume_spine_skill_bundle import build_resume_spine_skill_bundle

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
BUNDLE_JSON = REPORTS / "resume_spine_skill_bundle.json"
D7_JSON = REPORTS / "graph_skills_fec_set_equality_receipt.json"
W5_JSON = REPORTS / "graph_skills_quality_w5_spine_fec.json"
RECEIPT_W5 = REPORTS / "graph_skills_quality_w5_receipt.json"

PYTEST_TARGETS = [
    "tests/unit/apps_rg/test_graph_skills_spine_fec_w5.py",
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
    bundle = build_resume_spine_skill_bundle(repo_root=REPO)
    d7 = audit_all_d7_lanes(repo_root=REPO)
    REPORTS.mkdir(parents=True, exist_ok=True)
    BUNDLE_JSON.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    D7_JSON.write_text(json.dumps(d7, indent=2) + "\n", encoding="utf-8")

    pytest_cmd = [sys.executable, "-m", "pytest", *PYTEST_TARGETS, "-q", "-o", "addopts="]
    env = {**dict(os.environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(pytest_cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=env, check=False)
    tests_ok = proc.returncode == 0

    status = "PASS"
    if d7.get("status") != "PASS":
        status = "FAIL"
    if not bundle.get("lanes"):
        status = "FAIL"
    if not tests_ok:
        status = "FAIL"

    payload = {
        "schema": "graph_skills_quality_w5_spine_fec_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W5",
        "status": status,
        "resume_spine_skill_bundle": BUNDLE_JSON.relative_to(REPO).as_posix(),
        "unique_skill_count": bundle.get("unique_skill_count"),
        "dedupe_pass": bundle.get("dedupe_pass"),
        "dedupe_collision_count": bundle.get("dedupe_collision_count"),
        "d7_receipt": D7_JSON.relative_to(REPO).as_posix(),
        "d7_pass_count": d7.get("d7_pass_count"),
        "d7_target_count": d7.get("d7_target_count"),
        "d7_lanes": list(D7_SET_EQUALITY_LANES),
        "phase_gate_g_w5": {
            "gate": "G-W5",
            "status": "PASS" if status == "PASS" else "FAIL",
            "resume_spine_skill_bundle_on_disk": BUNDLE_JSON.is_file(),
            "d7_set_equality_6_of_6": d7.get("d7_all_pass") is True,
            "contract_tests_pass": tests_ok,
        },
    }
    W5_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w5.py"]
    code = 0 if status == "PASS" else 1
    receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W5",
        "proof_class": "CONTRACT_TEST_PROOF",
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        "exit_code": code,
        "artifact_paths": [
            BUNDLE_JSON.relative_to(REPO).as_posix(),
            D7_JSON.relative_to(REPO).as_posix(),
            W5_JSON.relative_to(REPO).as_posix(),
            RECEIPT_W5.relative_to(REPO).as_posix(),
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": {"gate": "G-W5", "status": "PASS" if code == 0 else "FAIL"},
    }
    RECEIPT_W5.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "ok": code == 0,
                "status": status,
                "d7": f"{d7.get('d7_pass_count')}/{d7.get('d7_target_count')}",
                "bundle": str(BUNDLE_JSON),
            }
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
