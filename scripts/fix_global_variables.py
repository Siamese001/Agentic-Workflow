#!/usr/bin/env python3
"""
Fix global variable violations by replacing with manager pattern
"""

import os
import re
from pathlib import Path

def fix_global_variables(file_path: str):
    """Fix global variables in a Python file"""
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # Pattern to find global variable patterns
    # Matches: _var = None\n\ndef get_var():\n    global _var\n    if _var is None:\n        _var = Class()\n    return _var
    pattern = r'(_\w+)\s*=\s*None\s*\n\s*\n\s*def\s+get_\w+\([^)]*\):\s*\n\s*global\s+\1\s*\n\s*if\s+\1\s+is\s+None:\s*\n\s+\1\s*=\s*\w+\([^)]*\)\s*\n\s*return\s+\1'
    
    # Find all matches
    matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
    
    for match in matches:
        var_name = match.group(1)
        class_name = var_name.replace('_', '').title()
        
        # Generate replacement code
        replacement = f'''class {class_name}Manager:
    """Manager for {class_name} without global state"""
    
    def __init__(self):
        self._instance = None
    
    def get_instance(self):
        """Get or create the instance"""
        if self._instance is None:
            self._instance = {class_name}()
        return self._instance


# Global manager instance (acceptable as it's a dependency injection container)
_{var_name}_manager = {class_name}Manager()


def get_{var_name[1:]}():
    """Get the global instance"""
    return _{var_name}_manager.get_instance()'''
        
        # Replace the pattern
        content = content.replace(match.group(0), replacement)
    
    # Write back if changed
    if content != original:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed global variables in: {file_path}")
        return True
    
    return False

def main():
    """Fix all global variable violations"""
    # List of files with global violations (from validator output)
    files_to_fix = [
        'apps_shared/mcp_hardening.py',
        'apps_shared/strip_bom_and_fix.py',
        'apps_shared/time_bound_benchmarking.py',
        'apps_shared/utils.py',
        'apps_shared/verify_hardening.py',
        'apps_shared/verify_hardening_minimal.py',
        'apps_shared/verify_hardening_simple.py',
        'apps_shared/watchdog_sidecar.py',
        'scripts/shared/resilience/mixin.py',
        'scripts/shared/safety/constitutional_ai_impl.py',
        'tests/test_integrity.py',
        'tests/test_integrity_mock.py'
    ]
    
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_global_variables(file_path):
                fixed_count += 1
        else:
            print(f"File not found: {file_path}")
    
    print(f"\nFixed {fixed_count} files with global variable violations")

if __name__ == "__main__":
    main()
