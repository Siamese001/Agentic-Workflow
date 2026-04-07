"""
Repair script: fix malformed imports and missing constants in test files.
Two problems introduced by the batch fix:
1. SyntaxError: import block inserted mid-way through an existing multi-line import
2. NameError: constant used in body but not listed in the import block

Strategy:
- Parse each file with ast; if SyntaxError, find and repair the malformed insertion
- For NameError-style: detect constants used in module body that are absent from the import
- Add missing constants to the import block
"""
from __future__ import annotations

import ast
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALL_CONSTANTS = {'AGENTIC_CORE_DIR', 'APPS_LIC_DIR', 'APPS_RG_DIR', 'APPS_SHARED_DIR', 'SYSTEM_LEARNING_DIR', 'TOOLS_DIR', 'TESTS_DIR', 'OPS_SCRIPTS_DIR', 'L0_ROUTING_DIR', 'L1_COGNITION_DIR', 'L2_EXECUTION_DIR', 'L3_ORCHESTRATION_DIR', 'L4_STATE_DIR', 'L5_SAFETY_DIR', 'L6_OBSERVABILITY_DIR', 'ARCHIVES_DIR', 'DASHBOARD_DIR', 'SCRIPTS_DIR', 'L0_MAINTENANCE_DIR'}
IMPORT_BLOCK_RE = re.compile('from agentic_core\\.L0_routing\\.config\\.path_constants import \\(([^)]*)\\)', re.DOTALL)
SINGLE_IMPORT_RE = re.compile('from agentic_core\\.L0_routing\\.config\\.path_constants import ([A-Z_]+(?:,\\s*[A-Z_]+)*)\\n')

def fix_syntax_error(src: str) -> str:
    """
    The batch script inserted:
        from some.module import (

from agentic_core...import (
    CONST,
)

            original_symbol,
        )
    Repair: remove the injected block from inside the existing import, add it cleanly after.
    """
    injected = re.compile('(from \\S+ import \\()\\s*\\n(\\nfrom agentic_core\\.L0_routing\\.config\\.path_constants import \\([^)]*\\)\\n)(\\s+\\S)', re.DOTALL)
    match = injected.search(src)
    if not match:
        return src
    injected_block = match.group(2).strip()
    src = src[:match.start(2)] + '\n' + src[match.end(2):]
    lines = src.splitlines(keepends=True)
    insert_after = 0
    in_import = False
    paren_depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('import ', 'from ')):
            in_import = True
        if in_import:
            paren_depth += line.count('(') - line.count(')')
            if paren_depth <= 0:
                insert_after = i + 1
                in_import = False
                paren_depth = 0
    lines.insert(insert_after, '\n' + injected_block + '\n')
    return ''.join(lines)

def get_used_constants(src: str) -> set[str]:
    """Find which path_constants are referenced in the source."""
    used = set()
    for const in ALL_CONSTANTS:
        # guardian: allow-path-string
        if re.search('\\b' + re.escape(const) + '\\b', src):
            used.add(const)
    return used

def get_imported_constants(src: str) -> set[str]:
    """Find which path_constants are already imported."""
    imported = set()
    m = IMPORT_BLOCK_RE.search(src)
    if m:
        imported.update(re.findall('\\b([A-Z_]{3,})\\b', m.group(1)))
    m2 = SINGLE_IMPORT_RE.search(src)
    if m2:
        imported.update(n.strip() for n in m2.group(1).split(','))
    return imported & ALL_CONSTANTS

def add_missing_to_import(src: str, missing: set[str]) -> str:
    """Add missing constants to the existing path_constants import block."""
    m = IMPORT_BLOCK_RE.search(src)
    if m:
        body = m.group(1)
        existing = set(re.findall('\\b([A-Z_]{3,})\\b', body))
        truly_missing = missing - existing
        if not truly_missing:
            return src
        sorted_missing = sorted(truly_missing)
        stripped_body = body.rstrip().rstrip(',')
        new_body = stripped_body + ',\n    ' + ',\n    '.join(sorted_missing) + ','
        new_block = 'from agentic_core.L0_routing.config.path_constants import (' + new_body + '\n)'
        return src.replace(m.group(0), new_block)
    sorted_missing = sorted(missing)
    new_import = 'from agentic_core.L0_routing.config.path_constants import (\n    ' + ',\n    '.join(sorted_missing) + ',\n)'
    lines = src.splitlines(keepends=True)
    insert_after = 0
    in_import = False
    paren_depth = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(('import ', 'from ')):
            in_import = True
        if in_import:
            paren_depth += line.count('(') - line.count(')')
            if paren_depth <= 0:
                insert_after = i + 1
                in_import = False
                paren_depth = 0
    lines.insert(insert_after, '\n' + new_import + '\n')
    return ''.join(lines)

def repair_file(filepath: Path) -> tuple[bool, str]:
    src = filepath.read_text(encoding='utf-8')
    original = src
    try:
        ast.parse(src)
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime
        src = fix_syntax_error(src)
        try:
            ast.parse(src)
        except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
            return (False, f'SyntaxError after fix attempt: {e}')
    used = get_used_constants(src)
    imported = get_imported_constants(src)
    needed_but_missing = (used & ALL_CONSTANTS) - imported
    if needed_but_missing:
        src = add_missing_to_import(src, needed_but_missing)
    try:
        ast.parse(src)
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime
        return (False, f'SyntaxError after repair: {e}')
    if src != original:
        filepath.write_text(src, encoding='utf-8')
        return (True, 'fixed')
    return (True, 'ok')

def main():
    problem_files = ['tests/architecture/test_phantom_folder_regression.py', 'tests/architecture/test_redis_cache_wiring_invariants.py', 'tests/architecture/test_wave1_phase1_parse_failures_and_ssot_paths.py', 'tests/architecture/test_cross_cutting_invariants.py', 'tests/governance/test_gateway_egress_invariants.py', 'tests/governance/test_guardian_heal_routing_containment.py', 'tests/governance/test_healing_reentry.py', 'tests/governance/test_l6_purity.py', 'tests/governance/test_layer_sovereignty_guard.py', 'tests/governance/test_req417_runtime_mutation_guard.py', 'tests/governance/test_req_p0_gateway_monopoly.py', 'tests/governance/test_ssot_structure_validation_enforcer.py', 'tests/guardian/test_activation_gate.py', 'tests/guardian/test_deterministic_loop_detector.py', 'tests/guardian/test_execute_ssot_v15_contract.py', 'tests/guardian/test_v15_p10_2_policy_pack.py', 'tests/guardian/test_v15_p8_cat_c.py', 'tests/guardian/test_v15_p8_cat_d.py', 'tests/guardian/test_v15_p8_cat_e.py', 'tests/integration_full_deps/test_seed_pack_full_build_b5.py', 'tests/unit/agentic_core/L0_routing/scripts/test_execute_ssot_contracts.py', 'tests/unit/agentic_core/L0_routing/scripts/test_healer_naming_convention.py', 'tests/unit/agentic_core/L2_execution/healers/test_healing_provider_adapters.py', 'tests/unit/agentic_core/L3_orchestration/workflow_engines/test_dag_runtime_inspector_agent.py', 'tests/unit/agentic_core/L5_safety/reasoning/test_depth_pipeline_execute_ssot.py', 'tests/unit/test_depth_violation_no_archive_invariant.py', 'tests/unit/test_integration_config.py', 'tests/unit/test_l1_purity_enforcement.py', 'tests/unit/test_l3_orchestration_agent_inventory_contract.py', 'tests/unit/test_l4_state_agent_inventory_contract.py', 'tests/unit/test_l6_agent_inventory_contract.py', 'tests/unit/test_meta_learning_bridge.py', 'tests/unit/test_nested_lcd_detection_hook.py', 'tests/unit/test_phase4_ml_end_to_end_envelope.py', 'tests/unit/test_phase6_retrieval_snapshot.py', 'tests/unit/test_wave2_gravity_exclusion.py', 'tests/unit/test_wave5_longpaths_guard.py', 'tests/unit/test_wave6_hitl_gates.py', 'tests/unit_min_deps/test_config_property_contract.py', 'tests/unit_min_deps/test_decorator_timeout_layer_constraints.py', 'tests/unit_min_deps/test_fire_meta_learning_timestamps.py', 'tests/unit_min_deps/test_formal_verification.py', 'tests/unit_min_deps/test_import_graph_contract.py', 'tests/unit_min_deps/test_proposal_capture.py', 'tests/unit_min_deps/test_ssot_mutation_fence.py', 'tests/unit_min_deps/test_static_checks.py', 'tests/unit_min_deps/test_wave0c_meta_learning_intake_wiring.py']
    test_root = ROOT / TESTS_DIR
    all_test_files = {str(p.relative_to(ROOT)).replace('\\', '/') for p in test_root.rglob('*.py')}
    all_targets = set(problem_files) | all_test_files
    fixed = 0
    errors = []
    for rel in sorted(all_targets):
        fp = ROOT / rel
        if not fp.exists():
            continue
        ok, msg = repair_file(fp)
        if not ok:
            errors.append((rel, msg))
            print(f'ERROR: {rel}: {msg}')
        elif msg == 'fixed':
            fixed += 1
            print(f'FIXED: {rel}')
    print(f'\nDone: {fixed} files repaired, {len(errors)} errors.')
    for r, e in errors:
        print(f'  ERROR {r}: {e}')
if __name__ == '__main__':
    main()
