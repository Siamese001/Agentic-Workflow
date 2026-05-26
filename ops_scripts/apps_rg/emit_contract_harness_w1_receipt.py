#!/usr/bin/env python3
"""W1: verify B1 harness migration — no ``--provider mock`` exit-0 expectations."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

PLAN_ID = "apps-rg-contract-harness-modernization-f4e8b2"
REPORTS = REPO / "docs" / "reports" / "apps_rg"
RECEIPT_JSON = REPORTS / "contract_harness_modernization_w1_receipt.json"
JUNIT_PATH = REPORTS / "contract_harness_w1_junit.xml"

B1_MODULES = [
    "tests/_apps_contract/test_ibm_bullets_runtime_slice.py",
    "tests/_apps_contract/test_apps_rg_augmented_skills_graph_all_sections_runtime_receipts.py",
    "tests/_apps_contract/test_apps_rg_section_input_usage_ledgers.py",
    "tests/_apps_contract/test_unify_narrative_section_pipeline.py",
    "tests/_apps_contract/test_unify_narrative_l6_shadow_learning.py",
    "tests/_apps_contract/test_unify_narrative_runtime_slice.py",
]

MOCK_PROVIDER_SUBPROCESS_RE = re.compile(
    r"""['"]--provider['"]\s*,\s*['"]mock['"]|['"]mock['"]\s*,\s*['"]--provider['"]"""
)


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


def _scan_mock_provider_usage() -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []
    for rel in B1_MODULES:
        path = REPO / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if MOCK_PROVIDER_SUBPROCESS_RE.search(text):
            violations.append({"file": rel, "reason": "subprocess argv uses --provider mock"})
        if '"--provider", "mock"' in text or "'--provider', 'mock'" in text:
            violations.append({"file": rel, "reason": "literal --provider mock in test module"})
    return violations


def _run_b1_pytest() -> tuple[int, str, dict[str, int]]:
    REPORTS.mkdir(parents=True, exist_ok=True)
    cmd = [
        sys.executable,
        "-m",
        "pytest",
        *B1_MODULES,
        "-q",
        "--tb=no",
        f"--junitxml={JUNIT_PATH}",
        "-o",
        "addopts=",
    ]
    env = {**dict(__import__("os").environ), "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1", "PYTHONPATH": str(REPO)}
    completed = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=1800,
        env=env,
        check=False,
    )
    summary = (completed.stdout or "") + (completed.stderr or "")
    counts = {"failed": 0, "error": 0, "passed": 0, "skipped": 0}
    m = re.search(r"(\d+) failed", summary)
    if m:
        counts["failed"] = int(m.group(1))
    m = re.search(r"(\d+) error", summary)
    if m:
        counts["error"] = int(m.group(1))
    m = re.search(r"(\d+) passed", summary)
    if m:
        counts["passed"] = int(m.group(1))
    m = re.search(r"(\d+) skipped", summary)
    if m:
        counts["skipped"] = int(m.group(1))
    tail = summary[-4000:] if len(summary) > 4000 else summary
    return completed.returncode, tail, counts


def main() -> int:
    from ops_scripts.apps_rg.l6_benchmarks.receipt_links import enrich_manifest_links, path_link

    violations = _scan_mock_provider_usage()
    code, pytest_tail, counts = _run_b1_pytest()
    commit = _git_commit()
    pytest_green = code == 0 and counts.get("failed", 0) == 0 and counts.get("error", 0) == 0
    no_mock_argv = len(violations) == 0
    status = "PASS" if pytest_green and no_mock_argv else "FAIL"
    if pytest_green and not no_mock_argv:
        status = "PARTIAL"

    receipt = enrich_manifest_links(
        {
            "schema": "contract_harness_modernization_wave_receipt_v1",
            "plan_id": PLAN_ID,
            "wave_id": "W1",
            "status": status,
            "git_commit": commit,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "b1_modules": B1_MODULES,
            "mock_provider_violations": violations,
            "pytest_exit_code": code,
            "counts": counts,
            "fixes": [
                "apps_rg/runtime/c0/c02_fact_vector_ingest.py: import apply_apps_rg_embedding_env_guards in maybe_upsert_c02_fact_vectors",
                "tests/_apps_contract: B1 modules use live qwen_vllm via run_lane_cli + pytest.mark.skipif(not qwen_live_available())",
                "tests/_apps_contract/lane_cli_common.py: removed offline stub harness; contract_env strips stub/mock-judge env",
            ],
            "junit_path": "docs/reports/apps_rg/contract_harness_w1_junit.xml",
            "phase_gate": f"PHASE_GATE: wave=W1 status={status} gate=G-W1",
        }
    )
    receipt["junit_path_link"] = path_link(receipt["junit_path"])
    RECEIPT_JSON.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "status": status,
                "mock_violations": len(violations),
                "pytest_exit_code": code,
                "counts": counts,
                "receipt": str(RECEIPT_JSON.relative_to(REPO)),
            },
            indent=2,
        )
    )
    print("\n--- pytest tail ---\n", pytest_tail[-1200:], sep="")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
