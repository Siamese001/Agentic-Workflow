#!/usr/bin/env python3
"""
Fix markdown code fences in Python files.
Removes ```python and ``` from files that have them.
"""

import re
from pathlib import Path

def fix_markdown_fences(file_path: str) -> bool:
    """Remove markdown code fences from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has markdown fences
        if '```python' not in content and '```' not in content:
            return False
        
        # Remove opening fence
        content = re.sub(r'^```python\s*\n', '', content, flags=re.MULTILINE)
        
        # Remove closing fence at end of file
        content = re.sub(r'\n```\s*$', '', content)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Fixed: {file_path}")
        return True
    except Exception as e:
        print(f"❌ Error fixing {file_path}: {e}")
        return False

def main():
    """Find and fix all Python files with markdown fences."""
    root = Path("c:/Git/Agentic-Workflow/agentic_core")
    
    fixed_count = 0
    for py_file in root.rglob("*.py"):
        if fix_markdown_fences(str(py_file)):
            fixed_count += 1
    
    print(f"\n🎯 Fixed {fixed_count} files")

if __name__ == "__main__":
    main()
