from __future__ import annotations
import os
'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import sys
from typing import Any, List, Dict, Optional
from archives.location_violations.file_utils import safe_read_file, safe_write_file

def get_file_hash(filepath: Path) -> str:
    """Docstring."""
    HASHER: Any = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            HASHER.update(chunk)
    return HASHER.hexdigest()
