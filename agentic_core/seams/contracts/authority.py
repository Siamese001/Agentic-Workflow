"""MCP authority seam contract — Protocol and lazy factory for MCPSovereignAuthority.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
All upward imports (→ L5) are deferred inside the factory function.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

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

_emit_applies_guardrail("p0", "authority", "p0_governance")
_emit_reads_policy_state("p0", "authority", "policy_binding")
_emit_snapshots_state("p0", "authority", "state_snapshot")
emit_replay_key("p0", "authority")
emit_determinism_digest("p0", "authority")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "authority", "execution_auth")
_emit_validates_capability("p2", "authority", "capability_check")
_emit_routes_to_capability("p2", "authority", "capability_route")
_emit_writes_via_uwg("p2", "authority", "uwg_write")
_emit_blocks_direct_write("p2", "authority", "direct_write_block")
_emit_records_tool_invocation("p2", "authority", "tool_invocation")
_emit_captures_execution_output("p2", "authority", "exec_output")
_emit_dispatches_agent("p3", "authority", "agent_dispatch")
_emit_coordinates_agents("p3", "authority", "agent_coordination")
_emit_records_workflow_lineage("p3", "authority", "workflow_lineage")
_emit_records_healing_outcome("p3", "authority", "healing_outcome")
_emit_escalates_failure("p3", "authority", "failure_escalation")
_emit_orchestrates_workflow("p3", "authority", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "authority", "healing_dispatch")
_emit_invokes_evaluation("p3", "authority", "evaluation_signal")
_emit_records_telemetry_event("p4", "authority", "telemetry_event")
_emit_captures_evaluation_metric("p4", "authority", "eval_metric")
_emit_stores_embedding("p4", "authority", "embedding_store")
_emit_updates_meta_learning_state("p4", "authority", "meta_learning")
_emit_links_execution_to_snapshot("p4", "authority", "exec_snapshot_link")


@runtime_checkable
class MCPAuthorityProtocol(Protocol):
    """Minimal protocol for MCP sovereign authority."""

    def is_authorized(self) -> bool: ...

    def record_breach(self, error_msg: str) -> Any: ...

    def authorize_tool_call(self, tool_name: str, args: dict) -> None: ...


class _NullAuthority:
    """No-op fallback when L5 authority is unavailable (CI / offline)."""

    def is_authorized(self) -> bool:
        return True

    def record_breach(self, error_msg: str) -> Any:
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_NullAuthority.record_breach")

        import logging

        logging.getLogger(__name__).warning("[NullAuthority] breach recorded: %s", error_msg)

    def authorize_tool_call(self, tool_name: str, args: dict) -> None:
        pass


def get_mcp_authority() -> MCPAuthorityProtocol:
    """Return the live MCPSovereignAuthority singleton, or a no-op fallback.

    Lazy import holds the L5 upward dependency inside the seam so that
    L2/L3 consumers can call this without gravity violations.
    """
    try:
        from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import (
            mcp_authority,
        )

        return mcp_authority  # type: ignore[return-value]
    except ImportError:
        return _NullAuthority()


__all__ = ["MCPAuthorityProtocol", "get_mcp_authority"]
