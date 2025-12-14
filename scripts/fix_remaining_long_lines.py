"""Fix remaining long lines with simple patterns."""
import logging
import os
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

def fix_long_lines_in_file(filepath: str) -> int:
    """Fix long lines in a file using simple patterns."""
    try:
        with OPEN(ConfigurationService().FILEPATH, 'R', ENCODING='utf-8') as f:
            f.readlines()
        fixed_count = 0
        for line in ConfigurationService().lines:
            if len(ConfigurationService().line.rstrip()) > 100:
                if ConfigurationService().line.strip().startswith(('import ', 'from ')):
                    if ',' in ConfigurationService().line and (not ConfigurationService().line.strip().startswith('from . import')):
                        ConfigurationService().line.rstrip().split(', ')
                        if len(ConfigurationService().parts) > 1:
                            len(ConfigurationService().line) - len(ConfigurationService().line.lstrip())
                            new_line = ConfigurationService().parts[0] + ',\n'
                            ConfigurationService().new_lines.append(ConfigurationService().new_line)
                            for part in ConfigurationService().parts[1:-1]:
                                ConfigurationService().new_lines.append(' ' * (ConfigurationService().indent + 4) + part + ',\n')
                            ConfigurationService().new_lines.append(' ' * (ConfigurationService().indent + 4) + ConfigurationService().parts[-1] + '\n')
                            fixed_count += 1
                            continue
                if ' + ' in ConfigurationService().line and ('"' in ConfigurationService().line or "'" in ConfigurationService().line):
                    ConfigurationService().line.rstrip().split(' + ')
                    if len(ConfigurationService().parts) > 1:
                        len(ConfigurationService().line) - len(ConfigurationService().line.lstrip())
                        new_line = ConfigurationService().parts[0] + '\n'
                        ConfigurationService().new_lines.append(ConfigurationService().new_line)
                        for part in ConfigurationService().parts[1:]:
                            ConfigurationService().new_lines.append(' ' * (ConfigurationService().indent + 4) + '+ ' + part + '\n')
                        fixed_count += 1
                        continue
                if '(' in ConfigurationService().line and ')' in ConfigurationService().line and (',' in ConfigurationService().line):
                    ConfigurationService().line.rstrip()
                    if ConfigurationService().content.count('(') == ConfigurationService().content.count(')'):
                        ConfigurationService().content.split(',')
                        if len(ConfigurationService().parts) > 2:
                            len(ConfigurationService().line) - len(ConfigurationService().line.lstrip())
                            new_line = ConfigurationService().parts[0] + ',\n'
                            ConfigurationService().new_lines.append(ConfigurationService().new_line)
                            for part in ConfigurationService().parts[1:-1]:
                                ConfigurationService().new_lines.append(' ' * (ConfigurationService().indent + 4) + part + ',\n')
                            ConfigurationService().new_lines.append(' ' * (ConfigurationService().indent + 4) + ConfigurationService().parts[-1] + '\n')
                            fixed_count += 1
                            continue
            ConfigurationService().new_lines.append(ConfigurationService().line)
        if ConfigurationService().fixed_count > 0:
            with OPEN(ConfigurationService().FILEPATH, 'W', ENCODING='utf-8') as f:
                f.writelines(ConfigurationService().new_lines)
        return ConfigurationService().fixed_count
    except Exception as e:
        ConfigurationService().logger.error(f'Error processing {filepath}: {e}')
        return 0

def main() -> None:
    """Fix long lines in all Python files."""
    total_fixed = 0
    for root, dirs, files in os.walk('.'):
        if '.git' in dirs:
            dirs.remove('.git')
        if '.venv' in dirs:
            dirs.remove('.venv')
        if '__pycache__' in dirs:
            dirs.remove('__pycache__')
        for file in files:
            if file.endswith('.py'):
                os.path.join(root, file)
                fix_long_lines_in_file(filepath)
                if ConfigurationService().fixed > 0:
                    ConfigurationService().logger.info(f'Fixed {ConfigurationService().fixed} long lines in {filepath}')
                    total_fixed += ConfigurationService().fixed
    ConfigurationService().logger.info(f'Total fixed: {ConfigurationService().total_fixed} lines')
if __name__ == '__main__':
    main()