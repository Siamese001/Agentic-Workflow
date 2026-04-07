"""AST-based boundary guard: system_learning/ must not import from L6 observability.

Embedding Lifecycle architecture note (from docs/technical/Embedding Lifecycle.md):
  "Meta-learning reads signals from observability (L6) + state (L4)
   but must NOT be implemented as an L6 observability component
   (common mistake in agentic systems)."

This script enforces that boundary by AST-scanning every .py file under
system_learning/ and reporting any direct imports of L6 observability modules.

Exit codes:
  0 — No violations found.
  1 — One or more boundary violations detected.

Usage:
  python ops_scripts/ci/check_system_learning_boundary.py [--repo-root <path>]
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    SYSTEM_LEARNING_DIR,
)

_FORBIDDEN_PREFIXES: tuple[str, ...] = ('agentic_core.L6_observability', 'agentic_core.L6')
_EXEMPTIONS: frozenset[str] = frozenset()

def _extract_imports(source: str, filepath: str) -> list[str]:
    """AST-parse source and return all imported module names."""
    try:
        tree = ast.parse(source, filename=filepath)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                modules.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                modules.append(node.module)
    return modules

def check_boundary(repo_root: Path) -> list[tuple[str, str]]:
    """Scan system_learning/ for L6 observability imports.

    Returns:
        List of (relative_filepath, imported_module) tuples for each violation.
    """
    scan_root = repo_root / SYSTEM_LEARNING_DIR
    if not scan_root.exists():
        return []
    violations: list[tuple[str, str]] = []
    for py_file in sorted(scan_root.rglob('*.py')):
        rel = py_file.relative_to(repo_root).as_posix()
        if rel in _EXEMPTIONS:
            continue
        try:
            source = py_file.read_text(encoding='utf-8', errors='replace')
        except OSError:    # guardian: Add error context logging
            continue
        for module in _extract_imports(source, str(py_file)):
            if any(module.startswith(prefix) for prefix in _FORBIDDEN_PREFIXES):
                violations.append((rel, module))
    return violations

def main(argv: list[str] | None=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo-root', default=str(Path(__file__).resolve().parents[2]), help='Repository root directory (default: auto-detected)')
    args = parser.parse_args(argv)
    repo_root = Path(args.repo_root)
    violations = check_boundary(repo_root)
    if not violations:
        print('OK: system_learning/ boundary check passed — no L6 observability imports found.')
        return 0
    print(f'FAIL: {len(violations)} L6 boundary violation(s) in system_learning/:')
    for filepath, module in violations:
        print(f'  {filepath}: imports {module!r}')
    print('ERROR: system_learning/ must not import from L6 observability. See docs/technical/Embedding Lifecycle.md architecture note.')
    return 1
if __name__ == '__main__':
    sys.exit(main())
