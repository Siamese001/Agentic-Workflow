"""
Immutable Staging Buffer.

A write-once data structure that prevents state mutation bugs in multi-hop workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin

    class MCPHardenedMixin(mcp_hardened_mixin):
        pass
except ImportError:

    class MCPHardenedMixin:
        pass


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:

    class HealerMixin:
        pass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class ImmutableStagingBuffer(MCPHardenedMixin, HealerMixin):
    """
    A hardened buffer that enforces write-once semantics per key.
    Once a key is written, it is locked forever.
    """

    _buffer: dict[str, Any] = field(default_factory=dict)
    _locked_keys: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Initialize mixins."""
        super().__init__()

    def write_once(self, key: str, value: Any) -> None:
        """
        Writes a value to the buffer if the key is not locked.

        Args:
            key: The identifier for the data.
            value: The data to store.

        Raises:
            ValueError: If the key has already been written to.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ImmutableStagingBuffer.write_once")

        if key in self._locked_keys:
            raise ValueError(f"Key '{key}' is immutable - already written.")
        self._buffer[key] = value
        self._locked_keys.add(key)

    def read(self, key: str) -> Any | None:
        """
        Reads a value from the buffer.

        Args:
            key: The identifier to read.

        Returns:
            The value if found, else None.
        """
        return self._buffer.get(key)

    def is_locked(self, key: str) -> bool:
        """Checks if a key has been written."""
        return key in self._locked_keys

    def get_snapshot(self) -> dict[str, Any]:
        """Returns a copy of the current buffer state."""
        return self._buffer.copy()
