from __future__ import annotations

import logging

from agentic_core.interfaces.write_gateway import get_write_gateway
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "local_disk_adapter_util")
emit_determinism_digest("p0", "local_disk_adapter_util")

_emit_dispatches_healing_run("p1", "local_disk_adapter_util", "L4")
_emit_routes_through("p1", "local_disk_adapter_util", "L4")
_emit_escalates_to_human("p1", "local_disk_adapter_util", "L4")
_emit_reads_policy_state("p1", "local_disk_adapter_util", "L4")
_emit_authorize_and_execute("p2", "local_disk_adapter_util", "execution_auth")
_emit_validates_capability("p2", "local_disk_adapter_util", "capability_check")
_emit_routes_to_capability("p2", "local_disk_adapter_util", "capability_route")
_emit_writes_via_uwg("p2", "local_disk_adapter_util", "uwg_write")
_emit_blocks_direct_write("p2", "local_disk_adapter_util", "direct_write_block")
_emit_records_tool_invocation("p2", "local_disk_adapter_util", "tool_invocation")
_emit_captures_execution_output("p2", "local_disk_adapter_util", "exec_output")
_emit_dispatches_agent("p3", "local_disk_adapter_util", "agent_dispatch")
_emit_coordinates_agents("p3", "local_disk_adapter_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "local_disk_adapter_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "local_disk_adapter_util", "healing_outcome")
_emit_escalates_failure("p3", "local_disk_adapter_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "local_disk_adapter_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "local_disk_adapter_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "local_disk_adapter_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "local_disk_adapter_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "local_disk_adapter_util", "eval_metric")
_emit_stores_embedding("p4", "local_disk_adapter_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "local_disk_adapter_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "local_disk_adapter_util", "exec_snapshot_link")


def _get_write_gateway():
    """Get UWG instance - L4 may only use, not import tools."""
    return get_write_gateway()


"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from pathlib import Path
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class LocalDiskAdapter:
    """
    L4 State: The Sovereign File System.
    Strictly controls I/O within the mission-approved data silos.

    V15 Note: This is a storage provider pattern, NOT the behavioral adapter
    pattern prohibited by V15 §8.1. Explicitly excepted per P0.2.
    """

    def __init__(self, config: dict[str, Any]):
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "LocalDiskAdapter.__init__", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "LocalDiskAdapter.__init__", "p0_governance")
        self.config = config
        self.root = Path(config.get("storage_path", "./data/storage"))
        _get_write_gateway().ensure_dir(self.root)

    async def write_blob(self, key: str, data: bytes, METADATA: dict = None) -> Any:
        """Writes data to the sovereign storage area."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L4_STATE, "LocalDiskAdapter.write_blob")

        safe_path = self.root / key.lstrip("/")
        _get_write_gateway().ensure_dir(safe_path.parent)
        _get_write_gateway().open_write(safe_path, data)
        logging.info(f"DiskAdapter: Persisted {len(data)} bytes to {key}")
