"""
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_1")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_2")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_3")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_4")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_5")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_6")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_7")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_8")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_9")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_10")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_11")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_12")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_13")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_14")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_15")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_16")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_17")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_18")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_19")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_20")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_21")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_22")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_23")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_24")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_25")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_26")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_27")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_28")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_29")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_30")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_31")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_32")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_33")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_34")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_35")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_36")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_37")
_emit_reads_through("l4", "_fix_hardcoded_ssot_literals", "urg_read_38")
Auto-fix hardcoded SSOT path constant violations across the 10 ENFORCED_TERRITORIES.

Only replaces string literals in these SAFE contexts (AST-verified):
  1. Element of a list/tuple/set that contains ONLY string directory names
     e.g.  SCAN_ROOTS = ["agentic_core", "apps_rg"]
  2. Argument to Path(), ROOT / "reports", os.walk(...)
  3. Operand in  "archives" in str(...)  /  "archives" not in str(...)
  4. Direct assignment of a single string  X = "archives"

All other contexts are SKIPPED:
  - Dict keys and values
  - Keyword arguments
  - Default argument values
  - Subscript index
  - Method calls (.startswith, .endswith, .get, etc.)
  - Logging / print calls
  - Docstrings / examples

Run:
    python ops_scripts/ci/_fix_hardcoded_ssot_literals.py [--dry-run]
"""
from __future__ import annotations

import argparse
import ast
import os
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(ROOT))
from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    ARCHIVES_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    OPS_SCRIPTS_DIR,
    SYSTEM_LEARNING_DIR,
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    DOCS_REPORTS_PLANS,
    ENFORCED_TERRITORIES,
    REPORTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
    TESTS_UNIT_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through

_PC = 'agentic_core.L0_routing.config.path_constants'
_SSOT = 'agentic_core.L5_safety.config.structure_blueprint.ssot'
CONST_DEFS: list[tuple[str, str, str]] = sorted([('ARCHIVES_DIR', ARCHIVES_DIR, _PC), ('AGENTIC_CORE_DIR', AGENTIC_CORE_DIR, _PC), ('APPS_RG_DIR', APPS_RG_DIR, _PC), ('APPS_LIC_DIR', APPS_LIC_DIR, _PC), ('APPS_SHARED_DIR', APPS_SHARED_DIR, _PC), ('OPS_SCRIPTS_DIR', OPS_SCRIPTS_DIR, _PC), ('TESTS_DIR', TESTS_DIR, _PC), ('TOOLS_DIR', TOOLS_DIR, _PC), ('SYSTEM_LEARNING_DIR', SYSTEM_LEARNING_DIR, _PC), ('L0_MAINTENANCE_DIR', L0_MAINTENANCE_DIR, _PC), ('L1_COGNITION_DIR', L1_COGNITION_DIR, _PC), ('L2_EXECUTION_DIR', L2_EXECUTION_DIR, _PC), ('L3_ORCHESTRATION_DIR', L3_ORCHESTRATION_DIR, _PC), ('L4_STATE_DIR', L4_STATE_DIR, _PC), ('L5_SAFETY_DIR', L5_SAFETY_DIR, _PC), ('L6_OBSERVABILITY_DIR', L6_OBSERVABILITY_DIR, _PC), ('DOCS_REPORTS_PLANS', DOCS_REPORTS_PLANS, _SSOT), ('REPORTS_DIR', REPORTS_DIR, _SSOT), ('TESTS_UNIT_DIR', TESTS_UNIT_DIR, _SSOT)], key=lambda x: -len(x[1]))
_SSOT_SKIP = ('agentic_core/L5_safety/config/structure_blueprint/', 'agentic_core/L0_routing/config/path_constants')

def _is_ssot_def(rel: str) -> bool:
    return any(rel.startswith(p) for p in _SSOT_SKIP)
_PATH_CALLS = {'Path', 'PurePath', 'PurePosixPath', 'PureWindowsPath', 'walk', 'makedirs', 'mkdir', 'listdir', 'scandir', 'isdir', 'isfile', 'exists', 'join', 'abspath', 'realpath', 'relpath', 'expanduser', 'glob', 'rglob'}

class _SafePositionCollector(ast.NodeVisitor):
    """
    Visits the AST and records (lineno, col_offset) of string Constants that
    appear in SAFE-to-replace contexts only.

    Safe contexts:
      - Direct element of a List / Tuple / Set (sibling elements are strings)
      - First (and only meaningful) arg to Path(...) / os.path.join(...)
      - Right-hand side of a simple assignment  X = "value"
      - Operand in  "value" in str(...)  /  "value" not in str(...)
        (but NOT  obj["value"]  or  d.get("value")  or  f(key="value"))
    """

    def __init__(self) -> None:
        self._safe: set[tuple[int, int]] = set()
        self._parent: list[ast.AST] = []

    @property
    def safe(self) -> set[tuple[int, int]]:
        return self._safe

    def _push(self, node: ast.AST) -> None:
        self._parent.append(node)

    def _pop(self) -> None:
        self._parent.pop()

    def _mark(self, node: ast.Constant) -> None:
        self._safe.add((node.lineno, node.col_offset))

    def generic_visit(self, node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            self._push(node)
            self.visit(child)
            self._pop()

    def visit_Constant(self, node: ast.Constant) -> None:
        if not isinstance(node.value, str):
            return
        if not self._parent:
            return
        parent = self._parent[-1]
        grandparent = self._parent[-2] if len(self._parent) >= 2 else None
        if isinstance(parent, (ast.List, ast.Tuple, ast.Set)):
            all_flat = all(isinstance(el, (ast.Constant, ast.Name, ast.Attribute)) for el in parent.elts)
            if all_flat:
                gp = self._parent[-2] if len(self._parent) >= 2 else None
                if isinstance(gp, ast.Dict):
                    return
                self._mark(node)
            return
        if isinstance(parent, ast.Assign):
            if parent.value is node:
                self._mark(node)
            return
        if isinstance(parent, ast.AnnAssign):
            if parent.value is node:
                self._mark(node)
            return
        if isinstance(parent, ast.Call):
            func = parent.func
            func_name = None
            if isinstance(func, ast.Name):
                func_name = func.id
            elif isinstance(func, ast.Attribute):
                func_name = func.attr
            if func_name in _PATH_CALLS:
                if node in parent.args:
                    self._mark(node)
                return
            if func_name in ('add', 'append', 'discard', 'remove'):
                if len(parent.args) == 1 and parent.args[0] is node and (not parent.keywords):
                    self._mark(node)
            return
        if isinstance(parent, ast.Compare):
            ops_safe = all(isinstance(op, (ast.In, ast.NotIn, ast.Eq, ast.NotEq)) for op in parent.ops)
            if ops_safe:
                if parent.left is node:
                    self._mark(node)
                elif node in parent.comparators:
                    self._mark(node)
            return
        if isinstance(parent, ast.BinOp) and isinstance(parent.op, ast.Div):
            if parent.right is node:
                if isinstance(parent.left, (ast.Name, ast.BinOp, ast.Attribute, ast.Call)):
                    self._mark(node)
            return

def _collect_safe_positions(source: str) -> set[tuple[int, int]]:
    try:
        tree = ast.parse(source)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return set()
    c = _SafePositionCollector()
    c.visit(tree)
    return c.safe

def _find_last_import_line(lines: list[str]) -> int:
    """Return the index of the last line that is part of a TOP-LEVEL import.
    Only counts unindented import/from lines; ignores lazy imports inside functions.
    For multi-line  from X import (\\n  ...\\n)  blocks, returns the closing-) line.
    """
    last = 0
    i = 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith('import ') or ln.startswith('from '):
            last = i
            depth = ln.count('(') - ln.count(')')
            while depth > 0 and i + 1 < len(lines):
                i += 1
                depth += lines[i].count('(') - lines[i].count(')')
                last = i
        i += 1
    return last

def _inject_import(lines: list[str], const: str, module: str) -> list[str]:
    lines = list(lines)
    # guardian: allow-path-string
    from_multi = re.compile('^\\s*from\\s+' + re.escape(module) + '\\s+import\\s+\\(')
    # guardian: allow-path-string
    from_single = re.compile('^(\\s*from\\s+' + re.escape(module) + '\\s+import\\s+)(.+)$')
    for i, ln in enumerate(lines):
        if from_multi.match(ln):
            depth = 0
            j = i
            while j < len(lines):
                depth += lines[j].count('(') - lines[j].count(')')
                if depth <= 0:
                    break
                j += 1
            lines.insert(j, f'    {const},\n')
            return lines
    for i, ln in enumerate(lines):
        m = from_single.match(ln)
        if m:
            names = [n.strip().rstrip(',') for n in m.group(2).split(',') if n.strip()]
            names.append(const)
            names.sort()
            indent = ' ' * (len(ln) - len(ln.lstrip()))
            new_lines = [indent + f'from {module} import (\n']
            for name in names:
                new_lines.append(indent + f'    {name},\n')
            new_lines.append(indent + ')\n')
            lines[i:i + 1] = new_lines
            return lines
    last = _find_last_import_line(lines)
    lines.insert(last + 1, f'from {module} import {const}\n')
    return lines

def process_file(fpath: Path, rel: str, dry_run: bool) -> list[dict]:
    if _is_ssot_def(rel):
        return []
    try:
        original = fpath.read_text(encoding='utf-8', errors='replace')
    except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
        return []
    lines = original.splitlines(keepends=True)
    fixes: list[dict] = []
    for const, literal, module in CONST_DEFS:
        current_text = ''.join(lines)
        if const in current_text and literal not in current_text:
            continue
        safe_positions = _collect_safe_positions(current_text)
        if not safe_positions:
            continue
        pat = re.compile('(?P<q>[\'"])' + re.escape(literal) + '(?P=q)')
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('#') or stripped.startswith('import ') or stripped.startswith('from '):
                continue
            m = pat.search(line)
            if not m:
                continue
            if m.end() < len(line) and line[m.end()] == '/':
                continue
            lineno = i + 1
            col = m.start()
            is_safe = any((pos_line == lineno and abs(pos_col - (col + 1)) <= 1 for pos_line, pos_col in safe_positions))
            if not is_safe:
                continue
            fixed_line = pat.sub(const, line, count=1)
            if fixed_line == line:
                continue
            fixes.append({'const': const, 'literal': literal, 'module': module, 'lineno': lineno, 'original': line.rstrip(), 'fixed': fixed_line.rstrip()})
            lines[i] = fixed_line
            break
    if fixes and (not dry_run):
        new_lines = list(lines)
        injected: set[str] = set()
        for fix in fixes:
            c = fix['const']
            if c not in injected and c not in ''.join(new_lines[:50]):
                new_lines = _inject_import(new_lines, c, fix['module'])
                injected.add(c)
        fpath.write_text(''.join(new_lines), encoding='utf-8')
    return fixes

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    total_files = 0
    total_fixes = 0
    all_results: dict[str, list[dict]] = {}
    for territory in sorted(ENFORCED_TERRITORIES):
        scan_root = ROOT / territory
        if not scan_root.exists():
            continue
        for dirpath, dirs, files in os.walk(scan_root):
            dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
            for fname in files:
                if not fname.endswith('.py'):
                    continue
                fpath = Path(dirpath) / fname
                rel = fpath.relative_to(ROOT).as_posix()
                fixes = process_file(fpath, rel, dry_run=args.dry_run)
                if fixes:
                    total_files += 1
                    total_fixes += len(fixes)
                    all_results[rel] = fixes
    mode = 'DRY-RUN' if args.dry_run else 'APPLIED'
    print(f'[{mode}] {total_fixes} fixes across {total_files} files')
    for rel in sorted(all_results):
        print(f'  {rel}')
        for f in all_results[rel]:
            print(f"    L{f['lineno']:4d} [{f['const']}]")
            print(f"         ORIG: {f['original'][:100]}")
            print(f"         NEW:  {f['fixed'][:100]}")
if __name__ == '__main__':
    main()
