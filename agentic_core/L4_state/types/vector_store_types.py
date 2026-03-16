from abc import ABC, abstractmethod

from agentic_core.L4_state.types.memory_item_types import MemoryItem, MemoryQuery
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "vector_store_types")
emit_determinism_digest("p0", "vector_store_types")

_emit_dispatches_healing_run("p1", "vector_store_types", "L4")
_emit_routes_through("p1", "vector_store_types", "L4")
_emit_escalates_to_human("p1", "vector_store_types", "L4")
_emit_reads_policy_state("p1", "vector_store_types", "L4")

_emit_snapshots_state("p0", "vector_store_types", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "vector_store_types", "p0_governance")
_emit_records_execution_trace("p0", "evidence", "vector_store_types")


class BaseVectorStore(ABC):
    """
    Interface for vector database interactions.
    All methods must be Async to support high-throughput IO.
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Perform any connection handshakes or schema setups."""
        pass

    @abstractmethod
    async def upsert(self, items: list[MemoryItem]) -> bool:
        """Insert or Update memory items."""
        pass

    @abstractmethod
    async def query(self, query: MemoryQuery) -> list[MemoryItem]:
        """Retrieve nearest neighbors."""
        pass

    @abstractmethod
    async def delete(self, item_ids: list[str]) -> bool:
        """Remove items by ID."""
        pass
