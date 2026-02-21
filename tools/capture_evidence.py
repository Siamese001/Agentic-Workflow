#!/usr/bin/env python3
"""
Evidence capture utility for execute_ssot mutation fence implementation.

Runs commands via subprocess with argv arrays (no shell), captures stdout/stderr/exit code,
and aborts if output contains PowerShell indicators.
"""

import subprocess
import sys
from pathlib import Path


def capture_command(argv: list[str], evidence_file: Path) -> int:
    """
    Execute command and append results to evidence file.

    Args:
        argv: Command arguments as list
        evidence_file: Path to evidence markdown file

    Returns:
        Exit code from command

    Raises:
        RuntimeError: If PowerShell detected in output
    """
    # Run command with no shell
    result = subprocess.run(
        argv,
        capture_output=True,
        text=True,
        shell=False,
    )

    # Check for PowerShell indicators
    combined_output = result.stdout + result.stderr
    if "pwsh" in combined_output.lower() or "powershell" in combined_output.lower():
        raise RuntimeError(
            f"ABORT: PowerShell detected in command output.\n"
            f"Command: {' '.join(argv)}\n"
            f"Output snippet: {combined_output[:200]}"
        )

    # Append to evidence file
    with open(evidence_file, "a", encoding="utf-8") as f:
        f.write(f"\n## Command: {' '.join(argv)}\n\n")
        f.write(f"**Exit Code:** {result.returncode}\n\n")
        if result.stdout:
            f.write("**STDOUT:**\n```\n")
            f.write(result.stdout)
            f.write("\n```\n\n")
        if result.stderr:
            f.write("**STDERR:**\n```\n")
            f.write(result.stderr)
            f.write("\n```\n\n")

    return result.returncode


def main():
    """Main entry point for evidence capture."""
    if len(sys.argv) < 4 or sys.argv[1] != "--":
        print("Usage: python capture_evidence.py -- <command> [args...]", file=sys.stderr)
        return 1

    # Evidence file is expected to be set via environment or hardcoded
    # For now, we'll use a default path
    evidence_file = Path("docs/evidence/execute_ssot_exhaustive_audit_wave1.md")

    # Extract command argv (everything after --)
    command_argv = sys.argv[2:]

    try:
        exit_code = capture_command(command_argv, evidence_file)
        return exit_code
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
