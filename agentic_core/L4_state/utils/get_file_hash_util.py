from __future__ import annotations
import hashlib
from pathlib import Path
'Brief description of functionality and purpose.'
'Brief description of functionality and purpose.'
from typing import Any
from agentic_core.L0_routing.config.path_constants import BATCH_SIZE, BUFFER_SIZE, DEFAULT_SLEEP, DEFAULT_TIMEOUT, MAX_DEPTH, MAX_FILES, MAX_RETRIES, THRESHOLD

def get_file_hash(filepath: Path) -> str:
    """Docstring."""
    HASHER: Any = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            HASHER.update(chunk)
    return HASHER.hexdigest()
