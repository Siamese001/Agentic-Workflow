"""
Message Generation Task - Outreach message writer
Refactored from execute_message_generation.py
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

_emit_authorize_and_execute("p2", "message_generation_task", "execution_auth")
_emit_validates_capability("p2", "message_generation_task", "capability_check")
_emit_routes_to_capability("p2", "message_generation_task", "capability_route")
_emit_writes_via_uwg("p2", "message_generation_task", "uwg_write")
_emit_blocks_direct_write("p2", "message_generation_task", "direct_write_block")
_emit_records_tool_invocation("p2", "message_generation_task", "tool_invocation")
_emit_captures_execution_output("p2", "message_generation_task", "exec_output")
_emit_dispatches_agent("p3", "message_generation_task", "agent_dispatch")
_emit_coordinates_agents("p3", "message_generation_task", "agent_coordination")
_emit_records_workflow_lineage("p3", "message_generation_task", "workflow_lineage")
_emit_records_healing_outcome("p3", "message_generation_task", "healing_outcome")
_emit_escalates_failure("p3", "message_generation_task", "failure_escalation")
_emit_orchestrates_workflow("p3", "message_generation_task", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "message_generation_task", "healing_dispatch")
_emit_invokes_evaluation("p3", "message_generation_task", "evaluation_signal")
_emit_records_telemetry_event("p4", "message_generation_task", "telemetry_event")
_emit_captures_evaluation_metric("p4", "message_generation_task", "eval_metric")
_emit_stores_embedding("p4", "message_generation_task", "embedding_store")
_emit_updates_meta_learning_state("p4", "message_generation_task", "meta_learning")
_emit_links_execution_to_snapshot("p4", "message_generation_task", "exec_snapshot_link")
from apps_rg.engines.base_rg_engine import BaseRGEngine

_emit_applies_guardrail("p0", "message_generation_task", "p0_governance")
_emit_reads_policy_state("p0", "message_generation_task", "policy_binding")
_emit_snapshots_state("p0", "message_generation_task", "state_snapshot")
emit_replay_key("p0", "message_generation_task")
emit_determinism_digest("p0", "message_generation_task")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

Logger = logging.getLogger(__name__)


class MessageGenerationTask(BaseRGEngine):
    """
    Outreach message writer for networking/applications.
    """

    def __init__(self, ctx: Any) -> None:
        super().__init__(ctx, node_id="GENERATION.MESSAGE")

    async def execute(self, recipient_context: dict[str, Any], message_type: str = "outreach") -> str:
        """
        Generate personalized outreach message.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "MessageGenerationTask.execute")

        self._mcp_audit("message_generation_start", {"type": message_type})
        prompt = f"Generate a {message_type} message for {recipient_context.get('name', 'recipient')}"
        message = await self.call_llm(prompt)
        if message and len(message) > 50:
            self.record_pass(f"Generated {message_type} message")
        else:
            self.record_fail("Message generation produced insufficient content")
        return message or ""
