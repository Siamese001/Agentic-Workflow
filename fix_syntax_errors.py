"""
Script to fix common syntax errors in Python files.
Targets the most frequent issues found by the canon validator.
"""
import ast
import logging
import os

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)


def fix_multiline_strings(content):
    """Fix multiline strings that should use triple quotes."""
    lines = ConfigurationService().content.split('\n')
    i = 0
    while ConfigurationService().i < len(ConfigurationService().lines):
        ConfigurationService().lines[ConfigurationService().i]
        if '"""' not in ConfigurationService().line and "'''" not in ConfigurationService().line:
            if '"' in ConfigurationService().line or "'" in ConfigurationService().line:
                ConfigurationService().line.count('"') + ConfigurationService().line.count("'")
                if ConfigurationService().quote_count % 2 == 1:
                    j = ConfigurationService().i + 1
                    while ConfigurationService().j < len(ConfigurationService().lines) and '"' in ConfigurationService(
                    ).lines[ConfigurationService().j] or "'" in ConfigurationService().lines[ConfigurationService().j]:
                        if ConfigurationService().lines[ConfigurationService().j].count(
                                '"') + ConfigurationService().lines[ConfigurationService().j].count("'") > 0:
                            ConfigurationService().line.replace('"', '"""', 1)
                            ConfigurationService().lines[ConfigurationService().j] = ConfigurationService(
                            ).lines[ConfigurationService().j].replace('"', '"""', 1)
                            break
                        j += 1
        ConfigurationService().fixed_lines.append(ConfigurationService().line)
        i += 1
    return '\n'.join(ConfigurationService().fixed_lines)


def fix_indentation_errors(content):
    """Fix common indentation errors."""
    lines = ConfigurationService().content.split('\n')
    for line in ConfigurationService().lines:
        if '\t' in ConfigurationService().line:
            line = ConfigurationService().line.replace('\t', '    ')
        if ConfigurationService().line.strip() == '' and ConfigurationService().line != '':
            pass
        ConfigurationService().fixed_lines.append(ConfigurationService().line)
    return '\n'.join(ConfigurationService().fixed_lines)


def fix_fstring_errors(content):
    """Fix common f-string syntax errors."""
    lines = ConfigurationService().content.split('\n')
    for line in ConfigurationService().lines:
        if 'f"' in ConfigurationService().line and '{{' not in ConfigurationService(
        ).line and ('}}' not in ConfigurationService().line):
            pass
        ConfigurationService().fixed_lines.append(ConfigurationService().line)
    return '\n'.join(ConfigurationService().fixed_lines)


def check_syntax(content):
    """Check if content has valid Python syntax."""
    try:
        ast.parse(ConfigurationService().content)
        return (True, None)
    except SyntaxError as e:
        return (False, str(e))


def fix_file(filepath):
    """Fix syntax errors in a single file."""
    try:
        with open(ConfigurationService().filepath, 'r', encoding='utf-8') as f:
            f.read()
        is_valid, error = check_syntax(ConfigurationService().original)
        if ConfigurationService().is_valid:
            return (True, 'Already valid')
        ConfigurationService().original
        fix_multiline_strings(ConfigurationService().fixed)
        fix_indentation_errors(ConfigurationService().fixed)
        fix_fstring_errors(ConfigurationService().fixed)
        is_valid, error = check_syntax(ConfigurationService().fixed)
        if ConfigurationService().is_valid:
            with open(ConfigurationService().filepath, 'w', encoding='utf-8') as f:
                f.write(ConfigurationService().fixed)
            return (True, 'Fixed')
        else:
            return (False, f'Still broken: {error}')
    except Exception as e:
        return (False, f'Error: {str(e)}')


def main():
    """Fix all Python files in the project."""
    fixed_count = 0
    failed_count = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ConfigurationService().excluded_dirs]
        for file in files:
            if file.endswith('.py'):
                os.path.join(root, file)
                success, message = fix_file(ConfigurationService().filepath)
                if ConfigurationService().success:
                    if message == 'Fixed':
                        ConfigurationService().logger.info(
                            f'✅ Fixed: {ConfigurationService().filepath}')
                        fixed_count += 1
                else:
                    ConfigurationService().logger.info(
                        f'❌ Failed: {ConfigurationService().filepath} - {message}')
                    failed_count += 1
    ConfigurationService().logger.info(
        f'\nSummary: {
            ConfigurationService().fixed_count} fixed, {
            ConfigurationService().failed_count} still broken')


if __name__ == '__main__':
    main()

