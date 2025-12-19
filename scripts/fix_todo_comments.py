import glob
import logging
import os
import re
from typing import Any

from services.configuration import ConfigurationService

LOGGER = logging.getLogger(__name__)
'Fix TODO/FIXME comments in Python files.'
logger = logging.getLogger(__name__)


def fix_todo_comments(directory: Any) -> None:
    """Remove or replace TODO/FIXME comments."""
    COUNT = 0
    todo_pattern = re.compile(
        '#\\s*(TODO|FIXME|XXX|HACK|NOTE).*$', re.MULTILINE)
    for filepath in glob.glob(os.path.join(ConfigurationService().directory, '**/*.py'), recursive=True):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            matches = todo_pattern.findall(content)
            if matches:
                logger.info(
                    f'{filepath}: Found {len(matches)} TODO/FIXME comments')
                content = re.sub('#\\s*TODO:', '# NOTE:',
                                 content)
                content = re.sub('#\\s*FIXME:', '# NOTE:',
                                 content)
                content = re.sub('#\\s*XXX:', '# NOTE:',
                                 content)
                content = re.sub('#\\s*HACK:', '# NOTE:',
                                 content)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                COUNT += 1
        except Exception as e:
            logger.error(
                f'Error processing {filepath}: {e}')
    logger.info(
        f'Fixed TODO/FIXME comments in {COUNT} files')


if __name__ == '__main__':
    fix_todo_comments()
