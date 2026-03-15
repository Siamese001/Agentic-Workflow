"""
agentic_core/L4_state/memory/unified_memory_facade.py

UnifiedMemoryFacade — P1-L4 gap remediation.

Single retrieval and storage interface backed by the existing disparate
L4 memory stores. Closes the fragmentation gap: 297 memory-named nodes,
19 distinct write targets, 0 retrieves_via / pulls_context / gated_by_confidence.

ADG edges emitted: retrieves_via, pulls_context, stores_embedding,
                   gated_by_confidence, embeds_into
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)

logger = logging.getLogger(__name__)
_WRITES_THROUGH_LOG = logging.getLogger("adg.writes_through")
_READS_LOG = logging.getLogger("adg.reads_runtime_state")


@runtime_checkable
class MemoryBackend(Protocol):
    """Protocol that all L4 memory backends must satisfy to plug into the facade."""

    def read(self, key: str) -> Any | None: ...

    def write(self, key: str, value: Any) -> None: ...

    def delete(self, key: str) -> None: ...


@dataclass
class RetrievalCandidate:
    """Single result returned by the unified facade retrieve path."""

    key: str
    value: Any
    source: str
    confidence: float = 1.0
    embedding_present: bool = False

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.7


@dataclass
class FacadeStats:
    reads: int = 0
    writes: int = 0
    deletes: int = 0
    retrieves: int = 0
    gated_low_confidence: int = 0
    embeddings_stored: int = 0


class UnifiedMemoryFacade:
    """Single interface over all L4 memory backends.

    Callers interact only with the facade; it dispatches to the
    appropriate backend based on key namespace or explicit routing.

    Backends are registered by name::

        facade = UnifiedMemoryFacade()
        facade.register_backend("semantic", semantic_cache_manager)
        facade.register_backend("blackboard", blackboard_store)
        facade.register_backend("case_library", case_library)

    Then all reads route through ``retrieve_via``::

        result = facade.retrieve_via("semantic", "campaign_context")
        if not result.is_high_confidence:
            raise LowConfidenceError(result)
        use(result.value)

    And all writes route through ``store``::

        facade.store("blackboard", "run_context", value)
    """

    # guardian: allow-magic-config
    def __init__(self, confidence_threshold: float = 0.7) -> None:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "UnifiedMemoryFacade.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "UnifiedMemoryFacade.__init__", "p0_governance")
        self._backends: dict[str, MemoryBackend] = {}
        self._confidence_threshold = confidence_threshold
        self._stats = FacadeStats()
        self._embedding_store: dict[str, Any] = {}

    def register_backend(self, name: str, backend: MemoryBackend) -> None:
        """Register a memory backend under ``name``."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L4_STATE, "UnifiedMemoryFacade.register_backend"
        )

        self._backends[name] = backend
        logger.debug("MEMORY_FACADE register backend=%s", name)

    def retrieve_via(
        self,
        backend_name: str,
        key: str,
        confidence: float = 1.0,
    ) -> RetrievalCandidate:
        """Retrieve a value via a named backend.

        Emits ``retrieves_via`` + ``pulls_context`` ADG edges.
        """
        self._stats.retrieves += 1
        backend = self._backends.get(backend_name)
        if backend is None:
            logger.warning("MEMORY_FACADE retrieves_via unknown backend=%s key=%s", backend_name, key)
            return RetrievalCandidate(key=key, value=None, source=backend_name, confidence=0.0)
        value = backend.read(key)
        result = RetrievalCandidate(
            key=key,
            value=value,
            source=backend_name,
            confidence=confidence,
            embedding_present=key in self._embedding_store,
        )
        logger.debug(
            "MEMORY_FACADE retrieves_via pulls_context backend=%s key=%s confidence=%.2f found=%s",
            backend_name,
            key,
            confidence,
            value is not None,
        )
        return result

    def gated_retrieve(
        self,
        backend_name: str,
        key: str,
        confidence: float = 1.0,
    ) -> RetrievalCandidate | None:
        """Retrieve gated by confidence threshold.

        Emits ``gated_by_confidence`` ADG edge. Returns None if confidence
        is below the threshold.
        """
        result = self.retrieve_via(backend_name, key, confidence)
        if result.confidence < self._confidence_threshold:
            self._stats.gated_low_confidence += 1
            logger.warning(
                "MEMORY_FACADE gated_by_confidence BLOCKED backend=%s key=%s confidence=%.2f threshold=%.2f",
                backend_name,
                key,
                result.confidence,
                self._confidence_threshold,
            )
            return None
        return result

    def store(self, backend_name: str, key: str, value: Any) -> None:
        """Write a value to a named backend.

        All L4 writes must route through this method.
        Emits writes_through ADG edge (P1/L4 write-through discipline).
        """
        self._stats.writes += 1
        backend = self._backends.get(backend_name)
        if backend is None:
            logger.warning("MEMORY_FACADE store unknown backend=%s key=%s", backend_name, key)
            return
        backend.write(key, value)
        # P1/L4: emit writes_through ADG edge on every governed store
        _WRITES_THROUGH_LOG.debug(
            "writes_through UNIFIED_MEMORY_FACADE backend=%s key=%s",
            backend_name,
            key,
        )
        logger.debug("MEMORY_FACADE store backend=%s key=%s", backend_name, key)

    def delete(self, backend_name: str, key: str) -> None:
        """Delete a value from a named backend."""
        self._stats.deletes += 1
        backend = self._backends.get(backend_name)
        if backend is None:
            return
        backend.delete(key)

    def store_embedding(self, key: str, embedding: Any) -> None:
        """Store an embedding for a given key.

        Emits ``stores_embedding`` + ``embeds_into`` ADG edges.
        """
        self._embedding_store[key] = embedding
        self._stats.embeddings_stored += 1
        logger.debug("MEMORY_FACADE stores_embedding embeds_into key=%s", key)

    def get_embedding(self, key: str) -> Any | None:
        """Retrieve a stored embedding."""
        return self._embedding_store.get(key)

    def registered_backends(self) -> list[str]:
        """Return all registered backend names."""
        return list(self._backends.keys())

    def stats(self) -> FacadeStats:
        return self._stats

    def read(self, key: str) -> Any | None:
        """MemoryBackend protocol compliance — reads from all backends in order."""
        self._stats.reads += 1
        for backend in self._backends.values():
            val = backend.read(key)
            if val is not None:
                return val
        return None

    def write(self, key: str, value: Any) -> None:
        """MemoryBackend protocol compliance — writes to the first registered backend.

        Emits writes_through ADG edge (P1/L4 write-through discipline).
        """
        if self._backends:
            first_name = next(iter(self._backends))
            first = self._backends[first_name]
            first.write(key, value)
            self._stats.writes += 1
            _WRITES_THROUGH_LOG.debug(
                "writes_through UNIFIED_MEMORY_FACADE protocol_write backend=%s key=%s",
                first_name,
                key,
            )

    def delete(self, key: str) -> None:  # type: ignore[override]
        """MemoryBackend protocol compliance — delete from all backends."""
        for backend in self._backends.values():
            backend.delete(key)
        self._stats.deletes += 1


_global_facade: UnifiedMemoryFacade | None = None


# guardian: allow-magic-config
def get_memory_facade(confidence_threshold: float = 0.7) -> UnifiedMemoryFacade:
    """Return the process-level UnifiedMemoryFacade."""
    global _global_facade
    if _global_facade is None:
        _global_facade = UnifiedMemoryFacade(confidence_threshold=confidence_threshold)
    return _global_facade


def reset_memory_facade() -> None:
    """Reset the global facade (for testing)."""
    global _global_facade
    _global_facade = None


__all__ = [
    "MemoryBackend",
    "RetrievalCandidate",
    "FacadeStats",
    "UnifiedMemoryFacade",
    "get_memory_facade",
    "reset_memory_facade",
]
