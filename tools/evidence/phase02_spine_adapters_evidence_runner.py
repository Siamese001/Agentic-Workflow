#!/usr/bin/env python3
"""Phase 2 Spine Adapters Evidence Runner.

Captures verbatim outputs for Phase 2 completion evidence.
All commands executed via subprocess with argv arrays (shell=False).
Fails immediately if any stdout/stderr contains PowerShell references.
"""

import subprocess
import sys
from pathlib import Path


def run_cmd(args, cwd=None):
    """Execute command and return (rc, stdout, stderr)."""
    r = subprocess.run(
        args, cwd=cwd, capture_output=True, text=True, shell=False, encoding="utf-8", errors="replace"
    )

    # Check for PowerShell usage
    output = (r.stdout + r.stderr).lower()
    if "pwsh" in output or "powershell" in output:
        print(f"ERROR: PowerShell usage detected in command: {' '.join(args)}")
        print(f"Output: {output}")
        sys.exit(1)

    return r.returncode, r.stdout, r.stderr


def main():
    """Run all Phase 2 evidence commands."""
    print("=== Phase 2 Spine Adapters Evidence Runner ===")

    # Change to repo root
    repo_root = Path(__file__).parent.parent.parent
    print(f"Repo root: {repo_root}")

    evidence = []

    # 1. LIC unit tests
    print("\n1. Running LIC unit tests...")
    rc, out, err = run_cmd(
        [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_lic_spine_adapter.py"],
        cwd=repo_root,
    )
    evidence.append("Command: python -m pytest -q tests/unit_min_deps/test_apps_lic_spine_adapter.py\n")
    evidence.append(f"Exit code: {rc}\n")
    evidence.append(f"Output:\n{out}\n")
    if err:
        evidence.append(f"Error:\n{err}\n")
    if rc != 0:
        print("FAILED: LIC tests")
        sys.exit(1)

    # 2. RG unit tests
    print("\n2. Running RG unit tests...")
    rc, out, err = run_cmd(
        [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_rg_spine_adapter.py"],
        cwd=repo_root,
    )
    evidence.append("Command: python -m pytest -q tests/unit_min_deps/test_apps_rg_spine_adapter.py\n")
    evidence.append(f"Exit code: {rc}\n")
    evidence.append(f"Output:\n{out}\n")
    if err:
        evidence.append(f"Error:\n{err}\n")
    if rc != 0:
        print("FAILED: RG tests")
        sys.exit(1)

    # 3. Full test suite
    print("\n3. Running full test suite...")
    rc, out, err = run_cmd([sys.executable, "-m", "pytest", "-q"], cwd=repo_root)
    evidence.append("Command: python -m pytest -q\n")
    evidence.append(f"Exit code: {rc}\n")
    evidence.append(f"Output:\n{out}\n")
    if err:
        evidence.append(f"Error:\n{err}\n")
    if rc != 0:
        print("FAILED: Full test suite")
        sys.exit(1)

    # 4. Check spine bypass
    print("\n4. Checking spine bypass...")
    rc, out, err = run_cmd([sys.executable, "ops_scripts/ci/check_spine_bypass.py"], cwd=repo_root)
    evidence.append("Command: python ops_scripts/ci/check_spine_bypass.py\n")
    evidence.append(f"Exit code: {rc}\n")
    evidence.append(f"Output:\n{out}\n")
    if err:
        evidence.append(f"Error:\n{err}\n")
    if rc != 0:
        print("FAILED: Spine bypass check")
        sys.exit(1)

    # 5. Git diff stat
    print("\n5. Getting git diff stat...")
    rc, out, err = run_cmd(["git", "diff", "--stat"], cwd=repo_root)
    evidence.append("Command: git diff --stat\n")
    evidence.append(f"Exit code: {rc}\n")
    evidence.append(f"Output:\n{out}\n")
    if err:
        evidence.append(f"Error:\n{err}\n")

    # 6. Git full diff
    print("\n6. Getting git full diff...")
    rc, out, err = run_cmd(["git", "diff"], cwd=repo_root)
    evidence.append("Command: git diff\n")
    evidence.append(f"Exit code: {rc}\n")
    evidence.append(f"Output:\n{out}\n")
    if err:
        evidence.append(f"Error:\n{err}\n")

    # Write evidence to file
    evidence_file = repo_root / "docs" / "reports" / "plans" / "phase_02_spine_adapters_evidence.txt"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    evidence_file.write_text("".join(evidence), encoding="utf-8")
    print(f"\nEvidence written to: {evidence_file}")

    print("\n=== All Phase 2 evidence captured successfully ===")


if __name__ == "__main__":
    main()
