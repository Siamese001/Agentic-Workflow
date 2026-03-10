"""Bulk-fix: replace hardcoded directory-exclusion sets with SSOT imports.

Strategy per file:
1. Read the source.
2. Identify which SSOT constants are needed (from scanner output).
3. Add the import block (if not already present).
4. Replace the hardcoded assignment with the SSOT expression.

Only replaces the *assignment RHS* for known variable names.
Falls through to a manual-review list for complex/inline cases.

Usage: python ops_scripts/ci/_fix_hardcoded_dirs.py [--dry-run]
"""

from __future__ import annotations

import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    TESTS_DIR,
)

SSOT_DIR_NAMES: frozenset[str] = (
    GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
)
MIN_OVERLAP = 2

SSOT_IMPORT_LINE = "from agentic_core.L5_safety.config.structure_blueprint.ssot import ("
SSOT_NAMES = {
    "GLOBAL_EXCLUDED_DIRS",
    "SOVEREIGN_EXCLUDED_FOLDERS",
    "DISCOVERY_EXCLUDED_TERRITORIES",
}

# Files that ARE the SSOT — never touch these
SSOT_PATHS = {
    "agentic_core/L5_safety/config/structure_blueprint/ssot.py",
    "agentic_core/L5_safety/config/structure_blueprint/_constants.py",
    "agentic_core/L5_safety/config/structure_blueprint/_verify.py",
}

SKIP_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES

SCAN_ROOTS = [
    ROOT / OPS_SCRIPTS_DIR,
    ROOT / AGENTIC_CORE_DIR,
    ROOT / TESTS_DIR,
    ROOT / APPS_RG_DIR,
    ROOT / APPS_LIC_DIR,
    ROOT / APPS_SHARED_DIR,
]

DRY_RUN = "--dry-run" in sys.argv


# ── helpers ──────────────────────────────────────────────────────────────────


def _excluded(path: pathlib.Path) -> bool:
    return bool(set(path.parts) & SKIP_DIRS)


def _string_literals_in_node(node: ast.AST) -> list[str]:
    strings: list[str] = []
    if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                strings.append(elt.value)
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in ("frozenset", "set"):
            for arg in node.args:
                strings.extend(_string_literals_in_node(arg))
    return strings


def _needed_ssot(overlap: list[str]) -> list[str]:
    needed = []
    if any(s in GLOBAL_EXCLUDED_DIRS for s in overlap):
        needed.append("GLOBAL_EXCLUDED_DIRS")
    if any(s in SOVEREIGN_EXCLUDED_FOLDERS for s in overlap):
        needed.append("SOVEREIGN_EXCLUDED_FOLDERS")
    if any(s in DISCOVERY_EXCLUDED_TERRITORIES for s in overlap):
        needed.append("DISCOVERY_EXCLUDED_TERRITORIES")
    return needed


def _ssot_expr(needed: list[str]) -> str:
    return " | ".join(needed)


def _has_ssot_import(source: str) -> bool:
    return SSOT_IMPORT_LINE in source


def _already_imports(source: str, name: str) -> bool:
    return bool(re.search(rf"\b{name}\b", source.split("def ")[0]))


def _insert_ssot_import(source: str, needed: list[str]) -> str:
    """Add SSOT import block after existing imports, before first non-import line."""
    import_block = (
        "from agentic_core.L5_safety.config.structure_blueprint.ssot import (\n"
        + "".join(f"    {n},\n" for n in sorted(needed))
        + ")\n"
    )

    # Check what's already imported
    already = [n for n in needed if _already_imports(source, n)]
    to_add = [n for n in needed if n not in already]
    if not to_add:
        return source

    # Try to add after last `from ... import` or `import ...` block
    lines = source.splitlines(keepends=True)
    last_import_idx = 0
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            last_import_idx = i
        elif stripped and not stripped.startswith("#") and i > 5 and last_import_idx > 0:
            # First non-import non-comment line after imports
            break

    insert_block = (
        "from agentic_core.L5_safety.config.structure_blueprint.ssot import (\n"
        + "".join(f"    {n},\n" for n in sorted(to_add))
        + ")\n"
    )
    lines.insert(last_import_idx + 1, insert_block)
    return "".join(lines)


def _make_frozenset_expr(needed: list[str]) -> str:
    """Build frozenset(...) expression using SSOT names."""
    return _ssot_expr(needed)


# ── per-file fix ──────────────────────────────────────────────────────────────


def fix_file(path: pathlib.Path) -> tuple[bool, list[str]]:
    """Returns (modified, list_of_notes)."""
    source = path.read_text(encoding="utf-8", errors="replace")
    original = source
    notes: list[str] = []

    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:
        return False, ["SKIP: syntax error"]

    # Collect all assignment nodes with hardcoded overlap
    replacements: list[tuple[int, int, str, list[str]]] = []  # (lineno, col, varname, needed)

    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            name = "<expr>"
            for t in node.targets:
                if isinstance(t, ast.Name):
                    name = t.id
            strings = _string_literals_in_node(node.value)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) >= MIN_OVERLAP:
                needed = _needed_ssot(overlap)
                replacements.append((node.lineno, node.col_offset, name, needed))

        elif isinstance(node, ast.AugAssign):
            name = node.target.id if isinstance(node.target, ast.Name) else "<expr>"
            strings = _string_literals_in_node(node.value)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) >= MIN_OVERLAP:
                needed = _needed_ssot(overlap)
                replacements.append((node.lineno, node.col_offset, name, needed))

    if not replacements:
        return False, []

    # Collect all needed SSOT names across this file
    all_needed: set[str] = set()
    for _, _, _, needed in replacements:
        all_needed.update(needed)

    # Add import block
    source = _insert_ssot_import(source, sorted(all_needed))

    # Now replace each hardcoded assignment line using line-based rewrite
    # Re-parse the modified source for accurate line numbers
    lines = source.splitlines(keepends=True)

    # We process replacements in reverse line order to keep line numbers stable
    for lineno, col_offset, varname, needed in sorted(replacements, key=lambda x: -x[0]):
        idx = lineno - 1  # 0-based
        if idx >= len(lines):
            notes.append(f"  SKIP L{lineno}: line out of range")
            continue

        line = lines[idx]

        # Pattern: `varname = {..."archives"...}` or `varname: ... = frozenset({...})`
        # We replace the RHS (everything after `=`) with the SSOT expression
        # Handle both `= {` and `= frozenset({` and multi-line
        # Find the `=` after the variable name
        assign_match = re.match(r"^(\s*" + re.escape(varname) + r"\s*(?::[^=]*)?)=", line)
        if not assign_match and varname == "<expr>":
            notes.append(f"  MANUAL L{lineno}: cannot auto-fix inline expression")
            continue
        if not assign_match:
            notes.append(f"  MANUAL L{lineno} {varname}: no assignment pattern found")
            continue

        prefix = assign_match.group(0)  # everything up to and including `=`
        ssot_expr = _ssot_expr(needed)

        # Detect if it's a multi-line set/frozenset — consume continuation lines
        new_rhs = f" {ssot_expr}\n"

        # Check if the assignment spans multiple lines (opening brace without close)
        brace_depth = 0
        end_idx = idx
        for j in range(idx, min(idx + 50, len(lines))):
            brace_depth += lines[j].count("{") + lines[j].count("[") + lines[j].count("(")
            brace_depth -= lines[j].count("}") + lines[j].count("]") + lines[j].count(")")
            if brace_depth <= 0:
                end_idx = j
                break

        # Replace lines[idx..end_idx] with single replacement line
        lines[idx : end_idx + 1] = [prefix + new_rhs]
        notes.append(f"  FIXED L{lineno} {varname} -> {ssot_expr}")

    source = "".join(lines)

    if source == original:
        return False, notes

    if not DRY_RUN:
        path.write_text(source, encoding="utf-8")

    return True, notes


# ── main ──────────────────────────────────────────────────────────────────────


def main() -> int:
    fixed_files = 0
    manual_review: list[str] = []

    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if _excluded(py_file):
                continue
            rel = str(py_file.relative_to(ROOT)).replace("\\", "/")
            if rel in SSOT_PATHS:
                continue

            modified, notes = fix_file(py_file)
            if modified or notes:
                label = "FIXED" if modified else "SKIPPED"
                print(f"[{label}] {rel}")
                for note in notes:
                    print(note)
                    if "MANUAL" in note:
                        manual_review.append(f"{rel}: {note.strip()}")
                if modified:
                    fixed_files += 1

    print(f"\n{'DRY-RUN ' if DRY_RUN else ''}Fixed {fixed_files} files.")
    if manual_review:
        print(f"\nManual review required ({len(manual_review)}):")
        for m in manual_review:
            print(f"  {m}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
