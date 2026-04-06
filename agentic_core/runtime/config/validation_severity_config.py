from __future__ import annotations

import logging
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from agentic_core.L5_safety.config.severity import (
    SeverityLevel as ValidationSeverity,
)
from agentic_core.L5_safety.config.severity import (
    from_legacy_string,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
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

_emit_emits_metric_event("validation_severity_config", "p4obs", "metric_1")
_emit_emits_metric_event("validation_severity_config", "p4obs", "metric_2")
_emit_emits_metric_event("validation_severity_config", "p4obs", "metric_3")
_emit_emits_metric_event("validation_severity_config", "p4obs", "metric_4")
_emit_emits_metric_event("validation_severity_config", "p4obs", "metric_5")
_emit_emits_metric_event("validation_severity_config", "p4obs", "metric_6")
_emit_records_incident_event("validation_severity_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("validation_severity_config", "p4obs", "anomaly")
_emit_writes_observability_log("validation_severity_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("validation_severity_config", "p4obs", "mon_state")
_emit_triggers_alert("validation_severity_config", "p4obs", "alert")
_emit_links_incident_trace("validation_severity_config", "p4obs", "trace_link")
_emit_captures_pattern("validation_severity_config", "p3lm", "pattern")
_emit_records_learning_event("validation_severity_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("validation_severity_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("validation_severity_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("validation_severity_config", "p3lm", "routing")
_emit_improves_agent_policy("validation_severity_config", "p3lm", "policy")
_emit_stores_learning_state("validation_severity_config", "p3lm", "state")
_emit_records_execution_trace("validation_severity_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("validation_severity_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("validation_severity_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("validation_severity_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("validation_severity_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("validation_severity_config", "env_read", "p2_env_1")
_emit_reads_environ("validation_severity_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("validation_severity_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("validation_severity_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "validation_severity_config", "context_pull")
_emit_pulls_context("p1", "validation_severity_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "validation_severity_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "validation_severity_config", "uwg_term_2")
_emit_writes_through("p1", "validation_severity_config", "write_through")
_emit_writes_through("p1", "validation_severity_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "validation_severity_config", "safety_validation")
_emit_invokes_eval("p1", "validation_severity_config", "eval_call")
_emit_proposal_commits_routing("p1", "validation_severity_config", "routing_commit")
_emit_escalates_to_human("p1", "validation_severity_config", "human_escalation")
_emit_routes_through("p1", "validation_severity_config", "route_through")
_emit_checks_agent_registry("p1", "validation_severity_config", "agent_registry")
_emit_validates_agent_capability("p1", "validation_severity_config", "capability")
_emit_dispatches_execution_plan("p1", "validation_severity_config", "exec_plan")
_emit_agent_executes_agent("p1", "validation_severity_config", "sub_agent")
_emit_routes_to_agent("p1", "validation_severity_config", "target_agent")
_emit_verifies_policy("p1", "validation_severity_config", "policy_check")
_emit_observes_runtime_state("p1", "validation_severity_config", "runtime_state")
_emit_verifies_boundary("p1", "validation_severity_config", "boundary_check")
_emit_transcripts_response("p1", "validation_severity_config", "transcript")
_emit_hard_fails_untranscripted("p1", "validation_severity_config")
_emit_gated_by_confidence("p1", "validation_severity_config", "confidence_gate")

_logger = logging.getLogger(__name__)


# NAMING FIXED: Provider → Provider
class Provider(str, Enum):
    """Available LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    QWEN = "qwen"
    GEMINI = "gemini"


# NAMING FIXED: APICallStatus → ApiCallStatus
class ApiCallStatus(Enum):
    """Status of API calls."""

    PENDING = "pending"
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"


class ValidationSeverityConfig(BaseModel):
    """[HARDENED] Wrapper schema for validation severity metadata.

    SEVERITY SSOT: Uses agentic_core.L5_safety.config.severity.SeverityLevel
    Legacy values (WARNING, ERROR) are mapped via from_legacy_string():
    - WARNING → MEDIUM
    - ERROR → HIGH
    """

    # [HARDENED] Enforcing SSOT immutability with frozen=True and extra="forbid"
    model_config = ConfigDict(frozen=True, extra="forbid")

    severity: ValidationSeverity = Field(..., description="Severity level for validation")

    @field_validator("severity", mode="before")
    @classmethod
    def validate_severity(cls, value) -> ValidationSeverity:
        """[HARDENED] Ensure severity is a valid enum member. Converts legacy strings."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "ValidationSeverityConfig.validate_severity",
        )

        if value is None:
            raise ValueError("Severity is required")

        # Convert legacy string values to SSOT enum
        if isinstance(value, str):
            return from_legacy_string(value)

        # Already an enum, validate it's the right type
        if isinstance(value, ValidationSeverity):
            return value

        raise ValueError(f"Invalid severity: {value}")
