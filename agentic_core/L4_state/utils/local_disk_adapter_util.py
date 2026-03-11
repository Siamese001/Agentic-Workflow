from __future__ import annotations

import logging

from agentic_core.interfaces.write_gateway import get_write_gateway

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
from pathlib import Path
from typing import Any


class LocalDiskAdapter:  # v15-exception: storage-provider-not-behavioral-adapter
    """
    L4 State: The Sovereign File System.
    Strictly controls I/O within the mission-approved data silos.

    V15 Note: This is a storage provider pattern, NOT the behavioral adapter
    pattern prohibited by V15 §8.1. Explicitly excepted per P0.2.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.root = Path(config.get("storage_path", "./data/storage"))
        _get_write_gateway().ensure_dir(self.root)

    async def write_blob(self, key: str, data: bytes, METADATA: dict = None) -> Any:
        """Writes data to the sovereign storage area."""
        safe_path = self.root / key.lstrip("/")
        _get_write_gateway().ensure_dir(safe_path.parent)
        _get_write_gateway().open_write(safe_path, data)
        logging.info(f"DiskAdapter: Persisted {len(data)} bytes to {key}")
