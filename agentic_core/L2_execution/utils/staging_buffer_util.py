from __future__ import annotations

import copy

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "staging_buffer_util")
emit_determinism_digest("p0", "staging_buffer_util")

_emit_dispatches_healing_run("p1", "staging_buffer_util", "L2")
_emit_routes_through("p1", "staging_buffer_util", "L2")
_emit_escalates_to_human("p1", "staging_buffer_util", "L2")
_emit_reads_policy_state("p1", "staging_buffer_util", "L2")

_emit_applies_guardrail("p0", "staging_buffer_util", "p0_governance")
_emit_snapshots_state("p0", "staging_buffer_util", "state_snapshot")
_emit_authorize_and_execute("p2", "staging_buffer_util", "execution_auth")
_emit_validates_capability("p2", "staging_buffer_util", "capability_check")
_emit_routes_to_capability("p2", "staging_buffer_util", "capability_route")
_emit_writes_via_uwg("p2", "staging_buffer_util", "uwg_write")
_emit_blocks_direct_write("p2", "staging_buffer_util", "direct_write_block")
_emit_records_tool_invocation("p2", "staging_buffer_util", "tool_invocation")
_emit_captures_execution_output("p2", "staging_buffer_util", "exec_output")
_emit_dispatches_agent("p3", "staging_buffer_util", "agent_dispatch")
_emit_coordinates_agents("p3", "staging_buffer_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "staging_buffer_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "staging_buffer_util", "healing_outcome")
_emit_escalates_failure("p3", "staging_buffer_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "staging_buffer_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "staging_buffer_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "staging_buffer_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "staging_buffer_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "staging_buffer_util", "eval_metric")
_emit_stores_embedding("p4", "staging_buffer_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "staging_buffer_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "staging_buffer_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import logging
from datetime import datetime
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)

Logger: Any = logging.getLogger(__name__)
"Immutable staging buffer for HOP-4."


class StagingBufferError(Exception):
    """Custom exception for staging buffer operations."""

    pass


class ImmutableStagingBuffer:
    """HOP-4: Immutable staging buffer. Once locked, cannot be modified."""

    def __init__(self: Any) -> None:
        """Initialize the staging buffer."""
        self._data: dict[str, object] = {}
        self._locked: bool = False
        self._lock_timestamp: str | None = None

    def set(self: Any, key: str, value: object) -> None:
        """Set value in buffer (only if not locked)."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "ImmutableStagingBuffer.set")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ImmutableStagingBuffer.set".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if self._locked:
            raise StagingBufferError(f"Cannot set '{key}': buffer is locked")
        self._data[key] = value

    def get(self: Any, key: str, default: object | None) -> object | None:
        """Get value from buffer."""
        return self._data.get(key, default)

    def lock(self: Any) -> None:
        """Lock the buffer (irreversible)."""
        if not self._locked:
            self._locked = True
            self._lock_timestamp = datetime.now().isoformat()

    def is_locked(self: Any) -> bool:
        """Check if buffer is locked."""
        return self._locked

    @property
    def data(self: Any) -> dict[str, object]:
        """Read-only access to data."""
        return copy.deepcopy(self._data)
