"""Tier 6 runtime/static proof gate verification entrypoint.

Orchestrates:
  1. tier_fixture_bootstrap.materialize() (deterministic JSON fixtures)
  2. python scripts/verify_tier6_enforcement_gate.py  (metadata gate)
  3. python -m pytest tests/runtime/test_tier6_final_rows_fixtures.py -q -p no:randomly
  4. agentic_core.runtime.prove_requirements.tier6_runtime_proof_gate.evaluate()

Writes:
  - artifacts/runtime/requirements_proof/tier6_runtime_proof_gate_result.json
  - artifacts/runtime/requirements_proof/tier6_runtime_proof_gate_report.md

Exits 0 only when the runtime-proof gate result is READY.

Does NOT execute replay machinery, OTEL exporters, or the proof harness.
Does NOT run any tests outside the targeted Tier 6 fixture file.
Does NOT treat the 15 NON_BLOCKING_REFERENCE rows as runtime-proof rows --
those are validated through the reference-only policy contract instead.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.prove_requirements import (
    tier6_runtime_proof_gate,
    tier_fixture_bootstrap,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

TARGETED_TESTS = ("tests/runtime/test_tier6_final_rows_fixtures.py",)


def _run_metadata_gate() -> str:
    proc = subprocess.run(
        [sys.executable, "scripts/verify_tier6_enforcement_gate.py"],
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
        [sys.executable, "-m", "pytest", *rels, "-q", "-p", "no:randomly"],
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

    result = tier6_runtime_proof_gate.evaluate(
        metadata_gate_status=metadata_status,
        targeted_tests_status=tests_status,
        targeted_tests_run=tests_run,
    )
    result_path = tier6_runtime_proof_gate.write_result(result)
    report_path = tier6_runtime_proof_gate.write_report(result)

    print(f"Tier 6 runtime proof gate: {result['result']}")
    print(f"Metadata gate: {metadata_status}")
    print(f"Targeted tests: {tests_status}")
    print(f"MUST rows checked: {len(result['must_rows_checked'])}")
    print(f"REFERENCE-only rows checked: {len(result['reference_only_rows_checked'])}")
    print(f"Failed REQ_IDs: {result['failed_req_ids']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")

    return 0 if result["result"] == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
