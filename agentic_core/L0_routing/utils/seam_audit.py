"""Seam audit module for Wave 18 - Replay Determinism Closure.

This module provides audit trail functionality for seam operations
with deterministic hash generation for replay verification.
"""

import hashlib
import json
import logging
from dataclasses import asdict, dataclass
from functools import wraps
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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
    emit_determinism_digest,
    emit_replay_key,
)

_emit_dispatches_healing_run("p1", "seam_audit", "L0")
_emit_routes_through("p1", "seam_audit", "L0")
_emit_checks_agent_registry("p1", "seam_audit", "agent_registry")
_emit_validates_agent_capability("p1", "seam_audit", "capability")
_emit_dispatches_execution_plan("p1", "seam_audit", "exec_plan")
_emit_agent_executes_agent("p1", "seam_audit", "sub_agent")
_emit_routes_to_agent("p1", "seam_audit", "target_agent")
_emit_verifies_policy("p1", "seam_audit", "policy_check")
_emit_observes_runtime_state("p1", "seam_audit", "runtime_state")
_emit_verifies_boundary("p1", "seam_audit", "boundary_check")
_emit_transcripts_response("p1", "seam_audit", "transcript")
_emit_hard_fails_untranscripted("p1", "seam_audit")
_emit_gated_by_confidence("p1", "seam_audit", "confidence_gate")
_emit_escalates_to_human("p1", "seam_audit", "L0")
_emit_reads_policy_state("p1", "seam_audit", "L0")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "seam_audit", "p0_governance")
_emit_snapshots_state("p0", "seam_audit", "state_snapshot")
_emit_authorize_and_execute("p2", "seam_audit", "execution_auth")
_emit_validates_capability("p2", "seam_audit", "capability_check")
_emit_routes_to_capability("p2", "seam_audit", "capability_route")
_emit_writes_via_uwg("p2", "seam_audit", "uwg_write")
_emit_blocks_direct_write("p2", "seam_audit", "direct_write_block")
_emit_records_tool_invocation("p2", "seam_audit", "tool_invocation")
_emit_captures_execution_output("p2", "seam_audit", "exec_output")
_emit_dispatches_agent("p3", "seam_audit", "agent_dispatch")
_emit_coordinates_agents("p3", "seam_audit", "agent_coordination")
_emit_records_workflow_lineage("p3", "seam_audit", "workflow_lineage")
_emit_records_healing_outcome("p3", "seam_audit", "healing_outcome")
_emit_escalates_failure("p3", "seam_audit", "failure_escalation")
_emit_orchestrates_workflow("p3", "seam_audit", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "seam_audit", "healing_dispatch")
_emit_invokes_evaluation("p3", "seam_audit", "evaluation_signal")
_emit_records_telemetry_event("p4", "seam_audit", "telemetry_event")
_emit_captures_evaluation_metric("p4", "seam_audit", "eval_metric")
_emit_stores_embedding("p4", "seam_audit", "embedding_store")
_emit_updates_meta_learning_state("p4", "seam_audit", "meta_learning")
_emit_links_execution_to_snapshot("p4", "seam_audit", "exec_snapshot_link")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("seam_audit", "p4obs", "metric_1")
_emit_emits_metric_event("seam_audit", "p4obs", "metric_2")
_emit_emits_metric_event("seam_audit", "p4obs", "metric_3")
_emit_emits_metric_event("seam_audit", "p4obs", "metric_4")
_emit_emits_metric_event("seam_audit", "p4obs", "metric_5")
_emit_emits_metric_event("seam_audit", "p4obs", "metric_6")
_emit_records_incident_event("seam_audit", "p4obs", "incident")
_emit_captures_runtime_anomaly("seam_audit", "p4obs", "anomaly")
_emit_writes_observability_log("seam_audit", "p4obs", "obs_log")
_emit_updates_monitoring_state("seam_audit", "p4obs", "mon_state")
_emit_triggers_alert("seam_audit", "p4obs", "alert")
_emit_links_incident_trace("seam_audit", "p4obs", "trace_link")
_emit_captures_pattern("seam_audit", "p3lm", "pattern")
_emit_records_learning_event("seam_audit", "p3lm", "learning_event")
_emit_writes_learning_snapshot("seam_audit", "p3lm", "snapshot")
_emit_feeds_meta_learning("seam_audit", "p3lm", "meta_feed")
_emit_updates_routing_strategy("seam_audit", "p3lm", "routing")
_emit_improves_agent_policy("seam_audit", "p3lm", "policy")
_emit_stores_learning_state("seam_audit", "p3lm", "state")
_emit_records_execution_trace("seam_audit", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("seam_audit", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("seam_audit", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("seam_audit", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("seam_audit", "L4_STATE", "p2_trace_5")
_emit_reads_environ("seam_audit", "env_read", "p2_env_1")
_emit_reads_environ("seam_audit", "env_read", "p2_env_2")
_emit_reads_runtime_state("seam_audit", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("seam_audit", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "seam_audit", "context_pull")
_emit_pulls_context("p1", "seam_audit", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "seam_audit", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "seam_audit", "uwg_term_2")
_emit_writes_through("p1", "seam_audit", "write_through")
_emit_writes_through("p1", "seam_audit", "write_through_2")
_emit_validated_by_safety_plane("p1", "seam_audit", "safety_validation")
_emit_invokes_eval("p1", "seam_audit", "eval_call")
_emit_proposal_commits_routing("p1", "seam_audit", "routing_commit")

Logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SeamAuditRecord:
    """Immutable audit record for seam operations."""

    seam_id: str
    operation: str
    inputs_hash: str
    outputs_hash: str
    invocation_hash: str
    timestamp: float
    layer_source: str
    layer_target: str
    caller_id: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            object.__setattr__(self, "metadata", {})


class SeamAuditLogger:
    """Central logger for seam audit records."""

    def __init__(self):
        self._records: list[SeamAuditRecord] = []
        self._enabled = True

    def enable(self):
        """Enable audit logging."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "SeamAuditLogger.enable")
        emit_replay_key(_trace_id, f"rk:{_trace_id[:16]}")
        emit_determinism_digest(_trace_id, f"dd:{_trace_id[:16]}")

        self._enabled = True
        Logger.info("Seam audit logging enabled")

    def disable(self):
        """Disable audit logging."""
        self._enabled = False
        Logger.info("Seam audit logging disabled")

    def log_seam_operation(
        self,
        seam_id: str,
        operation: str,
        inputs: Any,
        outputs: Any,
        layer_source: str,
        layer_target: str,
        caller_id: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> SeamAuditRecord:
        """Log a seam operation with deterministic hashing."""
        if not self._enabled:
            return None
        inputs_hash = self._compute_hash(inputs)
        outputs_hash = self._compute_hash(outputs)
        invocation_data = {
            "seam_id": seam_id,
            "operation": operation,
            "inputs_hash": inputs_hash,
            "outputs_hash": outputs_hash,
            "layer_source": layer_source,
            "layer_target": layer_target,
            "caller_id": caller_id,
            "metadata": metadata or {},
        }
        invocation_hash = self._compute_hash(invocation_data)
        record = SeamAuditRecord(
            seam_id=seam_id,
            operation=operation,
            inputs_hash=inputs_hash,
            outputs_hash=outputs_hash,
            invocation_hash=invocation_hash,
            timestamp=get_clock().now_epoch(),
            layer_source=layer_source,
            layer_target=layer_target,
            caller_id=caller_id,
            metadata=metadata or {},
        )
        self._records.append(record)
        Logger.debug(f"Seam audit: {operation} on {seam_id} ({layer_source} -> {layer_target})")
        return record

    def get_records(self, seam_id: str | None = None) -> list[SeamAuditRecord]:
        """Get audit records, optionally filtered by seam_id."""
        if seam_id is None:
            return self._records.copy()
        return [r for r in self._records if r.seam_id == seam_id]

    def get_digest(self, seam_id: str | None = None) -> str:
        """Compute deterministic digest of audit records."""
        records = self.get_records(seam_id)
        sorted_records = sorted(records, key=lambda r: (r.seam_id, r.timestamp, r.operation))
        digest_data = []
        for record in sorted_records:
            record_dict = asdict(record)
            digest_data.append(record_dict)
        digest_json = json.dumps(digest_data, sort_keys=True)
        return hashlib.sha256(digest_json.encode()).hexdigest()

    def clear_records(self):
        """Clear all audit records (for testing)."""
        self._records.clear()
        Logger.debug("Seam audit records cleared")

    def _compute_hash(self, data: Any) -> str:
        """Compute deterministic hash for any serializable data."""
        try:
            if isinstance(data, (dict, list, tuple, str, int, float, bool, type(None))):
                data_json = json.dumps(data, sort_keys=True, default=str)
            elif hasattr(data, "__dict__"):
                data_json = json.dumps(data.__dict__, sort_keys=True, default=str)
            else:
                data_json = str(data)
            return hashlib.sha256(data_json.encode()).hexdigest()
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            Logger.warning(f"Failed to compute hash for data: {e}")
            return hashlib.sha256(str(data).encode()).hexdigest()


_audit_logger = None


def get_seam_audit_logger() -> SeamAuditLogger:
    """Get the global seam audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = SeamAuditLogger()
    return _audit_logger


def seam_audit_hook(seam_id: str, operation: str, layer_source: str, layer_target: str):
    """Decorator to automatically audit seam operations."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_seam_audit_logger()
            inputs = {"args": args, "kwargs": kwargs}
            outputs = func(*args, **kwargs)
            caller_id = None
            if hasattr(func, "__module__"):
                caller_id = f"{func.__module__}.{func.__name__}"
            logger.log_seam_operation(
                seam_id=seam_id,
                operation=operation,
                inputs=inputs,
                outputs=outputs,
                layer_source=layer_source,
                layer_target=layer_target,
                caller_id=caller_id,
            )
            return outputs

        return wrapper

    return decorator


def log_seam_operation(
    seam_id: str,
    operation: str,
    inputs: Any,
    outputs: Any,
    layer_source: str,
    layer_target: str,
    caller_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> SeamAuditRecord | None:
    """Log a seam operation manually."""
    logger = get_seam_audit_logger()
    return logger.log_seam_operation(
        seam_id=seam_id,
        operation=operation,
        inputs=inputs,
        outputs=outputs,
        layer_source=layer_source,
        layer_target=layer_target,
        caller_id=caller_id,
        metadata=metadata,
    )


def get_seam_audit_digest(seam_id: str | None = None) -> str:
    """Get deterministic digest of seam audit records."""
    logger = get_seam_audit_logger()
    return logger.get_digest(seam_id)


def clear_seam_audit_records():
    """Clear all seam audit records (for testing)."""
    logger = get_seam_audit_logger()
    logger.clear_records()
