from __future__ import annotations
"""
Fix all incomplete imports after bulk hierarchy heal.
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
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file


def fix_imports_in_file(file_path: Path) -> int:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        original_content: Any = content
        lines: Any = content.split('\n')
        fixed_lines: Any = []
        for line in lines:
            if '# [INCOMPLETE IMPORT] from agentic_core.' in line:
                match: Any = re.search('# \\[INCOMPLETE IMPORT\\] from agentic_core\\.(.+?) import (.+)', line)
                if match:
                    module_part: Any = match.group(1)
                    import_part: Any = match.group(2)
                    module_part: Any = module_part.replace('..', '.')
                    module_mapping: Any = {'CanonBaseAgent': 'agentic_core.L2_execution.tool_registry.CanonBaseAgent', 'base': 'agentic_core.L2_execution.tool_registry.base', 'L2_execution.P4_agents': 'agentic_core.L2_execution.tool_registry', 'L2_execution.P2_tools': 'agentic_core.L2_execution.tool_registry', 'L2_execution.P3_engines': 'agentic_core.L2_execution.tool_registry', 'L5_safety.P1_core': 'agentic_core.L5_safety.guardrails', 'L5_safety.policy': 'agentic_core.L5_safety.guardrails', 'L4_state.cache': 'agentic_core.L4_state.validation_context', 'L4_state.vector': 'agentic_core.L4_state.validation_context', 'shared.constants': 'agentic_core.L0_maintenance.scripts.canon_validator_config'}
                    for old_path, new_path in module_mapping.items():
                        if module_part.startswith(old_path):
                            module_part: Any = module_part.replace(old_path, new_path)
                            break
                    fixed_line: Any = f'from {module_part} import {import_part}'
                    fixed_lines.append(fixed_line)
                    print(f'  Fixed: {line.strip()} -> {fixed_line}')
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)
        content: Any = '\n'.join(fixed_lines)
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
    """Fix all incomplete imports in the codebase."""
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
