#!/usr/bin/env python3
"""
Fix missing mixin imports across the codebase.
Targets: SubatomicTestingMixin, HealerMixin, MCPHardenedMixin
"""
import re
from pathlib import Path

def fix_mixin_imports():
    """Add missing mixin imports where classes inherit from them."""
    targets = {
        'SubatomicTestingMixin': 'from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin',
        'HealerMixin': 'from agentic_core.utils.core_extensions.healer_mixin import HealerMixin',
        'MCPHardenedMixin': 'from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin',
    }
    
    core_path = Path('agentic_core')
    fixed_count = 0
    
    print(f"--- [FIXING MIXIN IMPORTS] Path: {core_path.absolute()} ---")
    
    for py_file in core_path.rglob('*.py'):
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            modified = False
            
            for mixin_name, import_stmt in targets.items():
                # Check if class inherits from mixin but import is missing
                class_pattern = rf'class\s+\w+\([^)]*\b{mixin_name}\b'
                if re.search(class_pattern, content) and import_stmt not in content:
                    # Find the best place to insert the import
                    lines = content.splitlines()
                    insert_idx = 0
                    
                    # Find after __future__ imports and before other imports
                    for i, line in enumerate(lines):
                        if line.startswith('from __future__'):
                            insert_idx = i + 1
                        elif line.startswith('import ') or line.startswith('from '):
                            if insert_idx == 0:
                                insert_idx = i
                            break
                        elif line.startswith('"""') and i == 0:
                            # Skip docstring
                            for j, l in enumerate(lines[1:], 1):
                                if '"""' in l:
                                    insert_idx = j + 1
                                    break
                    
                    lines.insert(insert_idx, import_stmt)
                    content = '\n'.join(lines)
                    modified = True
                    print(f"  Fixed: {py_file.relative_to(core_path)} (added {mixin_name} import)")
            
            if modified:
                py_file.write_text(content + '\n', encoding='utf-8')
                fixed_count += 1
                
        except Exception as e:
            print(f"  Error processing {py_file}: {e}")
    
    print(f"--- [FIX COMPLETE] Fixed {fixed_count} files ---")
    return fixed_count

if __name__ == "__main__":
    print("=" * 70)
    print("Fixing Mixin Imports")
    print("=" * 70)
    
    fixed = fix_mixin_imports()
    
    print("\n" + "=" * 70)
    print(f"Total: {fixed} files fixed")
    print("=" * 70)
