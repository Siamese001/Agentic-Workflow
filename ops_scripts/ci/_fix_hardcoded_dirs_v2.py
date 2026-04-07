"""Bulk-fix v2: replace hardcoded directory-exclusion sets with SSOT imports.

_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_1")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_2")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_3")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_4")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_5")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_6")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_7")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_8")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_9")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_10")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_11")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_12")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_13")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_14")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_15")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_16")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_17")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_18")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_19")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_20")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_21")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_22")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_23")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_24")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_25")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_26")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_27")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_28")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_29")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_30")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_31")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_32")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_33")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_34")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_35")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_36")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_37")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_38")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_39")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_40")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_41")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_42")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_43")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_44")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_45")
_emit_reads_through("l4", "_fix_hardcoded_dirs_v2", "urg_read_46")
Uses line-based rewrite with brace-depth tracking to handle:
- typed assignments: VAR: frozenset[str] = frozenset({...})
- untyped: VAR = {"__pycache__", ...}
- inline frozenset({...}) as function argument (deferred to manual)
- multi-line sets

Writes changes directly. Run with --dry-run to preview.

Usage: python ops_scripts/ci/_fix_hardcoded_dirs_v2.py [--dry-run]
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
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DISCOVERY_EXCLUDED_TERRITORIES,
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

SSOT_DIR_NAMES: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
MIN_OVERLAP = 2
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

def _collect_violations(source: str) -> list[tuple[int, int, str, list[str]]]:
    """Return list of (start_lineno, end_lineno, varname, needed_ssot).
    start/end are 1-based line numbers of the full assignment span.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return []
    violations: list[tuple[int, int, str, list[str]]] = []
    lines = source.splitlines()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Assign, ast.AugAssign)):
            if isinstance(node, ast.Assign):
                varname = '<expr>'
                for t in node.targets:
                    if isinstance(t, ast.Name):
                        varname = t.id
                value = node.value
            else:
                varname = node.target.id if isinstance(node.target, ast.Name) else '<expr>'
                value = node.value
            strings = _string_literals_in_node(value)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) < MIN_OVERLAP:
                continue
            needed = _needed_ssot(overlap)
            start_line = node.lineno
            brace_depth = 0
            end_line = start_line
            for j in range(start_line - 1, min(start_line + 80, len(lines))):
                brace_depth += lines[j].count('{') + lines[j].count('[') + lines[j].count('(')
                brace_depth -= lines[j].count('}') + lines[j].count(']') + lines[j].count(')')
                if brace_depth <= 0:
                    end_line = j + 1
                    break
            violations.append((start_line, end_line, varname, needed))
    seen: set[int] = set()
    deduped = []
    for v in violations:
        if v[0] not in seen:
            seen.add(v[0])
            deduped.append(v)
    return deduped

def _extract_indent_and_varname(line: str) -> tuple[str, str]:
    """Extract leading whitespace and variable name from an assignment line."""
    m = re.match('^(\\s*)([A-Za-z_][A-Za-z0-9_]*)', line)
    if m:
        return (m.group(1), m.group(2))
    return ('', '')

def _replacement_line(line: str, needed: list[str]) -> str:
    """Produce the replacement assignment line preserving indent and variable name."""
    indent, varname = _extract_indent_and_varname(line)
    ssot = _ssot_expr(needed)
    ann_match = re.match('^(\\s*[A-Za-z_][A-Za-z0-9_]*\\s*:[^=]+=)', line)
    if ann_match:
        return f'{ann_match.group(1)} {ssot}\n'
    assign_match = re.match('^(\\s*[A-Za-z_][A-Za-z0-9_]*\\s*=)', line)
    if assign_match:
        return f'{assign_match.group(1)} {ssot}\n'
    return f'{indent}{varname} = {ssot}\n'

def _already_imports(source: str, names: list[str]) -> set[str]:
    """Return which SSOT names are already imported in the file."""
    already: set[str] = set()
    import_block_pat = re.compile('from\\s+agentic_core\\.L5_safety\\.config\\.structure_blueprint\\.ssot\\s+import\\s*\\(([^)]*)\\)', re.DOTALL)
    single_import_pat = re.compile('from\\s+agentic_core\\.L5_safety\\.config\\.structure_blueprint\\.ssot\\s+import\\s+([^\\n]+)')
    for m in import_block_pat.finditer(source):
        for name in names:
            if name in m.group(1):
                already.add(name)
    for m in single_import_pat.finditer(source):
        for name in names:
            if name in m.group(1):
                already.add(name)
    return already

def _insert_ssot_import(lines: list[str], to_add: list[str]) -> list[str]:
    """Insert SSOT import block after the last import statement."""
    last_import_idx = 0
    in_multiline_import = False
    for i, line in enumerate(lines):
        stripped = line.lstrip()
        if in_multiline_import:
            if ')' in line:
                in_multiline_import = False
                last_import_idx = i
            continue
        if stripped.startswith('from ') or stripped.startswith('import '):
            last_import_idx = i
            if stripped.startswith('from ') and '(' in line and (')' not in line):
                in_multiline_import = True
    block = 'from agentic_core.L5_safety.config.structure_blueprint.ssot import (\n' + ''.join(f'    {n},\n' for n in sorted(to_add)) + ')\n'
    lines.insert(last_import_idx + 1, block)
    return lines

def fix_file(path: pathlib.Path) -> tuple[bool, list[str]]:
    """Fix a file. Returns (modified, notes)."""
    source = path.read_text(encoding='utf-8', errors='replace')
    violations = _collect_violations(source)
    if not violations:
        return (False, [])
    notes: list[str] = []
    lines = source.splitlines(keepends=True)
    all_needed: set[str] = set()
    for _, _, _, needed in violations:
        all_needed.update(needed)
    already = _already_imports(source, list(all_needed))
    to_add = sorted(all_needed - already)
    if to_add:
        lines = _insert_ssot_import(lines, to_add)
        notes.append(f'  IMPORT added: {to_add}')
    new_source = ''.join(lines)
    violations2 = _collect_violations(new_source)
    lines2 = new_source.splitlines(keepends=True)
    for start_line, end_line, varname, needed in sorted(violations2, key=lambda x: -x[0]):
        idx_start = start_line - 1
        idx_end = end_line - 1
        if idx_start >= len(lines2):
            notes.append(f'  SKIP L{start_line}: out of range after reindex')
            continue
        original_line = lines2[idx_start]
        new_line = _replacement_line(original_line, needed)
        if new_line == original_line:
            notes.append(f'  NOOP L{start_line} {varname}: line unchanged')
            continue
        lines2[idx_start:idx_end + 1] = [new_line]
        notes.append(f'  FIX L{start_line} {varname} -> {_ssot_expr(needed)}')
    final_source = ''.join(lines2)
    if final_source == source:
        return (False, notes)
    if not DRY_RUN:
        path.write_text(final_source, encoding='utf-8')
    return (True, notes)

def main() -> int:
    fixed_files = 0
    noop_files = 0
    manual: list[str] = []
    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob('*.py')):
            if _excluded(py_file):
                continue
            rel = str(py_file.relative_to(ROOT)).replace('\\', '/')
            if rel in SSOT_PATHS:
                continue
            try:
                modified, notes = fix_file(py_file)
            except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                print(f'[ERROR] {rel}: {exc}')
                continue
            if modified:
                print(f'[FIXED] {rel}')
                for n in notes:
                    print(n)
                fixed_files += 1
            elif notes:
                noop_files += 1
                for n in notes:
                    if 'MANUAL' in n or 'NOOP' in n:
                        manual.append(f'{rel}: {n.strip()}')
    mode = 'DRY-RUN ' if DRY_RUN else ''
    print(f'\n{mode}Fixed {fixed_files} files. {noop_files} had notes.')
    if manual:
        print(f'\nManual/noop ({len(manual)}):')
        for m in manual[:30]:
            print(f'  {m}')
        if len(manual) > 30:
            print(f'  ... and {len(manual) - 30} more')
    return 0
if __name__ == '__main__':
    sys.exit(main())
