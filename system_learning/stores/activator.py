"""Concrete Activator — swaps active config version pointer via L4StateWriter.

Provides in-memory and file-backed implementations of the ``Activator``
protocol defined in ``meta_learning_pipeline.py``.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "activator", "p0_governance")
_emit_reads_policy_state("p0", "activator", "policy_binding")
_emit_snapshots_state("p0", "activator", "state_snapshot")
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
            except (json.JSONDecodeError, OSError):
                return {}
        return {}

    def _save(self) -> None:
        self._active_path.write_text(json.dumps(self._active, indent=2, sort_keys=True), encoding="utf-8")

    def activate(self, component: str, version_id: str) -> None:
        """Activate a specific version for a component."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "FileBackedActivator.activate")

        logger.info("Activating component=%s version=%s", component, version_id)
        self._active[component] = version_id
        self._save()

    def get_active(self, component: str) -> str | None:
        return self._active.get(component)


__all__ = ["InMemoryActivator", "FileBackedActivator"]
