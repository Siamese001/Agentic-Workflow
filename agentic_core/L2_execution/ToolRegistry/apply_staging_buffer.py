from __future__ import annotations

import copy

'''Brief description of functionality and purpose.'''

'Brief description of functionality and purpose.'
import logging
from datetime import datetime
from typing import Any

Logger: Any = logging.getLogger(__name__)
'Immutable staging buffer for HOP-4.'

class StagingBufferError(Exception):
    """Custom exception for staging buffer operations."""
    pass

class ImmutableStagingBuffer:
    """HOP-4: Immutable staging buffer. Once locked, cannot be modified."""

    def __init__(self: Any) -> None:
        """Initialize the staging buffer."""
        self._data: dict[str, object] = {}
        self._locked: bool = False
        self._lock_timestamp: str | None = None

    def set(self: Any, key: str, value: object) -> None:
        """Set value in buffer (only if not locked)."""
        if self._locked:
            raise StagingBufferError(f"Cannot set '{key}': buffer is locked")
        self._data[key] = value

    def get(self: Any, key: str, default: object | None) -> object | None:
        """Get value from buffer."""
        return self._data.get(key, default)

    def lock(self: Any) -> None:
        """Lock the buffer (irreversible)."""
        if not self._locked:
            self._locked = True
            self._lock_timestamp = datetime.now().isoformat()

    def is_locked(self: Any) -> bool:
        """Check if buffer is locked."""
        return self._locked

    @property
    def data(self: Any) -> dict[str, object]:
        """Read-only access to data."""
        return copy.deepcopy(self._data)
