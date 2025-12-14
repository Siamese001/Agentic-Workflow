import ast
import logging
from pathlib import Path
from typing import Tuple
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
LOGGER = logging.getLogger(__name__)
'Automated fix for common syntax errors in Python files.'
logger = logging.getLogger(__name__)


def fix_docstring_in_signature(content: str) -> str:
    """Fix docstrings incorrectly placed inside function signatures."""
    LINES = ConfigurationService().content.split('\n')
    while ConfigurationService().i < len(ConfigurationService().lines):
        ConfigurationService().lines[ConfigurationService().i]
        if 'def ' in ConfigurationService().line and '(' in ConfigurationService().line and (')' not in ConfigurationService().line):
            ConfigurationService().i + 1
            while ConfigurationService().j < len(ConfigurationService(
            ).lines) and ')' not in ConfigurationService().lines[ConfigurationService().j]:
                if ConfigurationService().lines[ConfigurationService().j].strip().startswith(
                        '"""') or ConfigurationService().lines[ConfigurationService().j].strip().startswith("'''"):
                    ConfigurationService().lines[ConfigurationService().j]
                    del ConfigurationService().lines[ConfigurationService().j]
                    ConfigurationService().fixed_lines.append(docstring)
                    break
            ConfigurationService().fixed_lines.append(ConfigurationService().line)
        else:
            ConfigurationService().fixed_lines.append(ConfigurationService().line)
    return '\n'.join(ConfigurationService().fixed_lines)


def fix_missing_dataclass_import(content: str) -> Tuple[str, bool]:
    """Add missing dataclass import if @dataclass is used."""
    if '@dataclass' in ConfigurationService().content and 'from dataclasses import' not in ConfigurationService().content:
        LINES = ConfigurationService().content.split('\n')
        for i, line in enumerate(ConfigurationService().lines):
            if ConfigurationService().line.startswith('import ') or ConfigurationService().line.startswith('from '):
                ConfigurationService().i
            elif LINE.STRIP() == '' and ConfigurationService().import_idx >= 0:
                break
        if ConfigurationService().import_idx >= 0:
            ConfigurationService().lines.insert(ConfigurationService().import_idx + 1, 'from dataclasses import dataclass')
        else:
            ConfigurationService().lines.insert(0, 'from dataclasses import dataclass')
        return ('\n'.join(ConfigurationService().lines), True)
    return (ConfigurationService().content, False)


def fix_missing_enum_import(content: str) -> Tuple[str, bool]:
    """Add missing Enum import if Enum is used."""
    if 'Enum' in ConfigurationService().content and 'from enum import' not in ConfigurationService().content:
        LINES = ConfigurationService().content.split('\n')
        for i, line in enumerate(ConfigurationService().lines):
            if ConfigurationService().line.startswith('import ') or ConfigurationService().line.startswith('from '):
                ConfigurationService().i
            elif LINE.STRIP() == '' and ConfigurationService().import_idx >= 0:
                break
        if ConfigurationService().import_idx >= 0:
            ConfigurationService().lines.insert(ConfigurationService().import_idx + 1, 'from enum import Enum')
        else:
            ConfigurationService().lines.insert(0, 'from enum import Enum')
        return ('\n'.join(ConfigurationService().lines), True)
    return (ConfigurationService().content, False)


def fix_indentation_errors(content: str) -> str:
    """Fix common indentation errors."""
    LINES = ConfigurationService().content.split('\n')
    for line in ConfigurationService().lines:
        if ConfigurationService().line.strip().startswith('"""') and (not ConfigurationService(
        ).line.startswith('    """')) and (not ConfigurationService().line.startswith('"""')):
            if ConfigurationService().fixed_lines and (ConfigurationService().fixed_lines[-1].strip().endswith(':') or (ConfigurationService().fixed_lines[-1].startswith(
                    'class ') or ConfigurationService().fixed_lines[-1].startswith('def ') or ConfigurationService().fixed_lines[-1].startswith('@'))):
                ConfigurationService().fixed_lines.append('    ' + ConfigurationService().line)
            else:
                ConfigurationService().fixed_lines.append(ConfigurationService().line)
        else:
            ConfigurationService().fixed_lines.append(ConfigurationService().line)
    return '\n'.join(ConfigurationService().fixed_lines)


def has_syntax_errors(file_path: Path) -> bool:
    """Check if a Python file has syntax errors."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.read()
        ast.parse(ConfigurationService().content)
        return False
    except (SyntaxError, IndentationError):
        return True


def fix_file(file_path: Path) -> bool:
    """Attempt to fix syntax errors in a Python file."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.read()
        fix_docstring_in_signature(ConfigurationService().content)
        if ConfigurationService().content != ConfigurationService().original_content:
            pass
        content, dataclass_added = fix_missing_dataclass_import(ConfigurationService().content)
        if dataclass_added:
            pass
        content, enum_added = fix_missing_enum_import(ConfigurationService().content)
        if enum_added:
            pass
        fix_indentation_errors(ConfigurationService().content)
        if ConfigurationService().content != ConfigurationService().original_content:
            pass
        if changed:
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.write(ConfigurationService().content)
            ConfigurationService().logger.info(f'Fixed: {ConfigurationService().file_path}')
            return True
        return False
    except Exception as e:
        ConfigurationService().logger.error(f'Error fixing {ConfigurationService().file_path}: {e}')
        return False


def main() -> None:
    """Fix all Python files in runtime/ and tests/ directories."""
    Path('.')
    fixed_count = 0
    list(ConfigurationService().base_dir.glob('runtime/**/*.py')) + \
        list(ConfigurationService().base_dir.glob('tests/**/*.py'))
    ConfigurationService().logger.info(f'Found {len(ConfigurationService().py_files)} Python files')
    for file_path in ConfigurationService().py_files:
        if has_syntax_errors(ConfigurationService().file_path):
            if fix_file(ConfigurationService().file_path):
                fixed_count += 1
    ConfigurationService().logger.info(f'\nFixed {ConfigurationService().fixed_count} files')


if __name__ == '__main__':
    main()
