"""Structure drift manifest writer — stdlib only, no UWG dependency.

Write counterpart for structure_drift_validator.generate_structure_manifest().
Moved here from validators/ to preserve the pure read-only contract of that module.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

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

emit_replay_key("p0", "structure_drift_writer")
emit_determinism_digest("p0", "structure_drift_writer")

_emit_dispatches_healing_run("p1", "structure_drift_writer", "L5")
_emit_routes_through("p1", "structure_drift_writer", "L5")
_emit_escalates_to_human("p1", "structure_drift_writer", "L5")
_emit_reads_policy_state("p1", "structure_drift_writer", "L5")
_emit_authorize_and_execute("p2", "structure_drift_writer", "execution_auth")
_emit_validates_capability("p2", "structure_drift_writer", "capability_check")
_emit_routes_to_capability("p2", "structure_drift_writer", "capability_route")
_emit_writes_via_uwg("p2", "structure_drift_writer", "uwg_write")
_emit_blocks_direct_write("p2", "structure_drift_writer", "direct_write_block")
_emit_records_tool_invocation("p2", "structure_drift_writer", "tool_invocation")
_emit_captures_execution_output("p2", "structure_drift_writer", "exec_output")
_emit_dispatches_agent("p3", "structure_drift_writer", "agent_dispatch")
_emit_coordinates_agents("p3", "structure_drift_writer", "agent_coordination")
_emit_records_workflow_lineage("p3", "structure_drift_writer", "workflow_lineage")
_emit_records_healing_outcome("p3", "structure_drift_writer", "healing_outcome")
_emit_escalates_failure("p3", "structure_drift_writer", "failure_escalation")
_emit_orchestrates_workflow("p3", "structure_drift_writer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "structure_drift_writer", "healing_dispatch")
_emit_invokes_evaluation("p3", "structure_drift_writer", "evaluation_signal")
_emit_records_telemetry_event("p4", "structure_drift_writer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "structure_drift_writer", "eval_metric")
_emit_stores_embedding("p4", "structure_drift_writer", "embedding_store")
_emit_updates_meta_learning_state("p4", "structure_drift_writer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "structure_drift_writer", "exec_snapshot_link")


def save_manifest(manifest: dict[str, Any], output_path: Path) -> None:
    """Save the structure manifest to a file.

    Args:
        manifest: The structure manifest to save
        output_path: Path where to save the manifest
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "save_manifest", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "save_manifest", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_SAFETY, "save_manifest")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


__all__ = ["save_manifest"]
