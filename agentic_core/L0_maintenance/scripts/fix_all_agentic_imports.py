"""
Fix all import issues in AgenticCore after bulk hierarchy heal.
"""
import os
import re
from pathlib import Path

from typing import Any

# [SSOT IMPORT] Structure blueprint is the single source of truth
from AgenticCore.config.blueprint_sovereign.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


def fix_file_imports(file_path: Path) -> bool:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        original: Any = content
        mappings: Any = {'from AgenticCore.base import': 'from AgenticCore.L2_execution.ToolRegistry.base import', 'from AgenticCore.CanonBaseAgent import': 'from AgenticCore.L2_execution.ToolRegistry.CanonBaseAgent import', 'from AgenticCore.L2_execution.ToolRegistry.': 'from AgenticCore.L2_execution.ToolRegistry.', 'from AgenticCore.L2_execution.P2_tools.': 'from AgenticCore.L2_execution.ToolRegistry.', 'from AgenticCore.L2_execution.P3_engines.': 'from AgenticCore.L2_execution.ToolRegistry.', 'from AgenticCore.L5_safety.P1_core.': 'from AgenticCore.L5_safety.guardrails.', 'from AgenticCore.L5_safety.policy.': 'from AgenticCore.L5_safety.guardrails.', 'from AgenticCore.L4_state.cache.': 'from AgenticCore.L4_state.ValidationContext.', 'from AgenticCore.L4_state.vector.': 'from AgenticCore.L4_state.ValidationContext.', 'from AgenticCore.shared.constants import': 'from AgenticCore.L0_maintenance.scripts.canon_validator_config import', 'import AgenticCore.base': 'import AgenticCore.L2_execution.ToolRegistry.base', 'import AgenticCore.L2_execution.ToolRegistry.': 'import AgenticCore.L2_execution.ToolRegistry.', 'import AgenticCore.L2_execution.P2_tools.': 'import AgenticCore.L2_execution.ToolRegistry.', 'import AgenticCore.L2_execution.P3_engines.': 'import AgenticCore.L2_execution.ToolRegistry.', 'from L2_execution.ToolRegistry.base import': 'from AgenticCore.L2_execution.ToolRegistry.base import', 'from L2_execution.ToolRegistry.CanonBaseAgent import': 'from AgenticCore.L2_execution.ToolRegistry.CanonBaseAgent import'}
        for old, new in mappings.items():
            content: Any = content.replace(old, new)
        content: Any = re.sub('# \\[INCOMPLETE IMPORT\\] from AgenticCore\\.\\.([^\\s]+) import (.+)', 'from AgenticCore.L2_execution.ToolRegistry.\\1 import \\2', content)
        content: Any = re.sub('from AgenticCore\\.AgenticCore\\.', 'from AgenticCore.', content)
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f'Error fixing {file_path}: {e}')
        return False

def main() -> Any:
    """Fix all imports in AgenticCore."""
    fixed: Any = 0
    total: Any = 0
    for py_file in Path('AgenticCore').rglob('*.py'):
        total += 1
        if fix_file_imports(py_file):
            fixed += 1
            print(f'Fixed: {py_file}')
    print(f'\nFixed {fixed} out of {total} files')
if __name__ == '__main__':
    main()
