#!/usr/bin/env python3
"""
Systematic fix for all indentation errors caused by the reorganization.
Pattern: except ...:\n    pass\npass\nlogger.error
"""

import os
import re


def fix_indentation_errors(file_path):
    """Fix indentation errors in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Pattern to match malformed exception blocks
        # This handles various whitespace patterns
        patterns = [
            # Pattern 1: except:\n    pass\npass\nlogger.error
            (r'(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n(.+?logger\.)', r'\1            \2'),
            # Pattern 2: except:\n    pass\npass\nreturn
            (r'(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n(.+?return)', r'\1            \2'),
            # Pattern 3: except:\n    pass\npass\nraise
            (r'(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n(.+?raise)', r'\1            \2'),
            # Pattern 4: except:\n    pass\npass\nif
            (r'(\s+except\s+.*?:\s*\n)\s+pass\n\s+pass\n(.+?if\s)', r'\1            \2'),
            # Pattern 5: Generic pattern for any content after pass\npass
            (r'\n\s+pass\n\s+pass\n(.+)', r'\n            \1'),
        ]

        changed = False
        for pattern, replacement in patterns:
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
            if new_content != content:
                content = new_content
                changed = True

        # Additional fix for orphaned pass statements
        content = re.sub(r'\n\s+pass\n\s+pass\n', '\n', content)

        if changed or content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Fix all Python files in the current directory and subdirectories."""
    fixed_count = 0
    total_files = 0

    for root, dirs, files in os.walk('.'):
        # Skip .git and other hidden directories
        dirs[:] = [d for d in dirs if not d.startswith('.')]

        for file in files:
            if file.endswith('.py'):
                total_files += 1
                file_path = os.path.join(root, file)
                if fix_indentation_errors(file_path):
                    print(f"Fixed: {file_path}")
                    fixed_count += 1

    print(f"\nSummary: Fixed {fixed_count} out of {total_files} Python files")

if __name__ == "__main__":
    main()
