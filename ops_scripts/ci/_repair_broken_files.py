"""
_emit_reads_through("l4", "_repair_broken_files", "urg_read_1")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_2")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_3")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_4")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_5")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_6")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_7")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_8")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_9")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_10")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_11")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_12")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_13")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_14")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_15")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_16")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_17")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_18")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_19")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_20")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_21")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_22")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_23")
_emit_reads_through("l4", "_repair_broken_files", "urg_read_24")
Restore syntax-broken files to their HEAD version, then re-apply ONLY the
string literal replacements (no import injection).

Import injection will be handled separately with a fixed algorithm.
"""
from __future__ import annotations

import ast
import os
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
sys.path.insert(0, str(ROOT))
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    ENFORCED_TERRITORIES,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

CONST_DEFS: list[tuple[str, str, str]] = sorted([('ARCHIVES_DIR', ARCHIVES_DIR, 'agentic_core.L0_routing.config.path_constants'), ('AGENTIC_CORE_DIR', AGENTIC_CORE_DIR, 'agentic_core.L0_routing.config.path_constants'), ('APPS_RG_DIR', APPS_RG_DIR, 'agentic_core.L0_routing.config.path_constants'), ('APPS_LIC_DIR', APPS_LIC_DIR, 'agentic_core.L0_routing.config.path_constants'), ('APPS_SHARED_DIR', APPS_SHARED_DIR, 'agentic_core.L0_routing.config.path_constants'), ('OPS_SCRIPTS_DIR', OPS_SCRIPTS_DIR, 'agentic_core.L0_routing.config.path_constants'), ('TESTS_DIR', TESTS_DIR, 'agentic_core.L0_routing.config.path_constants'), ('TOOLS_DIR', TOOLS_DIR, 'agentic_core.L0_routing.config.path_constants'), ('SYSTEM_LEARNING_DIR', SYSTEM_LEARNING_DIR, 'agentic_core.L0_routing.config.path_constants'), ('L0_MAINTENANCE_DIR', L0_MAINTENANCE_DIR, 'agentic_core.L0_routing.config.path_constants'), ('L1_COGNITION_DIR', L1_COGNITION_DIR, 'agentic_core.L0_routing.config.path_constants'), ('L2_EXECUTION_DIR', L2_EXECUTION_DIR, 'agentic_core.L0_routing.config.path_constants'), ('L3_ORCHESTRATION_DIR', L3_ORCHESTRATION_DIR, 'agentic_core.L0_routing.config.path_constants'), ('L4_STATE_DIR', L4_STATE_DIR, 'agentic_core.L0_routing.config.path_constants'), ('L5_SAFETY_DIR', L5_SAFETY_DIR, 'agentic_core.L0_routing.config.path_constants'), ('L6_OBSERVABILITY_DIR', L6_OBSERVABILITY_DIR, 'agentic_core.L0_routing.config.path_constants'), ('DOCS_REPORTS_PLANS', DOCS_REPORTS_PLANS, 'agentic_core.L5_safety.config.structure_blueprint.ssot'), ('REPORTS_DIR', REPORTS_DIR, 'agentic_core.L5_safety.config.structure_blueprint.ssot'), ('TESTS_UNIT_DIR', TESTS_UNIT_DIR, 'agentic_core.L5_safety.config.structure_blueprint.ssot')], key=lambda x: -len(x[1]))
_SSOT_SKIP = ('agentic_core/L5_safety/config/structure_blueprint/', 'agentic_core/L0_routing/config/path_constants')

def is_syntax_ok(fpath: Path) -> bool:
    try:
        ast.parse(fpath.read_text(encoding='utf-8', errors='replace'))
        return True
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return False

def restore_from_head(rel: str) -> bool:
    result = subprocess.run(['git', 'checkout', 'HEAD', '--', rel], cwd=str(ROOT), capture_output=True, text=True)
    return result.returncode == 0

def reapply_replacements(fpath: Path, rel: str) -> list[str]:
    """Apply string literal replacements WITHOUT import injection."""
    if any(rel.startswith(p) for p in _SSOT_SKIP):
        return []
    try:
        original = fpath.read_text(encoding='utf-8', errors='replace')
    except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling    # guardian: File operations with encoding need error-specific handling
        return []
    lines = list(original.splitlines(keepends=True))
    applied: list[str] = []
    for const, literal, module in CONST_DEFS:
        current = ''.join(lines)
        if const in current:
            continue
        try:
            safe_pos = _collect_safe(current)
        except (SyntaxError, ValueError):
            continue
        pat = re.compile('(?P<q>[\'"])' + re.escape(literal) + '(?P=q)')
        for i, line in enumerate(lines):
            s = line.strip()
            if s.startswith('#') or s.startswith('import ') or s.startswith('from '):
                continue
            m = pat.search(line)
            if not m:
                continue
            if m.end() < len(line) and line[m.end()] == '/':
                continue
            lineno = i + 1
            col = m.start()
            is_safe = any((pl == lineno and abs(pc - (col + 1)) <= 1 for pl, pc in safe_pos))
            if not is_safe:
                continue
            fixed = pat.sub(const, line, count=1)
            if fixed != line:
                lines[i] = fixed
                applied.append(f'L{lineno} [{const}]')
                break
    if applied:
        fpath.write_text(''.join(lines), encoding='utf-8')
    return applied
_PATH_CALLS = {'Path', 'PurePath', 'walk', 'makedirs', 'mkdir', 'listdir', 'scandir', 'isdir', 'isfile', 'exists', 'join', 'abspath', 'realpath', 'relpath', 'expanduser', 'glob', 'rglob', 'add', 'append', 'discard', 'remove'}

def _collect_safe(source: str) -> set[tuple[int, int]]:
    try:
        tree = ast.parse(source)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return set()
    safe: set[tuple[int, int]] = set()
    parent_stack: list[ast.AST] = []

    def visit(node: ast.AST) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if parent_stack:
                p = parent_stack[-1]
                gp = parent_stack[-2] if len(parent_stack) >= 2 else None
                if isinstance(p, (ast.List, ast.Tuple, ast.Set)):
                    if isinstance(gp, ast.Dict):
                        pass
                    elif all(isinstance(e, (ast.Constant, ast.Name, ast.Attribute)) for e in p.elts):
                        safe.add((node.lineno, node.col_offset))
                elif isinstance(p, ast.Assign) and p.value is node:
                    safe.add((node.lineno, node.col_offset))
                elif isinstance(p, ast.AnnAssign) and p.value is node:
                    safe.add((node.lineno, node.col_offset))
                elif isinstance(p, ast.Call):
                    fn = p.func
                    fname = fn.id if isinstance(fn, ast.Name) else fn.attr if isinstance(fn, ast.Attribute) else None
                    if fname in _PATH_CALLS and node in p.args:
                        safe.add((node.lineno, node.col_offset))
                elif isinstance(p, ast.Compare):
                    ops_ok = all(isinstance(op, (ast.In, ast.NotIn, ast.Eq, ast.NotEq)) for op in p.ops)
                    if ops_ok and (p.left is node or node in p.comparators):
                        safe.add((node.lineno, node.col_offset))
                elif isinstance(p, ast.BinOp) and isinstance(p.op, ast.Div) and (p.right is node):
                    if isinstance(p.left, (ast.Name, ast.BinOp, ast.Attribute, ast.Call)):
                        safe.add((node.lineno, node.col_offset))
        for child in ast.iter_child_nodes(node):
            parent_stack.append(node)
            visit(child)
            parent_stack.pop()
    visit(tree)
    return safe

def main() -> None:
    broken: list[Path] = []
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
                if not is_syntax_ok(fpath):
                    broken.append(fpath)
    print(f'Found {len(broken)} broken files')
    restored = 0
    for fpath in broken:
        rel = fpath.relative_to(ROOT).as_posix()
        if restore_from_head(rel):
            fixes = reapply_replacements(fpath, rel)
            if fixes:
                print(f'  RESTORED+FIXED {rel}: {fixes}')
            else:
                print(f'  RESTORED {rel}')
            restored += 1
        else:
            print(f'  FAILED to restore {rel}')
    print(f'\nRestored {restored}/{len(broken)} files')
    still_broken = [f for f in broken if not is_syntax_ok(f)]
    print(f'Still broken after repair: {len(still_broken)}')
    for f in still_broken:
        print(f'  {f.relative_to(ROOT)}')
if __name__ == '__main__':
    main()
