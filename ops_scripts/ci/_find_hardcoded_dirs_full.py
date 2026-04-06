"""Same as _find_hardcoded_dirs.py but writes full output to a report file."""
from __future__ import annotations

import ast
import pathlib
import sys


_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_1")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_2")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_3")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_4")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_5")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_6")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_7")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_8")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_9")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_10")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_11")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_12")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_13")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_14")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_15")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_16")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_17")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_18")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_19")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_20")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_21")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_22")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_23")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_24")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_25")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_26")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_27")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_28")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_29")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_30")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_31")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_32")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_33")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_34")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_35")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_36")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_37")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_38")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_39")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_40")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_41")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_42")
_emit_reads_through("l4", "_find_hardcoded_dirs_full", "urg_read_43")
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
    REPORTS_DIR,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_reads_through

SSOT_DIR_NAMES: frozenset[str] = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
MIN_OVERLAP = 2
SSOT_PATHS = {'agentic_core/L5_safety/config/structure_blueprint/ssot.py', 'agentic_core/L5_safety/config/structure_blueprint/_constants.py', 'agentic_core/L5_safety/config/structure_blueprint/_verify.py'}
EXEMPT_LOCATIONS: frozenset[tuple[str, int]] = frozenset({('agentic_core/L0_routing/config/path_constants.py', 99), ('agentic_core/L0_routing/config/path_constants.py', 146), ('agentic_core/L0_routing/config/path_constants.py', 183), ('agentic_core/L0_routing/scripts/run_guardian_drift_detection.py', 40), ('agentic_core/L5_safety/reasoning/LocationHealerAgent.py', 1589), ('agentic_core/L5_safety/reasoning/LocationHealerAgent.py', 1624), ('agentic_core/L5_safety/enforcement/mission_utils_enforcer.py', 167), ('ops_scripts/maintenance/purge_cache.py', 59), ('agentic_core/L2_execution/engines/execute_command_executor.py', 277), ('ops_scripts/general/validate_structure.py', 32), ('ops_scripts/general/validate_structure.py', 58), ('ops_scripts/ci/_fix_hardcoded_dirs_inline.py', 38), ('ops_scripts/ci/_fix_bad_import_injection.py', 46), ('ops_scripts/ci/_repair_and_fix_all.py', 25), ('ops_scripts/ci/_repair_bad_injections.py', 32), ('ops_scripts/ci/check_kernel_extension_boundary.py', 19), ('ops_scripts/dev_tools/l0_scripts/generate_hooks_util.py', 44), ('agentic_core/L0_routing/scripts/execute_ssot.py', 8243), ('agentic_core/L0_routing/scripts/run_hygiene_guardian_util.py', 26), ('agentic_core/L5_safety/reasoning/DDDAlignmentAgent.py', 265), ('agentic_core/L5_safety/reasoning/GovernanceAgent.py', 392), ('agentic_core/L5_safety/reasoning/hierarchy_healer.py', 1536), ('agentic_core/L5_safety/reasoning/root_hygiene_healer.py', 312)})
SKIP_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS | DISCOVERY_EXCLUDED_TERRITORIES
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
        func = node.func
        if isinstance(func, ast.Name) and func.id in ('frozenset', 'set'):
            for arg in node.args:
                strings.extend(_string_literals_in_node(arg))
    return strings

def _suggest_ssot(overlap: list[str]) -> str:
    parts = []
    if any(s in GLOBAL_EXCLUDED_DIRS for s in overlap):
        parts.append('GLOBAL_EXCLUDED_DIRS')
    if any(s in SOVEREIGN_EXCLUDED_FOLDERS for s in overlap):
        parts.append('SOVEREIGN_EXCLUDED_FOLDERS')
    if any(s in DISCOVERY_EXCLUDED_TERRITORIES for s in overlap):
        parts.append('DISCOVERY_EXCLUDED_TERRITORIES')
    return ' | '.join(parts) if parts else 'SSOT constant'

def scan_file(path: pathlib.Path) -> list[tuple[int, str, list[str], str]]:
    try:
        source = path.read_text(encoding='utf-8', errors='replace')
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling    # guardian: Multiple exceptions (SyntaxError, OSError) need specific handling
        return []
    findings: list[tuple[int, str, list[str], str]] = []
    seen: set[tuple[int, str]] = set()
    for node in ast.walk(tree):
        name = '<expr>'
        value_node = None
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    name = target.id
            value_node = node.value
        elif isinstance(node, ast.AugAssign):
            if isinstance(node.target, ast.Name):
                name = node.target.id
            value_node = node.value
        elif isinstance(node, ast.Call):
            for arg in node.args:
                strings = _string_literals_in_node(arg)
                overlap = [s for s in strings if s in SSOT_DIR_NAMES]
                if len(overlap) >= MIN_OVERLAP:
                    key = (node.lineno, str(overlap))
                    if key not in seen:
                        seen.add(key)
                        fname = ''
                        if isinstance(node.func, ast.Name):
                            fname = node.func.id
                        elif isinstance(node.func, ast.Attribute):
                            fname = node.func.attr
                        findings.append((node.lineno, f'arg to {fname}()', overlap, _suggest_ssot(overlap)))
            continue
        if value_node is not None:
            strings = _string_literals_in_node(value_node)
            overlap = [s for s in strings if s in SSOT_DIR_NAMES]
            if len(overlap) >= MIN_OVERLAP:
                key = (node.lineno, str(overlap))
                if key not in seen:
                    seen.add(key)
                    findings.append((node.lineno, name, overlap, _suggest_ssot(overlap)))
    return findings

def main() -> int:
    report_path = ROOT / 'docs' / REPORTS_DIR / 'plans' / 'hardcoded_dirs_audit.md'
    lines_out: list[str] = []
    all_results: list[tuple[str, int, str, list[str], str]] = []
    for scan_root in SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob('*.py')):
            if _excluded(py_file):
                continue
            rel = str(py_file.relative_to(ROOT)).replace('\\', '/')
            if rel in SSOT_PATHS:
                continue
            findings = scan_file(py_file)
            for lineno, varname, overlap, suggestion in findings:
                all_results.append((rel, lineno, varname, overlap, suggestion))
    seen_keys: set[tuple[str, int]] = set()
    deduped: list[tuple[str, int, str, list[str], str]] = []
    for r in all_results:
        k = (r[0], r[1])
        if k not in seen_keys and k not in EXEMPT_LOCATIONS:
            seen_keys.add(k)
            deduped.append(r)
    lines_out.append('# Hardcoded Directory Names Audit\n')
    lines_out.append(f'SSOT owns {len(SSOT_DIR_NAMES)} directory names. Min overlap: {MIN_OVERLAP}\n')
    lines_out.append(f'**Total violations (deduplicated): {len(deduped)}**\n\n')
    for rel, lineno, varname, overlap, suggestion in deduped:
        lines_out.append(f'## `{rel}:{lineno}`\n')
        lines_out.append(f'- **var**: `{varname}`\n')
        lines_out.append(f'- **duplicated from SSOT**: `{overlap}`\n')
        lines_out.append(f'- **replace with**: `{suggestion}`\n\n')
    report_path.write_text('\n'.join(lines_out), encoding='utf-8')
    print(f'Report written to: {report_path}')
    print(f'Total deduplicated violations: {len(deduped)}')
    current_file = ''
    for rel, lineno, varname, overlap, suggestion in deduped:
        if rel != current_file:
            current_file = rel
            print(f'\nFILE: {rel}')
        print(f'  :{lineno}  var={varname}  use={suggestion}')
    return 1 if deduped else 0
if __name__ == '__main__':
    sys.exit(main())
