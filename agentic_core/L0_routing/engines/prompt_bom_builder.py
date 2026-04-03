"""PromptBOM Builder — L0 Router → Assembly Stage bridge.

Creates PromptBOM from InstructionPacket, bridging L0 to L_PG territory.
"""

from __future__ import annotations

import uuid
from typing import Any

from agentic_core.L0_routing.types.l0_instruction_packet import InstructionPacket
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    emit_replay_key
)
# Lazy import to avoid L0->L_PG gravity violation
def _get_prompt_bom():
    from agentic_core.prompt_governance.contracts.prompt_bom_types import PromptBOM
    return PromptBOM

# Self-bootstrap governance wiring
_emit_authorize_and_execute("p2", "PromptBOMBuilder", "execution_auth")
_emit_validates_capability("p2", "PromptBOMBuilder", "capability_check")
_emit_routes_to_capability("p2", "PromptBOMBuilder", "capability_route")
_emit_writes_via_uwg("p2", "PromptBOMBuilder", "uwg_write")
_emit_blocks_direct_write("p2", "PromptBOMBuilder", "direct_write_block")
_emit_records_tool_invocation("p2", "PromptBOMBuilder", "tool_invocation")
_emit_captures_execution_output("p2", "PromptBOMBuilder", "exec_output")
_emit_dispatches_agent("p3", "PromptBOMBuilder", "agent_dispatch")
_emit_coordinates_agents("p3", "PromptBOMBuilder", "agent_coordination")
_emit_records_workflow_lineage("p3", "PromptBOMBuilder", "workflow_lineage")
_emit_records_healing_outcome("p3", "PromptBOMBuilder", "healing_outcome")
_emit_escalates_failure("p3", "PromptBOMBuilder", "failure_escalation")
_emit_orchestrates_workflow("p3", "PromptBOMBuilder", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "PromptBOMBuilder", "healing_dispatch")
_emit_invokes_evaluation("p3", "PromptBOMBuilder", "evaluation_signal")
_emit_records_telemetry_event("p4", "PromptBOMBuilder", "telemetry_event")
_emit_captures_evaluation_metric("p4", "PromptBOMBuilder", "eval_metric")
_emit_stores_embedding("p4", "PromptBOMBuilder", "embedding_store")
_emit_updates_meta_learning_state("p4", "PromptBOMBuilder", "meta_learning")
_emit_links_execution_to_snapshot("p4", "PromptBOMBuilder", "exec_snapshot_link")
_emit_dispatches_healing_run("p1", "PromptBOMBuilder", "L0")
_emit_routes_through("p1", "PromptBOMBuilder", "L0")
_emit_checks_agent_registry("p1", "PromptBOMBuilder", "agent_registry")
_emit_validates_agent_capability("p1", "PromptBOMBuilder", "capability")
_emit_dispatches_execution_plan("p1", "PromptBOMBuilder", "exec_plan")
_emit_routes_to_agent("p1", "PromptBOMBuilder", "target_agent")
_emit_verifies_policy("p1", "PromptBOMBuilder", "policy_check")
_emit_observes_runtime_state("p1", "PromptBOMBuilder", "runtime_state")
_emit_verifies_boundary("p1", "PromptBOMBuilder", "boundary_check")
_emit_transcripts_response("p1", "PromptBOMBuilder", "transcript")
_emit_gated_by_confidence("p1", "PromptBOMBuilder", "confidence_gate")
_emit_escalates_to_human("p1", "PromptBOMBuilder", "L0")
_emit_reads_policy_state("p1", "PromptBOMBuilder", "L0")


def _get_version_store():
    """Lazy import to avoid circular dependencies."""
    from agentic_core.L4_state.memory.prompt_version_store import get_version_store
    return get_version_store()


class PromptBOMBuilder:
    """Builds PromptBOM from InstructionPacket.

    Bridges L0 routing decisions to L_PG assembly stage.
    Fetches system version hash from L4 state store.
    """

    def build(
        self,
        packet: InstructionPacket,
        raw_u0: str,
        raw_c0: dict[str, Any] | None = None,
        template_args: dict[str, Any] | None = None,
    ) -> "PromptBOM":
        """Build PromptBOM from instruction packet.

        Args:
            packet: InstructionPacket from PathRouter.
            raw_u0: Raw user input (U0 slot).
            raw_c0: Context pointers for C0 slot.
            template_args: Template variable bindings.

        Returns:
            Immutable PromptBOM for Assembly Stage.
        """
        PromptBOM = _get_prompt_bom()
        trace_id = str(uuid.uuid4())
        _emit_records_execution_trace(
            trace_id, LayerSegment.L0_ROUTING, "PromptBOMBuilder.build"
        )
        emit_replay_key(trace_id, f"bom:{packet.trace_id}")
        emit_determinism_digest(trace_id, f"path:{packet.path}")

        # Fetch system version hash from L4 store
        version_store = _get_version_store()
        system_version_hash = version_store.get_current_system_hash()

        bom = PromptBOM(
            trace_id=packet.trace_id,
            system_version_hash=system_version_hash,
            mixins_required=tuple(sorted(packet.required_mixins)),
            raw_u0=raw_u0,
            raw_c0=dict(raw_c0) if raw_c0 else {},
            template_args=dict(template_args) if template_args else {},
            path=packet.path,
        )

        return bom


# Singleton instance
_builder_instance: PromptBOMBuilder | None = None


def get_prompt_bom_builder() -> PromptBOMBuilder:
    """Get singleton PromptBOMBuilder instance."""
    global _builder_instance
    if _builder_instance is None:
        _builder_instance = PromptBOMBuilder()
    return _builder_instance


__all__ = ["PromptBOMBuilder", "get_prompt_bom_builder"]
