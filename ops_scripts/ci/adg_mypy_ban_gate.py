# adg-mypy-ban: skip-file
"""ADG Mypy-Ban Gate — hard-fail enforcement for broad mypy subprocess calls.

Rejects Python files that invoke mypy directly (via subprocess or os.popen/system)
as a broad package-level analysis substitute.  All mypy analysis MUST go through
the ADG accelerator:

  Incremental type checking:  python tools/adg/adg_type_check.py --from-diff

The canonical accelerator (adg_type_check.py) calls mypy via sys.executable (NOT a
string literal "mypy" or "python") so it is automatically safe from this gate.

Banned patterns
───────────────
  subprocess.run(["mypy", ...]            ← literal "mypy" binary
  subprocess.run(["python", "-m", "mypy"  ← literal "python" + "-m" + "mypy"
  subprocess.run(["python3", "-m", "mypy" ← same with python3
  os.popen("mypy ...")                    ← shell popen with mypy
  os.popen("python -m mypy ...")          ← shell popen python -m mypy
  os.system("mypy ...")                   ← os.system with mypy
  os.system("python -m mypy ...")         ← os.system python -m mypy

Allowed (ADG canonical form)
────────────────────────────
  subprocess.run([sys.executable, "-m", "mypy", ...])   ← adg_type_check.py pattern

Exemptions
──────────
  Per-line:   # guardian: allow-mypy -- <justification>
  File-level: # adg-mypy-ban: skip-file  (first 5 lines only)

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
# The canonical ADG type-checker — auto-exempt from this gate
# ---------------------------------------------------------------------------
_CANONICAL_MYPY_TOOL = ROOT / "tools" / "adg" / "adg_type_check.py"

# ---------------------------------------------------------------------------
# Banned patterns
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
    r"\bos\s*\.\s*popen\s*\(\s*['\"][^'\"]*\bmypy\b",
)

# os.system("mypy ...") or os.system("python -m mypy ...")
_BANNED_OS_SYSTEM_MYPY_RE = re.compile(
    r"\bos\s*\.\s*system\s*\(\s*['\"][^'\"]*\bmypy\b",
)

# subprocess.run("python -m mypy ...", shell=True)  — shell string form
_BANNED_SHELL_STR_MYPY_RE = re.compile(
    r"\bsubprocess\s*\.\s*(?:run|call|check_output|check_call)"
    r"\s*\(\s*['\"][^'\"]*\bpython[23]?\s+-m\s+mypy\b",
)

_BANNED_PATTERNS: list[re.Pattern[str]] = [
    _BANNED_DIRECT_MYPY_RE,
    _BANNED_OS_POPEN_MYPY_RE,
    _BANNED_OS_SYSTEM_MYPY_RE,
    _BANNED_SHELL_STR_MYPY_RE,
]

# Separate check: "python" literal + mypy — only flag if "mypy" also appears on the line
_PYTHON_LITERAL_PATTERN = _BANNED_PYTHON_M_MYPY_RE

# ---------------------------------------------------------------------------
# Exemption + file-skip
# ---------------------------------------------------------------------------

# Per-line exemption: # guardian: allow-mypy -- <justification>
_EXEMPTION_RE = re.compile(r"#\s*guardian:\s*allow-mypy\s+--\s+\S")

# File-level skip: # adg-mypy-ban: skip-file  (first 5 lines only)
_FILE_SKIP_RE = re.compile(r"#\s*adg-mypy-ban:\s*skip-file")


# ---------------------------------------------------------------------------
# Core scanner
# ---------------------------------------------------------------------------


def scan_file(path: Path) -> list[tuple[int, str]]:
    """Return (1-indexed line_no, line_text) for each violation in path."""
    # Auto-exempt the canonical ADG type-checker itself
    try:
        if path.resolve() == _CANONICAL_MYPY_TOOL.resolve():
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

        hit = False
        for pattern in _BANNED_PATTERNS:
            if pattern.search(line):
                hit = True
                break

        # Special case: literal "python" in subprocess + "mypy" on same line
        if not hit and _PYTHON_LITERAL_PATTERN.search(line) and '"mypy"' in line:
            hit = True

        if hit:
            violations.append((line_no, line.rstrip()))

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
        prog="adg_mypy_ban_gate",
        description="Hard-fail gate: reject broad mypy subprocess calls (use adg_type_check.py instead).",
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
        print(f"OK: no mypy-ban violations in {len(paths)} file(s).")
        sys.exit(0)

    total = sum(len(vs) for vs in violations.values())
    print(
        f"\nFAIL: {total} mypy-ban violation(s) in {len(violations)} file(s).",
        file=sys.stderr,
    )
    print("Use the ADG accelerator instead of broad mypy:", file=sys.stderr)
    print(
        "  Incremental type check: python tools/adg/adg_type_check.py --from-diff",
        file=sys.stderr,
    )
    print(
        "  Exemption:              # guardian: allow-mypy -- <justification>",
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
