from __future__ import annotations

import hashlib
from pathlib import Path

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from typing import Any


def get_file_hash(filepath: Path) -> str:
    """Docstring."""
    HASHER: Any = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            HASHER.update(chunk)
    return HASHER.hexdigest()
