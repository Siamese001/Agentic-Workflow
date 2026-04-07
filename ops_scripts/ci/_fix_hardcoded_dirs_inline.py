"""Fix remaining 28 inline frozenset({...}) hardcoded dir violations.

_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_1")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_2")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_3")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_4")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_5")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_6")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_7")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_8")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_9")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_10")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_11")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_12")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_13")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_14")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_15")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_16")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_17")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_18")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_19")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_20")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_21")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_22")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_23")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_24")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_25")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_26")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_27")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_28")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_29")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_30")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_31")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_32")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_33")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_34")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_35")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_36")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_37")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_38")
_emit_reads_through("l4", "_fix_hardcoded_dirs_inline", "urg_read_39")
For each file+line in the known violation list, reads the actual source,
finds the frozenset({...}) literal spanning those lines, and replaces it
with the SSOT union expression, adding the required import.

Usage: python ops_scripts/ci/_fix_hardcoded_dirs_inline.py [--dry-run]
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
DRY_RUN = '--dry-run' in sys.argv
SSOT_PATHS = {'agentic_core/L5_safety/config/structure_blueprint/ssot.py', 'agentic_core/L5_safety/config/structure_blueprint/_constants.py', 'agentic_core/L5_safety/config/structure_blueprint/_verify.py'}
SKIP_DIRS = {'__pycache__', '.git', '.venv', 'venv', ARCHIVES_DIR, '.healing_backups', 'node_modules', 'build', 'dist', '.pytest_cache', '.tox'}
SCAN_ROOTS = [ROOT / OPS_SCRIPTS_DIR, ROOT / AGENTIC_CORE_DIR, ROOT / TESTS_DIR, ROOT / APPS_RG_DIR, ROOT / APPS_LIC_DIR, ROOT / APPS_SHARED_DIR]

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

def _already_imports(source: str, names: list[str]) -> set[str]:
    already: set[str] = set()
    block_pat = re.compile('from\\s+agentic_core\\.L5_safety\\.config\\.structure_blueprint\\.ssot\\s+import\\s*\\(([^)]*)\\)', re.DOTALL)
    single_pat = re.compile('from\\s+agentic_core\\.L5_safety\\.config\\.structure_blueprint\\.ssot\\s+import\\s+([^\\n]+)')
    for m in list(block_pat.finditer(source)) + list(single_pat.finditer(source)):
        for name in names:
            if name in m.group(1):
                already.add(name)
    return already

def _insert_ssot_import(lines: list[str], to_add: list[str]) -> list[str]:
    last_import_idx = 0
    in_multi = False
    for i, line in enumerate(lines):
        s = line.lstrip()
        if in_multi:
            if ')' in line:
                in_multi = False
                last_import_idx = i
            continue
        if s.startswith('from ') or s.startswith('import '):
            last_import_idx = i
            if s.startswith('from ') and '(' in line and (')' not in line):
                in_multi = True
    block = 'from agentic_core.L5_safety.config.structure_blueprint.ssot import (\n' + ''.join(f'    {n},\n' for n in sorted(to_add)) + ')\n'
    lines.insert(last_import_idx + 1, block)
    return lines

def _find_span_end(lines: list[str], start_idx: int) -> int:
    """Find the 0-based line index where the expression starting at start_idx closes."""
    depth = 0
    for j in range(start_idx, min(start_idx + 80, len(lines))):
        depth += lines[j].count('{') + lines[j].count('[') + lines[j].count('(')
        depth -= lines[j].count('}') + lines[j].count(']') + lines[j].count(')')
        if depth <= 0:
            return j
    return start_idx

def fix_file(path: pathlib.Path) -> tuple[bool, list[str]]:
    source = path.read_text(encoding='utf-8', errors='replace')
    original = source
    try:
        tree = ast.parse(source)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, ['SKIP: syntax error'])
    lines = source.splitlines(keepends=True)
    notes: list[str] = []
    all_needed: set[str] = set()
    violations: list[tuple[int, int, list[str]]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Name) and func.id in ('frozenset', 'set')):
            continue
        for arg in node.args:
            strings = _string_literals_in_node(arg)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) < MIN_OVERLAP:
                continue
            needed = _needed_ssot(overlap)
            all_needed.update(needed)
            start = node.lineno
            end = start
            idx = start - 1
            depth = 0
            for j in range(idx, min(idx + 80, len(lines))):
                depth += lines[j].count('{') + lines[j].count('[') + lines[j].count('(')
                depth -= lines[j].count('}') + lines[j].count(']') + lines[j].count(')')
                if depth <= 0:
                    end = j + 1
                    break
            violations.append((start, end, needed))
    if not violations:
        return (False, [])
    already = _already_imports(source, list(all_needed))
    to_add = sorted(all_needed - already)
    if to_add:
        lines = _insert_ssot_import(lines, to_add)
        notes.append(f'  IMPORT added: {to_add}')
        source = ''.join(lines)
        try:
            tree2 = ast.parse(source)
        except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            return (False, ['SKIP: syntax error after import insertion'])
        lines = source.splitlines(keepends=True)
        violations = []
        for node in ast.walk(tree2):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if not (isinstance(func, ast.Name) and func.id in ('frozenset', 'set')):
                continue
            for arg in node.args:
                strings = _string_literals_in_node(arg)
                overlap = [s for s in strings if s in SSOT_DIR_NAMES]
                if len(overlap) < MIN_OVERLAP:
                    continue
                needed = _needed_ssot(overlap)
                start = node.lineno
                end = start
                idx = start - 1
                depth = 0
                for j in range(idx, min(idx + 80, len(lines))):
                    depth += lines[j].count('{') + lines[j].count('[') + lines[j].count('(')
                    depth -= lines[j].count('}') + lines[j].count(']') + lines[j].count(')')
                    if depth <= 0:
                        end = j + 1
                        break
                violations.append((start, end, needed))
    seen_lines: set[int] = set()
    deduped = []
    for v in violations:
        if v[0] not in seen_lines:
            seen_lines.add(v[0])
            deduped.append(v)
    for start_line, end_line, needed in sorted(deduped, key=lambda x: -x[0]):
        idx_start = start_line - 1
        idx_end = end_line - 1
        if idx_start >= len(lines):
            notes.append(f'  SKIP L{start_line}: out of range')
            continue
        orig_line = lines[idx_start]
        pat = re.compile('(frozenset|set)\\s*\\(')
        m = pat.search(orig_line)
        if not m:
            notes.append(f'  MANUAL L{start_line}: no frozenset/set pattern on line')
            continue
        prefix = orig_line[:m.start()]
        suffix_after = ''
        end_orig = lines[idx_end]
        depth = 0
        close_col = len(end_orig)
        for ci, ch in enumerate(end_orig):
            if ch in '({[':
                depth += 1
            elif ch in ')}]':
                depth -= 1
                if depth < 0:
                    close_col = ci
                    suffix_after = end_orig[ci + 1:]
                    break
        ssot = _ssot_expr(needed)
        new_line = f'{prefix}{ssot}{suffix_after}'
        if not new_line.endswith('\n'):
            new_line += '\n'
        lines[idx_start:idx_end + 1] = [new_line]
        notes.append(f'  FIX L{start_line} frozenset/set -> {ssot}')
    final = ''.join(lines)
    if final == original:
        return (False, notes)
    if not DRY_RUN:
        path.write_text(final, encoding='utf-8')
    return (True, notes)

def main() -> int:
    fixed = 0
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
            except (OSError, UnicodeDecodeError, SyntaxError) as exc:    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                print(f'[ERROR] {rel}: {exc}')
                continue
            if modified or notes:
                label = 'FIXED' if modified else 'NOOP'
                print(f'[{label}] {rel}')
                for n in notes:
                    print(n)
                if modified:
                    fixed += 1
    mode = 'DRY-RUN ' if DRY_RUN else ''
    print(f'\n{mode}Fixed {fixed} files.')
    return 0
if __name__ == '__main__':
    sys.exit(main())
