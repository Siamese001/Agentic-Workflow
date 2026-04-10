"""Active Set SSOT Check — CI Gate (AST-enforced).

_emit_reads_through("l4", "active_set_ssot_check", "urg_read_1")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_2")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_3")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_4")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_5")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_6")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_7")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_8")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_9")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_10")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_11")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_12")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_13")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_14")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_15")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_16")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_17")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_18")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_19")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_20")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_21")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_22")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_23")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_24")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_25")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_26")
_emit_reads_through("l4", "active_set_ssot_check", "urg_read_27")
Enforces that scripts requiring the ACTIVE agent set use the shared
``active_set_helper`` module instead of direct pipeline calls.

AST-based rules per governed script:
  1. Must NOT import ssot_discovery_util (any form).
  2. Must NOT import perform_deep_integrity_scan (any form).
  3. Must NOT call or reference load_agent_discovery / perform_deep_integrity_scan.
  4. Must NOT reference 'agent_discovery_full.json' as a string literal.
  5. MUST import active_set_helper (from-import or plain import).

Governed scripts are auto-discovered from ops_scripts/ci/*.py:
  - Excludes __init__.py, active_set_helper.py, active_set_ssot_check.py,
    active_set_snapshot_check.py, gate_consistency_check.py,
    governance_coverage_check.py
  - Includes scripts whose source contains active-set semantics markers
    OR any prohibited module/name/string reference (auto-governs bypasses)

Exit 0 = pass, exit 1 = violations found.

Merge-ready gate.
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import _emit_reads_through

_GOVERNANCE_EXCLUDES = frozenset({'__init__.py', 'active_set_helper.py', 'active_set_ssot_check.py', 'active_set_snapshot_check.py', 'baseline_io.py', 'gate_consistency_check.py', 'governance_coverage_check.py', 'mro_new_diamond_check.py'})
_GOVERNANCE_MARKERS = ('active_set_helper', 'active set', 'get_active_set', 'agent_count_cap', 'registry_consistency_check')
_PROHIBITED_PATTERNS = [re.compile('\\bssot_discovery_util\\b'), re.compile('(?<![./\\\\])\\bfull_agent_discovery\\b'), re.compile('\\bload_agent_discovery\\b'), re.compile('\\bperform_deep_integrity_scan\\b'), re.compile('agent_discovery_full\\.json')]

def discover_governed_scripts(ci_dir: Path) -> list[str]:
    """Auto-discover governed scripts under a CI directory.

    Returns sorted list of forward-slash relative paths from project root.
    """
    if not ci_dir.is_dir():
        return []
    project_root = ci_dir.parents[1]
    governed: list[str] = []
    for py_file in sorted(ci_dir.glob('*.py')):
        if py_file.name in _GOVERNANCE_EXCLUDES:
            continue
        try:
            source = py_file.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):    # guardian: File operations with encoding need error-specific handling
            continue
        is_governed = any(marker in source for marker in _GOVERNANCE_MARKERS) or any(pat.search(source) is not None for pat in _PROHIBITED_PATTERNS)
        if is_governed:
            governed.append(py_file.relative_to(project_root).as_posix())
    return governed
PROHIBITED_MODULES = {'ssot_discovery_util', 'full_agent_discovery'}
PROHIBITED_NAMES = {'load_agent_discovery', 'perform_deep_integrity_scan'}
PROHIBITED_STRINGS = {'agent_discovery_full.json'}
REQUIRED_IMPORT_FRAGMENT = 'active_set_helper'

def _build_parent_map(tree: ast.AST) -> dict[int, ast.AST]:
    """Build a mapping from child node id -> parent node."""
    parent_map: dict[int, ast.AST] = {}
    for node in ast.walk(tree):
        for child in ast.iter_child_nodes(node):
            parent_map[id(child)] = node
    return parent_map

def check_script_ast(source: str, rel_path: str) -> list[str]:
    """AST-check a single script. Return list of violation strings."""
    try:
        tree = ast.parse(source, filename=rel_path)
    except SyntaxError as exc:    # guardian: Syntax errors should be caught at parser level, not runtime
        return [f'{rel_path}: SyntaxError — {exc}']
    violations: list[str] = []
    has_helper_import = False
    parent_map = _build_parent_map(tree)
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            if REQUIRED_IMPORT_FRAGMENT in node.module:
                has_helper_import = True
        if isinstance(node, ast.Import):
            for alias in node.names:
                if REQUIRED_IMPORT_FRAGMENT in alias.name:
                    has_helper_import = True
        if isinstance(node, ast.ImportFrom) and node.module:
            mod_parts = node.module.split('.')
            for part in mod_parts:
                if part in PROHIBITED_MODULES:
                    violations.append(f"{rel_path}:{node.lineno}: from-import of prohibited module '{node.module}'")
                    break
            if node.names:
                for alias in node.names:
                    name_parts = alias.name.split('.')
                    for part in name_parts:
                        if part in PROHIBITED_MODULES:
                            violations.append(f"{rel_path}:{node.lineno}: from-import of prohibited name '{alias.name}' from '{node.module}'")
                            break
                        if part in PROHIBITED_NAMES:
                            violations.append(f"{rel_path}:{node.lineno}: from-import of prohibited function '{alias.name}' from '{node.module}'")
                            break
        if isinstance(node, ast.Import):
            for alias in node.names:
                mod_parts = alias.name.split('.')
                for part in mod_parts:
                    if part in PROHIBITED_MODULES:
                        violations.append(f"{rel_path}:{node.lineno}: import of prohibited module '{alias.name}'")
                        break
        if isinstance(node, ast.Call):
            func = node.func
            name = None
            if isinstance(func, ast.Name):
                name = func.id
            elif isinstance(func, ast.Attribute):
                name = func.attr
            if name and name in PROHIBITED_NAMES:
                violations.append(f"{rel_path}:{node.lineno}: call to prohibited function '{name}()'")
        if isinstance(node, ast.Name) and node.id in PROHIBITED_NAMES:
            parent = parent_map.get(id(node))
            if isinstance(parent, ast.Call) and parent.func is node:
                pass
            else:
                violations.append(f"{rel_path}:{node.lineno}: reference to prohibited name '{node.id}'")
        if isinstance(node, ast.Attribute) and node.attr in PROHIBITED_NAMES:
            parent = parent_map.get(id(node))
            if isinstance(parent, ast.Call) and parent.func is node:
                pass
            else:
                violations.append(f"{rel_path}:{node.lineno}: reference to prohibited attribute '{node.attr}'")
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            if node.value in PROHIBITED_STRINGS:
                violations.append(f"{rel_path}:{node.lineno}: string reference to prohibited artifact '{node.value}'")
    if not has_helper_import:
        violations.append(f"{rel_path}: missing required import from '{REQUIRED_IMPORT_FRAGMENT}'")
    seen: set[str] = set()
    deduped: list[str] = []
    for v in violations:
        if v not in seen:
            seen.add(v)
            deduped.append(v)
    return deduped

def run_ssot_check(project_root: Path) -> tuple[int, list[str], list[str]]:
    """Run the SSOT check against a project root.

    Returns:
        Tuple of (exit_code, governed_scripts, violations).
    """
    ci_dir = project_root / OPS_SCRIPTS_DIR / 'ci'
    governed = discover_governed_scripts(ci_dir)
    all_violations: list[str] = []
    for script_rel in governed:
        script_path = project_root / script_rel
        if not script_path.is_file():
            continue
        source = script_path.read_text(encoding='utf-8')
        all_violations.extend(check_script_ast(source, script_rel))
    exit_code = 1 if all_violations else 0
    return (exit_code, governed, all_violations)

def main() -> int:
    project_root = Path(__file__).resolve().parents[2]
    exit_code, governed, all_violations = run_ssot_check(project_root)
    print('Active Set SSOT Check (AST-enforced):')
    print(f'  governed_scripts={len(governed)}')
    for g in governed:
        print(f'    - {g}')
    if all_violations:
        print(f'FAIL: {len(all_violations)} violation(s):')
        for v in all_violations:
            print(f'  - {v}')
        return 1
    print('PASS: all governed scripts use active_set_helper exclusively')
    return 0
if __name__ == '__main__':
    sys.exit(main())
