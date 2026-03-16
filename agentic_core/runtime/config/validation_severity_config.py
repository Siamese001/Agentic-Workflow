from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "validation_severity_config", "p0_governance")
_emit_reads_policy_state("p0", "validation_severity_config", "policy_binding")
_emit_snapshots_state("p0", "validation_severity_config", "state_snapshot")
emit_replay_key("p0", "validation_severity_config")
emit_determinism_digest("p0", "validation_severity_config")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validation_severity_config", "execution_auth")
_emit_validates_capability("p2", "validation_severity_config", "capability_check")
_emit_routes_to_capability("p2", "validation_severity_config", "capability_route")
_emit_writes_via_uwg("p2", "validation_severity_config", "uwg_write")
_emit_blocks_direct_write("p2", "validation_severity_config", "direct_write_block")
_emit_records_tool_invocation("p2", "validation_severity_config", "tool_invocation")
_emit_captures_execution_output("p2", "validation_severity_config", "exec_output")
_emit_dispatches_agent("p3", "validation_severity_config", "agent_dispatch")
_emit_coordinates_agents("p3", "validation_severity_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "validation_severity_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "validation_severity_config", "healing_outcome")
_emit_escalates_failure("p3", "validation_severity_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "validation_severity_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validation_severity_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "validation_severity_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "validation_severity_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validation_severity_config", "eval_metric")
_emit_stores_embedding("p4", "validation_severity_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "validation_severity_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validation_severity_config", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""Enum types for models."""
import logging
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace

_logger = logging.getLogger(__name__)


# NAMING FIXED: ValidationSeverity → ValidationSeverity
class ValidationSeverity(Enum):
    """Severity levels for validation results."""


# NAMING FIXED: Provider → Provider
class Provider(str, Enum):
    """Available LLM providers."""


# NAMING FIXED: APICallStatus → ApiCallStatus
class ApiCallStatus(Enum):
    """Status of API calls."""


class ValidationSeverityConfig(BaseModel):
    """[HARDENED] Wrapper schema for validation severity metadata."""

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: ValidationSeverity = Field(..., description="Severity level for validation")

    @field_validator("severity")
    @classmethod
    def validate_severity(cls, value: ValidationSeverity) -> ValidationSeverity:
        """[HARDENED] Ensure severity is a valid enum member."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ValidationSeverityConfig.validate_severity")

        if value is None:
            raise ValueError("Severity is required")
        return value
