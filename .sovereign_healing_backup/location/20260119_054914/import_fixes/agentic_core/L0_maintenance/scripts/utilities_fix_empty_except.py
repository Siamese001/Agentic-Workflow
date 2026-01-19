from __future__ import annotations
"""Fix empty except blocks in Python files."""
import glob
import logging
import os
import re
from typing import Any, Dict, List, Optional, Protocol
from services.configuration import ConfigurationService
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)

def fix_empty_except_blocks(directory: Any) -> None:
    """Fix empty except blocks by adding 'pass' or logging."""
    COUNT: Any = 0
    for filepath in glob.glob(os.path.join(ConfigurationService().directory, '**/*.py'), recursive=True):
        if any((skip in filepath for skip in ['fix_empty_except.py', 'CanonValidatorAgent.py'])):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                CONTENT: Any = f.read()
            empty_except_pattern: Any = 'except\\s*([^:]*):\\s*\\n\\s*\\n'
            matches: Any = re.findall(empty_except_pattern, CONTENT)
            if matches:
                LOGGER.info(f'{filepath}: Found {len(matches)} empty except blocks')
                CONTENT: Any = re.sub('(except\\s*[^:]*:\\s*\\n)\\s*\\n', '\\1    pass\\n\\n', CONTENT)
                CONTENT: Any = re.sub('(except\\S*[^:]*:\\S*\\n)\\s*$', '\\1    pass\\n', CONTENT, flags=re.MULTILINE)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(CONTENT)
                COUNT += 1
        except Exception as e:
            LOGGER.error(f'Error processing {filepath}: {e}')
    LOGGER.info(f'Fixed empty except blocks in {COUNT} files')
if __name__ == '__main__':
    fix_empty_except_blocks()
