from __future__ import annotations
"""
Subatomic Governance Audit Script.

Audits the codebase for compliance with the Three Laws:
- Law 1 (Depth): Files at depth 3-5
- Law 2 (Atomicity): 10-200 lines per file
- Law 3 (The Void): No .py files in root
"""
from collections import defaultdict
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.validators.structure_blueprint_2 import (
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
folders: Any = [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR, AGENTIC_CORE_DIR, 'schemas', 'prompt_governance', 'observability', 'config', SCRIPTS_DIR]

def count_lines(filepath: Any) -> Any:
    """Brief description of functionality and purpose."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            return len(f.readlines())
    except:
        return 0

def get_depth(path: Any, base: Any) -> Any:
    """Brief description of functionality and purpose."""
    rel: Any = Path(path).relative_to(base)
    return len(rel.parts)

def main() -> Any:
    """Brief description of functionality and purpose."""
    file_data: Any = []
    for folder in FOLDERS:
        folder_path: Any = Path(folder)
        if not folder_path.exists():
            continue
        for py_file in folder_path.rglob('*.py'):
            if '__pycache__' in str(py_file):
                continue
            depth: Any = get_depth(py_file, folder_path)
            lines: Any = count_lines(py_file)
            file_data.append((str(py_file), lines, depth, folder))
    print('=' * 80)
    print('CRITICAL VIOLATIONS (>500 lines) - PRIORITY 1')
    print('=' * 80)
    critical: Any = [(f, l, d, fo) for f, l, d, fo in file_data if l > 500]
    for f, l, d, fo in sorted(critical, key=lambda x: -x[1]):
        print(f'{l:5d} lines | depth {d} | {f}')
    print(f'\nTotal critical: {len(critical)}')
    print('\n' + '=' * 80)
    print('HIGH VIOLATIONS (201-500 lines) - PRIORITY 2 - TOP 30')
    print('=' * 80)
    high: Any = [(f, l, d, fo) for f, l, d, fo in file_data if 201 <= l <= 500]
    for f, l, d, fo in sorted(high, key=lambda x: -x[1])[:30]:
        print(f'{l:5d} lines | depth {d} | {f}')
    print(f'\nTotal high: {len(high)}')
    print('\n' + '=' * 80)
    print('DEPTH VIOLATIONS IN CORE FOLDERS (depth 1 or 2, non-init)')
    print('=' * 80)
    core_depth: Any = [(f, l, d, fo) for f, l, d, fo in file_data if fo in [APPS_RG_DIR, APPS_LIC_DIR, APPS_SHARED_DIR] and d < 3 and (not f.endswith('__init__.py'))]
    for f, l, d, fo in sorted(core_depth, key=lambda x: (x[2], -x[1])):
        print(f'depth {d} | {l:4d} lines | {f}')
    print(f'\nTotal core depth violations: {len(core_depth)}')
    print('\n' + '=' * 80)
    print('SUMMARY BY FOLDER')
    print('=' * 80)
    folder_stats: Any = defaultdict(lambda: {'files': 0, 'critical': 0, 'high': 0, 'depth_viol': 0})
    for f, l, d, fo in file_data:
        folder_stats[fo]['files'] += 1
        if l > 500:
            folder_stats[fo]['critical'] += 1
        elif l > 200:
            folder_stats[fo]['high'] += 1
        if d < 3 or d > 5:
            folder_stats[fo]['depth_viol'] += 1
    print(f"{'Folder':<20} {'Files':>6} {'Critical':>10} {'High':>8} {'Depth':>10}")
    print('-' * 60)
    for fo in sorted(folder_stats.keys()):
        s: Any = folder_stats[fo]
        print(f"{fo:<20} {s['files']:>6} {s['critical']:>10} {s['high']:>8} {s['depth_viol']:>10}")
    total_files: Any = len(file_data)
    total_critical: Any = len(critical)
    total_high: Any = len(high)
    depth_violations: Any = len([f for f, l, d, fo in file_data if d < 3 or d > 5])
    small_violations: Any = len([f for f, l, d, fo in file_data if l < 10])
    print('\n' + '=' * 80)
    print('OVERALL SUMMARY')
    print('=' * 80)
    print(f'Total .py files scanned: {total_files}')
    print(f'Critical (>500 lines): {total_critical}')
    print(f'High (201-500 lines): {total_high}')
    print(f'Depth violations: {depth_violations}')
    print(f'Too small (<10 lines): {small_violations}')
if __name__ == '__main__':
    main()
