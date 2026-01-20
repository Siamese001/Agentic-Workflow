from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set, Tuple

from agentic_core.L5_safety.validators.structure_blueprint import (
    AGENT_DISCOVERY_JSON,
    AGENT_DISCOVERY_MANIFEST_JSON,
    AGENTIC_CORE_DIR,
    SCRIPTS_DIR,
    TESTS_DIR,
    DASHBOARD_DIR,
    L0_MAINTENANCE_DIR,
    L1_COGNITION_DIR,
    L2_EXECUTION_DIR,
    L3_ORCHESTRATION_DIR,
    L4_STATE_DIR,
    L5_SAFETY_DIR,
    L6_OBSERVABILITY_DIR,
    get_validated_project_root,
)
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
root: Any = Path('C:/Git/Agentic-Workflow')
hierarchy: Any = {'LEVEL_0_SOVEREIGN_CORE': {'folders': [AGENTIC_CORE_DIR], 'description': 'The Sovereign Core - L1-L5 layers', 'can_import_from': []}, 'LEVEL_1_ARCHITECTURAL': {'folders': ['prompt_governance', 'schemas', 'config', SCRIPTS_DIR], 'description': 'Architectural Supports - Blueprints & Rules', 'can_import_from': [AGENTIC_CORE_DIR, 'prompt_governance', 'schemas', 'config', SCRIPTS_DIR]}, 'LEVEL_2_OBSERVABILITY': {'folders': ['observability'], 'description': 'The Mirror - Logs all activity', 'can_import_from': [AGENTIC_CORE_DIR, 'prompt_governance', 'schemas', 'config', SCRIPTS_DIR]}, 'LEVEL_3_SHARED': {'folders': [APPS_SHARED_DIR], 'description': 'Transit Zone - Shared utilities', 'can_import_from': [AGENTIC_CORE_DIR, 'prompt_governance', 'schemas', 'config', SCRIPTS_DIR, 'observability']}, 'LEVEL_4_DOWNSTREAM': {'folders': [APPS_RG_DIR, APPS_LIC_DIR], 'description': 'The Territory - Domain-specific apps', 'can_import_from': [AGENTIC_CORE_DIR, 'prompt_governance', 'schemas', 'config', SCRIPTS_DIR, 'observability', APPS_SHARED_DIR]}}
exempt_folders: Any = {'.git', '.venv', 'venv', '__pycache__', 'node_modules', 'data', ARCHIVES_DIR, TESTS_DIR, 'knowledge', 'infra', 'memory'}

def get_folder_level(folder_name: str) -> Tuple[int, str]:
    """Returns (level_number, level_name) for a folder, or (-1, 'UNKNOWN') if not in hierarchy."""
    for level_name, level_info in HIERARCHY.items():
        if folder_name in level_info['folders']:
            level_num: Any = int(level_name.split('_')[1])
            return (level_num, level_name)
    return (-1, 'UNKNOWN')

def check_import_violations(file_path: Path) -> List[str]:
    """Check if a file imports from folders it shouldn't according to hierarchy."""
    violations: Any = []
    try:
        rel_path: Any = file_path.relative_to(ROOT)
        if not rel_path.parts:
            return violations
        own_folder: Any = rel_path.parts[0]
        if own_folder in EXEMPT_FOLDERS:
            return violations
        own_level, own_level_name = get_folder_level(own_folder)
        if own_level == -1:
            return violations
        allowed_imports: Any = HIERARCHY[own_level_name]['can_import_from']
        with open(file_path, 'r', encoding='utf-8') as f:
            tree: Any = ast.parse(f.read())
        for node in ast.walk(tree):
            imported_module: Any = None
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_module: Any = alias.name.split('.')[0]
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported_module: Any = node.module.split('.')[0]
            if imported_module:
                imported_level, _ = get_folder_level(imported_module)
                if imported_level != -1:
                    if imported_module not in allowed_imports and imported_module != own_folder:
                        violations.append(f"GRAVITY VIOLATION: {rel_path} imports from '{imported_module}' (Level {imported_level}), but '{own_folder}' (Level {own_level}) can only import from: {allowed_imports}")
    except Exception as e:
        pass
    return violations

def audit_structure() -> Any:
    """Audit the entire repository structure against the hierarchy."""
    print('[*] STARTING STRUCTURE AUDIT AGAINST SOVEREIGN HIERARCHY...')
    print()
    print('=' * 80)
    print('PHASE 1: FOLDER STRUCTURE VALIDATION')
    print('=' * 80)
    all_folders_valid: Any = True
    for level_name, level_info in HIERARCHY.items():
        level_num: Any = int(level_name.split('_')[1])
        print(f"\n[LEVEL {level_num}] {level_info['description']}")
        for folder in level_info['folders']:
            folder_path: Any = ROOT / folder
            if folder_path.exists():
                # Phase 6.8: Use ssot_discovery instead of rglob
                from agentic_core.utils.ssot_discovery import get_python_files
                py_count: Any = len(list(get_python_files(folder_path)))
                print(f'  ✓ {folder:25} ({py_count} Python files)')
            else:
                print(f'  ✗ {folder:25} MISSING')
                all_folders_valid: Any = False
    print('\n' + '=' * 80)
    print('PHASE 2: UNAUTHORIZED ROOT FOLDERS')
    print('=' * 80)
    authorized_folders: Any = set()
    for level_info in HIERARCHY.values():
        authorized_folders.update(level_info['folders'])
    authorized_folders.update(EXEMPT_FOLDERS)
    unauthorized: Any = []
    for item in ROOT.iterdir():
        if item.is_dir() and item.name not in authorized_folders:
            if not item.name.startswith('.') and (not item.name[0:2].isdigit()):
                unauthorized.append(item.name)
    if unauthorized:
        print(f'\n[!] Found {len(unauthorized)} unauthorized root folders:')
        for folder in unauthorized:
            print(f'  ✗ {folder}')
    else:
        print('\n[✓] No unauthorized root folders found')
    print('\n' + '=' * 80)
    print('PHASE 3: IMPORT GRAVITY VIOLATIONS')
    print('=' * 80)
    all_violations: Any = []
    # Phase 6.8: Use ssot_discovery instead of rglob
    from agentic_core.utils.ssot_discovery import get_python_files
    for py_file in get_python_files(ROOT):
        violations: Any = check_import_violations(py_file)
        all_violations.extend(violations)
    if all_violations:
        print(f'\n[!] Found {len(all_violations)} gravity violations:')
        for Violation in all_violations[:20]:
            print(f'  ✗ {Violation}')
        if len(all_violations) > 20:
            print(f'  ... and {len(all_violations) - 20} more')
    else:
        print('\n[✓] No import gravity violations found')
    print('\n' + '=' * 80)
    print('AUDIT SUMMARY')
    print('=' * 80)
    total_issues: Any = len(unauthorized) + len(all_violations)
    if not all_folders_valid:
        total_issues += 1
    if total_issues == 0:
        print('\n[SUCCESS] ✓ Repository structure is 100% compliant with sovereign hierarchy')
    else:
        print(f'\n[ALERT] ✗ Found {total_issues} structural issues:')
        if not all_folders_valid:
            print('  - Missing required folders')
        if unauthorized:
            print(f'  - {len(unauthorized)} unauthorized root folders')
        if all_violations:
            print(f'  - {len(all_violations)} import gravity violations')
    print('\n' + '=' * 80)
    return {'folders_valid': all_folders_valid, 'unauthorized_folders': unauthorized, 'gravity_violations': all_violations, 'total_issues': total_issues}
if __name__ == '__main__':
    results: Any = audit_structure()
    report_path: Any = ROOT / 'structure_audit_report.md'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write('# Sovereign Hierarchy Structure Audit Report\n\n')
        f.write('## Hierarchy Definition\n\n')
        f.write('```\n')
        f.write('[LEVEL 0] agentic_core (Sovereign Core)\n')
        f.write('    ↓\n')
        f.write('[LEVEL 1] prompt_governance, schemas, config, scripts (Architectural)\n')
        f.write('    ↓\n')
        f.write('[LEVEL 2] observability (The Mirror)\n')
        f.write('    ↓\n')
        f.write('[LEVEL 3] apps_shared (Transit Zone)\n')
        f.write('    ↓\n')
        f.write('[LEVEL 4] apps_rg, apps_lic (Downstream Apps)\n')
        f.write('```\n\n')
        f.write('## Audit Results\n\n')
        if results['total_issues'] == 0:
            f.write('**STATUS: ✓ COMPLIANT**\n\n')
            f.write('Repository structure is 100% compliant with the sovereign hierarchy.\n')
        else:
            f.write(f"**STATUS: ✗ {results['total_issues']} ISSUES FOUND**\n\n")
            if results['unauthorized_folders']:
                f.write(f"### Unauthorized Root Folders ({len(results['unauthorized_folders'])})\n\n")
                for folder in results['unauthorized_folders']:
                    f.write(f'- `{folder}`\n')
                f.write('\n')
            if results['gravity_violations']:
                f.write(f"### Import Gravity Violations ({len(results['gravity_violations'])})\n\n")
                for Violation in results['gravity_violations']:
                    f.write(f'- {Violation}\n')
                f.write('\n')
    print(f'\n[OK] Detailed report written to: {report_path}')
