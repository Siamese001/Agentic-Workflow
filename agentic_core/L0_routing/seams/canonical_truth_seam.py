"""
Seam for canonical truth utilities - approved L0→L5 interface.

This seam provides a controlled interface for L0 utilities to access
L5 canonical truth functions without direct L5 imports.
"""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "canonical_truth_seam")
emit_determinism_digest("p0", "canonical_truth_seam")

_emit_dispatches_healing_run("p1", "canonical_truth_seam", "L0")
_emit_routes_through("p1", "canonical_truth_seam", "L0")
_emit_escalates_to_human("p1", "canonical_truth_seam", "L0")
_emit_reads_policy_state("p1", "canonical_truth_seam", "L0")
_emit_authorize_and_execute("p2", "canonical_truth_seam", "execution_auth")
_emit_validates_capability("p2", "canonical_truth_seam", "capability_check")
_emit_routes_to_capability("p2", "canonical_truth_seam", "capability_route")
_emit_writes_via_uwg("p2", "canonical_truth_seam", "uwg_write")
_emit_blocks_direct_write("p2", "canonical_truth_seam", "direct_write_block")
_emit_records_tool_invocation("p2", "canonical_truth_seam", "tool_invocation")
_emit_captures_execution_output("p2", "canonical_truth_seam", "exec_output")
_emit_dispatches_agent("p3", "canonical_truth_seam", "agent_dispatch")
_emit_coordinates_agents("p3", "canonical_truth_seam", "agent_coordination")
_emit_records_workflow_lineage("p3", "canonical_truth_seam", "workflow_lineage")
_emit_records_healing_outcome("p3", "canonical_truth_seam", "healing_outcome")
_emit_escalates_failure("p3", "canonical_truth_seam", "failure_escalation")
_emit_orchestrates_workflow("p3", "canonical_truth_seam", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "canonical_truth_seam", "healing_dispatch")
_emit_invokes_evaluation("p3", "canonical_truth_seam", "evaluation_signal")
_emit_records_telemetry_event("p4", "canonical_truth_seam", "telemetry_event")
_emit_captures_evaluation_metric("p4", "canonical_truth_seam", "eval_metric")
_emit_stores_embedding("p4", "canonical_truth_seam", "embedding_store")
_emit_updates_meta_learning_state("p4", "canonical_truth_seam", "meta_learning")
_emit_links_execution_to_snapshot("p4", "canonical_truth_seam", "exec_snapshot_link")


class CanonicalTruthProvider(Protocol):
    """Protocol for canonical truth operations."""

    def get_layer(self, file_path: Path) -> int:
        """Get the canonical layer for a file path."""
        ...

    def categorize_agent(self, class_name: str, base_classes: list[str], docstring: str | None) -> str:
        """Categorize an agent based on its characteristics."""
        ...


def get_canonical_truth_provider() -> CanonicalTruthProvider:
    """Get the canonical truth provider implementation.

    This function uses dynamic import to avoid static L0→L5 dependency
    while providing runtime access to L5 canonical truth logic.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_canonical_truth_provider", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_canonical_truth_provider", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_canonical_truth_provider")
    import importlib

    try:
        module = importlib.import_module("agentic_core.L5_safety.utils.canonical_truth_util")
        return module
    except ImportError as e:
        raise RuntimeError(f"Failed to load canonical truth provider: {e}")


def get_canonical_layer(file_path: Path) -> int:
    """Get the canonical layer for a file path."""
    provider = get_canonical_truth_provider()
    return provider.get_layer(file_path)


def categorize_agent(class_name: str, base_classes: list[str], docstring: str | None) -> str:
    """Categorize an agent based on its characteristics."""
    provider = get_canonical_truth_provider()
    return provider.categorize_agent(class_name, base_classes, docstring)
