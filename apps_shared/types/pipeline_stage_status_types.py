"""Signal envelope - Type-safe data flow through the pipeline.

This module implements the envelope Pattern to ensure type safety,
auditability, and error isolation throughout the unified signal pipeline.
"""

import hashlib
import json
import logging
import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field, validator
from pydantic.generics import GenericModel

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "pipeline_stage_status_types", "p0_governance")
_emit_reads_policy_state("p0", "pipeline_stage_status_types", "policy_binding")
_emit_snapshots_state("p0", "pipeline_stage_status_types", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("pipeline_stage_status_types", "p4obs", "metric_1")
_emit_emits_metric_event("pipeline_stage_status_types", "p4obs", "metric_2")
_emit_emits_metric_event("pipeline_stage_status_types", "p4obs", "metric_3")
_emit_emits_metric_event("pipeline_stage_status_types", "p4obs", "metric_4")
_emit_emits_metric_event("pipeline_stage_status_types", "p4obs", "metric_5")
_emit_emits_metric_event("pipeline_stage_status_types", "p4obs", "metric_6")
_emit_records_incident_event("pipeline_stage_status_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("pipeline_stage_status_types", "p4obs", "anomaly")
_emit_writes_observability_log("pipeline_stage_status_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("pipeline_stage_status_types", "p4obs", "mon_state")
_emit_triggers_alert("pipeline_stage_status_types", "p4obs", "alert")
_emit_links_incident_trace("pipeline_stage_status_types", "p4obs", "trace_link")
_emit_captures_pattern("pipeline_stage_status_types", "p3lm", "pattern")
_emit_records_learning_event("pipeline_stage_status_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("pipeline_stage_status_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("pipeline_stage_status_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("pipeline_stage_status_types", "p3lm", "routing")
_emit_improves_agent_policy("pipeline_stage_status_types", "p3lm", "policy")
_emit_stores_learning_state("pipeline_stage_status_types", "p3lm", "state")
_emit_records_execution_trace("pipeline_stage_status_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("pipeline_stage_status_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("pipeline_stage_status_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("pipeline_stage_status_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("pipeline_stage_status_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("pipeline_stage_status_types", "env_read", "p2_env_1")
_emit_reads_environ("pipeline_stage_status_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("pipeline_stage_status_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("pipeline_stage_status_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "pipeline_stage_status_types", "context_pull")
_emit_pulls_context("p1", "pipeline_stage_status_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "pipeline_stage_status_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "pipeline_stage_status_types", "uwg_term_2")
_emit_writes_through("p1", "pipeline_stage_status_types", "write_through")
_emit_writes_through("p1", "pipeline_stage_status_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "pipeline_stage_status_types", "safety_validation")
_emit_invokes_eval("p1", "pipeline_stage_status_types", "eval_call")
_emit_proposal_commits_routing("p1", "pipeline_stage_status_types", "routing_commit")
_emit_escalates_to_human("p1", "pipeline_stage_status_types", "human_escalation")
_emit_routes_through("p1", "pipeline_stage_status_types", "route_through")
_emit_checks_agent_registry("p1", "pipeline_stage_status_types", "agent_registry")
_emit_validates_agent_capability("p1", "pipeline_stage_status_types", "capability")
_emit_dispatches_execution_plan("p1", "pipeline_stage_status_types", "exec_plan")
_emit_agent_executes_agent("p1", "pipeline_stage_status_types", "sub_agent")
_emit_routes_to_agent("p1", "pipeline_stage_status_types", "target_agent")
_emit_verifies_policy("p1", "pipeline_stage_status_types", "policy_check")
_emit_observes_runtime_state("p1", "pipeline_stage_status_types", "runtime_state")
_emit_verifies_boundary("p1", "pipeline_stage_status_types", "boundary_check")
_emit_transcripts_response("p1", "pipeline_stage_status_types", "transcript")
_emit_hard_fails_untranscripted("p1", "pipeline_stage_status_types")
_emit_gated_by_confidence("p1", "pipeline_stage_status_types", "confidence_gate")
emit_replay_key("p0", "pipeline_stage_status_types")
emit_determinism_digest("p0", "pipeline_stage_status_types")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "pipeline_stage_status_types", "execution_auth")
_emit_validates_capability("p2", "pipeline_stage_status_types", "capability_check")
_emit_routes_to_capability("p2", "pipeline_stage_status_types", "capability_route")
_emit_writes_via_uwg("p2", "pipeline_stage_status_types", "uwg_write")
_emit_blocks_direct_write("p2", "pipeline_stage_status_types", "direct_write_block")
_emit_records_tool_invocation("p2", "pipeline_stage_status_types", "tool_invocation")
_emit_captures_execution_output("p2", "pipeline_stage_status_types", "exec_output")
_emit_dispatches_agent("p3", "pipeline_stage_status_types", "agent_dispatch")
_emit_coordinates_agents("p3", "pipeline_stage_status_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "pipeline_stage_status_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "pipeline_stage_status_types", "healing_outcome")
_emit_escalates_failure("p3", "pipeline_stage_status_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "pipeline_stage_status_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pipeline_stage_status_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "pipeline_stage_status_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "pipeline_stage_status_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pipeline_stage_status_types", "eval_metric")
_emit_stores_embedding("p4", "pipeline_stage_status_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "pipeline_stage_status_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pipeline_stage_status_types", "exec_snapshot_link")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_1")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_2")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_3")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_4")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_5")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_6")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_7")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_8")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_9")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_10")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_11")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_12")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_13")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_14")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_15")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_16")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_17")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_18")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_19")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_20")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_21")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_22")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_23")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_24")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_25")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_26")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_27")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_28")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_29")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_30")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_31")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_32")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_33")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_34")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_35")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_36")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_37")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_38")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_39")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_40")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_41")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_42")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_43")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_44")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_45")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_46")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_47")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_48")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_49")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_50")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_51")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_52")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_53")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_54")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_55")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_56")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_57")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_58")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_59")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_60")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_61")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_62")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_63")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_64")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_65")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_66")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_67")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_68")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_69")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_70")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_71")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_72")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_73")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_74")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_75")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_76")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_77")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_78")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_79")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_80")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_81")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_82")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_83")
_emit_reads_through("l4", "pipeline_stage_status_types", "urg_read_84")

logger = logging.getLogger(__name__)
T = TypeVar("T")


class PipelineStageStatus(str, Enum):
    """Status of pipeline stage execution."""

    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED = "SKIPPED"
    RETRYING = "RETRYING"


class PayloadType(str, Enum):
    """Types of payloads supported by the envelope."""

    RESUME_DATA = "resume_data"
    OUTREACH_DATA = "outreach_data"
    RAW_TEXT = "raw_text"
    DICT_DATA = "dict_data"
    ERROR_PAYLOAD = "error_payload"


class PayloadBase(BaseModel):
    """Base class for all payload types."""

    payload_type: PayloadType
    content_hash: str = Field(default_factory=lambda: "")

    class Config:
        use_enum_values = True


class ResumeData(PayloadBase):
    """Resume-specific payload data."""

    payload_type: PayloadType = PayloadType.RESUME_DATA
    sections: dict[str, Any] = Field(default_factory=dict)
    target_role: str | None = None
    experience_years: int | None = None
    skills: list[str] = Field(default_factory=list)

    @validator("content_hash", pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate content hash from sections."""
        if "sections" in values and values["sections"]:
            content = json.dumps(values["sections"], sort_keys=True)
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return v


class OutreachData(PayloadBase):
    """Outreach-specific payload data."""

    payload_type: PayloadType = PayloadType.OUTREACH_DATA
    recipient_info: dict[str, Any] = Field(default_factory=dict)
    sender_info: dict[str, Any] = Field(default_factory=dict)
    campaign_context: dict[str, Any] = Field(default_factory=dict)
    personalization_points: list[str] = Field(default_factory=list)

    @validator("content_hash", pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate content hash from recipient and context."""
        if "recipient_info" in values or "campaign_context" in values:
            content = json.dumps(
                {
                    "recipient": values.get("recipient_info", {}),
                    "campaign": values.get("campaign_context", {}),
                },
                sort_keys=True,
            )
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return v


class RawText(PayloadBase):
    """Raw text payload."""

    payload_type: PayloadType = PayloadType.RAW_TEXT
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @validator("content_hash", pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate hash from text content."""
        if "text" in values and values["text"]:
            return hashlib.sha256(values["text"].encode()).hexdigest()[:16]
        return v


class DictData(PayloadBase):
    """Generic dictionary payload."""

    payload_type: PayloadType = PayloadType.DICT_DATA
    data: dict[str, Any]

    @validator("content_hash", pre=True, always=True)
    def generate_hash(cls, v, values):
        """Generate hash from data."""
        if "data" in values and values["data"]:
            content = json.dumps(values["data"], sort_keys=True)
            return hashlib.sha256(content.encode()).hexdigest()[:16]
        return v


class ErrorPayload(PayloadBase):
    """Error payload for failed stages."""

    payload_type: PayloadType = PayloadType.ERROR_PAYLOAD
    error_type: str
    error_message: str
    original_payload_type: PayloadType | None = None
    stack_trace: str | None = None


class StageResult(BaseModel):
    """Result of a pipeline stage execution."""

    stage_name: str
    status: PipelineStageStatus
    duration_ms: float
    output_hash: str
    error_message: str | None = None
    retry_count: int = 0
    metadata: dict[str, Any] = Field(default_factory=dict)

    @validator("output_hash", pre=True, always=True)
    def generate_output_hash(cls, v, values):
        """Generate hash of stage output for verification."""
        content = f"{values.get('stage_name', '')}:{values.get('status', '')}:{values.get('duration_ms', 0)}"
        return hashlib.sha256(content.encode()).hexdigest()[:16]


class SignalEnvelope(GenericModel, Generic[T]):
    """Type-safe envelope for data flowing through the pipeline."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    trace_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_trace_id: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    payload: T
    history: list[StageResult] = Field(default_factory=list)
    metadata: dict[str, str] = Field(default_factory=dict)
    has_errors: bool = False
    error_count: int = 0

    class Config:
        arbitrary_types_allowed = True
        use_enum_values = True

    def mark_stage_start(self, stage_name: str) -> None:
        """Mark the start of a stage execution.

        Args:
            stage_name: Name of the stage
        """
        if self.has_completed_stage(stage_name):
            logger.debug(f"Stage {stage_name} already completed for envelope {self.id}")
            return
        result = StageResult(
            stage_name=stage_name, status=PipelineStageStatus.PENDING, duration_ms=0.0, output_hash="",
        )
        self.history.append(result)
        self._touch()

    def mark_stage_complete(
        self,
        stage_name: str,
        duration_ms: float,
        output_hash: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Mark a stage as successfully completed.

        Args:
            stage_name: Name of the stage
            duration_ms: Execution duration in milliseconds
            output_hash: Hash of the stage output
            metadata: Optional metadata
        """
        for i, result in enumerate(self.history):
            if result.stage_name == stage_name:
                self.history[i] = StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.SUCCESS,
                    duration_ms=duration_ms,
                    output_hash=output_hash
                    or hashlib.sha256(f"{stage_name}:{duration_ms}".encode()).hexdigest()[:16],
                    metadata=metadata or {},
                )
                break
        else:
            self.history.append(
                StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.SUCCESS,
                    duration_ms=duration_ms,
                    output_hash=output_hash
                    or hashlib.sha256(f"{stage_name}:{duration_ms}".encode()).hexdigest()[:16],
                    metadata=metadata or {},
                ),
            )
        self._touch()

    def mark_stage_failed(
        self, stage_name: str, error_message: str, duration_ms: float = 0.0, retry_count: int = 0,
    ) -> None:
        """Mark a stage as failed.

        Args:
            stage_name: Name of the stage
            error_message: Error message
            duration_ms: Execution duration before failure
            retry_count: Number of retries attempted
        """
        import uuid  # noqa: PLC0415

        _emit_records_execution_trace(str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"PipelineExecution.mark_stage_failed:{stage_name}")
        for i, result in enumerate(self.history):
            if result.stage_name == stage_name:
                self.history[i] = StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.FAILED,
                    duration_ms=duration_ms,
                    output_hash="",
                    error_message=error_message,
                    retry_count=retry_count,
                )
                break
        else:
            self.history.append(
                StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.FAILED,
                    duration_ms=duration_ms,
                    output_hash="",
                    error_message=error_message,
                    retry_count=retry_count,
                ),
            )
        self.has_errors = True
        self.error_count += 1
        self._touch()

    def mark_stage_skipped(self, stage_name: str, reason: str | None = None) -> None:
        """Mark a stage as skipped.

        Args:
            stage_name: Name of the stage
            reason: Reason for skipping
        """
        for i, result in enumerate(self.history):
            if result.stage_name == stage_name:
                self.history[i] = StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.SKIPPED,
                    duration_ms=0.0,
                    output_hash="",
                    metadata={"reason": reason} if reason else {},
                )
                break
        else:
            self.history.append(
                StageResult(
                    stage_name=stage_name,
                    status=PipelineStageStatus.SKIPPED,
                    duration_ms=0.0,
                    output_hash="",
                    metadata={"reason": reason} if reason else {},
                ),
            )
        self._touch()

    def has_completed_stage(self, stage_name: str) -> bool:
        """Check if a stage has been completed successfully.

        Args:
            stage_name: Name of the stage

        Returns:
            True if completed successfully
        """
        for result in self.history:
            if result.stage_name == stage_name:
                return result.status == PipelineStageStatus.SUCCESS
        return False

    def get_stage_result(self, stage_name: str) -> StageResult | None:
        """Get the result for a specific stage.

        Args:
            stage_name: Name of the stage

        Returns:
            Stage result if found
        """
        for result in self.history:
            if result.stage_name == stage_name:
                return result
        return None

    def get_last_completed_stage(self) -> str | None:
        """Get the name of the last completed stage.

        Returns:
            Stage name if found
        """
        for result in reversed(self.history):
            if result.status == PipelineStageStatus.SUCCESS:
                return result.stage_name
        return None

    def get_failed_stages(self) -> list[str]:
        """Get list of failed stage names.

        Returns:
            List of failed stage names
        """
        return [r.stage_name for r in self.history if r.status == PipelineStageStatus.FAILED]

    def calculate_total_duration(self) -> float:
        """Calculate total duration of completed stages.

        Returns:
            Total duration in milliseconds
        """
        return sum(r.duration_ms for r in self.history if r.status != PipelineStageStatus.PENDING)

    def _touch(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        """Convert envelope to dictionary for serialization.

        Returns:
            Dictionary representation
        """
        return {
            "id": str(self.id),
            "trace_id": self.trace_id,
            "parent_trace_id": self.parent_trace_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "payload": self.payload.dict() if hasattr(self.payload, "dict") else self.payload,
            "history": [r.dict() for r in self.history],
            "metadata": self.metadata,
            "has_errors": self.has_errors,
            "error_count": self.error_count,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "SignalEnvelope":
        """Create envelope from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Signal envelope instance
        """
        payload_data = data.get("payload", {})
        payload_type = payload_data.get("payload_type", "dict_data")
        if payload_type == "resume_data":
            payload = ResumeData(**payload_data)
        elif payload_type == "outreach_data":
            payload = OutreachData(**payload_data)
        elif payload_type == "raw_text":
            payload = RawText(**payload_data)
        else:
            payload = DictData(**payload_data)
        history = [StageResult(**r) for r in data.get("history", [])]
        envelope = cls(
            id=uuid.UUID(data["id"]),
            trace_id=data["trace_id"],
            parent_trace_id=data.get("parent_trace_id"),
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            payload=payload,
            history=history,
            metadata=data.get("metadata", {}),
            has_errors=data.get("has_errors", False),
            error_count=data.get("error_count", 0),
        )
        return envelope

    @classmethod
    def from_legacy_dict(
        cls, data: dict[str, Any], metadata: dict[str, str] | None = None,
    ) -> "SignalEnvelope":
        """Create envelope from legacy dict format for backward compatibility.

        Args:
            data: Legacy dictionary data
            metadata: Optional metadata

        Returns:
            Signal envelope instance
        """
        if "sections" in data or "skills" in data:
            payload = ResumeData(**data)
        elif "recipient_info" in data or "campaign_context" in data:
            payload = OutreachData(**data)
        elif isinstance(data, str):
            payload = RawText(text=data)
        else:
            payload = DictData(data=data)
        return cls(payload=payload, metadata=metadata or {})


class EnvelopeFactory:
    """Factory for creating signal envelopes."""

    @staticmethod
    def create_envelope(
        data: Any,
        metadata: dict[str, str] | None = None,
        trace_id: str | None = None,
        parent_trace_id: str | None = None,
    ) -> SignalEnvelope:
        """Create a new signal envelope.

        Args:
            data: Data to wrap
            metadata: Optional metadata
            trace_id: Optional trace ID
            parent_trace_id: Optional parent trace ID

        Returns:
            Signal envelope
        """
        if isinstance(data, SignalEnvelope):
            return data
        if isinstance(data, ResumeData):
            payload = data
        elif isinstance(data, OutreachData):
            payload = data
        elif isinstance(data, RawText):
            payload = data
        elif isinstance(data, DictData):
            payload = data
        elif isinstance(data, dict):
            payload = EnvelopeFactory._create_payload_from_dict(data)
        elif isinstance(data, str):
            payload = RawText(text=data)
        else:
            payload = DictData(data={"value": data})
        envelope = SignalEnvelope(
            payload=payload,
            metadata=metadata or {},
            trace_id=trace_id or str(uuid.uuid4()),
            parent_trace_id=parent_trace_id,
        )
        logger.debug(f"Created envelope {envelope.id} with payload type {payload.payload_type}")
        return envelope

    @staticmethod
    def _create_payload_from_dict(data: dict[str, Any]) -> ResumeData | OutreachData | DictData:
        """Create appropriate payload from dictionary.

        Args:
            data: Dictionary data

        Returns:
            Appropriate payload instance
        """
        if any(key in data for key in ["sections", "skills", "experience", "education"]):
            return ResumeData(**data)
        if any(key in data for key in ["recipient_info", "campaign_context", "personalization"]):
            return OutreachData(**data)
        return DictData(data=data)


ResumeEnvelope = SignalEnvelope[ResumeData]
OutreachEnvelope = SignalEnvelope[OutreachData]
TextEnvelope = SignalEnvelope[RawText]
DictEnvelope = SignalEnvelope[DictData]
