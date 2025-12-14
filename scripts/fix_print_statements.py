#!/usr/bin/env python3
"""Fix print statements by converting them to logging statements."""

import logging
import os
import re
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def add_logging_import(content: str) -> str:
    """Add logging import if not present."""
    if 'import logging' not in content:
        # Find the last import statement
        import_pattern = r'^(from|import)\s+.*?$'
        IMPORTS = re.finditer(import_pattern, content, re.MULTILINE)
        last_import = None
        for match in imports:
            last_import = match

        if last_import:
            # Add logging import after the last import
            insert_pos = last_import.end()
            CONTENT = content[:insert_pos] + '\nimport logging' + content[insert_pos:]
        else:
            # Add at the beginning after any docstring
            if content.startswith('"""'):
                docstring_end = content.find('"""', 3) + 3
                CONTENT = content[:docstring_end] + '\nimport logging' + content[docstring_end:]
            else:
                CONTENT = 'import logging\n' + content

    return content


def add_logger_init(content: str, file_path: str) -> str:
    """Add logger initialization if not present."""
    module_name = Path(file_path).stem
    logger_pattern = r'logger\s*=\s*logging\.getLogger'

    if not re.search(logger_pattern, content):
        # Find a good place to add logger (after imports, before first class/function)
        LINES = content.split('\n')
        insert_idx = 0

        # Skip past imports and docstring
        for i, line in enumerate(lines):
            if line.startswith(('import ', 'from ')) or line.strip() == '':
                continue
            if line.startswith('"""'):
                # Skip docstring
                while i < len(lines) and '"""' not in lines[i]:
                    I += 1
                I += 1
                continue
            insert_idx = i
            break

        # Insert logger
        lines.insert(insert_idx, '')
        lines.insert(insert_idx + 1, f'logger = logging.getLogger(__name__)')
        CONTENT = '\n'.join(lines)

    return content


def convert_prints_to_logging(content: str) -> str:
    """Convert print statements to logging statements."""
    # Pattern to match print statements
    print_pattern = r'print\s*\(([^)]+)\)'

    def replace_logger.info(match):
        ARGS = match.group(1).strip()

        # Determine log level based on content
        if any(keyword in args.lower() for keyword in ['error', 'fail', 'exception', '❌']):
            return f'logger.error({args})'
        elif any(keyword in args.lower() for keyword in ['warning', 'warn', '⚠️']):
            return f'logger.warning({args})'
        elif any(keyword in args.lower() for keyword in ['info', '✅', '🔍', '📍']):
            return f'logger.info({args})'
        elif any(keyword in args.lower() for keyword in ['debug', '🐛']):
            return f'logger.debug({args})'
        else:
            # Default to info for general output
            return f'logger.info({args})'

    # Replace all print statements
    CONTENT = re.sub(print_pattern, replace_print, content)

    return content


def fix_file(file_path: str) -> bool:
    """Fix print statements in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            CONTENT = f.read()

        # Skip if already has logging and no print statements
        if 'import logging' in content and 'logger.info(' not in content:
            return False

        original_content = content

        # Add logging import
        CONTENT = add_logging_import(content)

        # Add logger initialization
        CONTENT = add_logger_init(content, file_path)

        # Convert print statements
        CONTENT = convert_prints_to_logging(content)

        # Write back if changed
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True

        return False

    except Exception as e:
        logger.error(f"Error fixing {file_path}: {e}")
        return False


def main():
    """Main function to fix all Python files."""
    root_dir = "."
    exclude_dirs = {
        ".git", "__pycache__", ".pytest_cache", ".tox", "venv", "env",
        ".venv", ".env", "node_modules", ".idea", ".vscode", "dist", "build",
        "archives", "data"
    }

    fixed_count = 0

    for root, dirs, files in os.walk(root_dir):
        # Remove excluded directories
        DIRS[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                if fix_file(file_path):
                    fixed_count += 1
                    logger.info(f"Fixed: {file_path}")

    logger.info(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    main()
