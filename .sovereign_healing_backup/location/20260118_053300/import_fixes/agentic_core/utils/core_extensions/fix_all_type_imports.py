from __future__ import annotations
"""
Fix all Missing type imports in agentic_core implementation files.
Adds proper imports from corresponding *_types.py files.
"""
import re
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

root: Any = Path('C:/Git/Agentic-Workflow')
core: Any = ROOT / 'agentic_core'
type_import_fixes: Any = {'agent_gym_impl.py': {'module': 'agentic_core.L3_orchestration.training.agent_gym_types', 'types': ['GoldenStateEvaluator', 'JudgeEvaluator', 'TrainingScenario', 'BenchmarkResult', 'PerformanceMetrics']}}

def fix_type_imports() -> Any:
    """Brief description of functionality and purpose."""
    print('[*] FIXING ALL TYPE IMPORTS...')
    fixed: Any = 0
    for impl_file, config in TYPE_IMPORT_FIXES.items():
        for py_file in CORE.rglob(impl_file):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content: Any = f.read()
                if f"from {config['module']}" in content:
                    print(f'  [SKIP] {py_file.relative_to(CORE)} - already has imports')
                    continue
                import_pattern: Any = '(import logging\\s+from typing[^\\n]+\\s+)'
                types_str: Any = ', '.join(config['types'])
                new_import: Any = f"from {config['module']} import {types_str}\n\n"
                if 'LOGGER = logging.getLogger' in content:
                    content: Any = content.replace('LOGGER = logging.getLogger(__name__)', f"from {config['module']} import {types_str}\n\nLOGGER = logging.getLogger(__name__)")
                else:
                    content: Any = re.sub('(from typing import[^\\n]+\\n)', f'\\1{new_import}', content)
                content: Any = re.sub('# from \\.\\w+_types import \\*.*\\n', '', content)
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'  [✓] Fixed: {py_file.relative_to(CORE)}')
                fixed += 1
            except Exception as e:
                print(f'  [!] Error fixing {py_file.name}: {e}')
    print(f'\n[OK] Fixed {fixed} files')
if __name__ == '__main__':
    fix_type_imports()
