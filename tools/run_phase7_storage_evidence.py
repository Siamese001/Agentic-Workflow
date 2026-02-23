#!/usr/bin/env python3
"""
Phase 7 Persistent Storage Layer Evidence Runner

Captures deterministic command outputs for Phase 7 closure evidence.
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
    """Execute Phase 7 evidence collection."""
    evidence_lines = []

    # Header
    evidence_lines.append("# Phase 7 Persistent Storage Layer Evidence")
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

        # Test: storage tests
        evidence_lines.append(
            '### pytest -q tests/unit_min_deps/ -k "persistent_store or filesystem_store or replay_storage"'
        )
        result = run_cmd(
            [
                "python",
                "-m",
                "pytest",
                "-q",
                "tests/unit_min_deps/",
                "-k",
                "persistent_store or filesystem_store or replay_storage",
            ]
        )
        evidence_lines.append(f"EXIT CODE: {result.returncode}")
        evidence_lines.append("STDOUT:")
        evidence_lines.append(result.stdout)
        if result.stderr:
            evidence_lines.append("STDERR:")
            evidence_lines.append(result.stderr)
        evidence_lines.append("")

    # Run replay tool to show artifact storage
    evidence_lines.append("## REPLAY_STORAGE_TEST")
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

    # Verify stored artifacts exist
    evidence_lines.append("### STORED_ARTIFACTS_VERIFICATION")
    store_root = Path("docs/store")
    if store_root.exists():
        evidence_lines.append("STORE_ROOT_EXISTS: docs/store")

        # List stored artifacts
        replay_record_dir = store_root / "replay_record" / "execute_ssot_plan"
        if replay_record_dir.exists():
            versions = list(replay_record_dir.glob("v*.json"))
            evidence_lines.append(f"REPLAY_RECORD_VERSIONS: {len(versions)}")
            for v in sorted(versions, key=lambda p: p.name):
                evidence_lines.append(f"  - {v.name}")

        replay_summary_dir = store_root / "replay_summary" / "execute_ssot_plan"
        if replay_summary_dir.exists():
            versions = list(replay_summary_dir.glob("v*.json"))
            evidence_lines.append(f"REPLAY_SUMMARY_VERSIONS: {len(versions)}")
            for v in sorted(versions, key=lambda p: p.name):
                evidence_lines.append(f"  - {v.name}")
    else:
        evidence_lines.append("STORE_ROOT_NOT_FOUND: docs/store")
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

    # Write evidence file
    evidence_path = Path("docs/evidence/phase_persistent_storage_layer_phase7.md")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("\n".join(evidence_lines), encoding="utf-8")

    print(f"Evidence written to: {evidence_path.absolute()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
