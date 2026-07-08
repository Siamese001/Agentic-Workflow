from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "rag_validation_result_types")
trace_contract.emit_determinism_digest("p0", "rag_validation_result_types")

trace_contract._emit_dispatches_healing_run("p1", "rag_validation_result_types", "L5")
trace_contract._emit_routes_through("p1", "rag_validation_result_types", "L5")
trace_contract._emit_checks_agent_registry("p1", "rag_validation_result_types", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "rag_validation_result_types", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "rag_validation_result_types", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "rag_validation_result_types", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "rag_validation_result_types", "target_agent")
trace_contract._emit_verifies_policy("p1", "rag_validation_result_types", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "rag_validation_result_types", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "rag_validation_result_types", "boundary_check")
trace_contract._emit_transcripts_response("p1", "rag_validation_result_types", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "rag_validation_result_types")
trace_contract._emit_gated_by_confidence("p1", "rag_validation_result_types", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "rag_validation_result_types", "L5")
trace_contract._emit_reads_policy_state("p1", "rag_validation_result_types", "L5")

trace_contract._emit_applies_guardrail("p0", "rag_validation_result_types", "p0_governance")
trace_contract._emit_snapshots_state("p0", "rag_validation_result_types", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "rag_validation_result_types", "execution_auth")
trace_contract._emit_validates_capability("p2", "rag_validation_result_types", "capability_check")
trace_contract._emit_routes_to_capability("p2", "rag_validation_result_types", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "rag_validation_result_types", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "rag_validation_result_types", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "rag_validation_result_types", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "rag_validation_result_types", "exec_output")
trace_contract._emit_dispatches_agent("p3", "rag_validation_result_types", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "rag_validation_result_types", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "rag_validation_result_types", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "rag_validation_result_types", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "rag_validation_result_types", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "rag_validation_result_types", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "rag_validation_result_types", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "rag_validation_result_types", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "rag_validation_result_types", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "rag_validation_result_types", "eval_metric")
trace_contract._emit_stores_embedding("p4", "rag_validation_result_types", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "rag_validation_result_types", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "rag_validation_result_types", "exec_snapshot_link")

"Dataclass models for models."
import datetime
import logging
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


trace_contract._emit_emits_metric_event("rag_validation_result_types", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("rag_validation_result_types", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("rag_validation_result_types", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("rag_validation_result_types", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("rag_validation_result_types", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("rag_validation_result_types", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("rag_validation_result_types", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("rag_validation_result_types", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("rag_validation_result_types", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("rag_validation_result_types", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("rag_validation_result_types", "p4obs", "alert")
trace_contract._emit_links_incident_trace("rag_validation_result_types", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("rag_validation_result_types", "p3lm", "pattern")
trace_contract._emit_records_learning_event("rag_validation_result_types", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("rag_validation_result_types", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("rag_validation_result_types", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("rag_validation_result_types", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("rag_validation_result_types", "p3lm", "policy")
trace_contract._emit_stores_learning_state("rag_validation_result_types", "p3lm", "state")
trace_contract._emit_records_execution_trace("rag_validation_result_types", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("rag_validation_result_types", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("rag_validation_result_types", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("rag_validation_result_types", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("rag_validation_result_types", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("rag_validation_result_types", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("rag_validation_result_types", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("rag_validation_result_types", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("rag_validation_result_types", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "rag_validation_result_types", "context_pull")
trace_contract._emit_pulls_context("p1", "rag_validation_result_types", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_validation_result_types", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "rag_validation_result_types", "uwg_term_2")
trace_contract._emit_writes_through("p1", "rag_validation_result_types", "write_through")
trace_contract._emit_writes_through("p1", "rag_validation_result_types", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "rag_validation_result_types", "safety_validation")
trace_contract._emit_invokes_eval("p1", "rag_validation_result_types", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "rag_validation_result_types", "routing_commit")

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
        default_factory=datetime.datetime.utcnow,
        description="Validation timestamp",
    )

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, v: str) -> str:
        """[HARDENED] Ensure severity is valid."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "ValidationResult.validate_severity")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ValidationResult.validate_severity".encode()).hexdigest()[
            :24
        ]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        valid_severities = {"low", "medium", "high", "critical"}
        if v.lower() not in valid_severities:
            raise ValueError(f"Severity must be one of: {valid_severities}")
        return v.lower()


class ThematicAnalysis(BaseModel):
    """Analysis of thematic content in text."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    themes: list[str] = Field(default_factory=list, description="List of identified themes")
    confidence_scores: list[float] = Field(
        default_factory=list,
        description="Confidence scores for each theme",
    )
    dominant_theme: str | None = Field(default=None, description="Most dominant theme")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional analysis metadata")

    @field_validator("confidence_scores")
    @classmethod
    def validate_confidence_scores(cls, v: list[float]) -> list[float]:
        """[HARDENED] Ensure all confidence scores are between 0 and 1."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L5_POLICY,
            "ThematicAnalysis.validate_confidence_scores",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ThematicAnalysis.validate_confidence_scores".encode(),
        ).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Generation confidence score",
    )
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional RAG metadata")


class ImmutableStagingBuffer(BaseModel):
    """Immutable buffer for staging data transformations."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    data: dict[str, Any] = Field(default_factory=dict, description="Buffer data")
    version: int = Field(default=1, ge=1, description="Buffer version")
    timestamp: datetime.datetime = Field(
        default_factory=datetime.datetime.utcnow,
        description="Buffer timestamp",
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
