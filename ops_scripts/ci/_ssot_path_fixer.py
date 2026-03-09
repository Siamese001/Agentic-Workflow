#!/usr/bin/env python3
"""
SSOT Path Fixer — AST-based, single-pass.

Scans production code folders for hardcoded directory/file strings that
should reference SSOT constants from agentic_core.L0_routing.config,
then fixes them in-place: replaces the string literal with the constant
name and injects/extends the import block.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    get_validated_project_root,
)

ROOT = get_validated_project_root()

SSOT_MAP: dict[str, str] = {
    "agentic_core": "AGENTIC_CORE_DIR",
    "apps_lic": "APPS_LIC_DIR",
    "apps_rg": "APPS_RG_DIR",
    "apps_shared": "APPS_SHARED_DIR",
    "archives": "ARCHIVES_DIR",
    "ops_scripts": "OPS_SCRIPTS_DIR",
    "system_learning": "SYSTEM_LEARNING_DIR",
    "agentic_core/L6_observability/dashboards": "DASHBOARD_DIR",
    "agentic_core/L0_maintenance": "L0_MAINTENANCE_DIR",
    "agentic_core/L0_routing": "L0_ROUTING_DIR",
    "agentic_core/L1_cognition": "L1_COGNITION_DIR",
    "agentic_core/L2_execution": "L2_EXECUTION_DIR",
    "agentic_core/L3_orchestration": "L3_ORCHESTRATION_DIR",
    "agentic_core/L4_state": "L4_STATE_DIR",
    "agentic_core/L5_safety": "L5_SAFETY_DIR",
    "agentic_core/L6_observability": "L6_OBSERVABILITY_DIR",
    "agent_discovery.json": "AGENT_DISCOVERY_JSON",
    "agent_discovery_manifest.json": "AGENT_DISCOVERY_MANIFEST_JSON",
    "runtime_state.json": "RUNTIME_STATE_JSON",
}

PROD_SCAN_ROOTS = [
    ROOT / AGENTIC_CORE_DIR,
    ROOT / APPS_LIC_DIR,
    ROOT / APPS_RG_DIR,
    ROOT / APPS_SHARED_DIR,
    ROOT / SYSTEM_LEARNING_DIR,
]

EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", ".pytest_cache", ".mypy_cache", ".nox"}

# Files that define the SSOT or are architectural boundary leaf nodes — never touch them
SSOT_FILES = {
    ROOT / "agentic_core/L0_routing/config/path_constants.py",
    ROOT / "agentic_core/L0_routing/config/__init__.py",
    # L5 zero-dependency leaf — stdlib-only by design; adding L0 import is a layer violation
    ROOT / "agentic_core/L5_safety/config/structure_blueprint/_constants.py",
    # L5 verifier — SCAN_ROOTS tuple is intentional static data, not path construction
    ROOT / "agentic_core/L5_safety/config/structure_blueprint/_verify.py",
    # Independent root resolver — must not import from L0_routing to avoid cycles
    ROOT / "agentic_core/utils/project_root_util.py",
    # This script itself
    Path(__file__).resolve(),
}

PATH_CALL_NAMES = {
    "Path",
    "open",
    "rglob",
    "glob",
    "exists",
    "mkdir",
    "iterdir",
    "join",
    "isdir",
    "isfile",
    "listdir",
    "walk",
    "scandir",
}


# ---------------------------------------------------------------------------
# AST visitor
# ---------------------------------------------------------------------------


class PathConstructionVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.hits: list[tuple[int, int, str, str, str]] = []
        # (lineno, col_offset, raw_value, const_name, context)

    def _check(self, node: ast.expr, context: str) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value.strip().rstrip("/")
            if val in SSOT_MAP:
                self.hits.append((node.lineno, node.col_offset, val, SSOT_MAP[val], context))

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        fname = ""
        if isinstance(func, ast.Name):
            fname = func.id
        elif isinstance(func, ast.Attribute):
            fname = func.attr
        if fname in PATH_CALL_NAMES:
            for arg in node.args:
                self._check(arg, f"Call({fname})")
            for kw in node.keywords:
                self._check(kw.value, f"Call({fname})")
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if isinstance(node.op, ast.Div):
            self._check(node.left, "BinOp(/)")
            self._check(node.right, "BinOp(/)")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for container in ast.walk(node.value):
            if isinstance(container, (ast.List, ast.Tuple)):
                for elt in container.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        v = elt.value.strip().rstrip("/")
                        if v in SSOT_MAP:
                            self.hits.append((elt.lineno, elt.col_offset, v, SSOT_MAP[v], "List/Tuple"))
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def existing_ssot_import(tree: ast.Module) -> tuple[ast.ImportFrom | None, set[str]]:
    """Return the first L0_routing.config ImportFrom node and all names it imports."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if "L0_routing.config" in mod or "path_constants" in mod:
                return node, {alias.name for alias in node.names}
    return None, set()


def last_top_level_import_lineno(tree: ast.Module) -> int:
    """Return the end_lineno of the last top-level import statement, or 0."""
    last = 0
    for node in tree.body:  # top-level only — never walk into class/function bodies
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if hasattr(node, "end_lineno"):
                last = max(last, node.end_lineno)
    return last


# ---------------------------------------------------------------------------
# Per-file fix
# ---------------------------------------------------------------------------


def fix_file(py_file: Path) -> tuple[int, int]:
    """Return (replacements_made, new_imports_added)."""
    try:
        src = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=str(py_file))
    except SyntaxError:
        return 0, 0

    visitor = PathConstructionVisitor()
    visitor.visit(tree)
    if not visitor.hits:
        return 0, 0

    # Deduplicate by (lineno, value)
    seen: set[tuple[int, str]] = set()
    hits: list[tuple[int, int, str, str, str]] = []
    for lineno, col, val, const, ctx in visitor.hits:
        k = (lineno, val)
        if k not in seen:
            seen.add(k)
            hits.append((lineno, col, val, const, ctx))
    hits.sort(key=lambda x: x[0])

    needed_consts = sorted({const for _, _, _, const, _ in hits})
    ssot_node, existing = existing_ssot_import(tree)
    missing_consts = [c for c in needed_consts if c not in existing]

    lines = src.splitlines(keepends=True)

    # --- Step 1: replace string literals with constant names ---
    replacements = 0
    for lineno, _col, val, const, _ctx in hits:
        idx = lineno - 1
        if idx >= len(lines):
            continue
        line = lines[idx]
        replaced = False
        for q in ("'", '"'):
            old = q + val + q
            if old in line:
                lines[idx] = line.replace(old, const, 1)
                replacements += 1
                replaced = True
                break
        if not replaced:
            # Try backslash variant
            for q in ("'", '"'):
                old = q + val.replace("/", "\\") + q
                if old in line:
                    lines[idx] = line.replace(old, const, 1)
                    replacements += 1
                    break

    # --- Step 2: inject/extend imports ---
    new_imports = 0
    if missing_consts:
        const_items = ",\n    ".join(missing_consts)
        new_import_block = f"from agentic_core.L0_routing.config import (\n    {const_items},\n)\n"

        if ssot_node is not None:
            # Extend the existing import block — ssot_node is always top-level
            start = ssot_node.lineno - 1
            end = ssot_node.end_lineno - 1
            # Build the full updated set of imported names
            all_names = sorted(existing | set(missing_consts))
            names_str = ",\n    ".join(all_names)
            updated_import = f"from agentic_core.L0_routing.config import (\n    {names_str},\n)\n"
            lines[start : end + 1] = [updated_import]
        else:
            # Re-parse with current lines to get accurate top-level import position
            try:
                tree2 = ast.parse("".join(lines))
            except SyntaxError:
                tree2 = tree
            insert_after = last_top_level_import_lineno(tree2)
            # insert_after is 1-based end_lineno; 0-based index is insert_after
            # Insert AFTER that line means index = insert_after (0-based line after last import)
            if insert_after == 0:
                # No imports at all — insert at position 0 (before everything)
                lines.insert(0, new_import_block)
            else:
                lines.insert(insert_after, new_import_block)

        new_imports = len(missing_consts)

    if replacements > 0 or new_imports > 0:
        py_file.write_text("".join(lines), encoding="utf-8")

    return replacements, new_imports


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    total_files = 0
    total_replacements = 0
    total_new_imports = 0
    errors: list[tuple[str, str]] = []

    for scan_root in PROD_SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if any(part in EXCLUDE_DIRS for part in py_file.parts):
                continue
            if py_file.resolve() in SSOT_FILES:
                continue
            try:
                if dry_run:
                    src = py_file.read_text(encoding="utf-8", errors="replace")
                    try:
                        tree = ast.parse(src)
                    except SyntaxError:
                        continue
                    v = PathConstructionVisitor()
                    v.visit(tree)
                    if v.hits:
                        rel = py_file.relative_to(ROOT).as_posix()
                        _, existing = existing_ssot_import(tree)
                        needed = sorted({c for _, _, _, c, _ in v.hits})
                        missing = [c for c in needed if c not in existing]
                        print(f"WOULD FIX: {rel}  (hits={len(v.hits)}, new_imports={len(missing)})")
                        total_files += 1
                else:
                    replacements, new_imports = fix_file(py_file)
                    if replacements > 0 or new_imports > 0:
                        rel = py_file.relative_to(ROOT).as_posix()
                        print(f"FIXED: {rel}  (replacements={replacements}, new_imports={new_imports})")
                        total_files += 1
                        total_replacements += replacements
                        total_new_imports += new_imports
            except Exception as exc:
                rel = py_file.relative_to(ROOT).as_posix()
                errors.append((rel, str(exc)))

    print()
    if dry_run:
        print(f"DRY RUN: {total_files} files would be fixed")
    else:
        print(
            f"DONE: {total_files} files fixed, {total_replacements} string replacements, {total_new_imports} import names added"
        )
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for r, e in errors:
            print(f"  {r}: {e}")


if __name__ == "__main__":
    main()
