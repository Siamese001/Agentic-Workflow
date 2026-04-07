#!/usr/bin/env python3
"""
ADG Python Ban Gate — Consolidated enforcement for banned subprocess patterns

Combines grep-ban, mypy-ban, and pytest-ban gates into a single efficient scanner.
Rejects Python files that invoke banned tools as ADG substitutes.

Banned patterns (all three checks):
  - grep/rg/ripgrep/ag/ack/findstr via subprocess, os.popen, os.system, etc.
  - mypy directly (subprocess or python -m mypy) — use adg_type_check.py instead
  - pytest broadly (directory/no files) — use adg_test_selector.py instead

Exemptions:
  Per-line:   # guardian: allow-<type> -- <justification>
  File-level: # adg-<type>-ban: skip-file (first 5 lines only)

Exit codes:
  0 — no violations (clean)
  1 — violations found (hard fail — not a warning)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Pattern, Tuple

ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Grep ban patterns
# ---------------------------------------------------------------------------

# subprocess.{run,call,check_output,check_call,Popen}(["grep" / ['rg' / etc.)
_BANNED_SUBPROCESS_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"](?:grep|rg|ripgrep|ag|ack|findstr)\b",
)

# os.popen("grep ..." / os.popen('rg ...')
_BANNED_POPEN_RE = re.compile(
    r"\bos\s*\.\s*popen\s*\(\s*['\"](?:grep|rg|ripgrep|ag|ack|findstr)\s",
)

# subprocess.* (shell=True, cmd="grep ...")  — shell string form
_BANNED_SHELL_STR_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call)"
    r"\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep)\b",
)

# os.system("grep ...") — shell invocation via os.system
_BANNED_OS_SYSTEM_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep|ag|ack|findstr)\b",
)

# subprocess.getoutput("grep ...") — convenience shell wrapper
_BANNED_GETOUTPUT_RE = re.compile(
    r"\bsubprocess\s*\.\s*getoutput\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep|ag|ack|findstr)\b",
)

# subprocess.getstatusoutput("grep ...") — convenience shell wrapper
_BANNED_GETSTATUSOUTPUT_RE = re.compile(
    r"\bsubprocess\s*\.\s*getstatusoutput\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep|ag|ack|findstr)\b",
)

# ---------------------------------------------------------------------------
# Mypy ban patterns
# ---------------------------------------------------------------------------

# subprocess.*  with literal "mypy" as the FIRST argument (direct binary call)
_BANNED_DIRECT_MYPY_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]mypy['\"]",
)

# subprocess.* with literal "python" or "python3" + "-m" + "mypy"
# (NOT sys.executable — that's the canonical ADG form)
_BANNED_PYTHON_M_MYPY_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]python[23]?['\"]\s*,",
)

# os.popen("mypy ...") or os.popen("python -m mypy ...")
_BANNED_OS_POPEN_MYPY_RE = re.compile(
    r"\bos\s*\.\s*popen\s*\(\s*['\"](?:mypy|python\s+-m\s+mypy)\s",
)

# os.system with mypy
_BANNED_OS_SYSTEM_MYPY_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\b(?:mypy|python\s+-m\s+mypy)\b",
)

# ---------------------------------------------------------------------------
# Pytest ban patterns
# ---------------------------------------------------------------------------

# subprocess.* with literal "pytest" as first argument
_BANNED_DIRECT_PYTEST_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]pytest['\"]",
)

# subprocess.* with "python" + "-m" + "pytest"
_BANNED_PYTHON_M_PYTEST_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]python[23]?['\"]\s*,.*['\"]-m['\"]\s*,\s*['\"]pytest['\"]",
)

# os.popen with pytest
_BANNED_OS_POPEN_PYTEST_RE = re.compile(
    r"\bos\s*\.\s*popen\s*\(\s*['\"](?:pytest|python\s+-m\s+pytest)\s",
)

# os.system with pytest
_BANNED_OS_SYSTEM_PYTEST_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\b(?:pytest|python\s+-m\s+pytest)\b",
)

# ---------------------------------------------------------------------------
# Pattern collections
# ---------------------------------------------------------------------------

GREP_PATTERNS: list[Pattern[str]] = [
    _BANNED_SUBPROCESS_RE,
    _BANNED_POPEN_RE,
    _BANNED_SHELL_STR_RE,
    _BANNED_OS_SYSTEM_RE,
    _BANNED_GETOUTPUT_RE,
    _BANNED_GETSTATUSOUTPUT_RE,
]

MYPY_PATTERNS: list[Pattern[str]] = [
    _BANNED_DIRECT_MYPY_RE,
    _BANNED_PYTHON_M_MYPY_RE,
    _BANNED_OS_POPEN_MYPY_RE,
    _BANNED_OS_SYSTEM_MYPY_RE,
]

PYTEST_PATTERNS: list[Pattern[str]] = [
    _BANNED_DIRECT_PYTEST_RE,
    _BANNED_PYTHON_M_PYTEST_RE,
    _BANNED_OS_POPEN_PYTEST_RE,
    _BANNED_OS_SYSTEM_PYTEST_RE,
]

# ---------------------------------------------------------------------------
# Exemption patterns
# ---------------------------------------------------------------------------

# Guardian exemption — if present on the same line the violation is waived
_EXEMPTION_RE = re.compile(r"#\s*guardian:\s*allow-(grep|mypy|pytest)\s+--\s+\S")

# File-level skip directives — checked in first 5 lines only.
_FILE_SKIP_RE = re.compile(r"#\s*adg-(grep|mypy|pytest)-ban:\s*skip-file")

# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------

def scan_file(path: Path, checks: list[str]) -> dict[str, list[tuple[int, str]]]:
    """Return {check_name: [(line_no, line_text), ...]} for violations in path."""
    violations: dict[str, list[tuple[int, str]]] = {
        "grep": [],
        "mypy": [],
        "pytest": [],
    }

    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:
        print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
        return violations

    # Check for file-level skip directives
    for header_line in lines[:5]:
        skip_match = _FILE_SKIP_RE.search(header_line)
        if skip_match:
            skip_type = skip_match.group(1)
            # Skip all checks if "skip-file" matches any type
            if skip_type in checks:
                return violations

    for line_no, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue

        # Check for line-level exemption
        if _EXEMPTION_RE.search(line):
            continue

        # Check each enabled check type
        if "grep" in checks:
            for pattern in GREP_PATTERNS:
                if pattern.search(line):
                    violations["grep"].append((line_no, line.rstrip()))
                    break

        if "mypy" in checks:
            for pattern in MYPY_PATTERNS:
                if pattern.search(line):
                    violations["mypy"].append((line_no, line.rstrip()))
                    break

        if "pytest" in checks:
            for pattern in PYTEST_PATTERNS:
                if pattern.search(line):
                    violations["pytest"].append((line_no, line.rstrip()))
                    break

    return violations


def scan_files(paths: list[Path], checks: list[str]) -> dict[Path, dict[str, list[tuple[int, str]]]]:
    """Scan multiple files; return only those with violations."""
    result: dict[Path, dict[str, list[tuple[int, str]]]] = {}
    for p in paths:
        violations = scan_file(p, checks)
        if any(violations[check] for check in checks):
            result[p] = violations
    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _get_staged_py_files(root: Path) -> list[Path]:
    r = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
        cwd=str(root),
        capture_output=True,
        encoding="utf-8",
        timeout=30,
    )
    return [root / f for f in r.stdout.splitlines() if f.endswith(".py")]


def _get_all_tracked_py_files(root: Path) -> list[Path]:
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=str(root),
        capture_output=True,
        encoding="utf-8",
        timeout=60,
    )
    return [root / f for f in r.stdout.splitlines() if f.endswith(".py")]


def _cli() -> int:
    import argparse
    import os
    import sys

    # Add project root for schema imports
    project_root = Path(__file__).resolve().parents[2]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from ops_scripts.ci.pre_commit_issue_schema import PreCommitIssue, SeverityLevel

    parser = argparse.ArgumentParser(
        prog="adg_python_ban_gate",
        description="Consolidated ban gate: reject grep/mypy/pytest as ADG substitutes.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Explicit Python files to scan",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Scan staged Python files (git diff --cached)",
    )
    parser.add_argument(
        "--all-python",
        action="store_true",
        dest="all_python",
        help="Scan all Python files tracked by git",
    )
    parser.add_argument(
        "--checks",
        choices=["grep", "mypy", "pytest"],
        nargs="+",
        default=["grep", "mypy", "pytest"],
        help="Which checks to run (default: all)",
    )
    parser.add_argument(
        "--json-output",
        metavar="PATH",
        help="Write structured issues to JSON lines file",
    )
    args = parser.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files if f.endswith(".py")]
    elif args.all_python:
        paths = _get_all_tracked_py_files(ROOT)
    else:
        paths = _get_staged_py_files(ROOT)

    paths = [p for p in paths if p.is_file()]

    violations = scan_files(paths, args.checks)

    # Count violations by type
    total_violations = 0
    for file_violations in violations.values():
        for check in args.checks:
            total_violations += len(file_violations.get(check, []))

    # Build structured issues for JSON output
    json_issues = []
    check_names = {
        "grep": "ADG Python Ban — Grep/Ripgrep",
        "mypy": "ADG Python Ban — Mypy Direct Invocation",
        "pytest": "ADG Python Ban — Pytest Direct Invocation",
    }
    explanations = {
        "grep": "Use ADG Redis MCP tools (grep_search) instead of subprocess grep. Grep misses semantic relationships.",
        "mypy": "Use adg_type_check.py instead of invoking mypy directly. Direct mypy invocation bypasses ADG type analysis.",
        "pytest": "Use adg_test_selector.py instead of broad pytest. Broad pytest runs cause test deselection issues.",
    }

    for file_path, file_violations in violations.items():
        for check in args.checks:
            for line_no, line_text in file_violations.get(check, []):
                issue = PreCommitIssue(
                    hook_id="adg-python-ban-gate",
                    hook_name=check_names.get(check, "ADG Python Ban"),
                    severity=SeverityLevel.CRITICAL,
                    file_path=str(file_path.relative_to(ROOT)),
                    line_number=line_no,
                    message=f"Banned pattern: {check} via subprocess/os.system",
                    explanation=explanations.get(check, "Use ADG tools instead of direct tool invocation."),
                    issue_type=f"adg_{check}_ban",
                )
                json_issues.append(issue)

    # Write JSON output if requested
    if args.json_output and json_issues:
        output_path = Path(args.json_output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            for issue in json_issues:
                f.write(issue.to_json() + "\n")

    if total_violations == 0:
        print(f"OK: no {', '.join(args.checks)}-ban violations in {len(paths)} file(s).")
        return 0

    # Report violations
    print(f"\nFAIL: {total_violations} banned pattern(s) in {len(violations)} file(s).", file=sys.stderr)
    print("Do not use grep/mypy/pytest as ADG substitutes.", file=sys.stderr)
    print("  Exemption: # guardian: allow-<type> -- <justification>", file=sys.stderr)
    print("  File-level: # adg-<type>-ban: skip-file (first 5 lines)", file=sys.stderr)
    print("", file=sys.stderr)

    for path, file_violations in sorted(violations.items()):
        rel = path.relative_to(ROOT) if path.is_absolute() else path
        for check in args.checks:
            for line_no, line in file_violations.get(check, []):
                print(f"  {rel}:{line_no}: [{check}] {line.strip()}", file=sys.stderr)

    sys.exit(1)


if __name__ == "__main__":
    _cli()
