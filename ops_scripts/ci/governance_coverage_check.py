#!/usr/bin/env python3
"""Governance Coverage Audit — CI Gate.

Scans all ops_scripts/ci/*.py scripts. For each script that references
any SSOT-governed resource, asserts it imports from active_set_helper.

Detection layers (all AST-first where applicable):
  1. AST: direct import of ssot_discovery_util or full_agent_discovery modules.
  2. AST: import of load_agent_discovery / perform_deep_integrity_scan names.
  3. String: reference to agent_discovery_full.json literal.

This ensures no CI script bypasses the SSOT active-set abstraction.

Exit 0 = all governed, exit 1 = bypass detected.
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import OPS_SCRIPTS_DIR, get_validated_project_root

# Scripts that ARE the governance infrastructure — exempt from self-check.
# Justification required for each entry.
_EXEMPT_SCRIPTS = frozenset(
    {
        "__init__.py",  # package marker, no logic
        "active_set_helper.py",  # IS the helper — defines get_active_set
        "active_set_ssot_check.py",  # enforces SSOT rules on other scripts
        "active_set_snapshot_check.py",  # consumes helper, IS governance infra
        "gate_consistency_check.py",  # cross-gate validator, references names for validation
        "governance_coverage_check.py",  # THIS script — self-referential detection patterns
        "mro_new_diamond_check.py",  # MRO entry-level gate, no active-set usage
    },
)

# Prohibited module names — direct import of these is a bypass
_PROHIBITED_MODULES = frozenset(
    {
        "ssot_discovery_util",
        "full_agent_discovery",
    },
)

# Prohibited function/name imports
_PROHIBITED_NAMES = frozenset(
    {
        "load_agent_discovery",
        "perform_deep_integrity_scan",
    },
)

# String literal pattern for discovery output file
_DISCOVERY_OUTPUT_PATTERN = re.compile(r"\bagent_discovery_full\.json\b")

# The required import target
_REQUIRED_IMPORT = "active_set_helper"


def _imports_helper(tree: ast.AST) -> bool:
    """Check if AST imports from active_set_helper."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and _REQUIRED_IMPORT in node.module:
                return True
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if _REQUIRED_IMPORT in alias.name:
                    return True
    return False


def _find_governed_references(tree: ast.AST, source: str) -> list[str]:
    """Return list of governed references found via AST + string scan."""
    found: list[str] = []

    for node in ast.walk(tree):
        # Layer 1: direct module imports
        if isinstance(node, ast.ImportFrom) and node.module:
            for mod in _PROHIBITED_MODULES:
                if mod in node.module:
                    found.append(f"import from '{node.module}' (prohibited module)")
                    break
        if isinstance(node, ast.Import):
            for alias in node.names:
                for mod in _PROHIBITED_MODULES:
                    if mod in alias.name:
                        found.append(f"import '{alias.name}' (prohibited module)")
                        break

        # Layer 2: importing prohibited names
        if isinstance(node, ast.ImportFrom) and node.names:
            for alias in node.names:
                if alias.name in _PROHIBITED_NAMES:
                    found.append(f"import name '{alias.name}' (prohibited)")

    # Layer 3: string literal reference to discovery output
    if _DISCOVERY_OUTPUT_PATTERN.search(source):
        found.append("string reference to 'agent_discovery_full.json'")

    return found


def main() -> int:
    project_root = get_validated_project_root()
    ci_dir = project_root / OPS_SCRIPTS_DIR / "ci"

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

        try:
            tree = ast.parse(source)
        except SyntaxError:
            continue

        refs = _find_governed_references(tree, source)
        if not refs:
            continue

        governed += 1
        if not _imports_helper(tree):
            rel = str(pyfile.relative_to(project_root)).replace("\\", "/")
            violations.append(
                f"{rel}: {refs} but does NOT import {_REQUIRED_IMPORT}",
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
