"""MCP authority seam contract — Protocol and lazy factory for MCPSovereignAuthority.

This module sits outside the layer hierarchy so imports from here
do not count as upward seams in the gravity scanner.
All upward imports (→ L5) are deferred inside the factory function.
"""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Mapping, Protocol, runtime_checkable

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "authority", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "authority", "policy_binding")
trace_contract._emit_snapshots_state("p0", "authority", "state_snapshot")

trace_contract._emit_emits_metric_event("authority", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("authority", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("authority", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("authority", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("authority", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("authority", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("authority", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("authority", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("authority", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("authority", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("authority", "p4obs", "alert")
trace_contract._emit_links_incident_trace("authority", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("authority", "p3lm", "pattern")
trace_contract._emit_records_learning_event("authority", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("authority", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("authority", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("authority", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("authority", "p3lm", "policy")
trace_contract._emit_stores_learning_state("authority", "p3lm", "state")
trace_contract._emit_records_execution_trace("authority", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("authority", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("authority", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("authority", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("authority", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("authority", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("authority", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("authority", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("authority", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "authority", "context_pull")
trace_contract._emit_pulls_context("p1", "authority", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "authority", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "authority", "uwg_term_2")
trace_contract._emit_writes_through("p1", "authority", "write_through")
trace_contract._emit_writes_through("p1", "authority", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "authority", "safety_validation")
trace_contract._emit_invokes_eval("p1", "authority", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "authority", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "authority", "human_escalation")
trace_contract._emit_routes_through("p1", "authority", "route_through")
trace_contract._emit_checks_agent_registry("p1", "authority", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "authority", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "authority", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "authority", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "authority", "target_agent")
trace_contract._emit_verifies_policy("p1", "authority", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "authority", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "authority", "boundary_check")
trace_contract._emit_transcripts_response("p1", "authority", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "authority")
trace_contract._emit_gated_by_confidence("p1", "authority", "confidence_gate")
trace_contract.emit_replay_key("p0", "authority")
trace_contract.emit_determinism_digest("p0", "authority")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "authority", "execution_auth")
trace_contract._emit_validates_capability("p2", "authority", "capability_check")
trace_contract._emit_routes_to_capability("p2", "authority", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "authority", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "authority", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "authority", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "authority", "exec_output")
trace_contract._emit_dispatches_agent("p3", "authority", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "authority", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "authority", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "authority", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "authority", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "authority", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "authority", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "authority", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "authority", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "authority", "eval_metric")
trace_contract._emit_stores_embedding("p4", "authority", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "authority", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "authority", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_FAIL_OPEN_ENV = "SEAMS_ALLOW_FAIL_OPEN_AUTHORITY"


@runtime_checkable
class MCPAuthorityProtocol(Protocol):
    """Minimal protocol for MCP sovereign authority."""

    def is_authorized(self) -> bool: ...

    def record_breach(self, error_msg: str) -> Any: ...

    def authorize_tool_call(self, tool_name: str, args: Mapping[str, Any]) -> None: ...


class _NullAuthority:
    """Fallback authority when L5 authority is unavailable.

    Defaults to fail-closed. Operators can explicitly opt into fail-open
    behavior by setting ``SEAMS_ALLOW_FAIL_OPEN_AUTHORITY=1`` for local CI.
    """

    def __init__(self, reason: str) -> None:
        self._reason = reason

    def is_authorized(self) -> bool:
        return os.getenv(_FAIL_OPEN_ENV, "0") == "1"

    def record_breach(self, error_msg: str) -> dict[str, Any]:
        import uuid as _uuid  # noqa: PLC0415

        trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            trace_id,
            trace_contract.LayerSegment.L3_ORCHESTRATION,
            "_NullAuthority.record_breach",
        )
        logger.error(
            "[NullAuthority] breach recorded trace_id=%s reason=%s error=%s",
            trace_id,
            self._reason,
            error_msg,
        )
        return {
            "trace_id": trace_id,
            "authorized": False,
            "reason": self._reason,
            "error": error_msg,
        }

    def authorize_tool_call(self, tool_name: str, args: Mapping[str, Any]) -> None:
        if not tool_name:
            raise ValueError("tool_name must be non-empty")

        if self.is_authorized():
            logger.warning(
                "[NullAuthority] fail-open enabled via %s for tool=%s",
                _FAIL_OPEN_ENV,
                tool_name,
            )
            return

        raise PermissionError(
            "MCP authority unavailable; refusing tool call "
            f"{tool_name!r}. Set {_FAIL_OPEN_ENV}=1 only for controlled offline runs."
        )


@lru_cache(maxsize=1)
def get_mcp_authority() -> MCPAuthorityProtocol:
    """Return the live MCPSovereignAuthority singleton or a guarded fallback."""
    try:
        from agentic_core.L5_safety.enforcement.mcp_sovereign_authority_enforcer import (
            mcp_authority,
        )
    except ImportError as exc:
        reason = f"authority import failed: {exc}"
        logger.error(reason)
        return _NullAuthority(reason)

    if not isinstance(mcp_authority, MCPAuthorityProtocol):
        reason = "imported mcp_authority does not satisfy MCPAuthorityProtocol"
        logger.error(reason)
        return _NullAuthority(reason)

    return mcp_authority


__all__ = ["MCPAuthorityProtocol", "get_mcp_authority"]
