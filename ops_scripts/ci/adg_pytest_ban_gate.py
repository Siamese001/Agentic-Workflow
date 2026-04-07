# adg-pytest-ban: skip-file
"""ADG Pytest-Ban Gate — hard-fail enforcement for broad pytest subprocess calls.

Rejects Python files that invoke pytest broadly (on directories / with no file
arguments) instead of through the ADG test selector accelerator:

  ADG-selected tests:  python tools/adg/adg_test_selector.py --from-diff --pytest-args

Broad pytest runs waste CI time on unrelated tests and hide the root cause.
The ADG selector narrows pytest to only the tests covering changed files via
the ADG dependency graph's `covers` edges.

Banned patterns
───────────────
  subprocess.run(["pytest"])                      ← bare pytest, no files
  subprocess.run(["pytest", "tests/", ...])       ← literal directory
  subprocess.run(["pytest", "agentic_core/"])     ← literal production dir
  subprocess.run(["python", "-m", "pytest"])      ← bare python -m pytest
  subprocess.run(["python", "-m", "pytest", "tests/"])  ← literal directory
  os.system("pytest ...")                         ← shell invocation
  os.system("python -m pytest ...")               ← shell invocation

Allowed (ADG canonical forms)
──────────────────────────────
  subprocess.run(["pytest"] + adg_files, ...)           ← dynamic list from ADG
  subprocess.run([sys.executable, "-m", "pytest", ...]) ← sys.executable form
  subprocess.run(["pytest", "specific_test.py"])        ← explicit .py file (not dir)

Exemptions
──────────
  Per-line:   # guardian: allow-pytest -- <justification>
  File-level: # adg-pytest-ban: skip-file  (first 5 lines only)

Exit codes
──────────
  0 — no violations
  1 — violations found (hard fail)
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# The canonical ADG test selector — auto-exempt from this gate
# ---------------------------------------------------------------------------
_CANONICAL_TEST_SELECTOR = ROOT / "tools" / "adg" / "adg_test_selector.py"

# ---------------------------------------------------------------------------
# Banned patterns
# ---------------------------------------------------------------------------

# subprocess.run(["pytest"]) — bare pytest, no files/directories
# NOT: subprocess.run(["pytest"] + adg_files) — that's the ADG canonical form (list concat)
_BANNED_BARE_PYTEST_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[\s*['\"]pytest['\"]\s*\](?!\s*\+)",
)

# subprocess.run(["pytest", "<literal-dir>", ...]) — directory literal as arg
# Matches pytest followed by a string that ends in / or is a known test root
_BANNED_PYTEST_DIR_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r"\s*\(\s*\[.*?['\"]pytest['\"].*?,\s*['\"][a-zA-Z][^'\"]*[/\\]['\"]",
)

# subprocess.run(["python", "-m", "pytest"]) — bare python -m pytest (no files)
_BANNED_PYTHON_M_PYTEST_BARE_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r'\s*\(\s*\[.*?[\'"]python[23]?[\'"].*?[\'"]pytest[\'"]\s*\]',
)

# subprocess.run(["python", "-m", "pytest", "<literal-dir>"])
_BANNED_PYTHON_M_PYTEST_DIR_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call|Popen)"
    r'\s*\(\s*\[.*?[\'"]python[23]?[\'"].*?[\'"]pytest[\'"].*?,\s*[\'"][a-zA-Z][^\'\"]*[/\\][\'"]',
)

# os.system("pytest ...") or os.system("python -m pytest ...")
_BANNED_OS_SYSTEM_PYTEST_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\bpytest\b",
)

# subprocess.getoutput("pytest ...") or subprocess.getstatusoutput("pytest ...")
_BANNED_GETOUTPUT_PYTEST_RE = re.compile(
    r"\bsubprocess\s*\.\s*get(?:status)?output\s*\(\s*['\"][^'\"]*\bpytest\b",
)

_BANNED_PATTERNS: list[re.Pattern[str]] = [
    _BANNED_BARE_PYTEST_RE,
    _BANNED_PYTEST_DIR_RE,
    _BANNED_PYTHON_M_PYTEST_BARE_RE,
    _BANNED_PYTHON_M_PYTEST_DIR_RE,
    _BANNED_OS_SYSTEM_PYTEST_RE,
    _BANNED_GETOUTPUT_PYTEST_RE,
]

# ---------------------------------------------------------------------------
# Exemption + file-skip
# ---------------------------------------------------------------------------

_EXEMPTION_RE = re.compile(r"#\s*guardian:\s*allow-pytest\s+--\s+\S")
_FILE_SKIP_RE = re.compile(r"#\s*adg-pytest-ban:\s*skip-file")


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Return (1-indexed line_no, line_text) for each violation in path."""
    # Auto-exempt the canonical ADG test selector itself
    try:
        if path.resolve() == _CANONICAL_TEST_SELECTOR.resolve():
            return []
    except OSError:    # guardian: Add error context logging
        pass

    violations: list[tuple[int, str]] = []
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError as exc:    # guardian: Add error context logging
        print(f"WARNING: could not read {path}: {exc}", file=sys.stderr)
        return violations

    # File-level skip (first 5 lines)
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
        cwd=str(root), capture_output=True, encoding="utf-8", timeout=30,
    )
    return [root / f for f in r.stdout.splitlines() if f.endswith(".py")]


def _get_all_tracked_py_files(root: Path) -> list[Path]:
    r = subprocess.run(
        ["git", "ls-files"],
        cwd=str(root), capture_output=True, encoding="utf-8", timeout=60,
    )
    return [root / f for f in r.stdout.splitlines() if f.endswith(".py")]


def _cli() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        prog="adg_pytest_ban_gate",
        description="Hard-fail gate: reject broad pytest subprocess calls (use adg_test_selector.py instead).",
    )
    parser.add_argument("files", nargs="*", metavar="FILE")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--all-python", action="store_true", dest="all_python")
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
        print(f"OK: no pytest-ban violations in {len(paths)} file(s).")
        sys.exit(0)

    total = sum(len(vs) for vs in violations.values())
    print(f"\nFAIL: {total} pytest-ban violation(s) in {len(violations)} file(s).", file=sys.stderr)
    print("Use the ADG test selector instead of broad pytest:", file=sys.stderr)
    print("  python tools/adg/adg_test_selector.py --from-diff --pytest-args", file=sys.stderr)
    print("  Exemption: # guardian: allow-pytest -- <justification>", file=sys.stderr)
    print("", file=sys.stderr)
    for path, vs in sorted(violations.items()):
        for line_no, line in vs:
            rel = path.relative_to(ROOT) if path.is_absolute() else path
            print(f"  {rel}:{line_no}: {line.strip()}", file=sys.stderr)

    sys.exit(1)


if __name__ == "__main__":
    _cli()
