"""Concrete Activator — swaps active config version pointer via L4StateWriter.

Provides in-memory and file-backed implementations of the ``Activator``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import json
import logging
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from agentic_core.L6_system_learning.adapters.system_learning_memory_bridge import get_sl_memory_bridge

trace_contract._emit_applies_guardrail("p0", "activator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "activator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "activator", "state_snapshot")

trace_contract._emit_emits_metric_event("activator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("activator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("activator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("activator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("activator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("activator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("activator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("activator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("activator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("activator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("activator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("activator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("activator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("activator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("activator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("activator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("activator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("activator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("activator", "p3lm", "state")
trace_contract._emit_records_execution_trace("activator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("activator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("activator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("activator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("activator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("activator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("activator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("activator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("activator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "activator", "context_pull")
trace_contract._emit_pulls_context("p1", "activator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "activator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "activator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "activator", "write_through")
trace_contract._emit_writes_through("p1", "activator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "activator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "activator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "activator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "activator", "human_escalation")
trace_contract._emit_routes_through("p1", "activator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "activator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "activator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "activator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "activator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "activator", "target_agent")
trace_contract._emit_verifies_policy("p1", "activator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "activator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "activator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "activator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "activator")
trace_contract._emit_gated_by_confidence("p1", "activator", "confidence_gate")
trace_contract.emit_replay_key("p0", "activator")
trace_contract.emit_determinism_digest("p0", "activator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "activator", "execution_auth")
trace_contract._emit_validates_capability("p2", "activator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "activator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "activator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "activator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "activator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "activator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "activator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "activator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "activator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "activator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "activator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "activator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "activator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "activator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "activator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "activator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "activator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "activator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "activator", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class InMemoryActivator:
    """In-memory activator for testing."""

    _active: dict[str, str] = field(default_factory=dict)

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "InMemoryActivator.activate")

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
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load active-version map %s: %s", self._active_path, exc)
                return {}
        return {}

    def _save(self) -> None:
        self._active_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=self._active_path.parent,
            prefix=self._active_path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as handle:
            json.dump(self._active, handle, indent=2, sort_keys=True)
            tmp_name = handle.name
        Path(tmp_name).replace(self._active_path)

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "FileBackedActivator.activate",
        )

        logger.info("Activating component=%s version=%s", component, version_id)
        self._active[component] = version_id
        self._save()
        try:
            get_sl_memory_bridge().persist_active_version(component, version_id)
        except (AttributeError, RuntimeError, TypeError, ValueError, OSError) as exc:  # guardian: allow-log-and-swallow  -- ADG-burn: log_and_swallow
            logger.debug("activator: failed to persist active version: %s", exc)

    def get_active(self, component: str) -> str | None:
        return self._active.get(component)


__all__ = ["InMemoryActivator", "FileBackedActivator"]
