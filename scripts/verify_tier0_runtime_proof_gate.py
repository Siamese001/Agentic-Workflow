"""Tier 0 runtime-proof gate verification entrypoint.

Orchestrates:
  1. python scripts/verify_tier0_enforcement_gate.py  (metadata gate)
  2. python -m pytest tests/runtime/test_tier0_gate_schema_invariants.py
                       tests/runtime/test_tier0_l6_firewall_replay.py
  3. agentic_core.runtime.prove_requirements.tier0_runtime_proof_gate.evaluate()

Writes:
  - artifacts/runtime/requirements_proof/tier0_runtime_proof_gate_result.json
  - artifacts/runtime/requirements_proof/tier0_runtime_proof_gate_report.md

Exits non-zero if the runtime-proof gate is not READY.

Does NOT execute replay machinery, OTEL exporters, or the proof harness.
Does NOT run any tests outside the two targeted files.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.runtime.prove_requirements import (
    tier0_runtime_proof_gate,
    tier_fixture_bootstrap,
)

REPO_ROOT = Path(__file__).resolve().parents[1]

TARGETED_TESTS = (
    "tests/runtime/test_tier0_gate_schema_invariants.py",
    "tests/runtime/test_tier0_l6_firewall_replay.py",
)


def _run_metadata_gate() -> str:
    proc = subprocess.run(
        [sys.executable, "scripts/verify_tier0_enforcement_gate.py"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return "READY" if proc.returncode == 0 else "BLOCKED"


def _run_targeted_tests() -> str:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *TARGETED_TESTS, "-q"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    sys.stdout.write(proc.stdout)
    sys.stderr.write(proc.stderr)
    return "PASSED" if proc.returncode == 0 else "FAILED"


def main() -> int:
    tier_fixture_bootstrap.materialize()
    metadata_status = _run_metadata_gate()
    tests_status = _run_targeted_tests()

    result = tier0_runtime_proof_gate.evaluate(
        metadata_gate_status=metadata_status,
        targeted_tests_status=tests_status,
        targeted_tests_run=TARGETED_TESTS,
    )
    result_path = tier0_runtime_proof_gate.write_result(result)
    report_path = tier0_runtime_proof_gate.write_report(result)

    print(f"Tier 0 runtime proof gate: {result['result']}")
    print(f"Metadata gate: {metadata_status}")
    print(f"Targeted tests: {tests_status}")
    print(f"Failed REQ_IDs: {result['failed_req_ids']}")
    print(f"Result file: {result_path}")
    print(f"Report file: {report_path}")

    return 0 if result["result"] == "READY" else 1


if __name__ == "__main__":
    sys.exit(main())
