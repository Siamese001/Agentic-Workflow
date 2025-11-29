#!/usr/bin/env python3
"""
Script to fix JSON syntax errors in windsurf_validation_keys.json
"""

import re

def fix_json_syntax(file_path):
    """Fix common JSON syntax errors by adding missing commas."""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Fix missing commas between JSON entries
    # Pattern: line ending with "" followed by newline and another line starting with ""
    pattern = r'("",)\s*\n\s*("")'
    content = re.sub(pattern, r'\1,\n  \2', content)
    
    # Also fix lines ending with "" followed by newline and non-quoted content
    pattern2 = r'("",)\s*\n\s*([^"\s])'
    content = re.sub(pattern2, r'\1,\n  \2', content)
    
    # Write fixed content back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("JSON syntax fix applied")

if __name__ == "__main__":
    fix_json_syntax("scripts/windsurf_validation_keys.json")
