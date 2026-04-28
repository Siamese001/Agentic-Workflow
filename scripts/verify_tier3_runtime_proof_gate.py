"""Tier 3 runtime-proof gate verification entrypoint.

Orchestrates:
  1. tier_fixture_bootstrap.materialize() (deterministic JSON fixtures)
  2. python scripts/verify_tier3_enforcement_gate.py  (metadata gate)
  3. python -m pytest <Tier 3 targeted fixture files> -q
  4. agentic_core.runtime.prove_requirements.tier3_runtime_proof_gate.evaluate()

Writes:
  - artifacts/runtime/requirements_proof/tier3_runtime_proof_gate_result.json
  - artifacts/runtime/requirements_proof/tier3_runtime_proof_gate_report.md

Exits 0 only when the runtime-proof gate result is READY.

Does NOT execute replay machinery, OTEL exporters, or the proof harness.
Does NOT run any tests outside the targeted Tier 3 fixture files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.prove_requirements import (
    tier3_runtime_proof_gate,
    tier_fixture_bootstrap,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

TARGETED_TESTS = (
    "tests/runtime/test_tier3_runtime_gates_cluster_fixtures.py",
    "tests/runtime/test_tier3_remaining_subsystem_fixtures.py",
)


def _run_metadata_gate() -> str:
    proc = subprocess.run(
        [sys.executable, "scripts/verify_tier3_enforcement_gate.py"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return "READY" if proc.returncode == 0 else "BLOCKED"


def _run_targeted_tests() -> tuple[str, list[str]]:
    rels: list[str] = []
    for rel in TARGETED_TESTS:
        if (REPO_ROOT / rel).is_file():
            rels.append(rel)
    if not rels:
        return "SKIPPED", []
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *rels, "-q"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=180,
        check=False,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return ("PASSED" if proc.returncode == 0 else "FAILED", rels)


def main() -> int:
    tier_fixture_bootstrap.materialize()
    metadata_status = _run_metadata_gate()
    tests_status, tests_run = _run_targeted_tests()

    result = tier3_runtime_proof_gate.evaluate(
        metadata_gate_status=metadata_status,
        targeted_tests_status=tests_status,
        targeted_tests_run=tests_run,
    )
    result_path = tier3_runtime_proof_gate.write_result(result)
    report_path = tier3_runtime_proof_gate.write_report(result)

    print(f"Tier 3 runtime proof gate: {result['result']}")
    print(f"Metadata gate: {metadata_status}")
    print(f"Targeted tests: {tests_status}")
    print(f"Failed REQ_IDs: {result['failed_req_ids']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")

    return 0 if result["result"] == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
