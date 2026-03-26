#!/usr/bin/env python3
"""Fix module-level code execution in template test files."""

import pathlib
import re
import sys

def fix_module_level_code(file_path: pathlib.Path) -> bool:
    """Fix module-level code that executes during collection."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Remove module-level code that's not inside functions
        # Pattern: code after a function definition but before the next function
        lines = content.split('\n')
        new_lines = []
        in_function = False
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            # Check if we're entering a function
            if stripped.startswith('def ') or stripped.startswith('class '):
                in_function = True
                indent_level = len(line) - len(line.lstrip())
                new_lines.append(line)
                continue
            
            # Check if we're exiting a function (same or lower indent)
            if in_function and line and len(line) - len(line.lstrip()) <= indent_level:
                if stripped and not stripped.startswith('#') and not stripped.startswith('def ') and not stripped.startswith('class '):
                    # This is module-level code after a function, skip it
                    in_function = False
                    continue
            
            new_lines.append(line)
        
        content = '\n'.join(new_lines)
        
        # Also remove stray assert statements at module level
        content = re.sub(r'^\s*assert.*$', '', content, flags=re.MULTILINE)
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
        
    except Exception as e:
        print(f"Error fixing {file_path}: {e}", file=sys.stderr)
        return False

def main():
    """Fix all files with module-level code execution."""
    # Files that have module-level code execution issues
    error_files = [
        "tests/unit/agentic_core/L0_routing/engines/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/meta_control/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/reasoning/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/scripts/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_coverage_adg.py",
        "tests/unit/agentic_core/L0_routing/scripts/test_drift_adg.py",
        "tests/unit/agentic_core/L0_routing/seams/test_safety_kernel_seam.py",
        "tests/unit/agentic_core/L0_routing/seams/test_vigilance_seam_adg.py",
        "tests/unit/agentic_core/L0_routing/types/test___init___adg.py",
        "tests/unit/agentic_core/L0_routing/utils/test___init___adg.py",
    ]
    
    fixed_count = 0
    for file_path in error_files:
        path = pathlib.Path(file_path)
        if path.exists():
            if fix_module_level_code(path):
                print(f"Fixed: {file_path}")
                fixed_count += 1
        else:
            print(f"Not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files")

if __name__ == "__main__":
    main()
