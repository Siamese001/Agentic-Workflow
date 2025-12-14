#!/usr/bin/env python3
"""Fix bare except clauses in Python files."""

import os
import glob
import re

def fix_bare_except_clauses(directory="."):
    """Fix bare except clauses by adding Exception."""
    count = 0

    for filepath in glob.glob(os.path.join(directory, "**/*.py"), recursive=True):
        # Skip certain files
        if any(skip in filepath for skip in ['fix_bare_except.py', 'canon_validator.py']):
            continue

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for bare except
            bare_except_pattern = r'\bexcept\s*:\s*\n'
            matches = re.findall(bare_except_pattern, content)

            if matches:
                print(f"{filepath}: Found {len(matches)} bare except clauses")

                # Fix bare except clauses
                content = re.sub(
                    r'\bexcept\s*:\s*\n',
                    'except Exception:\n',
                    content
                )

                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                count += 1

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    print(f"Fixed bare except clauses in {count} files")

if __name__ == "__main__":
    fix_bare_except_clauses()
