#!/usr/bin/env python3
"""Governance Coverage Audit — CI Gate.

Scans all ops_scripts/ci/*.py scripts. For each script that references
any SSOT-governed resource (agent_discovery_full.json, load_agent_discovery,
perform_deep_integrity_scan), asserts it imports from active_set_helper.

This ensures no CI script bypasses the SSOT active-set abstraction.

Exit 0 = all governed, exit 1 = bypass detected.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

# Scripts that ARE the governance infrastructure — exempt from self-check
_EXEMPT_SCRIPTS = frozenset(
    {
        "__init__.py",
        "active_set_helper.py",
        "active_set_ssot_check.py",
        "active_set_snapshot_check.py",
        "gate_consistency_check.py",
        "governance_coverage_check.py",
    }
)

# Patterns indicating SSOT-governed resource access
_GOVERNED_PATTERNS = [
    re.compile(r"\bagent_discovery_full\.json\b"),
    re.compile(r"\bload_agent_discovery\b"),
    re.compile(r"\bperform_deep_integrity_scan\b"),
]

# The required import target
_REQUIRED_IMPORT = "active_set_helper"


def _imports_helper(source: str) -> bool:
    """Check if source imports from active_set_helper (AST-based)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and _REQUIRED_IMPORT in node.module:
                return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if _REQUIRED_IMPORT in alias.name:
                    return True
    return False


def _references_governed(source: str) -> list[str]:
    """Return list of governed patterns found in source."""
    found: list[str] = []
    for pat in _GOVERNED_PATTERNS:
        if pat.search(source):
            found.append(pat.pattern)
    return found


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    ci_dir = project_root / "ops_scripts" / "ci"

    if not ci_dir.is_dir():
        print("FAIL: ops_scripts/ci/ not found", file=sys.stderr)
        return 1

    violations: list[str] = []
    scanned = 0
    governed = 0

    for pyfile in sorted(ci_dir.glob("*.py")):
        if pyfile.name in _EXEMPT_SCRIPTS:
            continue
        scanned += 1

        try:
            source = pyfile.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        refs = _references_governed(source)
        if not refs:
            continue

        governed += 1
        if not _imports_helper(source):
            rel = str(pyfile.relative_to(project_root)).replace("\\", "/")
            violations.append(
                f"{rel}: references {refs} but does NOT import {_REQUIRED_IMPORT}",
            )

    print("Governance Coverage Audit:")
    print(f"  scanned={scanned}  governed={governed}  violations={len(violations)}")

    if violations:
        print(f"FAIL: {len(violations)} script(s) bypass SSOT:")
        for v in violations:
            print(f"  - {v}")
        return 1

    print("PASS: 100% governance coverage — no CI script bypasses SSOT")
    return 0


if __name__ == "__main__":
    sys.exit(main())
