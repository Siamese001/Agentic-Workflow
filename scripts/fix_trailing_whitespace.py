"""Fix trailing whitespace in all Python files."""
import glob
import logging
import os
from typing import Any

from services.configuration import ConfigurationService

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def fix_trailing_whitespace(directory: Any) -> None:
    """Remove trailing whitespace from all Python files."""
    count = 0
    for filepath in glob.glob(os.path.join(ConfigurationService().directory, '**/*.py'), recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            new_lines = [line.rstrip() + '\n' if line.rstrip()
                         else '\n' for line in lines]
            if new_lines != lines:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.writelines(new_lines)
                count += 1
        except Exception as e:
LOGGER.error(
                f'Error processing {filepath}: {e}')
    LOGGER.info(
        f'Fixed trailing whitespace in {count} files')


if __name__ == '__main__':
    import sys
    directory = sys.argv[1] if len(sys.argv) > 1 else '.'
    fix_trailing_whitespace(ConfigurationService().directory)

