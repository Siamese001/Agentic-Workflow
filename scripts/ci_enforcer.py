#!/usr/bin/env python3
"""
ci_enforcer.py
Runs all agentic enforcement validators in a single orchestrated pass.

Validators expected:
    manifest_validator.py
    ast_purity_scanner.py
    contract_registry_validator.py
    test_matrix_validator.py
    golden_trace_auditor.py

Behavior:
    - Runs validators sequentially.
    - Logs stdout/stderr for each.
    - Aggregates pass/fail statuses.
    - Produces a final compliance report.
    - Exits 0 if ALL pass, else exits 1.
"""

import subprocess
import os
import sys
from datetime import datetime

# ============================================================
# CONFIG
# ============================================================

REPO_ROOT = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11"

VALIDATOR_SCRIPTS = [
    "manifest_validator.py",
    "ast_purity_scanner.py",
    "contract_registry_validator.py",
    "test_matrix_validator.py",
    "golden_trace_auditor.py",
]

FAIL_FAST = False  # If True, stops on first failure; else continues and aggregates

# ============================================================
# UTILITIES
# ============================================================

def run_script(path):
    """
    Run a Python validator script and return:
        (passed: bool, stdout: str, stderr: str, exit_code: int)
    """

    if not os.path.exists(path):
        return False, "", f"SCRIPT NOT FOUND: {path}", 999

    proc = subprocess.Popen(
        [sys.executable, path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=os.path.dirname(path) or REPO_ROOT,
        text=True
    )

    out, err = proc.communicate()
    passed = proc.returncode == 0

    return passed, out.strip(), err.strip(), proc.returncode


def banner(title):
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80 + "\n")


# ============================================================
# MAIN ORCHESTRATION
# ============================================================

def main():
    banner("AGENTIC WORKFLOW – FULL CI ENFORCER INITIATED")
    print(f"Repo: {REPO_ROOT}")
    print(f"Timestamp: {datetime.now()}")
    print(f"Fail-Fast Mode: {FAIL_FAST}")
    print("\nValidators queued:")
    for v in VALIDATOR_SCRIPTS:
        print(f"  - {v}")

    results = []
    print("\nRunning validators...\n")

    for script in VALIDATOR_SCRIPTS:
        full_path = os.path.join(REPO_ROOT, script)
        banner(f"Running: {script}")

        passed, out, err, code = run_script(full_path)

        print(f"[STDOUT]\n{out}\n")
        if err:
            print(f"[STDERR]\n{err}\n")

        results.append((script, passed, code))

        if not passed and FAIL_FAST:
            banner("CI ENFORCER STOPPED (FAIL-FAST MODE ENABLED)")
            print(f"❌ {script} failed with exit code {code}")
            sys.exit(1)

    # Final summary
    banner("CI ENFORCER – FINAL SUMMARY")

    all_passed = all(p for (_, p, _) in results)

    for script, passed, code in results:
        status = "PASS" if passed else f"FAIL (exit={code})"
        print(f"{script:<35} → {status}")

    if all_passed:
        banner("ALL VALIDATIONS PASSED")
        print("✔ Full structural, AST, contract, coverage, and behavioral integrity confirmed.")
        sys.exit(0)
    else:
        banner("VALIDATION FAILURES DETECTED")
        print("❌ One or more validators failed.")
        print("Fix issues above before merge or deployment.")
        sys.exit(1)


if __name__ == "__main__":
    main()
