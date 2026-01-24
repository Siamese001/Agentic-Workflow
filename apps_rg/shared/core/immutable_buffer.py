"""
Immutable Staging Buffer for RG Sovereign Architecture.

A write-once data structure that prevents state mutation bugs in multi-hop workflows.
Aligned with LIC ImmutableStagingBuffer pattern.

HARDENING: Implements deepcopy on boundaries to prevent reference leakage.
Adds StateTransaction for audit trails.
"""

from __future__ import annotations

import copy
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, TypeVar

from agentic_core.L2_execution.mcp.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

Logger = logging.getLogger(__name__)
T = TypeVar("T")


@dataclass(frozen=True)
class StateTransaction:
    """Immutable record of a state change."""

    key: str
    timestamp: float
    source_agent: str
    value_hash: int
    cycle_id: str


@dataclass
class ImmutableStagingBuffer(MCPHardenedMixin, HealerMixin):
    """
    Sovereign State Container.
    Enforces Write-Once-Read-Many (WORM) with Deep Copy isolation.

    RG-Specific Keys:
    - mission_input: Initial job description and resume data
    - hop0_validation: JD validation results
    - hop1_extraction: Clerk extraction output
    - hop2_enrichment: Enrichment output
    - hop3_generation: Generated resume sections
    - hop4_validation: Quality validation results
    - hop5_gate_decision: Pass/fail gate decision
    - hop6_refinement: Refined content
    - hop7_qa_report: Final QA report
    """

    _buffer: dict[str, Any] = field(default_factory=dict)
    _locked_keys: set[str] = field(default_factory=set)
    _history: list[StateTransaction] = field(default_factory=list)
    _cycle_id: str = "INIT"

    def __post_init__(self) -> None:
        """Initialize mixins."""
        # Initialize MCP and Healer mixins
        MCPHardenedMixin.__init__(self)
        HealerMixin.__init__(self)

    def _mcp_audit(self, action: str, details: dict = None) -> None:
        """Safe MCP audit call - falls back to no-op if mixin not fully initialized."""
        if hasattr(super(), "_mcp_audit"):
            super()._mcp_audit(action, details or {})
        # Silent no-op if mixin not available

    def write(self, key: str, value: Any, source_agent: str = "SYSTEM") -> None:
        """
        Commit data to the buffer.
        CRITICAL: Stores a deep copy to prevent external mutation.

        Args:
            key: The identifier for the data.
            value: The data to store.
            source_agent: The agent performing the write.

        Raises:
            PermissionError: If the key has already been written to.
        """
        if key in self._locked_keys:
            self._mcp_audit("write_violation", {"key": key, "agent": source_agent})
            raise PermissionError(f"Key '{key}' is LOCKED. Immutable violation by {source_agent}.")

        # Deep Copy Hardening: Prevent reference storage
        try:
            snapshot = copy.deepcopy(value)
        except TypeError:
            # Fallback for non-pickleable objects (e.g., connections), store as-is but warn
            Logger.warning(
                f"[{source_agent}] Object for '{key}' is not deep-copyable. Storing reference."
            )
            snapshot = value

        self._buffer[key] = snapshot
        self._locked_keys.add(key)

        # Transaction Log
        self._history.append(
            StateTransaction(
                key=key,
                timestamp=datetime.utcnow().timestamp(),
                source_agent=source_agent,
                value_hash=hash(str(snapshot))
                if isinstance(snapshot, (str, int, float, tuple, frozenset))
                else hash(str(snapshot))
                if isinstance(snapshot, dict)
                else 0,
                cycle_id=self._cycle_id,
            )
        )

        self._mcp_audit("buffer_write", {"key": key, "agent": source_agent})

    def write_once(self, key: str, value: Any) -> None:
        """
        Legacy API: Writes a value to the buffer if the key is not locked.
        Delegates to write() with default source_agent.
        """
        self.write(key, value, source_agent="LEGACY")

    def read(self, key: str, default: Any = None) -> Any:
        """
        Retrieve data from the buffer.
        CRITICAL: Returns a deep copy to prevent downstream mutation of state.

        Args:
            key: The identifier to read.
            default: Default value if key not found.

        Returns:
            A deep copy of the value if found, else default.
        """
        if key not in self._buffer:
            return default

        data = self._buffer[key]
        try:
            return copy.deepcopy(data)
        except TypeError:
            return data

    def set_cycle(self, cycle_id: str) -> None:
        """Set the current cycle ID for transaction tracking."""
        self._cycle_id = cycle_id

    def get_history(self) -> list[StateTransaction]:
        """Returns a copy of the transaction history."""
        return list(self._history)

    def is_locked(self, key: str) -> bool:
        """Checks if a key has been written."""
        return key in self._locked_keys

    def get_snapshot(self) -> dict[str, Any]:
        """Returns a deep copy of the current buffer state."""
        return copy.deepcopy(self._buffer)

    def get_locked_keys(self) -> set[str]:
        """Returns a copy of the locked keys set."""
        return self._locked_keys.copy()

    def has_key(self, key: str) -> bool:
        """Check if a key exists in the buffer (locked or not)."""
        return key in self._buffer
