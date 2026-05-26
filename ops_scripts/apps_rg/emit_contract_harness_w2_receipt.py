#!/usr/bin/env python3
"""W2: verify B2/B3 graph authority contract tests pass."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PLAN_ID = "apps-rg-contract-harness-modernization-f4e8b2"
RECEIPT_JSON = REPO / "docs/reports/apps_rg/contract_harness_modernization_w2_receipt.json"

W2_TEST_PATHS = [
    "tests/_apps_contract/test_apps_rg_augmented_skills_graph_dual_source_all_sections.py",
    "tests/_apps_contract/test_apps_rg_augmented_skills_graph_source_authority.py",
    "tests/_apps_contract/test_unify_bullets_section_pipeline.py::test_canonicalize_bul_w7_unify_whitespace_source_fact_id",
]


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
    from ops_scripts.apps_rg.l6_benchmarks.receipt_links import enrich_manifest_links, path_link

    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *W2_TEST_PATHS,
        "-q",
        "--tb=no",
        "-o",
        "addopts=",
    ]
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONPATH": str(REPO)}
    completed = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=600, env=env, check=False)
    summary = (completed.stdout or "") + (completed.stderr or "")
    status = "PASS" if completed.returncode == 0 else "FAIL"
    receipt = enrich_manifest_links(
        {
            "schema": "contract_harness_modernization_wave_receipt_v1",
            "plan_id": PLAN_ID,
            "wave_id": "W2",
            "status": status,
            "git_commit": _git_commit(),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pytest_exit_code": completed.returncode,
            "w2_test_paths": W2_TEST_PATHS,
            "fixes": [
                "tests/_apps_contract/graph_authority_test_support.py: product_proof_pool_metadata + minimal_graph_proof_pool_metadata",
                "dual_source: claim_evidence_source_type may be augmented_skills_graph; proof_source graph SSOT",
                "source_authority: finalize pool metadata before proof_pool_mode_from_metadata / INPUT_AUTHORITY",
                "unify_bullets: runtime payload proof_pool_metadata includes evidence_authority block",
            ],
            "phase_gate": f"PHASE_GATE: wave=W2 status={status} gate=G-W2",
        }
    )
    RECEIPT_JSON.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": status, "receipt": str(RECEIPT_JSON.relative_to(REPO))}, indent=2))
    print(summary[-1500:])
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
