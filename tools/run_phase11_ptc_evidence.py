#!/usr/bin/env python3
"""
Phase 11 Programmatic Tool Calling Evidence Runner

Captures deterministic command outputs for Phase 11 closure evidence.
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
    """Execute Phase 11 evidence collection."""
    evidence_lines = []

    # Header
    evidence_lines.append("# Phase 11 Programmatic Tool Calling Evidence")
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

    # Run static invariants
    evidence_lines.append("## STATIC_INVARIANTS")
    evidence_lines.append("")

    evidence_lines.append("### python tools/run_static_invariants.py")
    result = run_cmd(["python", "tools/run_static_invariants.py"])
    evidence_lines.append(f"EXIT CODE: {result.returncode}")
    evidence_lines.append("STDOUT:")
    evidence_lines.append(result.stdout)
    if result.stderr:
        evidence_lines.append("STDERR:")
        evidence_lines.append(result.stderr)
    evidence_lines.append("")

    # Run PTC tests twice for determinism
    for run_num in [1, 2]:
        evidence_lines.append(f"## PTC_TEST_RUN_{run_num}")
        evidence_lines.append("")

        evidence_lines.append('### pytest -q tests/unit_min_deps/ -k "ptc"')
        result = run_cmd(["python", "-m", "pytest", "-q", "tests/unit_min_deps/", "-k", "ptc"])
        evidence_lines.append(f"EXIT CODE: {result.returncode}")
        evidence_lines.append("STDOUT:")
        evidence_lines.append(result.stdout)
        if result.stderr:
            evidence_lines.append("STDERR:")
            evidence_lines.append(result.stderr)
        evidence_lines.append("")

    # Execute_ssot plan with PTC
    evidence_lines.append("## EXECUTE_SSOT_PTC_PLAN")
    evidence_lines.append("")

    evidence_lines.append(
        "### python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --legacy --plan --ptc-plan"
    )
    result = run_cmd(
        [
            "python",
            "-m",
            "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
            "--legacy",
            "--plan",
            "--ptc-plan",
        ]
    )
    evidence_lines.append(f"EXIT CODE: {result.returncode}")
    evidence_lines.append("STDOUT:")
    evidence_lines.append(result.stdout)
    if result.stderr:
        evidence_lines.append("STDERR:")
        evidence_lines.append(result.stderr)
    evidence_lines.append("")

    # List stored tool call artifacts
    evidence_lines.append("## STORED_TOOL_CALL_ARTIFACTS")
    evidence_lines.append("")

    try:
        # List tool call artifacts from PTC store
        from agentic_core.L3_orchestration.ptc.tool_call_store import get_tool_call_store

        store = get_tool_call_store()
        calls = store.list_calls(limit=100)

        evidence_lines.append(f"Found {len(calls)} tool call artifacts:")
        for call in calls:
            tool_id = call["call"]["tool_id"]
            call_id = call["call"]["call_id"]
            evidence_lines.append(f"  - {tool_id}/{call_id}")

    except Exception as e:  # guardian: allow-silent-swallower
        evidence_lines.append(f"Error listing artifacts: {e}")

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
    evidence_path = Path("docs/evidence/phase_ptc_integration_layer_phase11.md")
    evidence_path.parent.mkdir(parents=True, exist_ok=True)
    evidence_path.write_text("\n".join(evidence_lines), encoding="utf-8")

    print(f"Evidence written to: {evidence_path.absolute()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
