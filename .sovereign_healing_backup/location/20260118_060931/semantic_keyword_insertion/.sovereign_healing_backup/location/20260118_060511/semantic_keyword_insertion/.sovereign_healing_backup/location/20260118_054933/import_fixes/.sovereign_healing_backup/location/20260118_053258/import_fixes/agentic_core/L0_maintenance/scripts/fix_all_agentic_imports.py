from __future__ import annotations
"""
Fix all import issues in agentic_core after bulk hierarchy heal.
"""
import os
import re
from pathlib import Path

from typing import Any

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_2 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


def fix_file_imports(file_path: Path) -> bool:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        original: Any = content
        mappings: Any = {'from agentic_core.base import': 'from agentic_core.L2_execution.ToolRegistry.base import', 'from agentic_core.CanonBaseAgent import': 'from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import', 'from agentic_core.L2_execution.ToolRegistry.': 'from agentic_core.L2_execution.ToolRegistry.', 'from agentic_core.L2_execution.P2_tools.': 'from agentic_core.L2_execution.ToolRegistry.', 'from agentic_core.L2_execution.P3_engines.': 'from agentic_core.L2_execution.ToolRegistry.', 'from agentic_core.L5_safety.P1_core.': 'from agentic_core.L5_safety.guardrails.', 'from agentic_core.L5_safety.policy.': 'from agentic_core.L5_safety.guardrails.', 'from agentic_core.L4_state.cache.': 'from agentic_core.L4_state.validation_context.', 'from agentic_core.L4_state.vector.': 'from agentic_core.L4_state.validation_context.', 'from agentic_core.shared.constants import': 'from agentic_core.L0_maintenance.scripts.canon_validator_config_1 import', 'import agentic_core.base': 'import agentic_core.L2_execution.tool_registry.base', 'import agentic_core.L2_execution.tool_registry.': 'import agentic_core.L2_execution.tool_registry.', 'import agentic_core.L2_execution.P2_tools.': 'import agentic_core.L2_execution.tool_registry.', 'import agentic_core.L2_execution.P3_engines.': 'import agentic_core.L2_execution.tool_registry.', 'from L2_execution.tool_registry.base import': 'from agentic_core.L2_execution.ToolRegistry.base import', 'from L2_execution.tool_registry.CanonBaseAgent import': 'from agentic_core.L2_execution.ToolRegistry.CanonBaseAgent import'}
        for old, new in mappings.items():
            content: Any = content.replace(old, new)
        content: Any = re.sub('# \\[INCOMPLETE IMPORT\\] from agentic_core\\.\\.([^\\s]+) import (.+)', 'from agentic_core.L2_execution.ToolRegistry.\\1 import \\2', content)
        content: Any = re.sub('from agentic_core\\.agentic_core\\.', 'from agentic_core.', content)
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f'Error fixing {file_path}: {e}')
        return False

def main() -> Any:
    """Fix all imports in agentic_core."""
    fixed: Any = 0
    total: Any = 0
    for py_file in Path('agentic_core').rglob('*.py'):
        total += 1
        if fix_file_imports(py_file):
            fixed += 1
            print(f'Fixed: {py_file}')
    print(f'\nFixed {fixed} out of {total} files')
if __name__ == '__main__':
    main()
