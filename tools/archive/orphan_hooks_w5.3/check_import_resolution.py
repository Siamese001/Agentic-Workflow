#!/usr/bin/env python3
"""T3e Pre-Commit Hook: Import Resolution Check.

Parses staged .py files, extracts internal imports, and resolves each
against the filesystem. Fails if any staged file introduces an unresolved
internal import.

This is NOT a prefix blacklist — it performs real filesystem resolution
using the same logic as ImportResolutionGuardian.

Exit codes:
  0 = PASS (all staged imports resolve)
  1 = FAIL (unresolved imports in staged files)

Usage (pre-commit):
  entry: python ops_scripts/hooks/check_import_resolution.py
  types: [python]
  require_serial: true

Usage (manual):
  python ops_scripts/hooks/check_import_resolution.py [file1.py file2.py ...]
  python ops_scripts/hooks/check_import_resolution.py --all
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INTERNAL_ROOTS: frozenset[str] = frozenset(
    {AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR},
)


def resolve_module_path(root: Path, module: str) -> Path | None:
    """Resolve a dotted module path to a filesystem Path, or None.

    Checks (in order):
      1. Package: root/a/b/c/__init__.py
      2. Module:  root/a/b/c.py
      3. Direct:  root/a/b.py (for two-part modules)
    """
    parts = module.split(".")
    # Try as package (directory with __init__.py)
    pkg_path = root / "/".join(parts) / "__init__.py"
    if pkg_path.is_file():
        return pkg_path
    # Try as module file
    if len(parts) >= 2:
        mod_path = root / "/".join(parts[:-1]) / (parts[-1] + ".py")
        if mod_path.is_file():
            return mod_path
    # Try as direct file
    direct_path = root / ("/".join(parts) + ".py")
    if direct_path.is_file():
        return direct_path
    return None


def check_file_imports(filepath: Path, root: Path) -> list[str]:
    """Check a single file for unresolved internal imports.

    Returns list of violation messages.
    """
    violations: list[str] = []

    try:
        source = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:    # guardian: Add error context logging
        return violations

    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        return violations

    rel = filepath.relative_to(root).as_posix() if filepath.is_relative_to(root) else str(filepath)

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            top = node.module.split(".")[0]
            if top not in INTERNAL_ROOTS:
                continue
            if resolve_module_path(root, node.module) is None:
                violations.append(
                    f"{rel}:{node.lineno}: unresolved import 'from {node.module} import ...'",
                )

        elif isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top not in INTERNAL_ROOTS:
                    continue
                if resolve_module_path(root, alias.name) is None:
                    violations.append(
                        f"{rel}:{node.lineno}: unresolved import '{alias.name}'",
                    )

    return violations


def main() -> int:
    """Entry point. Accepts file paths as arguments (from pre-commit) or --all."""
    import argparse

    parser = argparse.ArgumentParser(
        description="T3e: Import Resolution Pre-Commit Check",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="Staged Python files to check (provided by pre-commit)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        dest="check_all",
        help="Check all Python files (not just staged)",
    )
    args = parser.parse_args()

    root = PROJECT_ROOT

    if args.check_all:
        import os

        files_to_check: list[Path] = []
        walk_excludes = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
        for scan_root in INTERNAL_ROOTS:
            scan_dir = root / scan_root
            if not scan_dir.is_dir():
                continue
            for dirpath, dirnames, filenames in os.walk(scan_dir):
                dirnames[:] = [d for d in dirnames if d not in walk_excludes]
                for fn in filenames:
                    if fn.endswith(".py"):
                        files_to_check.append(Path(dirpath) / fn)
    elif args.files:
        files_to_check = [Path(f).resolve() for f in args.files]
    else:
        print("[T3e] No files to check.")
        return 0

    all_violations: list[str] = []
    for fpath in files_to_check:
        if not fpath.exists() or not fpath.suffix == ".py":
            continue
        violations = check_file_imports(fpath, root)
        all_violations.extend(violations)

    if all_violations:
        print(f"[T3e IMPORT-RESOLVE] FAIL: {len(all_violations)} unresolved import(s) in staged files:")
        for v in all_violations:
            print(f"  {v}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
