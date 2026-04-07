#!/usr/bin/env python3
"""
Pre-commit hook: Compound Suffix Validation (LCD+ P0).

Blocks commits containing .py files with multiple architectural suffixes.
These compound suffixes cause ambiguous classification in FileClassificationAgent.

Usage:
    python ops_scripts/hooks/check_compound_suffix_script.py [--staged-only]

Exit codes:
    0 - All files pass validation
    1 - Compound suffix violations found
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)

# Canonical architectural suffixes (mirrors KNOWN_ARCHITECTURAL_SUFFIXES in structure_blueprint_config.py)
KNOWN_ARCHITECTURAL_SUFFIXES: list[str] = [
    "_types",
    "_config",
    "_validator",
    "_script",
    "_util",
    "_mixin",
    "_protocol",
    "_strategy",
    "_adapter",
    "_factory",
    "_orchestrator",
    "_engine",
    "_gateway",
    "_sensor",
]

EXEMPT_FILES: set[str] = {"__init__.py", "__main__.py", "conftest.py"}


def check_compound_suffix(filename: str) -> list[str] | None:
    """Check a filename for compound suffix violations.

    Returns list of found suffixes if violation, None if clean.
    """
    if not filename.endswith(".py") or filename in EXEMPT_FILES:
        return None

    stem = filename[:-3]
    found = [s for s in KNOWN_ARCHITECTURAL_SUFFIXES if s in stem]

    if len(found) > 1:
        return found
    return None


def get_staged_files() -> list[str]:
    """Get list of staged .py files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [f for f in result.stdout.strip().split("\n") if f.endswith(".py")]
    except (subprocess.CalledProcessError, FileNotFoundError):    # guardian: File operations should check existence before access
        return []


def get_all_python_files(root: Path) -> list[Path]:
    """Scan for all .py files, excluding archives and venv."""
    exclude = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
    files = []
    for dirpath, dirnames, filenames in __import__("os").walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude]
        for f in filenames:
            if f.endswith(".py"):
                files.append(Path(dirpath) / f)
    return files


def main() -> int:
    staged_only = "--staged-only" in sys.argv

    if staged_only:
        files = get_staged_files()
        file_display = files
    else:
        root = Path.cwd()
        paths = get_all_python_files(root)
        files = [str(p) for p in paths]
        file_display = [str(p.relative_to(root)) for p in paths]

    violations = 0
    for filepath, display in zip(files, file_display, strict=False):
        filename = Path(filepath).name
        found = check_compound_suffix(filename)
        if found:
            violations += 1
            print(f"  VIOLATION: {display}")
            print(f"    Suffixes: {found}")
            print("    Rule: Files must have exactly ONE architectural suffix.")
            print()

    if violations:
        print(f"\n{violations} compound suffix violation(s) found.")
        print("Fix: Rename files to use a single primary suffix.")
        return 1

    if not staged_only:
        print("All files pass compound suffix validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
