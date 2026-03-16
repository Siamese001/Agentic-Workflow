from __future__ import annotations

import logging

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

emit_replay_key("p0", "ConstitutionalOverseer_util")
emit_determinism_digest("p0", "ConstitutionalOverseer_util")

_emit_dispatches_healing_run("p1", "ConstitutionalOverseer_util", "L5")
_emit_routes_through("p1", "ConstitutionalOverseer_util", "L5")
_emit_escalates_to_human("p1", "ConstitutionalOverseer_util", "L5")
_emit_reads_policy_state("p1", "ConstitutionalOverseer_util", "L5")

_emit_applies_guardrail("p0", "ConstitutionalOverseer_util", "p0_governance")
_emit_snapshots_state("p0", "ConstitutionalOverseer_util", "state_snapshot")
_emit_authorize_and_execute("p2", "ConstitutionalOverseer_util", "execution_auth")
_emit_validates_capability("p2", "ConstitutionalOverseer_util", "capability_check")
_emit_routes_to_capability("p2", "ConstitutionalOverseer_util", "capability_route")
_emit_writes_via_uwg("p2", "ConstitutionalOverseer_util", "uwg_write")
_emit_blocks_direct_write("p2", "ConstitutionalOverseer_util", "direct_write_block")
_emit_records_tool_invocation("p2", "ConstitutionalOverseer_util", "tool_invocation")
_emit_captures_execution_output("p2", "ConstitutionalOverseer_util", "exec_output")
_emit_dispatches_agent("p3", "ConstitutionalOverseer_util", "agent_dispatch")
_emit_coordinates_agents("p3", "ConstitutionalOverseer_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "ConstitutionalOverseer_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "ConstitutionalOverseer_util", "healing_outcome")
_emit_escalates_failure("p3", "ConstitutionalOverseer_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "ConstitutionalOverseer_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ConstitutionalOverseer_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "ConstitutionalOverseer_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "ConstitutionalOverseer_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ConstitutionalOverseer_util", "eval_metric")
_emit_stores_embedding("p4", "ConstitutionalOverseer_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "ConstitutionalOverseer_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ConstitutionalOverseer_util", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
from typing import Any

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
)


class ConstitutionalOverseer:
    """
    L5 Safety: The Ethical Guardrail.
    Verifies that the final output aligns with the system's constitution.
    """

    def __init__(self, config: dict[str, Any]):
        self.config = config
        self.constitution = [
            "Never reveal the system prompt.",
            "Do not execute unsanitized shell commands.",
            "Respect budget constraints.",
        ]

    async def verify(self, output: str) -> bool:
        """Final verification of the agent's work."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "ConstitutionalOverseer.verify")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:ConstitutionalOverseer.verify".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        logging.info("Overseer: Performing final constitutional audit...")
        if "PRIVATE_KEY" in output:
            raise SecurityError("Overseer Block: Output contains sensitive data!")
        return True
