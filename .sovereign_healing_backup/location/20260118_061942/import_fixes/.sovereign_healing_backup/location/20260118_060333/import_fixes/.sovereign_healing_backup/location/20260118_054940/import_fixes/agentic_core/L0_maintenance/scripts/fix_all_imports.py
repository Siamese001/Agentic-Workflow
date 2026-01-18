from __future__ import annotations
"""
Fix all incorrect imports after bulk hierarchy heal.
"""
import os
import re
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


def fix_imports_in_file(file_path: Path) -> int:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        original_content: Any = content
        replacements: Any = [('from agentic_core\\.base import', 'from agentic_core.L2_execution.ToolRegistry.base import'), ('import agentic_core\\.base', 'import agentic_core.L2_execution.tool_registry.base'), ('from agentic_core\\.L2_execution\\.P4_agents\\.', 'from agentic_core.L2_execution.ToolRegistry.'), ('import agentic_core\\.L2_execution\\.P4_agents\\.', 'import agentic_core.L2_execution.tool_registry.'), ('from agentic_core\\.L2_execution\\.P2_tools\\.', 'from agentic_core.L2_execution.ToolRegistry.'), ('import agentic_core\\.L2_execution\\.P2_tools\\.', 'import agentic_core.L2_execution.tool_registry.'), ('from agentic_core\\.L2_execution\\.P3_engines\\.', 'from agentic_core.L2_execution.ToolRegistry.'), ('import agentic_core\\.L2_execution\\.P3_engines\\.', 'import agentic_core.L2_execution.tool_registry.'), ('from agentic_core\\.L5_safety\\.P1_core\\.', 'from agentic_core.L5_safety.guardrails.'), ('import agentic_core\\.L5_safety\\.P1_core\\.', 'import agentic_core.L5_safety.guardrails.'), ('from agentic_core\\.L5_safety\\.policy\\.', 'from agentic_core.L5_safety.guardrails.'), ('import agentic_core\\.L5_safety\\.policy\\.', 'import agentic_core.L5_safety.guardrails.'), ('from agentic_core\\.L4_state\\.cache\\.', 'from agentic_core.L4_state.validation_context.'), ('import agentic_core\\.L4_state\\.cache\\.', 'import agentic_core.L4_state.validation_context.'), ('from agentic_core\\.L4_state\\.vector\\.', 'from agentic_core.L4_state.validation_context.'), ('import agentic_core\\.L4_state\\.vector\\.', 'import agentic_core.L4_state.validation_context.')]
        for pattern, replacement in replacements:
            content: Any = re.sub(pattern, replacement, content)
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed imports in: {file_path}')
            return 1
        return 0
    except Exception as e:
        print(f'Error processing {file_path}: {e}')
        return 0

def main() -> Any:
    """Fix all imports in the codebase."""
    fixed_count: Any = 0
    total_files: Any = 0
    for py_file in Path('agentic_core').rglob('*.py'):
        if py_file.name in ['__init__.py']:
            continue
        total_files += 1
        fixed_count += fix_imports_in_file(py_file)
    print(f'\nFixed imports in {fixed_count} out of {total_files} files')
if __name__ == '__main__':
    main()
