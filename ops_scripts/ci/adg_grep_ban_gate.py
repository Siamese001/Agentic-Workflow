"""ADG Grep-Ban Gate — hard-fail enforcement for grep/rg search substitutes.

Rejects Python files that invoke grep/rg/ripgrep via subprocess (or os.popen)
as an ADG query substitute. These tools MUST NOT be used as fallbacks — use the
ADG accelerators instead:

  Symbol/node search:  python tools/adg/adg_redis_query.py search-nodes <term>
  File path search:    python tools/adg/adg_redis_query.py search-files <term>
  Test selection:      python tools/adg/adg_test_selector.py --from-diff
  Incremental typing:  python tools/adg/adg_type_check.py --from-diff

A violation is exempted per line with:
    subprocess.run(["grep", ...])  # guardian: allow-grep -- <justification>

Exit codes:
  0 — no violations (clean)
  1 — violations found (hard fail — not a warning)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Forbidden patterns
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

_BANNED_PATTERNS: list[re.Pattern[str]] = [
    _BANNED_SUBPROCESS_RE,
    _BANNED_POPEN_RE,
    _BANNED_SHELL_STR_RE,
    _BANNED_OS_SYSTEM_RE,
    _BANNED_GETOUTPUT_RE,
    _BANNED_GETSTATUSOUTPUT_RE,
]

# Guardian exemption — if present on the same line the violation is waived
_EXEMPTION_RE = re.compile(r"#\s*guardian:\s*allow-grep\s+--\s+\S")

# File-level skip directive — checked in first 5 lines only.
# Use in test files that contain banned patterns as string literals (fixtures).
# Format: # adg-grep-ban: skip-file
_FILE_SKIP_RE = re.compile(r"#\s*adg-grep-ban:\s*skip-file")


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Return (1-indexed line_no, line_text) for each violation in path."""
    violations: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:    # guardian: Add error context logging
        print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
        return violations

    for header_line in lines[:5]:
        if _FILE_SKIP_RE.search(header_line):
            return violations

    for line_no, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if _EXEMPTION_RE.search(line):
            continue
        for pattern in _BANNED_PATTERNS:
            if pattern.search(line):
                violations.append((line_no, line.rstrip()))
                break

    return violations


def scan_files(paths: list[Path]) -> dict[Path, list[tuple[int, str]]]:
    """Scan multiple files; return only those with violations."""
    result: dict[Path, list[tuple[int, str]]] = {}
    for p in paths:
        vs = scan_file(p)
        if vs:
            result[p] = vs
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


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="adg_grep_ban_gate",
        description="Hard-fail gate: reject grep/rg/ripgrep as ADG query substitutes.",
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
    args = parser.parse_args()

    if args.files:
        paths = [Path(f) for f in args.files if f.endswith(".py")]
    elif args.all_python:
        paths = _get_all_tracked_py_files(ROOT)
    else:
        paths = _get_staged_py_files(ROOT)

    paths = [p for p in paths if p.is_file()]

    violations = scan_files(paths)

    if not violations:
        print(f"OK: no grep-ban violations in {len(paths)} file(s).")
        sys.exit(0)

    total = sum(len(vs) for vs in violations.values())
    print(
        f"\nFAIL: {total} grep-ban violation(s) in {len(violations)} file(s).",
        file=sys.stderr,
    )
    print("Use ADG accelerators instead of grep/rg/ripgrep:", file=sys.stderr)
    print(
        "  Symbol search:  python tools/adg/adg_redis_query.py search-nodes <term>",
        file=sys.stderr,
    )
    print(
        "  File search:    python tools/adg/adg_redis_query.py search-files <term>",
        file=sys.stderr,
    )
    print(
        "  Test selection: python tools/adg/adg_test_selector.py --from-diff",
        file=sys.stderr,
    )
    print(
        "  Type check:     python tools/adg/adg_type_check.py --from-diff",
        file=sys.stderr,
    )
    print(
        "  Exemption:      # guardian: allow-grep -- <justification>",
        file=sys.stderr,
    )
    print("", file=sys.stderr)
    for path, vs in sorted(violations.items()):
        for line_no, line in vs:
            rel = path.relative_to(ROOT) if path.is_absolute() else path
            print(f"  {rel}:{line_no}: {line.strip()}", file=sys.stderr)

    sys.exit(1)


if __name__ == "__main__":
    _cli()
