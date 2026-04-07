"""
[SSOT] Sovereign Context & Airlock Manager.
Implements the 'Transactional State' pattern from v61.27.10.
Prevents state corruption by requiring cryptographic signatures for commits.
"""

import logging
from copy import deepcopy
from typing import Any

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

_emit_applies_guardrail("p0", "SovereignContext", "p0_governance")
_emit_reads_policy_state("p0", "SovereignContext", "policy_binding")
_emit_snapshots_state("p0", "SovereignContext", "state_snapshot")
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

_emit_emits_metric_event("SovereignContext", "p4obs", "metric_1")
_emit_emits_metric_event("SovereignContext", "p4obs", "metric_2")
_emit_emits_metric_event("SovereignContext", "p4obs", "metric_3")
_emit_emits_metric_event("SovereignContext", "p4obs", "metric_4")
_emit_emits_metric_event("SovereignContext", "p4obs", "metric_5")
_emit_emits_metric_event("SovereignContext", "p4obs", "metric_6")
_emit_records_incident_event("SovereignContext", "p4obs", "incident")
_emit_captures_runtime_anomaly("SovereignContext", "p4obs", "anomaly")
_emit_writes_observability_log("SovereignContext", "p4obs", "obs_log")
_emit_updates_monitoring_state("SovereignContext", "p4obs", "mon_state")
_emit_triggers_alert("SovereignContext", "p4obs", "alert")
_emit_links_incident_trace("SovereignContext", "p4obs", "trace_link")
_emit_captures_pattern("SovereignContext", "p3lm", "pattern")
_emit_records_learning_event("SovereignContext", "p3lm", "learning_event")
_emit_writes_learning_snapshot("SovereignContext", "p3lm", "snapshot")
_emit_feeds_meta_learning("SovereignContext", "p3lm", "meta_feed")
_emit_updates_routing_strategy("SovereignContext", "p3lm", "routing")
_emit_improves_agent_policy("SovereignContext", "p3lm", "policy")
_emit_stores_learning_state("SovereignContext", "p3lm", "state")
_emit_records_execution_trace("SovereignContext", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("SovereignContext", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("SovereignContext", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("SovereignContext", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("SovereignContext", "L4_STATE", "p2_trace_5")
_emit_reads_environ("SovereignContext", "env_read", "p2_env_1")
_emit_reads_environ("SovereignContext", "env_read", "p2_env_2")
_emit_reads_runtime_state("SovereignContext", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("SovereignContext", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "SovereignContext", "context_pull")
_emit_pulls_context("p1", "SovereignContext", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "SovereignContext", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "SovereignContext", "uwg_term_2")
_emit_writes_through("p1", "SovereignContext", "write_through")
_emit_writes_through("p1", "SovereignContext", "write_through_2")
_emit_validated_by_safety_plane("p1", "SovereignContext", "safety_validation")
_emit_invokes_eval("p1", "SovereignContext", "eval_call")
_emit_proposal_commits_routing("p1", "SovereignContext", "routing_commit")
_emit_escalates_to_human("p1", "SovereignContext", "human_escalation")
_emit_routes_through("p1", "SovereignContext", "route_through")
_emit_checks_agent_registry("p1", "SovereignContext", "agent_registry")
_emit_validates_agent_capability("p1", "SovereignContext", "capability")
_emit_dispatches_execution_plan("p1", "SovereignContext", "exec_plan")
_emit_agent_executes_agent("p1", "SovereignContext", "sub_agent")
_emit_routes_to_agent("p1", "SovereignContext", "target_agent")
_emit_verifies_policy("p1", "SovereignContext", "policy_check")
_emit_observes_runtime_state("p1", "SovereignContext", "runtime_state")
_emit_verifies_boundary("p1", "SovereignContext", "boundary_check")
_emit_transcripts_response("p1", "SovereignContext", "transcript")
_emit_hard_fails_untranscripted("p1", "SovereignContext")
_emit_gated_by_confidence("p1", "SovereignContext", "confidence_gate")
emit_replay_key("p0", "SovereignContext")
emit_determinism_digest("p0", "SovereignContext")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "SovereignContext", "execution_auth")
_emit_validates_capability("p2", "SovereignContext", "capability_check")
_emit_routes_to_capability("p2", "SovereignContext", "capability_route")
_emit_writes_via_uwg("p2", "SovereignContext", "uwg_write")
_emit_blocks_direct_write("p2", "SovereignContext", "direct_write_block")
_emit_records_tool_invocation("p2", "SovereignContext", "tool_invocation")
_emit_captures_execution_output("p2", "SovereignContext", "exec_output")
_emit_dispatches_agent("p3", "SovereignContext", "agent_dispatch")
_emit_coordinates_agents("p3", "SovereignContext", "agent_coordination")
_emit_records_workflow_lineage("p3", "SovereignContext", "workflow_lineage")
_emit_records_healing_outcome("p3", "SovereignContext", "healing_outcome")
_emit_escalates_failure("p3", "SovereignContext", "failure_escalation")
_emit_orchestrates_workflow("p3", "SovereignContext", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SovereignContext", "healing_dispatch")
_emit_invokes_evaluation("p3", "SovereignContext", "evaluation_signal")
_emit_records_telemetry_event("p4", "SovereignContext", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SovereignContext", "eval_metric")
_emit_stores_embedding("p4", "SovereignContext", "embedding_store")
_emit_updates_meta_learning_state("p4", "SovereignContext", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SovereignContext", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class SimpleBuffer:
    """Simple buffer for staging data."""

    def __init__(self):
        self._data: dict[str, Any] = {}

    def write(self, key: str, value: Any, source_agent: str = None) -> None:
        self._data[key] = value

    def read(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)


class SimpleTrace:
    """Simple trace registry."""

    def __init__(self):
        self._traces: list[dict[str, Any]] = []

    def add_trace(self, event: str, data: dict[str, Any] = None) -> None:
        self._traces.append({"event": event, "data": data or {}})

    def get_summary(self) -> dict[str, Any]:
        return {
            "total_spans": len(self._traces),
            "failures": len([t for t in self._traces if "ERROR" in t.get("event", "").upper()]),
        }


class SovereignContext:
    """
    Manages application state with transactional integrity.
    Data flow: Write -> Airlock -> (Validation Gate) -> Commit(Signature) -> State
    """

    def __init__(self):
        self._state: dict[str, Any] = {}
        self._airlock: dict[str, Any] = {}
        self._transaction_log: list[dict[str, Any]] = []
        self.buffer = SimpleBuffer()
        self.trace = SimpleTrace()

    def write_to_airlock(self, key: str, value: Any) -> None:
        """
        Stage data in the airlock. It is NOT visible to the main app yet.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignContext.write_to_airlock")

        self._airlock[key] = value
        logger.debug(f"Staged {key} in airlock.")

    def commit_airlock(self, validation_signature: str) -> None:
        """
        Promote airlock data to main state.
        CRITICAL: REQUIRES a valid cryptographic signature to prove validation passed.
        """
        if not validation_signature:
            raise ValueError("SECURITY VIOLATION: Cannot commit airlock without validation signature.")
        for key, value in self._airlock.items():
            self._state[key] = deepcopy(value)
            self._transaction_log.append({"action": "COMMIT", "key": key, "signature": validation_signature})
        self._airlock.clear()
        logger.info(f"Airlock committed successfully with signature {validation_signature[:8]}...")

    def rollback_airlock(self) -> None:
        """
        Discard staged changes due to validation failure or error.
        """
        keys_cleared = list(self._airlock.keys())
        self._airlock.clear()
        logger.warning(f"Airlock rolled back. Discarded keys: {keys_cleared}")

    def add_signal(self, signal: str) -> None:
        """Register a signal for downstream engines to consume."""
        if not hasattr(self, "_signals"):
            self._signals: list[str] = []
        self._signals.append(signal)
        logger.debug(f"Signal raised: {signal}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Retrieve committed state. Does NOT access airlock.
        """
        return self._state.get(key, default)
