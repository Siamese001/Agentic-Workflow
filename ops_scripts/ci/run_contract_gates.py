#!/usr/bin/env python3
"""
Contract Gates Runner

Single entrypoint for running all contract validation gates in CI.
Executes pytest and evidence contract checker with deterministic ordering.

All commands executed via subprocess argv arrays (shell=False).
Fails if argv0 contains pwsh/powershell.
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import DOCS_REPORTS_PLANS


def run_cmd(args, cwd=None):
    """Execute command and return (rc, stdout, stderr).

    Args:
        args: Command arguments as list
        cwd: Working directory (optional)

    Returns:
        Tuple of (return_code, stdout, stderr)

    Raises:
        ValueError: If argv0 contains pwsh/powershell
    """
    # PowerShell detection at argv level only
    argv0_lower = str(args[0]).lower()
    if "pwsh" in argv0_lower or "powershell" in argv0_lower:
        raise ValueError(f"PowerShell usage detected in command: {' '.join(args)}")

    result = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, shell=False, encoding="utf-8", errors="replace"
    )
    return result.returncode, result.stdout, result.stderr


def main():
    """Run all contract gates in deterministic order."""
    repo_root = Path(__file__).parent.parent.parent

    gates = [
        (
            [sys.executable, "-m", "pytest", "-q", "--color=no"],
            "Full Test Suite",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_evidence_contract_v2.py", "--paths", DOCS_REPORTS_PLANS],
            "Evidence Contract v2 Checker (§2)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_tooling_apps_boundary.py"],
            "Tooling/Apps Boundary Guard (§4.5)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_powershell_ban.py"],
            "PowerShell Ban (§2)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_test_integrity.py"],
            "Test Integrity: zero-assert, silent swallowers, xfail (§11/§13)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_no_unconditional_xfail.py"],
            "No Unconditional xfail in Governance Tests (§11.4)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_utility_silent_swallowers.py"],
            "Utility Silent Swallowers — critical infrastructure (§10/§11)",
        ),
        (
            [sys.executable, "ops_scripts/ci/validate_timeout_progress.py"],
            "Timeout & Progress Compliance (§9)",
        ),
        (
            [sys.executable, "ops_scripts/ci/validate_timeout_recovery.py"],
            "Timeout Recovery with ADG (§9.6)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_adg_proof_artifact_truthfulness.py"],
            "ADG Proof-Artifact Truthfulness (§15)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_adg_schema_field_names.py"],
            "ADG Schema Canonical Field Names (§16)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_skip_convergence_gate.py"],
            "Skip Convergence Gate (§17)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_policy_drift_classification.py"],
            "Policy Drift Classification (§18)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_environment_contract.py"],
            "Environment Contract (§20)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_c0_boundary.py"],
            "C0 Informational Boundary (§21)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_ci_integrity.py"],
            "CI Integrity Gates §22 (all 13 conditions)",
        ),
        (
            [sys.executable, "ops_scripts/ci/adg_grep_ban_gate.py", "--all-python"],
            "ADG Grep-Ban Gate — no grep/rg as ADG query substitute (§2.6)",
        ),
        (
            [sys.executable, "ops_scripts/ci/guardian_exemption_gate.py"],
            "Guardian Exemption Ratchet — exemption quality + count gate (§2.6)",
        ),
        (
            [sys.executable, "ops_scripts/ci/adg_mypy_ban_gate.py", "--all-python"],
            "ADG Mypy-Ban Gate — no broad mypy; use adg_type_check.py (§2.6)",
        ),
        (
            [sys.executable, "ops_scripts/ci/adg_skip_file_ratchet.py"],
            "ADG Skip-File Ratchet — skip-file directive count ceiling (§2.6)",
        ),
        (
            [sys.executable, "ops_scripts/ci/adg_pytest_ban_gate.py", "--all-python"],
            "ADG Pytest-Ban Gate — no broad pytest; use adg_test_selector.py (§2.6)",
        ),
        (
            [sys.executable, "ops_scripts/ci/adg_yaml_grep_ban_gate.py", "--all-yaml"],
            "ADG YAML Grep-Ban Gate — no grep/rg in GitHub Actions run: steps (§2.6)",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_mcp_config_sovereignty.py"],
            "MCP Config Sovereignty — filesystem allowedDirectories locked to repo root (Rule #0)",
        ),
    ]

    print("Running contract gates in deterministic order...\n")

    failed_gates = []

    for cmd, title in gates:
        print(f"[{title}]")
        print(f"$ {' '.join(cmd)}")

        try:
            rc, out, err = run_cmd(cmd, cwd=repo_root)

            # Print output
            if out:
                print(out)
            if err:
                print(f"STDERR: {err}", file=sys.stderr)

            if rc != 0:
                print(f"EXIT CODE: {rc}")
                failed_gates.append(title)

            print()  # Blank line between gates

        except ValueError as e:
            print(f"ERROR: {e}")
            failed_gates.append(title)
            print()

    # Summary
    if failed_gates:
        print(f"ERROR: {len(failed_gates)} contract gate(s) failed:")
        for gate in failed_gates:
            print(f"  - {gate}")
        return 1
    else:
        print("OK: All contract gates passed")
        return 0


if __name__ == "__main__":
    sys.exit(main())
