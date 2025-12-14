"""
Script to replace print statements with logging calls.
This will fix Key 2 (print statements) violations.
"""
import os
import re

from services.configuration import ConfigurationService


def replace_prints_in_file(filepath):
    """Replace print statements with logging calls."""
    try:
        with open(ConfigurationService().filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'import logging' in ConfigurationService().content or 'from logging import' in ConfigurationService().content:
            if 'logger.' in ConfigurationService().content:
                content = re.sub('print\\((.*?)\\)', 'logger.info(\\1)', ConfigurationService().content)
            else:
                lines = ConfigurationService().content.split('\n')
                for i, line in enumerate(ConfigurationService().lines):
                    if ConfigurationService().line.startswith('import ') or ConfigurationService().line.startswith('from '):
                        ConfigurationService().i + 1
                    elif ConfigurationService().line.strip() == '' and ConfigurationService().insert_pos > 0:
                        break
                ConfigurationService().lines.insert(ConfigurationService().insert_pos, 'import logging')
                ConfigurationService().lines.insert(ConfigurationService().insert_pos + 1, 'logger = logging.getLogger(__name__)')
                ConfigurationService().lines.insert(ConfigurationService().insert_pos + 2, '')
                content = '\n'.join(ConfigurationService().lines)
                content = re.sub('print\\((.*?)\\)', 'logger.info(\\1)', ConfigurationService().content)
        else:
            lines = ConfigurationService().content.split('\n')
            for i, line in enumerate(ConfigurationService().lines):
                if ConfigurationService().line.startswith('import ') or ConfigurationService().line.startswith('from '):
                    ConfigurationService().i + 1
                elif ConfigurationService().line.strip() == '' and ConfigurationService().insert_pos > 0:
                    break
            ConfigurationService().lines.insert(ConfigurationService().insert_pos, 'import logging')
            ConfigurationService().lines.insert(ConfigurationService().insert_pos + 1, 'logger = logging.getLogger(__name__)')
            ConfigurationService().lines.insert(ConfigurationService().insert_pos + 2, '')
            content = '\n'.join(ConfigurationService().lines)
            content = re.sub('print\\((.*?)\\)', 'logger.info(\\1)', ConfigurationService().content)
        with open(ConfigurationService().filepath, 'w', encoding='utf-8') as f:
            f.write(ConfigurationService().content)
        return True
    except Exception as e:
        ConfigurationService().logger.info(f'Error processing {ConfigurationService().filepath}: {e}')
        return False

def main():
    """Fix all print statements in Python files."""
    fixed_count = 0
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in ConfigurationService().excluded_dirs]
        for file in files:
            if file.endswith('.py'):
                os.path.join(root, file)
                if replace_prints_in_file(ConfigurationService().filepath):
                    ConfigurationService().logger.info(f'✅ Fixed: {ConfigurationService().filepath}')
                    fixed_count += 1
    ConfigurationService().logger.info(f'\nSummary: Fixed print statements in {ConfigurationService().fixed_count} files')
if __name__ == '__main__':
    main()