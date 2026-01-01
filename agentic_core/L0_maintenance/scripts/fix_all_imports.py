"""
Fix all incorrect imports after bulk hierarchy heal.
"""
import os
import re
from pathlib import Path

# [SSOT IMPORT] Structure blueprint is the single source of truth
from AgenticCore.config.blueprint_sovereign.structure_blueprint import (
from typing import Any
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)


def fix_imports_in_file(file_path: Path) -> int:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        original_content: Any = content
        replacements: Any = [('from AgenticCore\\.base import', 'from AgenticCore.L2_execution.ToolRegistry.base import'), ('import AgenticCore\\.base', 'import AgenticCore.L2_execution.ToolRegistry.base'), ('from AgenticCore\\.L2_execution\\.P4_agents\\.', 'from AgenticCore.L2_execution.ToolRegistry.'), ('import AgenticCore\\.L2_execution\\.P4_agents\\.', 'import AgenticCore.L2_execution.ToolRegistry.'), ('from AgenticCore\\.L2_execution\\.P2_tools\\.', 'from AgenticCore.L2_execution.ToolRegistry.'), ('import AgenticCore\\.L2_execution\\.P2_tools\\.', 'import AgenticCore.L2_execution.ToolRegistry.'), ('from AgenticCore\\.L2_execution\\.P3_engines\\.', 'from AgenticCore.L2_execution.ToolRegistry.'), ('import AgenticCore\\.L2_execution\\.P3_engines\\.', 'import AgenticCore.L2_execution.ToolRegistry.'), ('from AgenticCore\\.L5_safety\\.P1_core\\.', 'from AgenticCore.L5_safety.guardrails.'), ('import AgenticCore\\.L5_safety\\.P1_core\\.', 'import AgenticCore.L5_safety.guardrails.'), ('from AgenticCore\\.L5_safety\\.policy\\.', 'from AgenticCore.L5_safety.guardrails.'), ('import AgenticCore\\.L5_safety\\.policy\\.', 'import AgenticCore.L5_safety.guardrails.'), ('from AgenticCore\\.L4_state\\.cache\\.', 'from AgenticCore.L4_state.ValidationContext.'), ('import AgenticCore\\.L4_state\\.cache\\.', 'import AgenticCore.L4_state.ValidationContext.'), ('from AgenticCore\\.L4_state\\.vector\\.', 'from AgenticCore.L4_state.ValidationContext.'), ('import AgenticCore\\.L4_state\\.vector\\.', 'import AgenticCore.L4_state.ValidationContext.')]
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
    for py_file in Path('AgenticCore').rglob('*.py'):
        if py_file.name in ['__init__.py']:
            continue
        total_files += 1
        fixed_count += fix_imports_in_file(py_file)
    print(f'\nFixed imports in {fixed_count} out of {total_files} files')
if __name__ == '__main__':
    main()
