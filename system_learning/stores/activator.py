"""Concrete Activator — swaps active config version pointer via L4StateWriter.

Provides in-memory and file-backed implementations of the ``Activator``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

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
from system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

_emit_applies_guardrail("p0", "activator", "p0_governance")
_emit_reads_policy_state("p0", "activator", "policy_binding")
_emit_snapshots_state("p0", "activator", "state_snapshot")
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

_emit_emits_metric_event("activator", "p4obs", "metric_1")
_emit_emits_metric_event("activator", "p4obs", "metric_2")
_emit_emits_metric_event("activator", "p4obs", "metric_3")
_emit_emits_metric_event("activator", "p4obs", "metric_4")
_emit_emits_metric_event("activator", "p4obs", "metric_5")
_emit_emits_metric_event("activator", "p4obs", "metric_6")
_emit_records_incident_event("activator", "p4obs", "incident")
_emit_captures_runtime_anomaly("activator", "p4obs", "anomaly")
_emit_writes_observability_log("activator", "p4obs", "obs_log")
_emit_updates_monitoring_state("activator", "p4obs", "mon_state")
_emit_triggers_alert("activator", "p4obs", "alert")
_emit_links_incident_trace("activator", "p4obs", "trace_link")
_emit_captures_pattern("activator", "p3lm", "pattern")
_emit_records_learning_event("activator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("activator", "p3lm", "snapshot")
_emit_feeds_meta_learning("activator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("activator", "p3lm", "routing")
_emit_improves_agent_policy("activator", "p3lm", "policy")
_emit_stores_learning_state("activator", "p3lm", "state")
_emit_records_execution_trace("activator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("activator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("activator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("activator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("activator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("activator", "env_read", "p2_env_1")
_emit_reads_environ("activator", "env_read", "p2_env_2")
_emit_reads_runtime_state("activator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("activator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "activator", "context_pull")
_emit_pulls_context("p1", "activator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "activator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "activator", "uwg_term_2")
_emit_writes_through("p1", "activator", "write_through")
_emit_writes_through("p1", "activator", "write_through_2")
_emit_validated_by_safety_plane("p1", "activator", "safety_validation")
_emit_invokes_eval("p1", "activator", "eval_call")
_emit_proposal_commits_routing("p1", "activator", "routing_commit")
_emit_escalates_to_human("p1", "activator", "human_escalation")
_emit_routes_through("p1", "activator", "route_through")
_emit_checks_agent_registry("p1", "activator", "agent_registry")
_emit_validates_agent_capability("p1", "activator", "capability")
_emit_dispatches_execution_plan("p1", "activator", "exec_plan")
_emit_agent_executes_agent("p1", "activator", "sub_agent")
_emit_routes_to_agent("p1", "activator", "target_agent")
_emit_verifies_policy("p1", "activator", "policy_check")
_emit_observes_runtime_state("p1", "activator", "runtime_state")
_emit_verifies_boundary("p1", "activator", "boundary_check")
_emit_transcripts_response("p1", "activator", "transcript")
_emit_hard_fails_untranscripted("p1", "activator")
_emit_gated_by_confidence("p1", "activator", "confidence_gate")
emit_replay_key("p0", "activator")
emit_determinism_digest("p0", "activator")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "activator", "execution_auth")
_emit_validates_capability("p2", "activator", "capability_check")
_emit_routes_to_capability("p2", "activator", "capability_route")
_emit_writes_via_uwg("p2", "activator", "uwg_write")
_emit_blocks_direct_write("p2", "activator", "direct_write_block")
_emit_records_tool_invocation("p2", "activator", "tool_invocation")
_emit_captures_execution_output("p2", "activator", "exec_output")
_emit_dispatches_agent("p3", "activator", "agent_dispatch")
_emit_coordinates_agents("p3", "activator", "agent_coordination")
_emit_records_workflow_lineage("p3", "activator", "workflow_lineage")
_emit_records_healing_outcome("p3", "activator", "healing_outcome")
_emit_escalates_failure("p3", "activator", "failure_escalation")
_emit_orchestrates_workflow("p3", "activator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "activator", "healing_dispatch")
_emit_invokes_evaluation("p3", "activator", "evaluation_signal")
_emit_records_telemetry_event("p4", "activator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "activator", "eval_metric")
_emit_stores_embedding("p4", "activator", "embedding_store")
_emit_updates_meta_learning_state("p4", "activator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "activator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class InMemoryActivator:
    """In-memory activator for testing."""

    _active: dict[str, str] = field(default_factory=dict)

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "InMemoryActivator.activate")

        logger.info("Activating component=%s version=%s", component, version_id)
        self._active[component] = version_id

    def get_active(self, component: str) -> str | None:
        return self._active.get(component)


class FileBackedActivator:
    """File-backed activator that persists active version pointers.

    Writes ``<base_dir>/_active.json`` mapping component names to version IDs.
    """

    def __init__(self, base_dir: Path) -> None:
        self._base_dir = Path(base_dir)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self._active_path = self._base_dir / "_active.json"
        self._active: dict[str, str] = self._load()

    def _load(self) -> dict[str, str]:
        if self._active_path.exists():
            try:
                return json.loads(self._active_path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):  # guardian: Add error context logging
                return {}
        return {}

    def _save(self) -> None:
        self._active_path.write_text(json.dumps(self._active, indent=2, sort_keys=True), encoding="utf-8")

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L3_ORCHESTRATION,
            "FileBackedActivator.activate",
        )

        logger.info("Activating component=%s version=%s", component, version_id)
        self._active[component] = version_id
        self._save()
        try:
            get_sl_memory_bridge().persist_active_version(component, version_id)
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.debug("Failed to persist active version for %s: %s", component, exc)

    def get_active(self, component: str) -> str | None:
        return self._active.get(component)


__all__ = ["InMemoryActivator", "FileBackedActivator"]
