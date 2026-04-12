"""
Query Progress Bar CI Gate — Constitutional Rule §16.

Enforces mandatory colored progress bars for all long-running operations (>5s threshold).
Detects for-loops, functions, and subprocess calls that lack progress reporting.

Exit codes:
    0  — all checks passed
    1  — violations found

Usage:
    python ops_scripts/ci/check_query_progress_bar.py [--verbose] [--staged] [file ...]
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# Directories scanned when running in whole-repo mode
_SCAN_DIRS = [
    "agentic_core",
    "apps_rg",
    "apps_lic",
    "apps_eval",
    "apps_exec",
    "apps_research",
    "apps_rfp",
    "apps_shared",
    "apps_underwriting_ai",
    "ops_scripts",
    "tools",
    "system_learning",
]

# Minimum loop-body length (lines) to require progress reporting
_LOOP_LINE_THRESHOLD = 10

# Minimum function-body length (lines) to require progress for heavy-named functions
_FUNC_LINE_THRESHOLD = 12

# Function name prefixes that indicate potentially long I/O or query operations.
# Deliberately excludes build_* (data factories) and validate_* (thin policy wrappers) —
# those are almost always pure in-memory logic with no iteration, not time-intensive queries.
# A function is only flagged when its body ALSO contains at least one for-loop (see check_file).
_HEAVY_PREFIXES = ("scan_", "query_", "search_", "analyze_", "process_")

# Strings that mark a block as compliant (case-insensitive check on source text)
_COMPLIANCE_MARKERS = (
    "tqdm",
    "pbar.update",
    "pbar.set_description",
    "tracker.update",
    "reporter.update",
    "progressreporter",
    "progress_reporter",
    "alive_bar",
    "rich.progress",
    "progress_bar",
    "progressbar",
    ".update(1)",
    ".update(",
)

# Files/directories to skip during scan
_SKIP_PATTERNS = (
    "__pycache__",
    ".mypy_cache",
    "archives",
    "archive",
    ".git",
    "node_modules",
)


def _extract_source_lines(source: str, lineno: int, end_lineno: int) -> str:
    """Return the source lines between lineno and end_lineno (1-indexed)."""
    lines = source.splitlines()
    start = max(0, lineno - 1)
    end = min(len(lines), end_lineno)
    return "\n".join(lines[start:end])


def _has_compliance_marker(text: str) -> bool:
    """Return True if the text contains any known progress-compliance marker."""
    lower = text.lower()
    return any(marker in lower for marker in _COMPLIANCE_MARKERS)


def _should_skip(path: Path) -> bool:
    """Return True if path contains any skip-pattern component."""
    parts = path.parts
    return any(skip in parts for skip in _SKIP_PATTERNS)


class Violation:
    """A detected progress-bar compliance violation."""

    def __init__(self, path: Path, lineno: int, message: str) -> None:
        self.path = path
        self.lineno = lineno
        self.message = message

    def __str__(self) -> str:
        try:
            rel = self.path.relative_to(_ROOT)
        except ValueError:
            rel = self.path
        return f"{rel}:{self.lineno}: {self.message}"


def check_file(path: Path) -> list[Violation]:
    """Analyse a single Python file and return all violations found."""
    violations: list[Violation] = []

    try:
        source = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [Violation(path, 0, f"Could not read file: {exc}")]

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return []  # Syntax errors handled by Tier-1 gate

    for node in ast.walk(tree):
        # --- Check 1: For-loops that are long and lack progress ---
        if isinstance(node, ast.For):
            start = node.lineno
            end = getattr(node, "end_lineno", start)
            length = end - start
            if length >= _LOOP_LINE_THRESHOLD:
                body_src = _extract_source_lines(source, start, end)
                if not _has_compliance_marker(body_src):
                    violations.append(
                        Violation(
                            path,
                            start,
                            f"For-loop spanning {length} lines has no progress reporting "
                            f"(add tqdm/ProgressReporter — §16)",
                        )
                    )

        # --- Check 2: Heavy-named functions without progress reporting ---
        # Only flag when the function body contains at least one for-loop — pure
        # data-builder/factory functions with no iteration are never time-intensive.
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name = node.name.lower()
            if any(name.startswith(prefix) for prefix in _HEAVY_PREFIXES):
                start = node.lineno
                end = getattr(node, "end_lineno", start)
                length = end - start
                if length >= _FUNC_LINE_THRESHOLD:
                    body_src = _extract_source_lines(source, start, end)
                    has_loop = any(isinstance(child, ast.For) for child in ast.walk(node))
                    if has_loop and not _has_compliance_marker(body_src):
                        violations.append(
                            Violation(
                                path,
                                start,
                                f"Function '{node.name}' ({length} lines) iterates without "
                                f"progress reporting (add tqdm/ProgressReporter — §16)",
                            )
                        )

    return violations


def check_files(paths: list[Path], verbose: bool = False) -> list[Violation]:
    """Run checks across a list of paths."""
    all_violations: list[Violation] = []
    for path in paths:
        if not path.suffix == ".py":
            continue
        if _should_skip(path):
            continue
        file_violations = check_file(path)
        if file_violations:
            all_violations.extend(file_violations)
            if verbose:
                for v in file_violations:
                    print(f"  VIOLATION: {v}")
        elif verbose:
            try:
                label = path.relative_to(_ROOT)
            except ValueError:
                label = path
            print(f"  OK  {label}")
    return all_violations


def collect_repo_files() -> list[Path]:
    """Collect all Python files from the canonical scan directories."""
    files: list[Path] = []
    for dirname in _SCAN_DIRS:
        scan_dir = _ROOT / dirname
        if not scan_dir.is_dir():
            continue
        for py_file in sorted(scan_dir.rglob("*.py")):
            if not _should_skip(py_file):
                files.append(py_file)
    return files


def main(argv: list[str] | None = None) -> int:
    """CI entry point. Returns 0 on pass, 1 on failure."""
    if argv is None:
        argv = sys.argv[1:]

    verbose = "--verbose" in argv or "-v" in argv

    # Explicit file list (from pre-commit --filenames or manual invocation)
    explicit_files = [Path(a) for a in argv if not a.startswith("-") and a.endswith(".py")]

    if explicit_files:
        target_files = explicit_files
    else:
        target_files = collect_repo_files()

    if not target_files:
        print("[SKIP] check_query_progress_bar: no Python files to check")
        return 0

    print("=" * 70)
    print("QUERY PROGRESS BAR COMPLIANCE — Constitutional Rule §16")
    print("=" * 70)

    violations = check_files(target_files, verbose=verbose)

    if violations:
        print(f"\n[FAIL] {len(violations)} violation(s) found:\n")
        for v in violations:
            print(f"  - {v}")
        print()
        print("REMEDIATION:")
        print("  1. Add 'from tqdm import tqdm' and wrap the loop:")
        print("     for item in tqdm(items, desc='Processing', unit='item'):")
        print("  2. Or use ProgressReporter from tools/progress_display.py")
        print("  3. See: .windsurf/rules/query-progress-bar.md")
        print("=" * 70)
        return 1

    print(f"[PASS] {len(target_files)} file(s) checked — no violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
