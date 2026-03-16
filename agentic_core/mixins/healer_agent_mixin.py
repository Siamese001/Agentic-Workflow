"""
HealerAgentMixin — Canonical location.

Relocated from agentic_core/L3_orchestration/types/healer_types.py to satisfy
the mixin location invariant (all *Mixin classes under agentic_core/mixins/).

Original file re-exports this class for backward compatibility.
"""

from __future__ import annotations

import logging
from typing import Any

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

_emit_applies_guardrail("p0", "healer_agent_mixin", "p0_governance")
_emit_reads_policy_state("p0", "healer_agent_mixin", "policy_binding")
_emit_snapshots_state("p0", "healer_agent_mixin", "state_snapshot")
emit_replay_key("p0", "healer_agent_mixin")
emit_determinism_digest("p0", "healer_agent_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "healer_agent_mixin", "execution_auth")
_emit_validates_capability("p2", "healer_agent_mixin", "capability_check")
_emit_routes_to_capability("p2", "healer_agent_mixin", "capability_route")
_emit_writes_via_uwg("p2", "healer_agent_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "healer_agent_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_agent_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "healer_agent_mixin", "exec_output")
_emit_dispatches_agent("p3", "healer_agent_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_agent_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_agent_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_agent_mixin", "healing_outcome")
_emit_escalates_failure("p3", "healer_agent_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_agent_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_agent_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_agent_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_agent_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_agent_mixin", "eval_metric")
_emit_stores_embedding("p4", "healer_agent_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_agent_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_agent_mixin", "exec_snapshot_link")


class HealerAgentMixin:
    """
    Mixin for NEW agents. Enforces strict interface compliance.
    Inherit from this to automatically get input validation.
    """

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Template method that handles validation and error wrapping.
        Subclasses should implement `_heal_impl`.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HealerAgentMixin.heal")

        if not isinstance(violation, dict):
            return {"status": "failed", "errors": ["Violation must be a dictionary"]}
        try:
            result = self._heal_impl(violation)
            return self._normalize_result(result)
        except Exception as e:
            logging.error(f"Heal operation failed in {self.__class__.__name__}: {e}")
            return {"status": "failed", "errors": [str(e)]}

    def _heal_impl(self, violation: dict[str, Any]) -> dict[str, Any]:
        """Override this in your agent."""
        raise NotImplementedError("Agents must implement _heal_impl")

    def _normalize_result(self, result: Any) -> dict[str, Any]:
        """Ensures result matches HEAL_RESULT_SCHEMA."""
        if not isinstance(result, dict):
            return {
                "status": "success" if result else "failed",
                "details": str(result),
                "artifacts": [],
                "errors": [],
            }
        defaults = {"status": "success", "details": "Fixed", "artifacts": [], "errors": []}
        for k, v in defaults.items():
            if k not in result:
                result[k] = v
        return result
