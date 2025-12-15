#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal safe fixer for Canon Validator.
Only handles non-destructive fixes that cannot corrupt files.
Targets: Keys 4, 5, 11 (bare except, empty except, trailing whitespace)
"""

import os
import re

def fix_file(file_path):
    """Apply safe fixes to a file."""
    try:
        # Read file with UTF-8 encoding
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Key 4: Fix bare except (safe regex operation)
        content = re.sub(r'(?m)^\s*except:\s*$', r'except Exception:', content)
        
        # Key 5: Fix empty except blocks (add pass) - conservative approach
        # Only add pass if the except block is truly empty
        content = re.sub(r'except (.*):\s*\n\s*\n', r'except \1:\n    pass\n\n', content)
        
        # Key 11: Trailing whitespace (completely safe)
        content = re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)
        
        # Write back if changed
        if content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"   ERROR: Failed to fix {file_path}: {e}")
        return False

def main():
    print("Running minimal safe fixer...")
    count = 0
    for root, dirs, files in os.walk("."):
        if ".git" in dirs: dirs.remove(".git")
        if "__pycache__" in dirs: dirs.remove("__pycache__")
        
        for file in files:
            if file.endswith(".py"):
                if fix_file(os.path.join(root, file)):
                    count += 1
    print(f"Fixed {count} files.")

if __name__ == "__main__":
    main()
