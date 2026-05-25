#!/usr/bin/env python3
"""W6: hybrid graph boost receipt + NEG-3 contract proof."""
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

from apps_rg.runtime.graph_skills_hybrid_boost import build_hybrid_graph_boost_receipt

PLAN_ID = "graph-skills-quality-enhancement-c4e8a1"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
HYBRID_JSON = REPORTS / "hybrid_graph_boost_receipt.json"
W6_JSON = REPORTS / "graph_skills_quality_w6_hybrid_boost.json"
RECEIPT_W6 = REPORTS / "graph_skills_quality_w6_receipt.json"

PYTEST_TARGETS = [
    "tests/unit/apps_rg/test_graph_skills_hybrid_boost_w6.py",
    "tests/unit/apps_rg/test_graph_skills_authority_separation.py::test_neg3_hybrid_fact_outside_resolver_pool",
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
    receipt = build_hybrid_graph_boost_receipt(repo_root=REPO)
    REPORTS.mkdir(parents=True, exist_ok=True)
    HYBRID_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")

    pytest_cmd = [sys.executable, "-m", "pytest", *PYTEST_TARGETS, "-q", "-o", "addopts="]
    env = {**dict(os.environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"}
    proc = subprocess.run(pytest_cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=env, check=False)
    tests_ok = proc.returncode == 0

    status = "PASS" if receipt.get("status") == "PASS" and tests_ok else "FAIL"
    payload = {
        "schema": "graph_skills_quality_w6_hybrid_boost_v1",
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_id": PLAN_ID,
        "wave": "W6",
        "status": status,
        "hybrid_graph_boost_receipt": HYBRID_JSON.relative_to(REPO).as_posix(),
        "neg3_all_lanes_pass": receipt.get("neg3_all_lanes_pass"),
        "reorder_applied_any_lane": receipt.get("reorder_applied_any_lane"),
        "phase_gate_g_w6": {
            "gate": "G-W6",
            "status": "PASS" if status == "PASS" else "FAIL",
            "hybrid_receipt_on_disk": HYBRID_JSON.is_file(),
            "neg3_pass": receipt.get("neg3_all_lanes_pass") is True and tests_ok,
            "reorder_only_enforced": receipt.get("reorder_only") is True,
        },
    }
    W6_JSON.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    cmd = [sys.executable, "ops_scripts/apps_rg/emit_graph_skills_quality_w6.py"]
    code = 0 if status == "PASS" else 1
    wave_receipt = {
        "schema": "graph_skills_quality_wave_receipt_v1",
        "wave_id": "W6",
        "proof_class": "CONTRACT_TEST_PROOF",
        "command": " ".join(cmd),
        "command_argv": cmd,
        "cwd": str(REPO),
        "env_vars": {"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"},
        "exit_code": code,
        "artifact_paths": [
            HYBRID_JSON.relative_to(REPO).as_posix(),
            W6_JSON.relative_to(REPO).as_posix(),
            RECEIPT_W6.relative_to(REPO).as_posix(),
        ],
        "timestamp_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "git_commit": _git_commit(),
        "phase_gate": {"gate": "G-W6", "status": "PASS" if code == 0 else "FAIL"},
    }
    RECEIPT_W6.write_text(json.dumps(wave_receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"ok": code == 0, "status": status, "hybrid": str(HYBRID_JSON)}))
    return code


if __name__ == "__main__":
    raise SystemExit(main())
