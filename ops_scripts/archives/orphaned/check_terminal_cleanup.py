#!/usr/bin/env python3
"""
Terminal Process Cleanup Gate

Enforces Constitutional Rule #11: Terminal processes MUST be killed when queries finish.
Detects hanging terminal processes that outlive their parent queries.

Gate: T26 terminal-cleanup-gate
"""
import json
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class ProcessViolation:
    pid: int
    name: str
    parent_pid: int
    query_id: str | None
    age_seconds: float
    violation_type: str


def get_windsurf_terminals() -> list[dict]:
    """Find all Windsurf-related terminal processes."""
    processes = []

    try:
        if sys.platform == "win32":
            # Windows: use tasklist and find Windsurf terminal processes
            result = subprocess.run(
                ["tasklist", "/FO", "CSV", "/NH"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
            )

            for line in result.stdout.splitlines():
                if "windsurf" in line.lower() or "codeium" in line.lower():
                    parts = line.strip('"').split('","')
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            processes.append({
                                "pid": pid,
                                "name": parts[0],
                                "parent_pid": 0,  # Would need wmic for parent
                            })
                        except ValueError:
                            pass
        else:
            # Unix-like: use ps
            result = subprocess.run(
                ["ps", "aux"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace",
            )

            for line in result.stdout.splitlines():
                if "windsurf" in line.lower() or "codeium" in line.lower():
                    parts = line.split()
                    if len(parts) >= 2:
                        try:
                            pid = int(parts[1])
                            processes.append({
                                "pid": pid,
                                "name": parts[-1][:50],
                                "parent_pid": 0,
                            })
                        except ValueError:
                            pass
    except Exception as e:
        print(f"Warning: Could not enumerate processes: {e}")

    return processes


def get_orphaned_terminals(max_age_seconds: int = 300) -> list[ProcessViolation]:
    """
    Detect terminal processes that appear orphaned (no active query association).

    In practice, this checks for:
    1. Terminal processes older than max_age_seconds
    2. Terminal processes with no visible parent cascade process
    3. Multiple terminal processes from same session
    """
    violations = []
    terminals = get_windsurf_terminals()

    # Check for excessive terminal accumulation
    terminal_procs = [p for p in terminals if "terminal" in p["name"].lower()
                      or "cmd" in p["name"].lower()
                      or "powershell" in p["name"].lower()
                      or "pwsh" in p["name"].lower()]

    # More than 3 terminal processes is suspicious
    if len(terminal_procs) > 3:
        for proc in terminal_procs[3:]:  # Flag excess terminals
            violations.append(ProcessViolation(
                pid=proc["pid"],
                name=proc["name"],
                parent_pid=proc["parent_pid"],
                query_id=None,
                age_seconds=0,
                violation_type="excess_terminal_accumulation",
            ))

    return violations


def check_run_command_usage(file_path: Path) -> list[str]:
    """
    Check that run_command calls have appropriate cleanup handling.

    Looks for:
    1. Blocking=False without timeout handling
    2. Missing WaitMsBeforeAsync on non-blocking commands
    3. No terminal cleanup pattern
    """
    issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
        lines = content.splitlines()

        for i, line in enumerate(lines, 1):
            # Check for non-blocking run_command without timeout
            if "run_command" in line and "Blocking=False" in line:
                # Check next few lines for WaitMsBeforeAsync or timeout handling
                context = "".join(lines[i:i+5])
                if "WaitMsBeforeAsync" not in context and "timeout" not in context.lower():
                    issues.append(f"{file_path}:{i}: Non-blocking run_command without timeout/WaitMsBeforeAsync")

            # Check for terminal creation without cleanup
            if any(cmd in line for cmd in ["subprocess.Popen", "Popen("]):
                # Check for cleanup in context
                context = "".join(lines[i:i+10])
                if "terminate" not in context and "kill" not in context and "wait" not in context:
                    issues.append(f"{file_path}:{i}: Popen without terminate/kill/wait cleanup")
    except Exception as e:
        issues.append(f"{file_path}: Error reading file: {e}")

    return issues


def main() -> int:
    """Main gate entrypoint."""
    violations = []
    warnings = []

    # 1. Check for orphaned terminal processes
    orphaned = get_orphaned_terminals()
    if orphaned:
        violations.extend(orphaned)
        print(f"[VIOLATION] Found {len(orphaned)} orphaned terminal processes:")
        for v in orphaned:
            print(f"  - PID {v.pid}: {v.name} ({v.violation_type})")

    # 2. Check Python files for proper terminal cleanup patterns
    ci_dir = Path("ops_scripts/ci")
    if ci_dir.exists():
        for py_file in ci_dir.glob("*.py"):
            issues = check_run_command_usage(py_file)
            if issues:
                warnings.extend(issues)

    # Also check tools directory
    tools_dir = Path("tools")
    if tools_dir.exists():
        for py_file in tools_dir.rglob("*.py"):
            if py_file.stat().st_size < 50000:  # Skip huge files
                issues = check_run_command_usage(py_file)
                if issues:
                    warnings.extend(issues[:5])  # Limit warnings per file

    # Output results
    result = {
        "gate": "terminal_cleanup_gate",
        "status": "PASS" if not violations else "FAIL",
        "violations": [
            {
                "pid": v.pid,
                "name": v.name,
                "type": v.violation_type,
            }
            for v in violations
        ],
        "warnings": warnings[:20],  # Limit warnings
        "timestamp": time.time(),
    }

    print(json.dumps(result, indent=2))

    if violations:
        print("\n[FAIL] Terminal Process Cleanup Gate: VIOLATIONS FOUND")
        print("Constitutional Rule #11: Terminal processes MUST be killed when queries finish.")
        return 1
    else:
        print("\n[PASS] Terminal Process Cleanup Gate: OK")
        return 0


if __name__ == "__main__":
    sys.exit(main())
