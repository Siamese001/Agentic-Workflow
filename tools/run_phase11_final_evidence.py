#!/usr/bin/env python3
"""
Phase 11 Final Evidence Runner

Executes all acceptance criteria and generates deterministic evidence.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run command and return exit code, stdout, stderr."""
    # Enforce no PowerShell
    if cmd[0].lower() in ("pwsh", "powershell", "pwsh.exe", "powershell.exe"):
        raise ValueError(f"FORBIDDEN: PowerShell argv0 detected: {cmd[0]}")

    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        shell=False,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode, result.stdout, result.stderr


def main():
    repo_root = Path.cwd()
    evidence_lines = []

    # Header
    evidence_lines.append("# Phase 11: Baseline-Aware Invariants & Deterministic PTC Storage")
    evidence_lines.append("")
    evidence_lines.append("## Scope")
    evidence_lines.append("- Semantic PowerShell ban (AST callsite only, no string literals)")
    evidence_lines.append("- Baseline category gating (skip unseeded categories)")
    evidence_lines.append("- Deterministic tool-call storage outside repo by default")
    evidence_lines.append("")

    # Get current commit
    exit_code, stdout, stderr = run_command(["git", "rev-parse", "HEAD"], repo_root)
    code_commit = stdout.strip() if exit_code == 0 else "unknown"

    evidence_lines.append("## CODE_COMMIT")
    evidence_lines.append(code_commit)
    evidence_lines.append("")
    evidence_lines.append("## EVIDENCE_COMMIT")
    evidence_lines.append("PENDING")
    evidence_lines.append("")

    # FILES_CHANGED_CODE
    exit_code, stdout, stderr = run_command(
        ["git", "show", "--name-only", "--pretty=format:", code_commit], repo_root
    )
    evidence_lines.append("## FILES_CHANGED_CODE")
    evidence_lines.append(stdout.strip())
    evidence_lines.append("")

    # Run static invariants
    evidence_lines.append("## Static Invariants Check")
    exit_code, stdout, stderr = run_command([sys.executable, "tools/run_static_invariants.py"], repo_root)
    evidence_lines.append("$ python tools/run_static_invariants.py")
    evidence_lines.append(stdout)
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("")

    # Run PTC tests
    evidence_lines.append("## PTC Tests (Run 1)")
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/", "-k", "ptc"], repo_root
    )
    evidence_lines.append("$ pytest -q tests/unit_min_deps/ -k ptc")
    evidence_lines.append(stdout)
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("")

    # Run PTC tests again for determinism
    evidence_lines.append("## PTC Tests (Run 2 - Determinism Check)")
    exit_code, stdout, stderr = run_command(
        [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/", "-k", "ptc"], repo_root
    )
    evidence_lines.append("$ pytest -q tests/unit_min_deps/ -k ptc")
    evidence_lines.append(stdout)
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("")

    # Run execute_ssot plan mode
    evidence_lines.append("## Execute SSOT Plan Mode")
    exit_code, stdout, stderr = run_command(
        [
            sys.executable,
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--ptc-plan",
        ],
        repo_root,
    )
    evidence_lines.append(
        "$ python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan --ptc-plan"
    )
    evidence_lines.append(stdout)
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("")

    # Check git status
    evidence_lines.append("## Git Status Check")
    exit_code, stdout, stderr = run_command(["git", "status", "--porcelain"], repo_root)
    evidence_lines.append("$ git status --porcelain")
    evidence_lines.append(stdout if stdout else "(clean)")
    if exit_code != 0:
        evidence_lines.append(f"EXIT CODE: {exit_code}")
    evidence_lines.append("")

    # Write evidence
    evidence_file = repo_root / "docs" / "evidence" / "phase11_final_acceptance.md"
    evidence_file.write_text("\n".join(evidence_lines), encoding="utf-8")

    print(f"Evidence written to: {evidence_file}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
