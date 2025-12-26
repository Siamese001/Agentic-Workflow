#!/usr/bin/env python3
"""
Fix all incorrect imports after bulk hierarchy heal.
"""

import os
import re
from pathlib import Path

def fix_imports_in_file(file_path: Path) -> int:
    """Fix imports in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Fix various incorrect imports
        replacements = [
            # agentic_core.base -> tool_registry.base
            (r'from agentic_core\.base import', 'from agentic_core.L2_execution.tool_registry.base import'),
            (r'import agentic_core\.base', 'import agentic_core.L2_execution.tool_registry.base'),
            
            # P4_agents -> tool_registry
            (r'from agentic_core\.L2_execution\.P4_agents\.', 'from agentic_core.L2_execution.tool_registry.'),
            (r'import agentic_core\.L2_execution\.P4_agents\.', 'import agentic_core.L2_execution.tool_registry.'),
            
            # P2_tools -> tool_registry  
            (r'from agentic_core\.L2_execution\.P2_tools\.', 'from agentic_core.L2_execution.tool_registry.'),
            (r'import agentic_core\.L2_execution\.P2_tools\.', 'import agentic_core.L2_execution.tool_registry.'),
            
            # P3_engines -> tool_registry
            (r'from agentic_core\.L2_execution\.P3_engines\.', 'from agentic_core.L2_execution.tool_registry.'),
            (r'import agentic_core\.L2_execution\.P3_engines\.', 'import agentic_core.L2_execution.tool_registry.'),
            
            # L5_safety.P1_core -> L5_safety.guardrails
            (r'from agentic_core\.L5_safety\.P1_core\.', 'from agentic_core.L5_safety.guardrails.'),
            (r'import agentic_core\.L5_safety\.P1_core\.', 'import agentic_core.L5_safety.guardrails.'),
            
            # L5_safety.policy -> L5_safety.guardrails
            (r'from agentic_core\.L5_safety\.policy\.', 'from agentic_core.L5_safety.guardrails.'),
            (r'import agentic_core\.L5_safety\.policy\.', 'import agentic_core.L5_safety.guardrails.'),
            
            # L4_state.cache -> L4_state.validation_context
            (r'from agentic_core\.L4_state\.cache\.', 'from agentic_core.L4_state.validation_context.'),
            (r'import agentic_core\.L4_state\.cache\.', 'import agentic_core.L4_state.validation_context.'),
            
            # L4_state.vector -> L4_state.validation_context
            (r'from agentic_core\.L4_state\.vector\.', 'from agentic_core.L4_state.validation_context.'),
            (r'import agentic_core\.L4_state\.vector\.', 'import agentic_core.L4_state.validation_context.'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Fix all imports in the codebase."""
    fixed_count = 0
    total_files = 0
    
    # Scan all Python files in agentic_core
    for py_file in Path("agentic_core").rglob("*.py"):
        if py_file.name in ["__init__.py"]:
            continue
        
        total_files += 1
        fixed_count += fix_imports_in_file(py_file)
    
    print(f"\nFixed imports in {fixed_count} out of {total_files} files")

if __name__ == "__main__":
    main()
