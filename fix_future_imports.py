#!/usr/bin/env python3
"""
Fix __future__ imports that were placed in wrong locations.
__future__ imports MUST be the very first statement in a Python file.
"""
import re
from pathlib import Path

def fix_future_imports():
    """Move __future__ imports to line 1 in all files where they're misplaced."""
    core_path = Path('agentic_core')
    fixed_count = 0
    
    print(f"--- [FIXING __future__ IMPORTS] Path: {core_path.absolute()} ---")
    
    for py_file in core_path.rglob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check if file has __future__ import but not at line 1
            if 'from __future__ import annotations' in content:
                lines = content.splitlines()
                
                # Find the __future__ import line
                future_idx = None
                for i, line in enumerate(lines):
                    if 'from __future__ import annotations' in line:
                        future_idx = i
                        break
                
                # If not at line 0, fix it
                if future_idx is not None and future_idx > 0:
                    # Remove the misplaced import
                    future_line = lines.pop(future_idx)
                    # Insert at the beginning
                    lines.insert(0, future_line)
                    
                    # Write back
                    py_file.write_text('\n'.join(lines) + '\n', encoding='utf-8')
                    print(f"  Fixed: {py_file.relative_to(core_path)} (moved from line {future_idx + 1} to line 1)")
                    fixed_count += 1
        except Exception as e:
            print(f"  Error processing {py_file}: {e}")
    
    print(f"--- [FIX COMPLETE] Fixed {fixed_count} files ---")
    return fixed_count

def add_missing_enum_auto():
    """Add 'auto' to enum imports where needed."""
    core_path = Path('agentic_core')
    fixed_count = 0
    
    print(f"\n--- [FIXING enum.auto IMPORTS] ---")
    
    for py_file in core_path.rglob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            
            # Check if file uses 'auto' but doesn't import it
            if re.search(r'\bauto\b', content) and 'from enum import' in content:
                if 'auto' not in content.split('from enum import')[1].split('\n')[0]:
                    # Need to add auto to the enum import
                    content = re.sub(
                        r'from enum import Enum\b',
                        'from enum import Enum, auto',
                        content
                    )
                    py_file.write_text(content, encoding='utf-8')
                    print(f"  Fixed: {py_file.relative_to(core_path)} (added auto to enum import)")
                    fixed_count += 1
        except Exception as e:
            print(f"  Error processing {py_file}: {e}")
    
    print(f"--- [FIX COMPLETE] Fixed {fixed_count} files ---")
    return fixed_count

if __name__ == "__main__":
    print("=" * 70)
    print("Fixing __future__ and enum imports")
    print("=" * 70)
    
    future_fixed = fix_future_imports()
    auto_fixed = add_missing_enum_auto()
    
    print("\n" + "=" * 70)
    print(f"Total: {future_fixed} __future__ fixes, {auto_fixed} enum.auto fixes")
    print("=" * 70)
