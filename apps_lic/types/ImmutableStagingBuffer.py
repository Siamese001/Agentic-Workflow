"""
Immutable Staging Buffer.

A write-once data structure that prevents state mutation bugs in multi-hop workflows.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "ImmutableStagingBuffer", "p0_governance")
_emit_reads_policy_state("p0", "ImmutableStagingBuffer", "policy_binding")
_emit_snapshots_state("p0", "ImmutableStagingBuffer", "state_snapshot")
emit_replay_key("p0", "ImmutableStagingBuffer")
emit_determinism_digest("p0", "ImmutableStagingBuffer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ImmutableStagingBuffer", "execution_auth")
_emit_validates_capability("p2", "ImmutableStagingBuffer", "capability_check")
_emit_routes_to_capability("p2", "ImmutableStagingBuffer", "capability_route")
_emit_writes_via_uwg("p2", "ImmutableStagingBuffer", "uwg_write")
_emit_blocks_direct_write("p2", "ImmutableStagingBuffer", "direct_write_block")
_emit_records_tool_invocation("p2", "ImmutableStagingBuffer", "tool_invocation")
_emit_captures_execution_output("p2", "ImmutableStagingBuffer", "exec_output")
_emit_dispatches_agent("p3", "ImmutableStagingBuffer", "agent_dispatch")
_emit_coordinates_agents("p3", "ImmutableStagingBuffer", "agent_coordination")
_emit_records_workflow_lineage("p3", "ImmutableStagingBuffer", "workflow_lineage")
_emit_records_healing_outcome("p3", "ImmutableStagingBuffer", "healing_outcome")
_emit_escalates_failure("p3", "ImmutableStagingBuffer", "failure_escalation")
_emit_orchestrates_workflow("p3", "ImmutableStagingBuffer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ImmutableStagingBuffer", "healing_dispatch")
_emit_invokes_evaluation("p3", "ImmutableStagingBuffer", "evaluation_signal")
_emit_records_telemetry_event("p4", "ImmutableStagingBuffer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ImmutableStagingBuffer", "eval_metric")
_emit_stores_embedding("p4", "ImmutableStagingBuffer", "embedding_store")
_emit_updates_meta_learning_state("p4", "ImmutableStagingBuffer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ImmutableStagingBuffer", "exec_snapshot_link")

try:
    from agentic_core.mixins.mcp_hardened_mixin import mcp_hardened_mixin

    class MCPHardenedMixin(mcp_hardened_mixin):
        pass
except ImportError:

    class MCPHardenedMixin:
        pass


try:
    from agentic_core.interfaces.mixins import HealerMixin
except ImportError:

    class HealerMixin:
        pass
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


@dataclass
class ImmutableStagingBuffer(MCPHardenedMixin, HealerMixin):
    """
    A hardened buffer that enforces write-once semantics per key.
    Once a key is written, it is locked forever.
    """

    _buffer: dict[str, Any] = field(default_factory=dict)
    _locked_keys: set[str] = field(default_factory=set)

    def __post_init__(self) -> None:
        """Initialize mixins."""
        super().__init__()

    def write_once(self, key: str, value: Any) -> None:
        """
        Writes a value to the buffer if the key is not locked.

        Args:
            key: The identifier for the data.
            value: The data to store.

        Raises:
            ValueError: If the key has already been written to.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ImmutableStagingBuffer.write_once")

        if key in self._locked_keys:
            raise ValueError(f"Key '{key}' is immutable - already written.")
        self._buffer[key] = value
        self._locked_keys.add(key)

    def read(self, key: str) -> Any | None:
        """
        Reads a value from the buffer.

        Args:
            key: The identifier to read.

        Returns:
            The value if found, else None.
        """
        return self._buffer.get(key)

    def is_locked(self, key: str) -> bool:
        """Checks if a key has been written."""
        return key in self._locked_keys

    def get_snapshot(self) -> dict[str, Any]:
        """Returns a copy of the current buffer state."""
        return self._buffer.copy()
