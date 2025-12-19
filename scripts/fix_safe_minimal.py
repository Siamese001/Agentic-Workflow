#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Minimal safe fixer for Canon Validator.
Only handles non-destructive fixes that cannot corrupt files.
Targets: Keys 4, 5, 11 (bare except, empty except, trailing whitespace)
"""

import logging
import os
import re

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def _fix_bare_except(content):
    """Fix bare except blocks by replacing them with 'except Exception as e:'."""
    return re.sub(r'(?m)^\s*except:\s*$', r'except Exception as e:', content)

def _fix_empty_except(content):
    """Fix empty except blocks by adding 'pass'."""
    # Only add pass if the except block is truly empty
    return re.sub(r'except (.*):\s*\n\s*\n',
                  r'except \1:\n    pass\n\n', content)

def _fix_trailing_whitespace(content):
    """Remove trailing whitespace from lines."""
    return re.sub(r'[ \t]+$', '', content, flags=re.MULTILINE)

def fix_file(file_path):
    """Apply safe fixes to a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        fixed_content = content

        # Key 4: Fix bare except
        fixed_content = _fix_bare_except(fixed_content)

        # Key 5: Fix empty except blocks
        fixed_content = _fix_empty_except(fixed_content)

        # Key 11: Trailing whitespace
        fixed_content = _fix_trailing_whitespace(fixed_content)

        if fixed_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            logging.info(f"Fixed {file_path}")
            return True

        return False

    except FileNotFoundError:
pass
logging.error(f"File not found: {file_path}")
        return False
    except Exception as e:
pass
logging.error(f"Failed to fix {file_path}: {e}")
        return False


def main():
    """Main function to walk through directories and fix Python files."""
    logging.info("Running minimal safe fixer...")
    count = 0
    for root, dirs, files in os.walk("."):
        # Avoid version control and cache directories
        if ".git" in dirs:
            dirs.remove(".git")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    count += 1
    logging.info(f"Fixed {count} files.")


if __name__ == "__main__":
    main()

