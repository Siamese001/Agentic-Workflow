#!/usr/bin/env python3
"""
Quick fix for the specific pass/pass indentation corruption pattern
"""

import os
import re


def fix_file(filepath):
    """Fix a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original = content
        
        # Fix the specific pattern: \n    pass\npass\n
        content = re.sub(r'\n\s+pass\n\s+pass\n', '\n', content)
        
        # Fix orphaned pass statements at start of except blocks
        content = re.sub(r'(\n\s+except\s+.*?:\s*\n)\s+pass\n', r'\1', content)
        
        # Fix double pass statements
        content = re.sub(r'(\n\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n', r'\1', content)
        
        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False
    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    fixed = 0
    for root, dirs, files in os.walk('/app'):
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if fix_file(filepath):
                    print(f"Fixed: {filepath}")
                    fixed += 1
    print(f"Fixed {fixed} files")

if __name__ == "__main__":
    main()
