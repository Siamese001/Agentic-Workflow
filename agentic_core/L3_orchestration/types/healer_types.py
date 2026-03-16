"""
File: agentic_core/base_agents/healer_interface.py
Description: Standardization layer for Healer Agents. Provides Mixins for new agents and Adapters for legacy ones.
"""

import logging
from typing import Any, Protocol, runtime_checkable

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

emit_replay_key("p0", "healer_types")
emit_determinism_digest("p0", "healer_types")

_emit_dispatches_healing_run("p1", "healer_types", "L3")
_emit_routes_through("p1", "healer_types", "L3")
_emit_escalates_to_human("p1", "healer_types", "L3")
_emit_reads_policy_state("p1", "healer_types", "L3")
_emit_authorize_and_execute("p2", "healer_types", "execution_auth")
_emit_validates_capability("p2", "healer_types", "capability_check")
_emit_routes_to_capability("p2", "healer_types", "capability_route")
_emit_writes_via_uwg("p2", "healer_types", "uwg_write")
_emit_blocks_direct_write("p2", "healer_types", "direct_write_block")
_emit_records_tool_invocation("p2", "healer_types", "tool_invocation")
_emit_captures_execution_output("p2", "healer_types", "exec_output")
_emit_dispatches_agent("p3", "healer_types", "agent_dispatch")
_emit_coordinates_agents("p3", "healer_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "healer_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "healer_types", "healing_outcome")
_emit_escalates_failure("p3", "healer_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "healer_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "healer_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "healer_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "healer_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "healer_types", "eval_metric")
_emit_stores_embedding("p4", "healer_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "healer_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "healer_types", "exec_snapshot_link")

HEAL_RESULT_SCHEMA = {"status": "str", "details": "str", "artifacts": "list", "errors": "list"}


@runtime_checkable
class IHealerProtocol(Protocol):
    """The strict interface Phase 2 expects."""

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]: ...


from agentic_core.mixins.healer_agent_mixin import HealerAgentMixin
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


class LegacyAgentAdapter:
    """
    Universal Wrapper for LEGACY agents.
    Translates 'heal(violation)' calls into whatever method the legacy agent has.
    """

    def __init__(self, legacy_agent: Any):
        self.agent = legacy_agent
        self.name = legacy_agent.__class__.__name__

    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        Smartly routes the heal request to known legacy signatures.
        """
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "LegacyAgentAdapter.heal", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "LegacyAgentAdapter.heal", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "LegacyAgentAdapter.heal")

        file_path = violation.get("file") or violation.get("file_path")
        try:
            if hasattr(self.agent, "fix"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.fix({file_path})")
                    res = self.agent.fix(file_path)
                    return self._wrap_legacy_result(res)
                else:
                    return {"status": "skipped", "details": "Legacy agent requires file path"}
            elif hasattr(self.agent, "run"):
                if file_path:
                    logging.info(f"Adapter: Calling {self.name}.run([{file_path}])")
                    res = self.agent.run([file_path])
                    return self._wrap_legacy_result(res)
            elif hasattr(self.agent, "resolve"):
                logging.info(f"Adapter: Calling {self.name}.resolve(violation)")
                res = self.agent.resolve(violation)
                return self._wrap_legacy_result(res)
            else:
                return {
                    "status": "failed",
                    "errors": [f"Agent {self.name} has no recognized healing method (fix/run/resolve)"],
                }
        except Exception as e:
            return {"status": "failed", "errors": [f"Legacy Adapter Error: {str(e)}"]}

    def _wrap_legacy_result(self, result: Any) -> dict[str, Any]:
        """Converts arbitrary legacy returns (bools, strings, lists) to SSOT Schema."""
        if isinstance(result, bool):
            return {
                "status": "success" if result else "failed",
                "details": "Legacy boolean return",
                "artifacts": [],
                "errors": [],
            }
        if isinstance(result, str):
            return {"status": "success", "details": result, "artifacts": [], "errors": []}
        if isinstance(result, list):
            return {
                "status": "success",
                "details": f"Modified {len(result)} files",
                "artifacts": result,
                "errors": [],
            }
        if isinstance(result, dict):
            return HealerAgentMixin()._normalize_result(result)
        return {"status": "unknown", "details": str(result), "artifacts": [], "errors": []}
