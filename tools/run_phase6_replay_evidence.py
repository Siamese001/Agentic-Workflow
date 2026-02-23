#!/usr/bin/env python3
"""
Phase 6 Deterministic Replay Engine Evidence Runner

Captures deterministic command outputs for Phase 6 closure evidence.
Uses subprocess.run with shell=False and validates no PowerShell usage.
"""

import subprocess
import sys
from pathlib import Path


def run_cmd(argv, capture_output=True, text=True, check=False):
    """Run command with subprocess.run, ensuring no PowerShell usage."""
    if len(argv) > 0 and ("pwsh" in argv[0] or "powershell" in argv[0]):
        sys.exit("FAIL: PowerShell detected in argv0: " + argv[0])

    result = subprocess.run(argv, shell=False, capture_output=capture_output, text=text, check=check)
    return result


def main():
    """Execute Phase 6 evidence collection."""
    evidence_lines = []

    # Header
    evidence_lines.append("# Phase 6 Deterministic Replay Engine Evidence")
    evidence_lines.append("")

    # Capture CODE_COMMIT
    result = run_cmd(["git", "rev-parse", "HEAD"])
    code_commit = result.stdout.strip()
    evidence_lines.append("## CODE_COMMIT")
    evidence_lines.append(code_commit)
    evidence_lines.append("")

    # Capture Python version
    result = run_cmd(["python", "-V"])
    evidence_lines.append("## PYTHON_VERSION")
    evidence_lines.append(result.stdout.strip())
    evidence_lines.append("")

    # Run tests twice for determinism
    for run_num in [1, 2]:
        evidence_lines.append(f"## TEST_RUN_{run_num}")
        evidence_lines.append("")

        # Test: deterministic replay tests
        evidence_lines.append('### pytest -q tests/unit_min_deps/ -k "deterministic_replay"')
        result = run_cmd(
            ["python", "-m", "pytest", "-q", "tests/unit_min_deps/", "-k", "deterministic_replay"]
        )
        evidence_lines.append(f"EXIT CODE: {result.returncode}")
        evidence_lines.append("STDOUT:")
        evidence_lines.append(result.stdout)
        if result.stderr:
            evidence_lines.append("STDERR:")
            evidence_lines.append(result.stderr)
        evidence_lines.append("")

    # Run execute_ssot replay tool
    evidence_lines.append("## EXECUTE_SSOT_REPLAY_TEST")
    evidence_lines.append("")

    evidence_lines.append("### python tools/run_replay_execute_ssot_plan.py")
    result = run_cmd(["python", "tools/run_replay_execute_ssot_plan.py"])
    evidence_lines.append(f"EXIT CODE: {result.returncode}")
    evidence_lines.append("STDOUT:")
    evidence_lines.append(result.stdout)
    if result.stderr:
        evidence_lines.append("STDERR:")
        evidence_lines.append(result.stderr)
    evidence_lines.append("")

    # Scope/hygiene verification
    evidence_lines.append("## SCOPE_VERIFICATION")
    evidence_lines.append("")

    # git diff --name-only
    evidence_lines.append("### git diff --name-only")
    result = run_cmd(["git", "diff", "--name-only"])
    evidence_lines.append(f"EXIT CODE: {result.returncode}")
    evidence_lines.append("STDOUT:")
    evidence_lines.append(result.stdout if result.stdout else "(empty)")
    evidence_lines.append("")

    # git status --porcelain
    evidence_lines.append("### git status --porcelain")
    result = run_cmd(["git", "status", "--porcelain"])
    evidence_lines.append(f"EXIT CODE: {result.returncode}")
    evidence_lines.append("STDOUT:")
    evidence_lines.append(result.stdout if result.stdout else "(empty)")
    evidence_lines.append("")

    # Verify replay record was created
    evidence_lines.append("### REPLAY_RECORD_VERIFICATION")
    record_path = Path("docs/replay/execute_ssot_replay_record.json")
    if record_path.exists():
        evidence_lines.append(f"REPLAY_RECORD_EXISTS: {record_path}")
        evidence_lines.append(f"REPLAY_RECORD_SIZE: {record_path.stat().st_size} bytes")
    else:
        evidence_lines.append(f"REPLAY_RECORD_NOT_FOUND: {record_path}")
    evidence_lines.append("")

    # Write evidence file
    evidence_path = Path("docs/evidence/phase_deterministic_replay_engine_phase6.md")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("\n".join(evidence_lines), encoding="utf-8")

    print(f"Evidence written to: {evidence_path.absolute()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
