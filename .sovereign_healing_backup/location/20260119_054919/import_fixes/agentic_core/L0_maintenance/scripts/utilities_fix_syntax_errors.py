from __future__ import annotations
"""
Script to fix common syntax errors in Python files.
Targets the most frequent issues found by the canon validator.
"""
import ast
import logging
import os
from services.configuration import ConfigurationService
from typing import Any
from agentic_core.utils.sovereign_index import SovereignIndex
from archives.location_violations.file_utils import safe_read_file, safe_write_file
Logger: Any = logging.getLogger(__name__)

def fix_multiline_strings(content: Any) -> Any:
    """Fix multiline strings that should use triple quotes."""
    lines: Any = content.split('\n')
    fixed_lines: Any = []
    i: Any = 0
    while i < len(lines):
        line: Any = lines[i]
        if '"""' not in line and "'''" not in line:
            if '"' in line or "'" in line:
                quote_count: Any = line.count('"') + line.count("'")
                if quote_count % 2 == 1:
                    j: Any = i + 1
                    while j < len(lines) and ('"' in lines[j] or "'" in lines[j]):
                        if lines[j].count('"') + lines[j].count("'") > 0:
                            line: Any = line.replace('"', '"""', 1)
                            lines[j] = lines[j].replace('"', '"""', 1)
                            break
                        j += 1
        fixed_lines.append(line)
        i += 1
    return '\n'.join(fixed_lines)

def fix_indentation_errors(content: Any) -> Any:
    """Fix common indentation errors."""
    lines: Any = content.split('\n')
    fixed_lines: Any = []
    for line in lines:
        if '\t' in line:
            line: Any = line.replace('\t', '    ')
        if line.strip() == '' and line != '':
            pass
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def fix_fstring_errors(content: Any) -> Any:
    """Fix common f-string syntax errors."""
    lines: Any = content.split('\n')
    fixed_lines: Any = []
    for line in lines:
        if 'f"' in line and '{{' not in line and ('}}' not in line):
            pass
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def check_syntax(content: Any) -> Any:
    """Check if content has valid Python syntax."""
    try:
        ast.parse(content)
        return (True, None)
    except SyntaxError as e:
        return (False, str(e))

def fix_file(filepath: Any) -> Any:
    """Fix syntax errors in a single file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_content: Any = f.read()
        is_valid, error = check_syntax(original_content)
        if is_valid:
            return (True, 'Already valid')
        fixed_content: Any = original_content
        fixed_content: Any = fix_multiline_strings(fixed_content)
        fixed_content: Any = fix_indentation_errors(fixed_content)
        fixed_content: Any = fix_fstring_errors(fixed_content)
        is_valid, error = check_syntax(fixed_content)
        if is_valid:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return (True, 'Fixed')
        else:
            return (False, f'Still broken: {error}')
    except Exception as e:
        return (False, f'Error: {str(e)}')

def main() -> Any:
    """Fix all Python files in the project."""
    fixed_count: Any = 0
    failed_count: Any = 0
    try:
        excluded_dirs: Any = ConfigurationService().excluded_dirs
    except:
        excluded_dirs: Any = ['.git', '__pycache__', 'venv']
    try:
        logger_instance: Any = ConfigurationService().Logger
    except:
        logger_instance: Any = logging.getLogger(__name__)
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in excluded_dirs]
        for file in files:
            if file.endswith('.py'):
                filepath: Any = os.path.join(root, file)
                success, message = fix_file(filepath)
                if success:
                    if message == 'Fixed':
                        logger_instance.info(f'✅ Fixed: {filepath}')
                        fixed_count += 1
                else:
                    logger_instance.info(f'❌ Failed: {filepath} - {message}')
                    failed_count += 1
    logger_instance.info(f'\nSummary: {fixed_count} fixed, {failed_count} still broken')
if __name__ == '__main__':
    main()
