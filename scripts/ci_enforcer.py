#!/usr/bin/env python3
"""
ci_enforcer.py
Runs all enforcement validators in one pass and aggregates results.

Validators:
- manifest_validator.py
- ast_purity_scanner.py
- contract_registry_validator.py
- test_matrix_validator.py
- golden_trace_auditor.py
"""

import os
import sys
import subprocess
from datetime import datetime

REPO_ROOT = (
    r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines"
    r"\Resume Gen\Git\Agentic_Workflow-10_11"
)

VALIDATORS = [
    "manifest_validator.py",
    "ast_purity_scanner.py",
    "contract_registry_validator.py",
    "test_matrix_validator.py",
    "golden_trace_auditor.py",
]

FAIL_FAST = False  # set True to stop on first failure


def run_script(script_name: str):
    full_path = os.path.join(REPO_ROOT, script_name)
    if not os.path.exists(full_path):
        return 999, "", f"[CI] SCRIPT NOT FOUND: {full_path}"

    proc = subprocess.Popen(
        [sys.executable, full_path],
        cwd=REPO_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate()
    return proc.returncode, out, err


def main():
    print("=" * 80)
    print("AGENTIC WORKFLOW – CI ENFORCER")
    print("Repo:", REPO_ROOT)
    print("Timestamp:", datetime.now())
    print("Fail Fast:", FAIL_FAST)
    print("=" * 80, "\n")

    results = []
    all_pass = True

    for script in VALIDATORS:
        print(f"\n--- Running {script} ---")
        code, out, err = run_script(script)
        if out.strip():
            print(out)
        if err.strip():
            print("[stderr]")
            print(err)

        results.append((script, code))
        if code != 0:
            all_pass = False
            if FAIL_FAST:
                print(f"[CI] {script} failed; stopping (fail-fast enabled).")
                break

    print("\n=== CI ENFORCER SUMMARY ===")
    for script, code in results:
        status = "PASS" if code == 0 else f"FAIL ({code})"
        print(f"{script:<30} {status}")

    if all_pass:
        print("\nALL VALIDATIONS PASSED.")
        sys.exit(0)
    else:
        print("\nVALIDATION FAILURES DETECTED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
