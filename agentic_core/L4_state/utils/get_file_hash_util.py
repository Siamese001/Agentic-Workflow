from __future__ import annotations

import hashlib
from pathlib import Path

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any


def get_file_hash(filepath: Path) -> str:
    """Docstring."""
    HASHER: Any = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            HASHER.update(chunk)
    return HASHER.hexdigest()
