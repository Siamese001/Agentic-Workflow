"""L4A/B/C sub-layer separation contracts.

Spec: L4 State Layer sub-layer architecture:
  L4A — Read-only retrieval (ephemeral, in-memory, no persistence).
  L4B — Short-term reasoning memory (mutable, session-scoped, not persisted).
  L4C — Persistent ledger (write-through, must go via UWG).

Each sub-layer exposes a protocol/base class that enforces its access contract.
Mixing sub-layer responsibilities raises SubLayerViolation at construction time.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SubLayerViolation(RuntimeError):
    """Raised when a sub-layer contract is violated at construction or call time."""


class L4SubLayer(str, Enum):
    """Canonical L4 sub-layer identifiers."""

    L4A = "L4A"  # Read-only retrieval — no writes, no persistence
    L4B = "L4B"  # Short-term reasoning memory — mutable, session-scoped
    L4C = "L4C"  # Persistent ledger — UWG-guarded writes only


# =============================================================================
# L4A — Read-Only Retrieval Contract
# =============================================================================


class L4AReadOnlyStore(ABC):
    """Base for all L4A stores.  MUST NOT mutate state or persist anything.

    Spec: L4A — ephemeral, read-only query layer.
    """

    sublayer: L4SubLayer = L4SubLayer.L4A

    def _assert_no_write(self, operation: str) -> None:
        raise SubLayerViolation(
            f"L4A store attempted write operation '{operation}'. "
            f"L4A is read-only — route mutations through L4B (session) or L4C (persistent)."
        )

    @abstractmethod
    def query(self, key: str, **kwargs: Any) -> Any:
        """Retrieve a value by key.  Must not mutate any state."""
        ...


# =============================================================================
# L4B — Short-Term Reasoning Memory Contract
# =============================================================================


@dataclass
class L4BEntry:
    """A single session-scoped reasoning memory entry."""

    key: str
    value: Any
    session_id: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.key or not self.key.strip():
            raise SubLayerViolation("L4BEntry.key must be non-empty")
        if not self.session_id or not self.session_id.strip():
            raise SubLayerViolation("L4BEntry.session_id must be non-empty")


class L4BSessionMemory(ABC):
    """Base for all L4B session memory stores.

    Spec: L4B — mutable, session-scoped, NOT persisted to disk.
    Persistence must be explicitly delegated to L4C.
    """

    sublayer: L4SubLayer = L4SubLayer.L4B

    def _assert_not_persistent_write(self, operation: str) -> None:
        raise SubLayerViolation(
            f"L4B store attempted persistent write '{operation}'. "
            f"L4B is session-scoped only — route persistence through L4C (ledger)."
        )

    @abstractmethod
    def put(self, entry: L4BEntry) -> None:
        """Store an entry in session memory (not persisted)."""
        ...

    @abstractmethod
    def get(self, key: str, session_id: str) -> Any:
        """Retrieve an entry from session memory."""
        ...

    @abstractmethod
    def clear_session(self, session_id: str) -> None:
        """Remove all entries for a session (cleanup at session end)."""
        ...


# =============================================================================
# L4C — Persistent Ledger Contract
# =============================================================================


@dataclass(frozen=True)
class L4CLedgerEntry:
    """An immutable ledger entry for L4C persistent writes.

    Spec: L4C — every entry must carry a correlation_id for audit.
    """

    correlation_id: str
    key: str
    value: Any
    operation: str  # "write" | "append" | "delete"

    def __post_init__(self) -> None:
        if not self.correlation_id or not self.correlation_id.strip():
            raise SubLayerViolation("L4CLedgerEntry.correlation_id must be non-empty")
        if not self.key or not self.key.strip():
            raise SubLayerViolation("L4CLedgerEntry.key must be non-empty")
        if self.operation not in ("write", "append", "delete"):
            raise SubLayerViolation(
                f"L4CLedgerEntry.operation must be 'write', 'append', or 'delete', "
                f"got '{self.operation}'."
            )


class L4CPersistentLedger(ABC):
    """Base for all L4C persistent ledger stores.

    Spec: L4C — all writes MUST go through UWG; no direct filesystem access.
    """

    sublayer: L4SubLayer = L4SubLayer.L4C

    @abstractmethod
    def commit(self, entry: L4CLedgerEntry) -> None:
        """Persist an entry via the UWG write gate."""
        ...

    @abstractmethod
    def read(self, key: str) -> Any:
        """Read a persisted entry (read-only path, bypasses UWG)."""
        ...


# =============================================================================
# Sub-layer boundary enforcement: prevent cross-layer method calls
# =============================================================================


def assert_sublayer(obj: Any, expected: L4SubLayer) -> None:
    """Assert an L4 object belongs to the expected sub-layer.

    Raises SubLayerViolation if the declared sublayer doesn't match.
    """
    actual = getattr(obj, "sublayer", None)
    if actual != expected:
        raise SubLayerViolation(
            f"Sub-layer mismatch: expected {expected.value}, "
            f"got {actual.value if actual else 'None'}. "
            f"Do not mix L4A/L4B/L4C responsibilities in a single object."
        )


__all__ = [
    "L4SubLayer",
    "SubLayerViolation",
    "L4AReadOnlyStore",
    "L4BEntry",
    "L4BSessionMemory",
    "L4CLedgerEntry",
    "L4CPersistentLedger",
    "assert_sublayer",
]
