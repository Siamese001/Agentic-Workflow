# Ownership: apps_rg / L2_execution
# -*- coding: utf-8 -*-
"""Immutable staging buffer for HOP-4."""

from __future__ import annotations

import copy
from datetime import datetime
from typing import Dict, Optional

from shared.exceptions import StagingBufferError


class ImmutableStagingBuffer:
    """HOP-4: Immutable staging buffer. Once locked, cannot be modified."""

    def __init__(self) -> None:
        """Initialize the staging buffer."""
        self._data: Dict[str, object] = {}
        self._locked: bool = False
        self._lock_timestamp: str | None = None

    def set(self, key: str, value: object) -> None:
        """Set value in buffer (only if not locked)."""
        if self._locked:
            raise StagingBufferError(f"Cannot set '{key}': buffer is locked")
        self._data[key] = value

    def get(self, key: str, default: Optional[object] = None) -> Optional[object]:
        """Get value from buffer."""
        return self._data.get(key, default)

    def lock(self) -> None:
        """Lock the buffer (irreversible)."""
        if not self._locked:
            self._locked = True
            self._lock_timestamp = datetime.now().isoformat()

    def is_locked(self) -> bool:
        """Check if buffer is locked."""
        return self._locked

    @property
    def data(self) -> Dict[str, object]:
        """Read-only access to data."""
        return copy.deepcopy(self._data)
