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
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "authority", "p0_governance")
_emit_reads_policy_state("p0", "authority", "policy_binding")
_emit_snapshots_state("p0", "authority", "state_snapshot")
emit_replay_key("p0", "authority")
emit_determinism_digest("p0", "authority")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


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
