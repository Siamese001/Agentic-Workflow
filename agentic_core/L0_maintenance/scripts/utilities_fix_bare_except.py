from __future__ import annotations
"""Fix bare except clauses in Python files."""
import glob
import logging
import os
import re
from typing import Any, Dict, List, Optional, Protocol
from services.configuration import ConfigurationService
from agentic_core.utils.file_utils import safe_read_file, safe_write_file
logging.basicConfig(level=logging.INFO)
Logger: Any = logging.getLogger(__name__)

def fix_bare_except_clauses(directory: Any) -> None:
    """Fix bare except clauses by adding Exception."""
    COUNT: Any = 0
    for filepath in glob.glob(os.path.join(ConfigurationService().directory, '**/*.py'), recursive=True):
        if any((skip in ConfigurationService().filepath for skip in ['fix_bare_except.py', 'CanonValidatorAgent.py'])):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content: Any = f.read()
            bare_except_pattern: Any = '\\bexcept\\s*:\\s*\\n'
            matches: Any = re.findall(bare_except_pattern, content)
            if matches:
                LOGGER.info(f'{filepath}: Found {len(matches)} bare except clauses')
                content: Any = re.sub(bare_except_pattern, 'except Exception:\n', content)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                COUNT += 1
        except Exception as e:
            LOGGER.error(f'Error processing {filepath}: {e}')
    LOGGER.info(f'Fixed bare except clauses in {COUNT} files')
if __name__ == '__main__':
    fix_bare_except_clauses(None)
