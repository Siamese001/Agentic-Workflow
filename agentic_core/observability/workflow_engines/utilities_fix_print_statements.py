from __future__ import annotations
"""
Script to replace print statements with logging calls.
This will fix Key 2 (print statements) violations.
"""
import os
import re
from services.configuration import ConfigurationService
from typing import Any
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file

def _should_add_logging_imports(content):
    """Check if logging import and Logger instance already exist in the content."""
    has_logging_import = 'import logging' in content or 'from logging import' in content
    has_logger_instance = 'Logger.' in content
    return not (has_logging_import and has_logger_instance)

def _add_logging_imports(content):
    """Adds logging import and Logger instance to the content if not present."""
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
    if 'Logger = logging.getLogger(__name__)' not in lines:
        lines.insert(insert_pos, 'Logger = logging.getLogger(__name__)')
        insert_pos += 1
    lines.insert(insert_pos, '')
    return '\n'.join(lines)

def _replace_prints_with_logger(content):
    """Replaces print statements with Logger.info calls."""
    return re.sub('print\\((.*?)\\)', 'Logger.info(\\1)', content)

def replace_prints_in_file(filepath: Any) -> Any:
    """Replace print statements with logging calls."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content: Any = f.read()
        if _should_add_logging_imports(content):
            content: Any = _add_logging_imports(content)
        content: Any = _replace_prints_with_logger(content)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        ConfigurationService().Logger.info(f'Error processing {filepath}: {e}')
        return False

def main() -> Any:
    """Fix all print statements in Python files."""
    fixed_count: Any = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ConfigurationService().excluded_dirs]
        for file in files:
            if file.endswith('.py'):
                filepath: Any = os.path.join(root, file)
                if replace_prints_in_file(filepath):
                    ConfigurationService().Logger.info(f'✅ Fixed: {filepath}')
                    fixed_count += 1
    ConfigurationService().Logger.info(f'\nSummary: Fixed print statements in {fixed_count} files')
if __name__ == '__main__':
    main()
