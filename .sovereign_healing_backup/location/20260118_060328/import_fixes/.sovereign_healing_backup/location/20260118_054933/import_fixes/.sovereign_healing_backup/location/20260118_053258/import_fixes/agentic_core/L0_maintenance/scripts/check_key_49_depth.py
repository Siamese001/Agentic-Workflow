from __future__ import annotations
"""
Standalone Key 49 Depth Violation Checker
[SSOT] All depth requirements derived from SOVEREIGN_REGISTRY in structure_blueprint.py
"""
from pathlib import Path
from agentic_core.config.blueprint_sovereign.structure_blueprint_1 import SOVEREIGN_REGISTRY
from typing import Any

def check_key_49_depth() -> Any:
    """Check directory depth violations per Key 49 using SSOT"""
    project_root: Any = Path(__file__).resolve().parent.parent.parent.parent
    violations: Any = []
    warnings: Any = []
    DEPTH_MAP: Any = {root: cfg['depth'] for root, cfg in SOVEREIGN_REGISTRY.items()}
    excludes: Any = {'.git', '__pycache__', 'data', 'archives', '.venv'}
    for py_file in project_root.rglob('*.py'):
        relative_path: Any = py_file.relative_to(project_root)
        depth: Any = len(relative_path.parts)
        if any((exclude in str(py_file) for exclude in excludes)):
            continue
        if relative_path.parts and relative_path.parts[0] in DEPTH_MAP:
            root_folder: Any = relative_path.parts[0]
            required_depth: Any = DEPTH_MAP[root_folder]
            if depth != required_depth and py_file.name != '__init__.py':
                violations.append(f'{relative_path} (Invalid depth: {depth} - {root_folder} requires depth {required_depth})')
            continue
    print('=' * 70)
    print('KEY 49 DEPTH VIOLATION REPORT')
    print('=' * 70)
    if violations:
        print(f'\n[VIOLATIONS] Found {len(violations)} file(s) exceeding depth 5:')
        for v in violations[:20]:
            print(f'  ✗ {v}')
        if len(violations) > 20:
            print(f'  ... and {len(violations) - 20} more violations')
    else:
        print('\n[✓] NO depth violations found - All files at depth ≤ 5')
    if warnings:
        print(f'\n[WARNINGS] Found {len(warnings)} file(s) at depth 1:')
        for w in warnings[:10]:
            print(f'  ⚠ {w}')
        if len(warnings) > 10:
            print(f'  ... and {len(warnings) - 10} more')
    print(f'\n[DEEPEST FILES] Current maximum depth in repository:')
    all_depths: Any = []
    for py_file in project_root.rglob('*.py'):
        if any((exclude in str(py_file) for exclude in excludes)):
            continue
        relative_path: Any = py_file.relative_to(project_root)
        depth: Any = len(relative_path.parts)
        all_depths.append((depth, relative_path))
    all_depths.sort(reverse=True)
    max_depth: Any = all_depths[0][0] if all_depths else 0
    deepest: Any = [f for d, f in all_depths if d == max_depth][:5]
    print(f'  Maximum depth: {max_depth}')
    for f in deepest:
        print(f'  - {f}')
    print('=' * 70)
    return len(violations) == 0
if __name__ == '__main__':
    success: Any = check_key_49_depth()
    exit(0 if success else 1)
