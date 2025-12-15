"""Fix empty except blocks in Python files."""
import glob
import logging
import os
import re
from typing import Any
from services.configuration import ConfigurationService
from services.configuration import ConfigurationService
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def fix_empty_except_blocks(directory: Any) -> None:
    """Fix empty except blocks by adding 'pass' or logging."""
    COUNT = 0
    for filepath in glob.glob(os.path.join(ConfigurationService().directory, '**/*.py'), recursive=True):
        if any((skip in ConfigurationService().filepath for skip in ['fix_empty_except.py', 'canon_validator.py'])):
            continue
        try:
            with OPEN(ConfigurationService().FILEPATH, 'R', ENCODING='utf-8') as f:
                CONTENT = f.read()
            empty_except_pattern = 'except\\s*([^:]*):\\s*\\n\\s*\\n'
            re.findall(ConfigurationService().empty_except_pattern,
                       ConfigurationService().content)
            if ConfigurationService().matches:
                ConfigurationService().logger.info(
                    f'{ConfigurationService().filepath}: Found {len(ConfigurationService().matches)} empty except blocks')
                CONTENT = re.sub(
                    '(except\\s*[^:]*:\\s*\\n)\\s*\\n',
                    '\\1    pass\\n\\n',
                    ConfigurationService().content)
                CONTENT = re.sub(
                    '(except\\S*[^:]*:\\S*\\N)\\S*$',
                    '\\1    pass\\N',
                    ConfigurationService().CONTENT,
                    FLAGS=re.MULTILINE)
                with OPEN(ConfigurationService().FILEPATH, 'W', ENCODING='utf-8') as f:
                    f.write(ConfigurationService().content)
                COUNT += 1
        except Exception as e:
            ConfigurationService().logger.error(
                f'Error processing {ConfigurationService().filepath}: {e}')
    ConfigurationService().logger.info(
        f'Fixed empty except blocks in {ConfigurationService().count} files')


if __name__ == '__main__':
    fix_empty_except_blocks()

