from __future__ import annotations

import logging

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import os
from typing import Any


class LocalDiskAdapter:
    """
    L4 State: The Sovereign File System.
    Strictly controls I/O within the mission-approved data silos.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.root = config.get('storage_path', './data/storage')
        if not os.path.exists(self.root):
            os.makedirs(self.root)

    async def write_blob(self, key: str, data: bytes, METADATA: dict=None) -> Any:
        """Writes data to the sovereign storage area."""
        safe_path: Any = os.path.join(self.root, key.lstrip('/'))
        os.makedirs(os.path.dirname(safe_path), exist_ok=True)
        with open(safe_path, 'wb') as f:
            f.write(data)
        logging.info(f'DiskAdapter: Persisted {len(data)} bytes to {key}')
