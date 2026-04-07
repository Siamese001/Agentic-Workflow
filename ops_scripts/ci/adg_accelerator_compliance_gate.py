"""adg_accelerator_compliance_gate.py — Unified ADG Accelerator Compliance Gate.

Consolidates adg_python_ban_gate.py + adg_yaml_grep_ban_gate.py into a single
pre-commit hook (T14).

Checks:
  Python files  — reject use of grep/rg/ripgrep/ag/ack, mypy, or broad pytest
                  as ADG substitutes (subprocess, os.popen, os.system forms).
  YAML files    — reject grep/rg/ripgrep/ag/ack in GitHub Actions run: steps.

Exemptions:
  Per-line   Python : # guardian: allow-<grep|mypy|pytest> -- <justification>
  Per-line   YAML   : # guardian: allow-grep-yaml -- <justification>
  File-level Python : # adg-<grep|mypy|pytest>-ban: skip-file  (first 5 lines)
  File-level YAML   : # adg-yaml-grep-ban: skip-file           (first 5 lines)

Exit codes:
  0 — no violations
  1 — violations found (hard fail)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ===========================================================================
# Python ban patterns  (sourced from adg_python_ban_gate.py)
# ===========================================================================

_BANNED_SUBPROCESS_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"](?:grep|rg|ripgrep|ag|ack|findstr)\b",
)
_BANNED_POPEN_RE = re.compile(
    r"\bos\s*\.\s*popen\s*\(\s*['\"](?:grep|rg|ripgrep|ag|ack|findstr)\s",
)
_BANNED_SHELL_STR_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call)"
    r"\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep)\b",
)
_BANNED_OS_SYSTEM_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep|ag|ack|findstr)\b",
)
_BANNED_GETOUTPUT_RE = re.compile(
    r"\bsubprocess\s*\.\s*getoutput\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep|ag|ack|findstr)\b",
)
_BANNED_GETSTATUSOUTPUT_RE = re.compile(
    r"\bsubprocess\s*\.\s*getstatusoutput\s*\(\s*['\"][^'\"]*\b(?:grep|rg|ripgrep|ag|ack|findstr)\b",
)

_BANNED_DIRECT_MYPY_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]mypy['\"]",
)
_BANNED_PYTHON_M_MYPY_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]python[23]?['\"]\s*,.*['\"]-m['\"]\s*,\s*['\"]mypy['\"]",
)
_BANNED_OS_POPEN_MYPY_RE = re.compile(
    r"\bos\s*\.\s*popen\s*\(\s*['\"](?:mypy|python\s+-m\s+mypy)\s",
)
_BANNED_OS_SYSTEM_MYPY_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\b(?:mypy|python\s+-m\s+mypy)\b",
)

_BANNED_DIRECT_PYTEST_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]pytest['\"]",
)
_BANNED_PYTHON_M_PYTEST_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]python[23]?['\"]\s*,.*['\"]-m['\"]\s*,\s*['\"]pytest['\"]",
)
_BANNED_OS_POPEN_PYTEST_RE = re.compile(
    r"\bos\s*\.\s*popen\s*\(\s*['\"](?:pytest|python\s+-m\s+pytest)\s",
)
_BANNED_OS_SYSTEM_PYTEST_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\b(?:pytest|python\s+-m\s+pytest)\b",
)

_PY_GREP_PATTERNS = [
    _BANNED_SUBPROCESS_RE,
    _BANNED_POPEN_RE,
    _BANNED_SHELL_STR_RE,
    _BANNED_OS_SYSTEM_RE,
    _BANNED_GETOUTPUT_RE,
    _BANNED_GETSTATUSOUTPUT_RE,
]
_PY_MYPY_PATTERNS = [
    _BANNED_DIRECT_MYPY_RE,
    _BANNED_PYTHON_M_MYPY_RE,
    _BANNED_OS_POPEN_MYPY_RE,
    _BANNED_OS_SYSTEM_MYPY_RE,
]
_PY_PYTEST_PATTERNS = [
    _BANNED_DIRECT_PYTEST_RE,
    _BANNED_PYTHON_M_PYTEST_RE,
    _BANNED_OS_POPEN_PYTEST_RE,
    _BANNED_OS_SYSTEM_PYTEST_RE,
]

_PY_EXEMPTION_RE = re.compile(r"#\s*guardian:\s*allow-(grep|mypy|pytest)\s+--\s+\S")
_PY_FILE_SKIP_RE = re.compile(r"#\s*adg-(grep|mypy|pytest)-ban:\s*skip-file")

# ===========================================================================
# YAML ban patterns  (sourced from adg_yaml_grep_ban_gate.py)
# ===========================================================================

_YAML_SHELL_GREP_CMD_RE = re.compile(
    r"(?:^|&&|\|\||\|)\s*\b(?:grep|rg|ripgrep|ag|ack)\b",
)
_YAML_EXEMPTION_RE = re.compile(r"#\s*guardian:\s*allow-grep-yaml\s+--\s+\S")
_YAML_FILE_SKIP_RE = re.compile(r"#\s*adg-yaml-grep-ban:\s*skip-file")


# ===========================================================================
# Python scanner
# ===========================================================================


def check_python_bans(staged_files: list[Path]) -> list[dict]:
    """Return list of issue dicts for Python ban violations."""
    issues: list[dict] = []
    py_files = [p for p in staged_files if p.suffix == ".py" and p.is_file()]
    checks = ["grep", "mypy", "pytest"]
    pattern_map = {"grep": _PY_GREP_PATTERNS, "mypy": _PY_MYPY_PATTERNS, "pytest": _PY_PYTEST_PATTERNS}

    for path in py_files:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
            continue

        # File-level skip
        skipped: set[str] = set()
        for header_line in lines[:5]:
            m = _PY_FILE_SKIP_RE.search(header_line)
            if m:
                skipped.add(m.group(1))

        for line_no, line in enumerate(lines, start=1):
            if line.lstrip().startswith("#"):
                continue
            if _PY_EXEMPTION_RE.search(line):
                continue
            for check in checks:
                if check in skipped:
                    continue
                for pattern in pattern_map[check]:
                    if pattern.search(line):
                        try:
                            rel = str(path.relative_to(ROOT))
                        except ValueError:
                            rel = str(path)
                        issues.append({
                            "file": rel,
                            "line": line_no,
                            "check": check,
                            "text": line.rstrip(),
                            "kind": "python",
                        })
                        break

    return issues


# ===========================================================================
# YAML scanner
# ===========================================================================


def _yaml_is_shell_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped or (stripped.endswith(":") and " " not in stripped):
        return False
    if stripped.startswith(("name:", "uses:", "with:")):
        return False
    return True


def check_yaml_bans(staged_files: list[Path]) -> list[dict]:
    """Return list of issue dicts for YAML ban violations."""
    issues: list[dict] = []
    yaml_files = [
        p for p in staged_files
        if p.suffix in (".yml", ".yaml") and p.is_file()
    ]

    for path in yaml_files:
        try:
            lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as exc:
            print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
            continue

        # File-level skip
        for header_line in lines[:5]:
            if _YAML_FILE_SKIP_RE.search(header_line):
                lines = []
                break

        in_run_block = False
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()

            # Match both '    run: ...' and '    - run: ...' (list-item form)
            if (
                re.match(r"^\s+run:\s*[|>]?\s*$", line)
                or re.match(r"^\s+run:\s+\S", line)
                or re.match(r"^\s+-\s+run:\s*[|>]?\s*$", line)
                or re.match(r"^\s+-\s+run:\s+\S", line)
            ):
                in_run_block = True
            if in_run_block and line_no > 1:
                if re.match(r"^\s{2,4}[a-zA-Z_-]+:", line) and not re.match(r"^\s{6,}", line):
                    in_run_block = False

            if stripped.startswith("#"):
                continue
            if _YAML_EXEMPTION_RE.search(line):
                continue

            # Inline: '    run: cmd' or '    - run: cmd'
            is_inline = bool(
                re.match(r"^\s+run:\s+\S", line)
                or re.match(r"^\s+-\s+run:\s+\S", line)
            )
            is_in_block = in_run_block and _yaml_is_shell_line(line)

            if is_inline or is_in_block:
                check_content = re.sub(r"^.*run:\s+", "", line) if is_inline else line
                if _YAML_SHELL_GREP_CMD_RE.search(check_content):
                    try:
                        rel = str(path.relative_to(ROOT))
                    except ValueError:
                        rel = str(path)
                    issues.append({
                        "file": rel,
                        "line": line_no,
                        "check": "grep-yaml",
                        "text": line.rstrip(),
                        "kind": "yaml",
                    })

    return issues


# ===========================================================================
# Staged file helpers
# ===========================================================================


def _get_staged_files(root: Path) -> list[Path]:
    try:
        r = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMRT"],
            cwd=str(root), capture_output=True, encoding="utf-8", timeout=30,
        )
    except OSError:
        return []
    return [root / f for f in r.stdout.splitlines()]


# ===========================================================================
# Unified report
# ===========================================================================


def _print_unified_report(issues: list[dict]) -> None:
    python_issues = [i for i in issues if i["kind"] == "python"]
    yaml_issues = [i for i in issues if i["kind"] == "yaml"]

    print(
        f"\nFAIL: {len(issues)} ADG accelerator compliance violation(s) "
        f"({len(python_issues)} Python, {len(yaml_issues)} YAML)",
        file=sys.stderr,
    )
    print("Do not use grep/mypy/pytest/rg as ADG substitutes.", file=sys.stderr)
    print("  Python exemption : # guardian: allow-<grep|mypy|pytest> -- <justification>", file=sys.stderr)
    print("  YAML exemption   : # guardian: allow-grep-yaml -- <justification>", file=sys.stderr)
    print("", file=sys.stderr)

    for issue in sorted(issues, key=lambda i: (i["file"], i["line"])):
        print(
            f"  {issue['file']}:{issue['line']}: [{issue['check']}] {issue['text'].strip()}",
            file=sys.stderr,
        )


# ===========================================================================
# Entry point
# ===========================================================================


def main() -> int:
    staged = _get_staged_files(ROOT)

    all_issues: list[dict] = []
    all_issues.extend(check_python_bans(staged))
    all_issues.extend(check_yaml_bans(staged))

    if all_issues:
        _print_unified_report(all_issues)
        return 1

    py_count = sum(1 for p in staged if p.suffix == ".py")
    yaml_count = sum(1 for p in staged if p.suffix in (".yml", ".yaml"))
    print(f"OK: no ADG accelerator compliance violations ({py_count} Python, {yaml_count} YAML files scanned).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
