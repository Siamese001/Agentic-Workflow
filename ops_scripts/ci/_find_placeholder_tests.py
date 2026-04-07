"""Find placeholder / stub test files using AST analysis.

A test file is classified as a placeholder if ALL its test_* functions have
trivially empty bodies — i.e. contain only:
  - docstrings (bare string literals)
  - pass / return statements
  - assert True
  - self.assertTrue(True)
  - self.assertEqual(1 + 1, 2)  or  self.assertEqual(1, 1)

Usage
-----
    # Report only (exit 0 always):
    python ops_scripts/ci/_find_placeholder_tests.py

    # Enforce: exit 1 if placeholders exist in high-priority directories:
    python ops_scripts/ci/_find_placeholder_tests.py --enforce

    # Filter to a specific subtree:
    python ops_scripts/ci/_find_placeholder_tests.py --dir tests/adg

    # Output as JSON (for CI artifact ingestion):
    python ops_scripts/ci/_find_placeholder_tests.py --json

    # Show files only (no per-function detail):
    python ops_scripts/ci/_find_placeholder_tests.py --files-only

Exit codes
----------
    0  — report-only mode, or enforce mode with zero placeholders found
    1  — enforce mode and at least one placeholder found in an enforced dir
    2  — usage / argument error
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from collections import defaultdict
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).parent.parent.parent
_TESTS_DIR = _REPO_ROOT / "tests"

# Directories where placeholders are BLOCKING (used with --enforce)
_ENFORCE_DIRS: frozenset[str] = frozenset(
    {
        "adg",
        "integration",
        "smoke",
        "e2e",
        "architecture",
        "governance",
        "contracts",
        "infrastructure",
    },
)

# Trivial call expressions that count as placeholder bodies
_TRIVIAL_CALL_UNPARSED: frozenset[str] = frozenset(
    {
        "self.assertTrue(True)",
        "self.assertEqual(1 + 1, 2)",
        "self.assertEqual((1 + 1), 2)",
        "self.assertEqual(1, 1)",
        "self.assertIsNone(None)",
        "self.assertIsNotNone(self)",
    },
)


# ---------------------------------------------------------------------------
# Core AST analysis
# ---------------------------------------------------------------------------


def _is_trivial_stmt(stmt: ast.stmt) -> bool:
    """Return True if stmt contributes zero real assertion logic."""
    if isinstance(stmt, (ast.Pass, ast.Return)):
        return True
    # Bare string literal (docstring)
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Constant):
        return True
    # assert True
    if isinstance(stmt, ast.Assert):
        test = stmt.test
        if isinstance(test, ast.Constant) and test.value is True:
            return True
    # Trivial self.assert* calls
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        unparsed = ast.unparse(stmt.value) if hasattr(ast, "unparse") else ""
        if unparsed in _TRIVIAL_CALL_UNPARSED:
            return True
    return False


def _classify_file(path: Path) -> list[str]:
    """Return list of trivial test function names. Empty list = not a placeholder."""
    try:
        src = path.read_text(encoding="utf-8")
        tree = ast.parse(src)
    except (OSError, SyntaxError):
        return []

    test_funcs = [
        n
        for n in ast.walk(tree)
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        and n.name.startswith("test_")
    ]

    if not test_funcs:
        return ["<no test functions>"]

    trivial = []
    for fn in test_funcs:
        if all(_is_trivial_stmt(s) for s in fn.body):
            trivial.append(fn.name)

    # Only flag the file if ALL test functions are trivial
    if len(trivial) == len(test_funcs):
        return trivial
    return []


# ---------------------------------------------------------------------------
# Scan
# ---------------------------------------------------------------------------


def scan(root: Path) -> dict[str, list[str]]:
    """Return {relative_path: [trivial_func_names]} for all placeholder files."""
    results: dict[str, list[str]] = {}
    for py in sorted(root.rglob("*.py")):
        trivial = _classify_file(py)
        if trivial:
            rel = str(py.relative_to(_TESTS_DIR))
            results[rel] = trivial
    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def _by_dir(results: dict[str, list[str]]) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for path in results:
        top = path.split(os.sep)[0].split("/")[0]
        grouped[top].append(path)
    return dict(grouped)


def print_report(results: dict[str, list[str]], files_only: bool = False) -> None:
    by_dir = _by_dir(results)
    total = len(results)
    print(f"\nPlaceholder test files: {total} found\n")
    for d, files in sorted(by_dir.items(), key=lambda x: -len(x[1])):
        marker = " [ENFORCED]" if d in _ENFORCE_DIRS else ""
        print(f"  tests/{d}/  ({len(files)} files){marker}")
        if not files_only:
            for f in files:
                funcs = results[f]
                print(f"    {f}")
                for fn in funcs[:5]:
                    print(f"      - {fn}()")
                if len(funcs) > 5:
                    print(f"      ... +{len(funcs) - 5} more")
    print()


def print_json(results: dict[str, list[str]]) -> None:
    out = {
        "total": len(results),
        "files": {path: funcs for path, funcs in results.items()},
        "by_dir": {
            d: files for d, files in sorted(_by_dir(results).items())
        },
    }
    print(json.dumps(out, indent=2))


# ---------------------------------------------------------------------------
# Enforcement
# ---------------------------------------------------------------------------


def check_enforce(results: dict[str, list[str]]) -> int:
    """Return 1 if any enforced directory has placeholders, else 0."""
    violations = {
        path: funcs
        for path, funcs in results.items()
        if path.split(os.sep)[0].split("/")[0] in _ENFORCE_DIRS
    }
    if violations:
        print(f"[ENFORCE] {len(violations)} placeholder(s) in enforced directories:\n")
        for path, funcs in sorted(violations.items()):
            print(f"  {path}")
            for fn in funcs:
                print(f"    - {fn}()")
        print(
            f"\nFix these by replacing placeholder bodies with real assertions.\n"
            f"Enforced dirs: {sorted(_ENFORCE_DIRS)}",
        )
        return 1
    return 0


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Find placeholder/stub test files via AST analysis.",
    )
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="Exit 1 if placeholders exist in enforced directories.",
    )
    parser.add_argument(
        "--dir",
        metavar="SUBDIR",
        default=None,
        help="Limit scan to tests/<SUBDIR> (e.g. 'adg').",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of human-readable report.",
    )
    parser.add_argument(
        "--files-only",
        action="store_true",
        help="Show file paths only, no per-function detail.",
    )
    args = parser.parse_args(argv)

    scan_root = _TESTS_DIR
    if args.dir:
        scan_root = _TESTS_DIR / args.dir
        if not scan_root.exists():
            print(f"Error: {scan_root} does not exist", file=sys.stderr)
            return 2

    results = scan(scan_root)

    if args.json:
        print_json(results)
    else:
        print_report(results, files_only=args.files_only)

    if args.enforce:
        return check_enforce(results)

    return 0


if __name__ == "__main__":
    sys.exit(main())
