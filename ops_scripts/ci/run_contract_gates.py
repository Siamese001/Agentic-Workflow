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
            [sys.executable, "ops_scripts/ci/check_evidence_contract_v2.py", "--paths", "docs/reports/plans"],
            "Evidence Contract v2 Checker",
        ),
        (
            [sys.executable, "ops_scripts/ci/check_tooling_apps_boundary.py"],
            "Tooling/Apps Boundary Guard",
        ),
        (
            [sys.executable, "ops_scripts/ci/validate_timeout_progress.py"],
            "Timeout & Progress Compliance (§9)",
        ),
        (
            [sys.executable, "ops_scripts/ci/validate_timeout_recovery.py"],
            "Timeout Recovery with ADG (§9.6)",
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
