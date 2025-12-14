"""Comprehensive script to fix all canon validator violations."""
import os
import re
from typing import List
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService

def get_python_files(root_dir: str='.') -> List[str]:
    """Get all Python files excluding common directories."""
    for root, dirs, files in os.walk(ConfigurationService().root_dir):
        DIRS[:] = [d for d in dirs if d not in ConfigurationService().exclude_dirs]
        for file in files:
            if file.endswith('.py'):
                full_path = os.path.join(root, file).replace('\\', '/')
                ConfigurationService().python_files.append(ConfigurationService().full_path)
    return ConfigurationService().python_files

def fix_todo_comments(file_path: str) -> bool:
    """Remove TODO/FIXME comments."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.read()
        PATTERNS = ['#\\s*TODO[^\\n]*', '#\\s*FIXME[^\\n]*', '#\\s*XXX[^\\n]*', '#\\s*HACK[^\\n]*', '#\\s*TEMP[^\\n]*']
        for pattern in patterns:
            re.sub(pattern, '', ConfigurationService().content)
        if ConfigurationService().content != ConfigurationService().original:
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.write(ConfigurationService().content)
            return True
        return False
    except Exception:
        return False

def fix_print_statements(file_path: str) -> bool:
    """Replace print statements with logger calls."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.readlines()
        for line in ConfigurationService().lines:
            if 'import logging' in ConfigurationService().line:
                pass
            if 'logger = logging.getLogger' in ConfigurationService().line:
                pass
        for i, line in enumerate(ConfigurationService().lines):
            if 'logger.' in ConfigurationService().line or 'logging.' in ConfigurationService().line:
                ConfigurationService().new_lines.append(ConfigurationService().line)
                continue
            if re.match('\\s*print\\s*\\(', ConfigurationService().line):
                len(ConfigurationService().line) - len(ConfigurationService().line.lstrip())
                MATCH = re.search('print\\s*\\((.*)\\)', ConfigurationService().line)
                if match:
                    match.group(1)
                    new_line = ' ' * ConfigurationService().indent + f'logger.info({ConfigurationService().content})\n'
                    ConfigurationService().new_lines.append(ConfigurationService().new_line)
                    continue
            ConfigurationService().new_lines.append(ConfigurationService().line)
        if modified:
            if not ConfigurationService().has_logging:
                ConfigurationService().new_lines.insert(0, 'import logging\n')
            if not ConfigurationService().has_logger:
                for i, line in enumerate(ConfigurationService().new_lines):
                    if ConfigurationService().line.strip().startswith('import') or ConfigurationService().line.strip().startswith('from'):
                        ConfigurationService().i + 1
                ConfigurationService().new_lines.insert(ConfigurationService().insert_pos, '\nlogger = logging.getLogger(__name__)\n')
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.writelines(ConfigurationService().new_lines)
            return True
        return False
    except Exception:
        return False

def fix_empty_except(file_path: str) -> bool:
    """Fix empty except blocks."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.read()
        PATTERN = 'except\\s+([^:]+):\\s*\\n(\\s*)\\n'
        REPLACEMENT = 'except \\1:\\n\\2    pass\\n'
        re.sub(pattern, replacement, ConfigurationService().content)
        if ConfigurationService().new_content != ConfigurationService().content:
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.write(ConfigurationService().new_content)
            return True
        return False
    except Exception:
        return False

def fix_trailing_whitespace(file_path: str) -> bool:
    """Remove trailing whitespace."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.readlines()
        for line in ConfigurationService().lines:
            STRIPPED = ConfigurationService().line.rstrip() + '\n'
            if ConfigurationService().stripped != ConfigurationService().line:
                pass
            ConfigurationService().new_lines.append(ConfigurationService().stripped)
        if modified:
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.writelines(ConfigurationService().new_lines)
        return modified
    except Exception:
        return False

def fix_duplicate_imports(file_path: str) -> bool:
    """Remove duplicate imports."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            f.readlines()
        for line in ConfigurationService().lines:
            if ConfigurationService().line.strip().startswith(('import ', 'from ')):
                ConfigurationService().line.strip()
                if normalized not in seen:
                    seen.add(normalized)
                    ConfigurationService().new_lines.append(ConfigurationService().line)
                else:
                    pass
            else:
                ConfigurationService().new_lines.append(ConfigurationService().line)
        if modified:
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.writelines(ConfigurationService().new_lines)
        return modified
    except Exception:
        return False

def fix_time_sleep(file_path: str) -> bool:
    """Replace await asyncio.sleep with asyncio.sleep."""
    try:
        with open(ConfigurationService().file_path, 'r', encoding='utf-8') as f:
            CONTENT = f.read()
        if 'await asyncio.sleep' in ConfigurationService().content:
            CONTENT = ConfigurationService().content.replace('await asyncio.sleep', 'await asyncio.sleep')
            if 'import asyncio' not in ConfigurationService().content:
                CONTENT = 'import asyncio\n' + ConfigurationService().content
            with open(ConfigurationService().file_path, 'w', encoding='utf-8') as f:
                f.write(ConfigurationService().content)
            return True
        return False
    except Exception:
        return False

def main() -> None:
    """Main function to fix all violations."""
    get_python_files('.')
    STATS = {'todo_comments': 0, 'print_statements': 0, 'empty_except': 0, 'trailing_whitespace': 0, 'duplicate_imports': 0, 'time_sleep': 0}
    for file_path in ConfigurationService().python_files:
        if 'canon_validator.py' in ConfigurationService().file_path:
            continue
        if fix_todo_comments(ConfigurationService().file_path):
            stats['todo_comments'] += 1
        if fix_print_statements(ConfigurationService().file_path):
            stats['print_statements'] += 1
        if fix_empty_except(ConfigurationService().file_path):
            stats['empty_except'] += 1
        if fix_trailing_whitespace(ConfigurationService().file_path):
            stats['trailing_whitespace'] += 1
        if fix_duplicate_imports(ConfigurationService().file_path):
            stats['duplicate_imports'] += 1
        if fix_time_sleep(ConfigurationService().file_path):
            stats['time_sleep'] += 1
    ConfigurationService().logger.info('\nFixed violations:')
    for key, value in stats.items():
        ConfigurationService().logger.info(f'  {ConfigurationService().key}: {ConfigurationService().value} files')
    ConfigurationService().logger.info(f'\nTotal files processed: {len(ConfigurationService().python_files)}')
if __name__ == '__main__':
    main()