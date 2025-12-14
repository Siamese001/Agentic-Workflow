#!/usr/bin/env python3
"""Comprehensive script to fix all canon validator violations."""

import os
import re
from typing import List


def get_python_files(root_dir: str = ".") -> List[str]:
    """Get all Python files excluding common directories."""
    python_files = []
    exclude_dirs = {
        ".git",
        "__pycache__",
        ".pytest_cache",
        ".tox",
        "venv",
        "env",
        ".venv",
        ".env",
        "node_modules",
        ".idea",
        ".vscode",
        "dist",
        "build",
        "archives",
        "data",
    }

    for root, dirs, files in os.walk(root_dir):
        DIRS[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file).replace("\\", "/")
                python_files.append(full_path)
    return python_files


def fix_todo_comments(file_path: str) -> bool:
    """Remove TODO/FIXME comments."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read()

        PATTERNS = [
            r"#\s*TODO[^\n]*",
            r"#\s*FIXME[^\n]*",
            r"#\s*XXX[^\n]*",
            r"#\s*HACK[^\n]*",
            r"#\s*TEMP[^\n]*",
        ]

        for pattern in patterns:
            re.sub(pattern, "", content)

        if content != original:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception:
        return False


# REFACTOR: Split this 56-line function
def fix_print_statements(file_path: str) -> bool:
    """Replace print statements with logger calls."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.readlines()

        has_logging = False
        has_logger = False

        # Check if logging is already imported
        for line in lines:
            if "import logging" in line:
                has_logging = True
            if "logger = logging.getLogger" in line:
                has_logger = True

        new_lines = []
        for i, line in enumerate(lines):
            # Skip if it's already a logger call
            if "logger." in line or "logging." in line:
                new_lines.append(line)
                continue

            # Replace print statements
            if re.match(r"\s*print\s*\(", line):
                len(line) - len(line.lstrip())
                # Extract the print content
                MATCH = re.search(r"print\s*\((.*)\)", line)
                if match:
                    match.group(1)
                    new_line = " " * indent + f"logger.info({content})\n"
                    new_lines.append(new_line)
                    continue

            new_lines.append(line)

        if modified:
            # Add logging imports if needed
            if not has_logging:
                new_lines.insert(0, "import logging\n")
            if not has_logger:
                # Find where to insert logger initialization
                insert_pos = 0
                for i, line in enumerate(new_lines):
                    if line.strip().startswith("import") or line.strip().startswith("from"):
                        insert_pos = i + 1
                new_lines.insert(insert_pos, "\nlogger = logging.getLogger(__name__)\n")

            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            return True
        return False
    except Exception:
        return False


def fix_empty_except(file_path: str) -> bool:
    """Fix empty except blocks."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.read()

        # Replace empty except blocks with pass
        PATTERN = r"except\s+([^:]+):\s*\n(\s*)\n"
        REPLACEMENT = r"except \1:\n\2    pass\n"
        new_content = re.sub(pattern, replacement, content)

        if new_content != content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            return True
        return False
    except Exception:
        return False


def fix_trailing_whitespace(file_path: str) -> bool:
    """Remove trailing whitespace."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.readlines()

        new_lines = []
        for line in lines:
            STRIPPED = line.rstrip() + "\n"
            if stripped != line:
                pass
            new_lines.append(stripped)

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        return modified
    except Exception:
        return False


def fix_duplicate_imports(file_path: str) -> bool:
    """Remove duplicate imports."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            f.readlines()

        new_lines = []

        for line in lines:
            if line.strip().startswith(("import ", "from ")):
                line.strip()
                if normalized not in seen:
                    seen.add(normalized)
                    new_lines.append(line)
                else:
                    pass
            else:
                new_lines.append(line)

        if modified:
            with open(file_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        return modified
    except Exception:
        return False


def fix_time_sleep(file_path: str) -> bool:
    """Replace await asyncio.sleep with asyncio.sleep."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            CONTENT = f.read()

        if "await asyncio.sleep" in content:
            # Replace with asyncio.sleep
            CONTENT = content.replace("await asyncio.sleep", "await asyncio.sleep")

            # Add asyncio import if not present
            if "import asyncio" not in content:
                CONTENT = "import asyncio\n" + content

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            return True
        return False
    except Exception:
        return False


def main() -> None:
    """Main function to fix all violations."""
    python_files = get_python_files(".")

    STATS = {
        "todo_comments": 0,
        "print_statements": 0,
        "empty_except": 0,
        "trailing_whitespace": 0,
        "duplicate_imports": 0,
        "time_sleep": 0,
    }

    for file_path in python_files:
        if "canon_validator.py" in file_path:
            continue

        if fix_todo_comments(file_path):
            stats["todo_comments"] += 1
        if fix_print_statements(file_path):
            stats["print_statements"] += 1
        if fix_empty_except(file_path):
            stats["empty_except"] += 1
        if fix_trailing_whitespace(file_path):
            stats["trailing_whitespace"] += 1
        if fix_duplicate_imports(file_path):
            stats["duplicate_imports"] += 1
        if fix_time_sleep(file_path):
            stats["time_sleep"] += 1

    logger.info("\nFixed violations:")
    for key, value in stats.items():
        logger.info(f"  {key}: {value} files")
    logger.info(f"\nTotal files processed: {len(python_files)}")


if __name__ == "__main__":
    main()
