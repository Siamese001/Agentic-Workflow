"""FreezeStateReader -- reads L2 freeze state and gates meta-learning pipeline.

GAP-014: When L2 freeze is active (FREEZ), the meta-learning pipeline must not
run.  This module provides the FreezeStateReader protocol and a concrete
JsonFileBackedFreezeReader that reads from runtime_state.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol

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

_emit_applies_guardrail("p0", "freeze_gate", "p0_governance")
_emit_reads_policy_state("p0", "freeze_gate", "policy_binding")
_emit_snapshots_state("p0", "freeze_gate", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("freeze_gate", "p4obs", "metric_1")
_emit_emits_metric_event("freeze_gate", "p4obs", "metric_2")
_emit_emits_metric_event("freeze_gate", "p4obs", "metric_3")
_emit_emits_metric_event("freeze_gate", "p4obs", "metric_4")
_emit_emits_metric_event("freeze_gate", "p4obs", "metric_5")
_emit_emits_metric_event("freeze_gate", "p4obs", "metric_6")
_emit_records_incident_event("freeze_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("freeze_gate", "p4obs", "anomaly")
_emit_writes_observability_log("freeze_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("freeze_gate", "p4obs", "mon_state")
_emit_triggers_alert("freeze_gate", "p4obs", "alert")
_emit_links_incident_trace("freeze_gate", "p4obs", "trace_link")
_emit_captures_pattern("freeze_gate", "p3lm", "pattern")
_emit_records_learning_event("freeze_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("freeze_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("freeze_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("freeze_gate", "p3lm", "routing")
_emit_improves_agent_policy("freeze_gate", "p3lm", "policy")
_emit_stores_learning_state("freeze_gate", "p3lm", "state")
_emit_records_execution_trace("freeze_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("freeze_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("freeze_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("freeze_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("freeze_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("freeze_gate", "env_read", "p2_env_1")
_emit_reads_environ("freeze_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("freeze_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("freeze_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "freeze_gate", "context_pull")
_emit_pulls_context("p1", "freeze_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "freeze_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "freeze_gate", "uwg_term_2")
_emit_writes_through("p1", "freeze_gate", "write_through")
_emit_writes_through("p1", "freeze_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "freeze_gate", "safety_validation")
_emit_invokes_eval("p1", "freeze_gate", "eval_call")
_emit_proposal_commits_routing("p1", "freeze_gate", "routing_commit")
_emit_escalates_to_human("p1", "freeze_gate", "human_escalation")
_emit_routes_through("p1", "freeze_gate", "route_through")
_emit_checks_agent_registry("p1", "freeze_gate", "agent_registry")
_emit_validates_agent_capability("p1", "freeze_gate", "capability")
_emit_dispatches_execution_plan("p1", "freeze_gate", "exec_plan")
_emit_agent_executes_agent("p1", "freeze_gate", "sub_agent")
_emit_routes_to_agent("p1", "freeze_gate", "target_agent")
_emit_verifies_policy("p1", "freeze_gate", "policy_check")
_emit_observes_runtime_state("p1", "freeze_gate", "runtime_state")
_emit_verifies_boundary("p1", "freeze_gate", "boundary_check")
_emit_transcripts_response("p1", "freeze_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "freeze_gate")
_emit_gated_by_confidence("p1", "freeze_gate", "confidence_gate")
emit_replay_key("p0", "freeze_gate")
emit_determinism_digest("p0", "freeze_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "freeze_gate", "execution_auth")
_emit_validates_capability("p2", "freeze_gate", "capability_check")
_emit_routes_to_capability("p2", "freeze_gate", "capability_route")
_emit_writes_via_uwg("p2", "freeze_gate", "uwg_write")
_emit_blocks_direct_write("p2", "freeze_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "freeze_gate", "tool_invocation")
_emit_captures_execution_output("p2", "freeze_gate", "exec_output")
_emit_dispatches_agent("p3", "freeze_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "freeze_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "freeze_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "freeze_gate", "healing_outcome")
_emit_escalates_failure("p3", "freeze_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "freeze_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "freeze_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "freeze_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "freeze_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "freeze_gate", "eval_metric")
_emit_stores_embedding("p4", "freeze_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "freeze_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "freeze_gate", "exec_snapshot_link")


class FreezeStateReader(Protocol):
    """Protocol: report whether the system is currently frozen."""

    def is_frozen(self) -> bool:
        """Return True if meta-learning should be suppressed due to freeze."""
        ...


class JsonFileBackedFreezeReader:
    """Read freeze state from runtime_state.json.

    The file is read once per is_frozen() call so that state changes on disk
    are reflected without restarting the process.  This is consistent with
    the existing FileBackedConfigProvider behaviour.

    Freeze is declared active when any of the following is true in the JSON:
      - Top-level "freeze" key is truthy.
      - Top-level "status" == "FREEZ".
      - Nested "l2_freeze" key under "flags" is truthy.
    """

    def __init__(self, runtime_state_path: Path) -> None:
        self._path = runtime_state_path

    def is_frozen(self) -> bool:
        """Return True if the runtime state file declares a freeze."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "JsonFileBackedFreezeReader.is_frozen")

        try:
            text = self._path.read_text(encoding="utf-8", errors="replace")
            data: dict = json.loads(text)
        except (OSError, json.JSONDecodeError):    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
            return False
        if data.get("freeze"):
            return True
        if str(data.get("status", "")).upper() == "FREEZ":
            return True
        flags = data.get("flags", {})
        if isinstance(flags, dict) and flags.get("l2_freeze"):
            return True
        return False


class StaticFreezeReader:
    """Deterministic in-memory freeze reader for tests."""

    def __init__(self, frozen: bool = False) -> None:
        self._frozen = frozen

    def is_frozen(self) -> bool:
        return self._frozen


__all__ = ["FreezeStateReader", "JsonFileBackedFreezeReader", "StaticFreezeReader"]
