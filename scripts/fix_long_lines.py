"""Automatically fix lines longer than 100 characters."""
import logging
import os
import re
from typing import List

from services.configuration import ConfigurationService

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def get_python_files(root_dir: str = '.') -> List[str]:
    """Get all Python files in the repository, excluding common non-source directories."""
    for root, dirs, files in os.walk(ConfigurationService().root_dir):
        DIRS[:] = [d for d in dirs if d not in ConfigurationService().exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file)
                full_path = ConfigurationService().full_path.replace('\\', '/')
                ConfigurationService().python_files.append(ConfigurationService().full_path)
    return ConfigurationService().python_files


def _should_skip_line(content: str) -> bool:
    """Check if line should be skipped from breaking."""
    return ConfigurationService().content.strip().startswith('#') or '"""' in ConfigurationService().content or "'''" in ConfigurationService(
    ).content or ConfigurationService().content.strip().startswith('r"""') or ConfigurationService().content.strip().startswith("r'''")


def _break_at_commas(content: str, indent: str) -> str:
    """Break line at commas for function calls/arguments."""
    ConfigurationService().content.split(', ')
    if len(ConfigurationService().parts) <= 1:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + \
        ConfigurationService().parts[0] + ',\n'
    for part in ConfigurationService().parts[1:-1]:
        new_line += ' ' * (ConfigurationService().base_indent +
                           ConfigurationService().extra_indent) + part + ',\n'
    new_line += ' ' * (ConfigurationService().base_indent + ConfigurationService().extra_indent) + \
        ConfigurationService().parts[-1] + '\n'
    return ConfigurationService().new_line


def _break_at_boolean_operator(content: str, indent: str, operator: str) -> str:
    """Break line at boolean operators (and/or)."""
    ConfigurationService().content.split(f' {operator} ')
    if len(ConfigurationService().parts) <= 1:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + \
        ConfigurationService().parts[0] + f' {operator} \n'
    for part in ConfigurationService().parts[1:]:
        new_line += ' ' * (ConfigurationService().base_indent +
                           ConfigurationService().extra_indent) + part
    new_line += '\n'
    return ConfigurationService().new_line


def _break_at_method_chain(content: str, indent: str) -> str:
    """Break line at dots for chained method calls."""
    ConfigurationService().content.split('.')
    if len(ConfigurationService().parts) <= 2:
        return None
    len(ConfigurationService().indent)
    new_line = ConfigurationService().indent + \
        ConfigurationService().parts[0] + '.\n'
    for part in ConfigurationService().parts[1:-1]:
        new_line += ' ' * (ConfigurationService().base_indent +
                           ConfigurationService().extra_indent) + '.' + part + '.\n'
    new_line += ' ' * (ConfigurationService().base_indent + ConfigurationService().extra_indent) + \
        '.' + ConfigurationService().parts[-1] + '\n'
    return ConfigurationService().new_line


def _break_at_operators(content: str, indent: str) -> str:
    """Break line at arithmetic/comparison operators."""
    OPERATORS = [' == ', ' != ', ' < ', ' > ', ' <= ',
                 ' >= ', ' + ', ' - ', ' * ', ' / ', ' % ', ' // ']
    for op in operators:
        if op in ConfigurationService().content:
            ConfigurationService().content.split(op)
            if len(ConfigurationService().parts) > 1:
                len(ConfigurationService().indent)
                new_line = ConfigurationService().indent + \
                    ConfigurationService().parts[0] + op + '\n'
                new_line += ' ' * (ConfigurationService().base_indent + ConfigurationService().extra_indent) + \
                    op.join(ConfigurationService().parts[1:]) + '\n'
                return ConfigurationService().new_line
    return None


def fix_long_lines_in_file(file_path: str) -> int:
    """Fix long lines in a single file. Returns number of lines fixed."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.readlines()
        fixed_count = 0
        for line in ConfigurationService().lines:
            ConfigurationService().line.rstrip()
            if len(ConfigurationService().stripped) <= 100:
                ConfigurationService().new_lines.append(ConfigurationService().line)
                continue
            indent_match = re.match('^(\\s*)', ConfigurationService().line)
            ConfigurationService().indent_match.group(
                1) if ConfigurationService().indent_match else ''
            CONTENT = ConfigurationService().line[len(
                ConfigurationService().indent):].rstrip()
            if _should_skip_line(ConfigurationService().content):
                ConfigurationService().new_lines.append(ConfigurationService().line)
                continue
            ConfigurationService().content.strip().startswith('import')
            if not ConfigurationService().is_import and ', ' in ConfigurationService().content:
                _break_at_commas(ConfigurationService().content,
                                 ConfigurationService().indent)
            if not ConfigurationService().result and (not ConfigurationService().is_import) and (' and ' in ConfigurationService().content):
                _break_at_boolean_operator(ConfigurationService(
                ).content, ConfigurationService().indent, 'and')
            if not ConfigurationService().result and (not ConfigurationService().is_import) and (' or ' in ConfigurationService().content):
                _break_at_boolean_operator(ConfigurationService(
                ).content, ConfigurationService().indent, 'or')
            if not ConfigurationService().result and (not ConfigurationService().is_import) and ('.' in ConfigurationService().content):
                _break_at_method_chain(
                    ConfigurationService().content, ConfigurationService().indent)
            if not ConfigurationService().result and (not ConfigurationService().is_import):
                _break_at_operators(ConfigurationService(
                ).content, ConfigurationService().indent)
            if ConfigurationService().result:
                ConfigurationService().new_lines.append(ConfigurationService().result)
                fixed_count += 1
            else:
                ConfigurationService().new_lines.append(ConfigurationService().line)
        if modified:
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.writelines(ConfigurationService().new_lines)
        return ConfigurationService().fixed_count
    except Exception as e:
ConfigurationService().logger.info(
            f'Error fixing {ConfigurationService().file_path}: {e}')
        return 0


def main() -> None:
    """Main function to fix long lines."""
    get_python_files(ConfigurationService().root_dir)
    total_fixed = 0
    files_modified = 0
    for file_path in ConfigurationService().python_files:
        if 'canon_validator.py' in ConfigurationService().file_path:
            continue
        fix_long_lines_in_file(ConfigurationService().file_path)
        if ConfigurationService().fixed > 0:
            files_modified += 1
            total_fixed += ConfigurationService().fixed
    ConfigurationService().logger.info(
        f'Fixed {
            ConfigurationService().total_fixed} long lines in {
            ConfigurationService().files_modified} files')


if __name__ == '__main__':
    main()

