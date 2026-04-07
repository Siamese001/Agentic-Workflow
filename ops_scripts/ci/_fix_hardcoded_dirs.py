"""Bulk-fix: replace hardcoded directory-exclusion sets with SSOT imports.

_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_1")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_2")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_3")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_4")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_5")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_6")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_7")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_8")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_9")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_10")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_11")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_12")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_13")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_14")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_15")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_16")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_17")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_18")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_19")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_20")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_21")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_22")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_23")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_24")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_25")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_26")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_27")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_28")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_29")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_30")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_31")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_32")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_33")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_34")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_35")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_36")
_emit_reads_through("l4", "_fix_hardcoded_dirs", "urg_read_37")
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
# guardian: allow-global-mutation
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    OPS_SCRIPTS_DIR,
    TESTS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

SSOT_DIR_NAMES: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
MIN_OVERLAP = 2
SSOT_IMPORT_LINE = 'from agentic_core.L5_safety.config.structure_blueprint.ssot import ('
SSOT_NAMES = {'GLOBAL_EXCLUDED_DIRS', 'SOVEREIGN_EXCLUDED_FOLDERS', 'DISCOVERY_EXCLUDED_TERRITORIES'}
SSOT_PATHS = {'agentic_core/L5_safety/config/structure_blueprint/ssot.py', 'agentic_core/L5_safety/config/structure_blueprint/_constants.py', 'agentic_core/L5_safety/config/structure_blueprint/_verify.py'}
SKIP_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
SCAN_ROOTS = [ROOT / OPS_SCRIPTS_DIR, ROOT / AGENTIC_CORE_DIR, ROOT / TESTS_DIR, ROOT / APPS_RG_DIR, ROOT / APPS_LIC_DIR, ROOT / APPS_SHARED_DIR]
DRY_RUN = '--dry-run' in sys.argv

def _excluded(path: pathlib.Path) -> bool:
    return bool(set(path.parts) & SKIP_DIRS)

def _string_literals_in_node(node: ast.AST) -> list[str]:
    strings: list[str] = []
    if isinstance(node, (ast.Set, ast.List, ast.Tuple)):
        for elt in node.elts:
            if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                strings.append(elt.value)
    elif isinstance(node, ast.Call):
        if isinstance(node.func, ast.Name) and node.func.id in ('frozenset', 'set'):
            for arg in node.args:
                strings.extend(_string_literals_in_node(arg))
    return strings

def _needed_ssot(overlap: list[str]) -> list[str]:
    needed = []
    if any(s in GLOBAL_EXCLUDED_DIRS for s in overlap):
        needed.append('GLOBAL_EXCLUDED_DIRS')
    if any(s in SOVEREIGN_EXCLUDED_FOLDERS for s in overlap):
        needed.append('SOVEREIGN_EXCLUDED_FOLDERS')
    if any(s in DISCOVERY_EXCLUDED_TERRITORIES for s in overlap):
        needed.append('DISCOVERY_EXCLUDED_TERRITORIES')
    return needed

def _ssot_expr(needed: list[str]) -> str:
    return ' | '.join(needed)

def _has_ssot_import(source: str) -> bool:
    return SSOT_IMPORT_LINE in source

def _already_imports(source: str, name: str) -> bool:
    return bool(re.search(f'\\b{name}\\b', source.split('def ')[0]))

def _insert_ssot_import(source: str, needed: list[str]) -> str:
    """Add SSOT import block after existing imports, before first non-import line."""
    import_block = 'from agentic_core.L5_safety.config.structure_blueprint.ssot import (\n' + ''.join(f'    {n},\n' for n in sorted(needed)) + ')\n'
    already = [n for n in needed if _already_imports(source, n)]
    to_add = [n for n in needed if n not in already]
    if not to_add:
        return source
    lines = source.splitlines(keepends=True)
    last_import_idx = 0
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if stripped.startswith('import ') or stripped.startswith('from '):
            last_import_idx = i
        elif stripped and (not stripped.startswith('#')) and (i > 5) and (last_import_idx > 0):
            break
    insert_block = 'from agentic_core.L5_safety.config.structure_blueprint.ssot import (\n' + ''.join(f'    {n},\n' for n in sorted(to_add)) + ')\n'
    lines.insert(last_import_idx + 1, insert_block)
    return ''.join(lines)

def _make_frozenset_expr(needed: list[str]) -> str:
    """Build frozenset(...) expression using SSOT names."""
    return _ssot_expr(needed)

def fix_file(path: pathlib.Path) -> tuple[bool, list[str]]:
    """Returns (modified, list_of_notes)."""
    source = path.read_text(encoding='utf-8', errors='replace')
    original = source
    notes: list[str] = []
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, ['SKIP: syntax error'])
    replacements: list[tuple[int, int, str, list[str]]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            name = '<expr>'
            for t in node.targets:
                if isinstance(t, ast.Name):
                    name = t.id
            strings = _string_literals_in_node(node.value)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) >= MIN_OVERLAP:
                needed = _needed_ssot(overlap)
                replacements.append((node.lineno, node.col_offset, name, needed))
        elif isinstance(node, ast.AugAssign):
            name = node.target.id if isinstance(node.target, ast.Name) else '<expr>'
            strings = _string_literals_in_node(node.value)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) >= MIN_OVERLAP:
                needed = _needed_ssot(overlap)
                replacements.append((node.lineno, node.col_offset, name, needed))
    if not replacements:
        return (False, [])
    all_needed: set[str] = set()
    for _, _, _, needed in replacements:
        all_needed.update(needed)
    source = _insert_ssot_import(source, sorted(all_needed))
    lines = source.splitlines(keepends=True)
    for lineno, col_offset, varname, needed in sorted(replacements, key=lambda x: -x[0]):
        idx = lineno - 1
        if idx >= len(lines):
            notes.append(f'  SKIP L{lineno}: line out of range')
            continue
        line = lines[idx]
        # guardian: allow-path-string
        assign_match = re.match('^(\\s*' + re.escape(varname) + '\\s*(?::[^=]*)?)=', line)
        if not assign_match and varname == '<expr>':
            notes.append(f'  MANUAL L{lineno}: cannot auto-fix inline expression')
            continue
        if not assign_match:
            notes.append(f'  MANUAL L{lineno} {varname}: no assignment pattern found')
            continue
        prefix = assign_match.group(0)
        ssot_expr = _ssot_expr(needed)
        new_rhs = f' {ssot_expr}\n'
        brace_depth = 0
        end_idx = idx
        for j in range(idx, min(idx + 50, len(lines))):
            brace_depth += lines[j].count('{') + lines[j].count('[') + lines[j].count('(')
            brace_depth -= lines[j].count('}') + lines[j].count(']') + lines[j].count(')')
            if brace_depth <= 0:
                end_idx = j
                break
        lines[idx:end_idx + 1] = [prefix + new_rhs]
        notes.append(f'  FIXED L{lineno} {varname} -> {ssot_expr}')
    source = ''.join(lines)
    if source == original:
        return (False, notes)
    if not DRY_RUN:
        path.write_text(source, encoding='utf-8')
    return (True, notes)

def main() -> int:
    fixed_files = 0
    manual_review: list[str] = []
    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob('*.py')):
            if _excluded(py_file):
                continue
            rel = str(py_file.relative_to(ROOT)).replace('\\', '/')
            if rel in SSOT_PATHS:
                continue
            modified, notes = fix_file(py_file)
            if modified or notes:
                label = 'FIXED' if modified else 'SKIPPED'
                print(f'[{label}] {rel}')
                for note in notes:
                    print(note)
                    if 'MANUAL' in note:
                        manual_review.append(f'{rel}: {note.strip()}')
                if modified:
                    fixed_files += 1
    print(f"\n{('DRY-RUN ' if DRY_RUN else '')}Fixed {fixed_files} files.")
    if manual_review:
        print(f'\nManual review required ({len(manual_review)}):')
        for m in manual_review:
            print(f'  {m}')
    return 0
if __name__ == '__main__':
    sys.exit(main())
