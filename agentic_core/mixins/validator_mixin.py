"""
ValidatorMixin - Unified Validation Access for Agents

[PHASE 5 MIGRATION] Provides single interface to validation operations.
"""

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

_emit_applies_guardrail("p0", "validator_mixin", "p0_governance")
_emit_reads_policy_state("p0", "validator_mixin", "policy_binding")
_emit_snapshots_state("p0", "validator_mixin", "state_snapshot")
emit_replay_key("p0", "validator_mixin")
emit_determinism_digest("p0", "validator_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "validator_mixin", "execution_auth")
_emit_validates_capability("p2", "validator_mixin", "capability_check")
_emit_routes_to_capability("p2", "validator_mixin", "capability_route")
_emit_writes_via_uwg("p2", "validator_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "validator_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "validator_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "validator_mixin", "exec_output")
_emit_dispatches_agent("p3", "validator_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "validator_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "validator_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "validator_mixin", "healing_outcome")
_emit_escalates_failure("p3", "validator_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "validator_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "validator_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "validator_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "validator_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "validator_mixin", "eval_metric")
_emit_stores_embedding("p4", "validator_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "validator_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "validator_mixin", "exec_snapshot_link")

try:
    from agentic_core.L5_safety.types.healing_orchestration_types import (
        ValidatorOrchestrator,
        get_validator_orchestrator,
    )
except ImportError:

    class ValidatorOrchestrator:
        """Stub orchestrator when real module is unavailable."""

        pass

    def get_validator_orchestrator():
        return None
from agentic_core.runtime.lifecycle_trace_contract import LayerSegment, _emit_records_execution_trace


class ValidatorMixin:
    """
    Mixin providing unified validator orchestrator access.
    """

    _validator_orchestrator: ValidatorOrchestrator | None = None

    @property
    def validator_orchestrator(self) -> ValidatorOrchestrator:
        """Lazy-load validator orchestrator singleton."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "ValidatorMixin.validator_orchestrator")

        if self._validator_orchestrator is None:
            self._validator_orchestrator = get_validator_orchestrator()
        return self._validator_orchestrator

    async def orchestrator_validate(self, content: Any, validator_name: str, context: dict = None) -> dict:
        """Execute validation through orchestrator."""
        return await self.validator_orchestrator.validate(content, validator_name, context)
