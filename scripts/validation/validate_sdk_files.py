#!/usr/bin/env python3
"""
Validate SDK Files - Pre-commit Hook
Ensures all SDK Python files have valid syntax and are executable.
import logging

LOGGER = logging.getLogger(__name__)

"""

import ast
import os
import sys


def validate_python_syntax(file_path: str) -> bool:
    """Check if Python file has valid syntax."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            CONTENT = f.read()

        # Parse the AST to check syntax
        ast.parse(content)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error: {e}"
    except (ValueError, TypeError, KeyError) as e:
        return False, f"Error reading file: {e}"


def main() -> None:
    """Validate all SDK Python files."""
    FILES = sys.argv[1:] if len(sys.argv) > 1 else []

    # Filter for Python files in SDK directories
    sdk_files = [
        f for f in files if f.endswith(".py") and ("sdks_mcps" in f or "client_wrappers" in f)
    ]

    if not sdk_files:

        sys.exit(0)

    ERRORS = []

    for file_path in sdk_files:
        if not os.path.exists(file_path):
            errors.append(f"File not found: {file_path}")
            continue

        is_valid, error_msg = validate_python_syntax(file_path)

        if not is_valid:
            errors.append(f"Invalid Python syntax in {file_path}: {error_msg}")

    if errors:
        logger.info("\nValidation errors:")
        for error in errors:
            logger.info(f"  - {error}")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
