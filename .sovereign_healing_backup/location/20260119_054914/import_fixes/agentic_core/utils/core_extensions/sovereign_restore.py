from __future__ import annotations
import ast
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from pathlib import Path
from typing import Any

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
core: Any = ROOT / AGENTIC_CORE_DIR

def get_class_names(file_path: Any) -> Any:
    """Statically parse class names to avoid execution/circular imports."""
    classes: Any = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            node: Any = ast.parse(f.read())
        for n in node.body:
            if isinstance(n, ast.ClassDef):
                classes.append(n.name)
    except Exception as e:
        print(f'  [!] AST Error {file_path.name}: {e}')
    return classes

def sovereign_restore() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] STARTING SOVEREIGN RESTORE (REBUILDING EXPORTS)...')
    for layer_dir in CORE.iterdir():
        if not layer_dir.is_dir() or not layer_dir.name.startswith('L'):
            continue
        print(f'\n[LAYER] {layer_dir.name}')
        exports: Any = []
        import_lines: Any = []
        for stage_dir in layer_dir.iterdir():
            if not stage_dir.is_dir():
                continue
            for py_file in stage_dir.glob('*.py'):
                if py_file.name == '__init__.py':
                    continue
                classes: Any = get_class_names(py_file)
                if classes:
                    module_path: Any = f'.{stage_dir.name}.{py_file.stem}'
                    import_lines.append(f"from {module_path} import {', '.join(classes)}")
                    exports.extend(classes)
        init_path: Any = layer_dir / '__init__.py'
        with open(init_path, 'w', encoding='utf-8') as f:
            f.write(f'"""Sovereign Layer: {layer_dir.name}"""\n\n')
            if import_lines:
                f.write('\n'.join(import_lines) + '\n\n')
                f.write(f'__all__ = {exports}\n')
        print(f'  [✓] Restored {len(exports)} exports to {init_path.relative_to(ROOT)}')
    with open(CORE / '__init__.py', 'w', encoding='utf-8') as f:
        f.write('"""agentic_core: Sovereign AI Architecture"""\n')
        f.write('# Root exports disabled to prevent circular death loops.\n')
        f.write('# Use: from agentic_core.L_layer import Component\n')
    print('\n[OK] SOVEREIGN RESTORE COMPLETE.')
if __name__ == '__main__':
    sovereign_restore()
