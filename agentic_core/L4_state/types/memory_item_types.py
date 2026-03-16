from typing import Any

from pydantic import BaseModel, Field, field_validator

from agentic_core.config.core.base_entity_config import BaseEntity
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "memory_item_types")
emit_determinism_digest("p0", "memory_item_types")

_emit_dispatches_healing_run("p1", "memory_item_types", "L4")
_emit_routes_through("p1", "memory_item_types", "L4")
_emit_escalates_to_human("p1", "memory_item_types", "L4")
_emit_reads_policy_state("p1", "memory_item_types", "L4")


class MemoryItem(BaseEntity):
    """
    Represents a single unit of semantic memory (e.g., a conversation turn, a fact).
    """

    content: str = Field(..., min_length=1, description="Text content of the memory")
    embedding: list[float] = Field(..., description="Vector representation")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Filterable tags")
    score: float | None = Field(default=None, description="Similarity score (only on retrieval)")

    @field_validator("embedding")
    @classmethod
    def check_vector_integrity(cls, v: list[float]) -> list[float]:
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "MemoryItem.check_vector_integrity", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "MemoryItem.check_vector_integrity", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "MemoryItem.check_vector_integrity")

        if not v:
            raise ValueError("Embedding vector cannot be empty")
        return v


class MemoryQuery(BaseModel):
    """
    Request object for semantic search.
    """

    vector: list[float] = Field(..., description="Query embedding")
    top_k: int = Field(default=5, ge=1, le=100)
    filter_metadata: dict[str, Any] | None = Field(default=None, description="Exact match filters")
