#!/usr/bin/env python3
"""
Fix imports in tool_registry files after bulk hierarchy heal.
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
        
        # Replace all variations of old imports
        replacements = [
            # P4_agents
            (r'from agentic_core\.L2_execution\.P4_agents\.', 'from agentic_core.L2_execution.tool_registry.'),
            (r'from agentic_core\.L2_execution\.P4_agents$', 'from agentic_core.L2_execution.tool_registry'),
            # P2_tools
            (r'from agentic_core\.L2_execution\.P2_tools\.', 'from agentic_core.L2_execution.tool_registry.'),
            (r'from agentic_core\.L2_execution\.P2_tools$', 'from agentic_core.L2_execution.tool_registry'),
            # P3_engines
            (r'from agentic_core\.L2_execution\.P3_engines\.', 'from agentic_core.L2_execution.tool_registry.'),
            (r'from agentic_core\.L2_execution\.P3_engines$', 'from agentic_core.L2_execution.tool_registry'),
            # Import statements
            (r'import agentic_core\.L2_execution\.P4_agents\.', 'import agentic_core.L2_execution.tool_registry.'),
            (r'import agentic_core\.L2_execution\.P2_tools\.', 'import agentic_core.L2_execution.tool_registry.'),
            (r'import agentic_core\.L2_execution\.P3_engines\.', 'import agentic_core.L2_execution.tool_registry.'),
        ]
        
        for pattern, replacement in replacements:
            content = re.sub(pattern, replacement, content)
        
        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Fixed imports in: {file_path.name}")
            return 1
        
        return 0
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return 0

def main():
    """Fix all imports in tool_registry directory."""
    tool_registry = Path("agentic_core/L2_execution/tool_registry")
    
    if not tool_registry.exists():
        print(f"Directory not found: {tool_registry}")
        return
    
    fixed_count = 0
    total_files = 0
    
    for py_file in tool_registry.glob("*.py"):
        if py_file.name in ["__init__.py", "fix_imports.py"]:
            continue
        
        total_files += 1
        fixed_count += fix_imports_in_file(py_file)
    
    print(f"\nFixed imports in {fixed_count} out of {total_files} files")

if __name__ == "__main__":
    main()
