#!/usr/bin/env python3
"""
Fix all import issues in agentic_core after bulk hierarchy heal.
"""

import os
import re
from pathlib import Path

def fix_file_imports(file_path: Path) -> bool:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Define import mappings
        mappings = {
            # Old path -> New path
            'from agentic_core.base import': 'from agentic_core.L2_execution.tool_registry.base import',
            'from agentic_core.canon_base_agent import': 'from agentic_core.L2_execution.tool_registry.canon_base_agent import',
            'from agentic_core.L2_execution.P4_agents.': 'from agentic_core.L2_execution.tool_registry.',
            'from agentic_core.L2_execution.P2_tools.': 'from agentic_core.L2_execution.tool_registry.',
            'from agentic_core.L2_execution.P3_engines.': 'from agentic_core.L2_execution.tool_registry.',
            'from agentic_core.L5_safety.P1_core.': 'from agentic_core.L5_safety.guardrails.',
            'from agentic_core.L5_safety.policy.': 'from agentic_core.L5_safety.guardrails.',
            'from agentic_core.L4_state.cache.': 'from agentic_core.L4_state.validation_context.',
            'from agentic_core.L4_state.vector.': 'from agentic_core.L4_state.validation_context.',
            'from agentic_core.shared.constants import': 'from agentic_core.L0_maintenance.scripts.canon_validator_config import',
            'import agentic_core.base': 'import agentic_core.L2_execution.tool_registry.base',
            'import agentic_core.L2_execution.P4_agents.': 'import agentic_core.L2_execution.tool_registry.',
            'import agentic_core.L2_execution.P2_tools.': 'import agentic_core.L2_execution.tool_registry.',
            'import agentic_core.L2_execution.P3_engines.': 'import agentic_core.L2_execution.tool_registry.',
            # Relative imports
            'from L2_execution.tool_registry.base import': 'from agentic_core.L2_execution.tool_registry.base import',
            'from L2_execution.tool_registry.canon_base_agent import': 'from agentic_core.L2_execution.tool_registry.canon_base_agent import',
        }
        
        # Apply mappings
        for old, new in mappings.items():
            content = content.replace(old, new)
        
        # Fix incomplete imports
        content = re.sub(
            r'# \[INCOMPLETE IMPORT\] from agentic_core\.\.([^\s]+) import (.+)',
            r'from agentic_core.L2_execution.tool_registry.\1 import \2',
            content
        )
        
        # Fix double agentic_core
        content = re.sub(
            r'from agentic_core\.agentic_core\.',
            r'from agentic_core.',
            content
        )
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}")
        return False

def main():
    """Fix all imports in agentic_core."""
    fixed = 0
    total = 0
    
    for py_file in Path("agentic_core").rglob("*.py"):
        total += 1
        if fix_file_imports(py_file):
            fixed += 1
            print(f"Fixed: {py_file}")
    
    print(f"\nFixed {fixed} out of {total} files")

if __name__ == "__main__":
    main()
