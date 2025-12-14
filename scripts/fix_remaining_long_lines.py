#!/usr/bin/env python3
"""Fix remaining long lines with simple patterns."""

import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fix_long_lines_in_file(filepath: str) -> int:
    """Fix long lines in a file using simple patterns."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()

        fixed_count = 0
        new_lines = []

        for line in lines:
            if len(line.rstrip()) > 100:
                # Pattern 1: Long import statements
                if line.strip().startswith(("import ", "from ")):
                    # Break imports at commas
                    if "," in line and not line.strip().startswith("from . import"):
                        parts = line.rstrip().split(", ")
                        if len(parts) > 1:
                            indent = len(line) - len(line.lstrip())
                            new_line = parts[0] + ",\n"
                            new_lines.append(new_line)
                            for part in parts[1:-1]:
                                new_lines.append(" " * (indent + 4) + part + ",\n")
                            new_lines.append(" " * (indent + 4) + parts[-1] + "\n")
                            fixed_count += 1
                            continue

                # Pattern 2: Long string concatenation
                if " + " in line and ('"' in line or "'" in line):
                    # Break string concatenation
                    parts = line.rstrip().split(" + ")
                    if len(parts) > 1:
                        indent = len(line) - len(line.lstrip())
                        new_line = parts[0] + "\n"
                        new_lines.append(new_line)
                        for part in parts[1:]:
                            new_lines.append(" " * (indent + 4) + "+ " + part + "\n")
                        fixed_count += 1
                        continue

                # Pattern 3: Long function calls with many arguments
                if "(" in line and ")" in line and "," in line:
                    # Try to break at commas
                    content = line.rstrip()
                    if content.count("(") == content.count(")"):  # Balanced parentheses
                        parts = content.split(",")
                        if len(parts) > 2:
                            indent = len(line) - len(line.lstrip())
                            new_line = parts[0] + ",\n"
                            new_lines.append(new_line)
                            for part in parts[1:-1]:
                                new_lines.append(" " * (indent + 4) + part + ",\n")
                            new_lines.append(" " * (indent + 4) + parts[-1] + "\n")
                            fixed_count += 1
                            continue

            new_lines.append(line)

        if fixed_count > 0:
            with open(filepath, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

        return fixed_count
    except Exception as e:
        logger.error(f"Error processing {filepath}: {e}")
        return 0


def main():
    """Fix long lines in all Python files."""
    total_fixed = 0

    for root, dirs, files in os.walk("."):
        if ".git" in dirs:
            dirs.remove(".git")
        if ".venv" in dirs:
            dirs.remove(".venv")
        if "__pycache__" in dirs:
            dirs.remove("__pycache__")

        for file in files:
            if file.endswith(".py"):
                filepath = os.path.join(root, file)
                fixed = fix_long_lines_in_file(filepath)
                if fixed > 0:
                    logger.info(f"Fixed {fixed} long lines in {filepath}")
                    total_fixed += fixed

    logger.info(f"Total fixed: {total_fixed} lines")


if __name__ == "__main__":
    main()
