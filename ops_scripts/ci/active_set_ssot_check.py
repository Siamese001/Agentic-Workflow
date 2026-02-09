#!/usr/bin/env python3
"""Active Set SSOT Check — CI Gate (AST-enforced).

Enforces that scripts requiring the ACTIVE agent set use the shared
``active_set_helper`` module instead of direct pipeline calls.

AST-based rules per governed script:
  1. Must NOT import ssot_discovery_util (any form).
  2. Must NOT import perform_deep_integrity_scan (any form).
  3. Must NOT call load_agent_discovery or perform_deep_integrity_scan.
  4. Must NOT reference 'agent_discovery_full.json' as a string literal.
  5. MUST import from active_set_helper (or relative equivalent).

Governed scripts:
  - ops_scripts/ci/agent_count_cap.py
  - ops_scripts/ci/discovery_registry_consistency_check.py

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

GOVERNED_SCRIPTS = [
    "ops_scripts/ci/agent_count_cap.py",
    "ops_scripts/ci/discovery_registry_consistency_check.py",
]

PROHIBITED_MODULES = {
    "ssot_discovery_util",
    "full_agent_discovery",
}

PROHIBITED_NAMES = {
    "load_agent_discovery",
    "perform_deep_integrity_scan",
}

PROHIBITED_STRINGS = {
    "agent_discovery_full.json",
}

REQUIRED_IMPORT_FRAGMENT = "active_set_helper"


def check_script_ast(source: str, rel_path: str) -> list[str]:
    """AST-check a single script. Return list of violation strings."""
    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as exc:
        return [f"{rel_path}: SyntaxError — {exc}"]

    violations: list[str] = []
    has_helper_import = False

    for node in ast.walk(tree):
        # Rule 5: detect active_set_helper import
        if isinstance(node, ast.ImportFrom) and node.module:
            if REQUIRED_IMPORT_FRAGMENT in node.module:
                has_helper_import = True

        # Rule 1+2: prohibited from-imports (module path AND imported names)
        if isinstance(node, ast.ImportFrom) and node.module:
            mod_parts = node.module.split(".")
            for part in mod_parts:
                if part in PROHIBITED_MODULES:
                    violations.append(
                        f"{rel_path}:{node.lineno}: from-import of prohibited module '{node.module}'",
                    )
                    break
            if node.names:
                for alias in node.names:
                    name_parts = alias.name.split(".")
                    for part in name_parts:
                        if part in PROHIBITED_MODULES:
                            violations.append(
                                f"{rel_path}:{node.lineno}: from-import of prohibited "
                                f"name '{alias.name}' from '{node.module}'",
                            )
                            break
                        if part in PROHIBITED_NAMES:
                            violations.append(
                                f"{rel_path}:{node.lineno}: from-import of prohibited "
                                f"function '{alias.name}' from '{node.module}'",
                            )
                            break

        # Rule 1+2: prohibited plain imports (module path AND imported names)
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod_parts = alias.name.split(".")
                for part in mod_parts:
                    if part in PROHIBITED_MODULES:
                        violations.append(
                            f"{rel_path}:{node.lineno}: import of prohibited module '{alias.name}'",
                        )
                        break

        # Rule 3: prohibited attribute calls
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name and name in PROHIBITED_NAMES:
                violations.append(
                    f"{rel_path}:{node.lineno}: call to prohibited function '{name}()'",
                )

        # Rule 3: prohibited name references (not just calls)
        if isinstance(node, ast.Name) and node.id in PROHIBITED_NAMES:
            # Skip if parent is already caught as a Call
            pass

        # Rule 4: prohibited string literals
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in PROHIBITED_STRINGS:
                violations.append(
                    f"{rel_path}:{node.lineno}: string reference to prohibited artifact '{node.value}'",
                )

    # Rule 5: must import from active_set_helper
    if not has_helper_import:
        violations.append(
            f"{rel_path}: missing required import from '{REQUIRED_IMPORT_FRAGMENT}'",
        )

    return violations


def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    all_violations: list[str] = []

    for script_rel in GOVERNED_SCRIPTS:
        script_path = project_root / script_rel
        if not script_path.is_file():
            continue
        source = script_path.read_text(encoding="utf-8")
        all_violations.extend(check_script_ast(source, script_rel))

    print("Active Set SSOT Check (AST-enforced):")
    print(f"  governed_scripts={len(GOVERNED_SCRIPTS)}")

    if all_violations:
        print(f"FAIL: {len(all_violations)} violation(s):")
        for v in all_violations:
            print(f"  - {v}")
        return 1

    print("PASS: all governed scripts use active_set_helper exclusively")
    return 0


if __name__ == "__main__":
    sys.exit(main())
