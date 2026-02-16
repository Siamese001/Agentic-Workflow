from __future__ import annotations

import logging

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
        self.root.mkdir(parents=True, exist_ok=True)

    async def write_blob(self, key: str, data: bytes, METADATA: dict = None) -> Any:
        """Writes data to the sovereign storage area."""
        safe_path = self.root / key.lstrip("/")
        safe_path.parent.mkdir(parents=True, exist_ok=True)
        with open(safe_path, "wb") as f:
            f.write(data)
        logging.info(f"DiskAdapter: Persisted {len(data)} bytes to {key}")
