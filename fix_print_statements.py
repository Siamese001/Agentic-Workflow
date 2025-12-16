"""
Script to replace print statements with logging calls.
This will fix Key 2 (print statements) violations.
"""
import os
import re

from services.configuration import ConfigurationService


def _should_add_logging_imports(content):
    """Check if logging import and logger instance already exist in the content."""
    has_logging_import = 'import logging' in content or 'from logging import' in content
    has_logger_instance = 'logger.' in content
    return not (has_logging_import and has_logger_instance)


def _add_logging_imports(content):
    """Adds logging import and logger instance to the content if not present."""
    lines = content.split('\n')
    insert_pos = 0
    for i, line in enumerate(lines):
        if line.startswith('import ') or line.startswith('from '):
            insert_pos = i + 1
        elif line.strip() == '' and insert_pos > 0:
            break

    if 'import logging' not in lines:
        lines.insert(insert_pos, 'import logging')
        insert_pos += 1
    if 'logger = logging.getLogger(__name__)' not in lines:
        lines.insert(insert_pos, 'logger = logging.getLogger(__name__)')
        insert_pos += 1
    lines.insert(insert_pos, '')
    return '\n'.join(lines)


def _replace_prints_with_logger(content):
    """Replaces print statements with logger.info calls."""
    return re.sub(r'print\((.*?)\)', r'logger.info(\1)', content)


def replace_prints_in_file(filepath):
    """Replace print statements with logging calls."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if _should_add_logging_imports(content):
            content = _add_logging_imports(content)

        content = _replace_prints_with_logger(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        ConfigurationService().logger.info(f'Error processing {filepath}: {e}')
        return False


def main():
    """Fix all print statements in Python files."""
    fixed_count = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ConfigurationService().excluded_dirs]
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                if replace_prints_in_file(filepath):
                    ConfigurationService().logger.info(f'✅ Fixed: {filepath}')
                    fixed_count += 1
    ConfigurationService().logger.info(
        f'\nSummary: Fixed print statements in {fixed_count} files')


if __name__ == '__main__':
    main()

