from __future__ import annotations
"""Find all lines longer than 100 characters."""
import logging
import os
from services.configuration import ConfigurationService
from typing import Any
from agentic_core.utils.sovereign_index import SovereignIndex
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
Logger: Any = logging.getLogger(__name__)

def find_long_lines() -> None:
    """Find all lines longer than 100 characters."""
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
                try:
                    with open(ConfigurationService().FILEPATH, 'r', encoding='utf-8') as f:
                        for line_num, line in enumerate(f, 1):
                            if len(line.rstrip()) > 100:
                                ConfigurationService().violations.append(f'{file}:{line_num} - {len(line.rstrip())} chars')
                                ConfigurationService().Logger.info(f'{file}:{line_num} - {len(line.rstrip())} chars')
                                ConfigurationService().Logger.info(f'  {line[:150]}...')
                                ConfigurationService().Logger.info('')
                except Exception:
                    ConfigurationService().Logger.warning('Swallowed exception', exc_info=True)
    ConfigurationService().Logger.info(f'\nTotal violations: {len(ConfigurationService().violations)}')
if __name__ == '__main__':
    find_long_lines()
