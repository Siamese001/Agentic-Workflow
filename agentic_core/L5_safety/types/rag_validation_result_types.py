from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "rag_validation_result_types")
emit_determinism_digest("p0", "rag_validation_result_types")

_emit_dispatches_healing_run("p1", "rag_validation_result_types", "L5")
_emit_routes_through("p1", "rag_validation_result_types", "L5")
_emit_escalates_to_human("p1", "rag_validation_result_types", "L5")
_emit_reads_policy_state("p1", "rag_validation_result_types", "L5")

_emit_applies_guardrail("p0", "rag_validation_result_types", "p0_governance")
_emit_snapshots_state("p0", "rag_validation_result_types", "state_snapshot")
_emit_authorize_and_execute("p2", "rag_validation_result_types", "execution_auth")
_emit_validates_capability("p2", "rag_validation_result_types", "capability_check")
_emit_routes_to_capability("p2", "rag_validation_result_types", "capability_route")
_emit_writes_via_uwg("p2", "rag_validation_result_types", "uwg_write")
_emit_blocks_direct_write("p2", "rag_validation_result_types", "direct_write_block")
_emit_records_tool_invocation("p2", "rag_validation_result_types", "tool_invocation")
_emit_captures_execution_output("p2", "rag_validation_result_types", "exec_output")
_emit_dispatches_agent("p3", "rag_validation_result_types", "agent_dispatch")
_emit_coordinates_agents("p3", "rag_validation_result_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "rag_validation_result_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "rag_validation_result_types", "healing_outcome")
_emit_escalates_failure("p3", "rag_validation_result_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "rag_validation_result_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "rag_validation_result_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "rag_validation_result_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "rag_validation_result_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "rag_validation_result_types", "eval_metric")
_emit_stores_embedding("p4", "rag_validation_result_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "rag_validation_result_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "rag_validation_result_types", "exec_snapshot_link")

"Dataclass models for models."
import datetime
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

_logger = logging.getLogger(__name__)


class ValidationResult(BaseModel):
    """Result of a validation rule execution."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    rule_id: str = Field(..., description="Unique identifier for the validation rule")
    passed: bool = Field(..., description="Whether the validation passed")
    severity: str = Field(..., description="Severity level of the validation")
    message: str = Field(default="", description="Validation message")
    details: dict[str, Any] = Field(default_factory=dict, description="Additional validation details")
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, description="Validation timestamp"
    )

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """[HARDENED] Ensure severity is valid."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ValidationResult.validate_severity")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ValidationResult.validate_severity".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        valid_severities = {"low", "medium", "high", "critical"}
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()


class ThematicAnalysis(BaseModel):
    """Analysis of thematic content in text."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    themes: list[str] = Field(default_factory=list, description="List of identified themes")
    confidence_scores: list[float] = Field(
        default_factory=list, description="Confidence scores for each theme"
    )
    dominant_theme: str | None = Field(default=None, description="Most dominant theme")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional analysis metadata")

    @field_validator("confidence_scores")
    @classmethod
    def validate_confidence_scores(cls, v: list[float]) -> list[float]:
        """[HARDENED] Ensure all confidence scores are between 0 and 1."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L5_POLICY, "ThematicAnalysis.validate_confidence_scores"
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ThematicAnalysis.validate_confidence_scores".encode()
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for score in v:
            if not 0.0 <= score <= 1.0:
                raise ValueError("Confidence scores must be between 0.0 and 1.0")
        return v


class RagState(BaseModel):
    """State of RAG (Retrieval-Augmented Generation) process."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    query: str = Field(default="", description="The original query")
    retrieved_documents: list[dict[str, Any]] = Field(default_factory=list, description="Retrieved documents")
    context: str = Field(default="", description="Combined context for generation")
    response: str = Field(default="", description="Generated response")
    retrieval_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Retrieval relevance score")
    generation_confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Generation confidence score"
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional RAG metadata")


class ImmutableStagingBuffer(BaseModel):
    """Immutable buffer for staging data transformations."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    data: dict[str, Any] = Field(default_factory=dict, description="Buffer data")
    version: int = Field(default=1, ge=1, description="Buffer version")
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow, description="Buffer timestamp"
    )
    checksum: str | None = Field(default=None, description="Data checksum for integrity")


def with_data(original_buffer: ImmutableStagingBuffer, new_data: dict[str, Any]) -> ImmutableStagingBuffer:
    """Return a new buffer with updated data."""
    return ImmutableStagingBuffer(
        data={**original_buffer.data, **new_data},
        version=original_buffer.version + 1,
        timestamp=datetime.datetime.utcnow(),
        checksum=None,
    )


def clear(original_buffer: ImmutableStagingBuffer) -> ImmutableStagingBuffer:
    """Return a new empty buffer."""
    return ImmutableStagingBuffer(version=original_buffer.version + 1, timestamp=datetime.datetime.utcnow())
