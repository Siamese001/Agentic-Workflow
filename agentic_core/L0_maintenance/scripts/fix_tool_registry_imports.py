"""
Fix imports in ToolRegistry files after bulk hierarchy heal.
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
        replacements: Any = [('from AgenticCore\\.L2_execution\\.P4_agents\\.', 'from AgenticCore.L2_execution.ToolRegistry.'), ('from AgenticCore\\.L2_execution\\.P4_agents$', 'from AgenticCore.L2_execution.ToolRegistry'), ('from AgenticCore\\.L2_execution\\.P2_tools\\.', 'from AgenticCore.L2_execution.ToolRegistry.'), ('from AgenticCore\\.L2_execution\\.P2_tools$', 'from AgenticCore.L2_execution.ToolRegistry'), ('from AgenticCore\\.L2_execution\\.P3_engines\\.', 'from AgenticCore.L2_execution.ToolRegistry.'), ('from AgenticCore\\.L2_execution\\.P3_engines$', 'from AgenticCore.L2_execution.ToolRegistry'), ('import AgenticCore\\.L2_execution\\.P4_agents\\.', 'import AgenticCore.L2_execution.ToolRegistry.'), ('import AgenticCore\\.L2_execution\\.P2_tools\\.', 'import AgenticCore.L2_execution.ToolRegistry.'), ('import AgenticCore\\.L2_execution\\.P3_engines\\.', 'import AgenticCore.L2_execution.ToolRegistry.')]
        for pattern, replacement in replacements:
            content: Any = re.sub(pattern, replacement, content)
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Fixed imports in: {file_path.name}')
            return 1
        return 0
    except Exception as e:
        print(f'Error processing {file_path}: {e}')
        return 0

def main() -> Any:
    """Fix all imports in ToolRegistry directory."""
    ToolRegistry: Any = Path('AgenticCore/L2_execution/ToolRegistry')
    if not ToolRegistry.exists():
        print(f'Directory not found: {ToolRegistry}')
        return
    fixed_count: Any = 0
    total_files: Any = 0
    for py_file in ToolRegistry.glob('*.py'):
        if py_file.name in ['__init__.py', 'fix_imports.py']:
            continue
        total_files += 1
        fixed_count += fix_imports_in_file(py_file)
    print(f'\nFixed imports in {fixed_count} out of {total_files} files')
if __name__ == '__main__':
    main()
