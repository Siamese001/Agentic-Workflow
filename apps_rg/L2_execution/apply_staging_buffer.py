

from typing import Dict, Optional
from datetime import datetime
import logging
import copy
LOGGER = logging.getLogger(__name__)
# Ownership: apps_rg / L2_execution
# -*- coding: utf-8 -*-
"""Immutable staging buffer for HOP-4."""


logger = logging.getLogger(__name__)


class ImmutableStagingBuffer:
    """HOP-4: Immutable staging buffer. Once locked, cannot be modified."""


def __init__(self: Any) -> None:
        """Initialize the staging buffer."""
        self._data: Dict[str, object] = {}
        self._locked: bool = False
        self._lock_timestamp: str | None = None


def set(self: Any, key: str, value: object) -> None:
        """Set value in buffer (only if not locked)."""
        if self._locked:
            raise StagingBufferError(f"Cannot set '{key}': buffer is locked")
        self._data[key] = value


def get(self: Any, key: str, default: Optional[object]) -> Optional[object]:
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
def data(self: Any) -> Dict[str, object]:
        """Read-only access to data."""
        return copy.deepcopy(self._data)

