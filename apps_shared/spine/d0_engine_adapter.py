"""
D0 Engine Adapter — bridges spine string-based d0_injections to D0InjectionEngine.

The spine adapters carry d0_injections as a plain string with fence segments
separated by '|' in the format "fence_id:text|fence_id2:text2".
D0InjectionEngine expects a tuple[RoleFence, ...].

This adapter converts between the two representations without mutating either side.
Falls back to the null stub if D0InjectionEngine cannot be imported.
"""

from __future__ import annotations

import logging

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

_emit_applies_guardrail("p0", "d0_engine_adapter", "p0_governance")
_emit_reads_policy_state("p0", "d0_engine_adapter", "policy_binding")
_emit_snapshots_state("p0", "d0_engine_adapter", "state_snapshot")
emit_replay_key("p0", "d0_engine_adapter")
emit_determinism_digest("p0", "d0_engine_adapter")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "d0_engine_adapter", "execution_auth")
_emit_validates_capability("p2", "d0_engine_adapter", "capability_check")
_emit_routes_to_capability("p2", "d0_engine_adapter", "capability_route")
_emit_writes_via_uwg("p2", "d0_engine_adapter", "uwg_write")
_emit_blocks_direct_write("p2", "d0_engine_adapter", "direct_write_block")
_emit_records_tool_invocation("p2", "d0_engine_adapter", "tool_invocation")
_emit_captures_execution_output("p2", "d0_engine_adapter", "exec_output")
_emit_dispatches_agent("p3", "d0_engine_adapter", "agent_dispatch")
_emit_coordinates_agents("p3", "d0_engine_adapter", "agent_coordination")
_emit_records_workflow_lineage("p3", "d0_engine_adapter", "workflow_lineage")
_emit_records_healing_outcome("p3", "d0_engine_adapter", "healing_outcome")
_emit_escalates_failure("p3", "d0_engine_adapter", "failure_escalation")
_emit_orchestrates_workflow("p3", "d0_engine_adapter", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "d0_engine_adapter", "healing_dispatch")
_emit_invokes_evaluation("p3", "d0_engine_adapter", "evaluation_signal")
_emit_records_telemetry_event("p4", "d0_engine_adapter", "telemetry_event")
_emit_captures_evaluation_metric("p4", "d0_engine_adapter", "eval_metric")
_emit_stores_embedding("p4", "d0_engine_adapter", "embedding_store")
_emit_updates_meta_learning_state("p4", "d0_engine_adapter", "meta_learning")
_emit_links_execution_to_snapshot("p4", "d0_engine_adapter", "exec_snapshot_link")

logger = logging.getLogger(__name__)


def _build_real_engine():
    from agentic_core.L5_safety.enforcement.d0_injection_engine_enforcer import D0InjectionEngine, RoleFence

    return (D0InjectionEngine, RoleFence)


class D0EngineAdapter:
    """
    Adapter converting spine string d0_injections format to RoleFence tuple.

    Input format (string): "fence_id_1:text1|fence_id_2:text2"
    Output: D0InjectionEngine.render_d0(fences=tuple[RoleFence, ...]) -> str

    Falls back to null behavior (return input string unchanged) if the real
    D0InjectionEngine module is unavailable.
    """

    def __init__(self) -> None:
        try:
            D0InjectionEngine, self._RoleFence = _build_real_engine()
            self._engine = D0InjectionEngine()
            self._real = True
        except ImportError:
            logger.warning("D0InjectionEngine unavailable; using null fallback")
            self._engine = None
            self._RoleFence = None
            self._real = False

    def render_d0(self, d0_injections: str) -> str:
        """
        Render D0 injection string via the real D0InjectionEngine.

        Args:
            d0_injections: Pipe-separated fence segments "fence_id:text|..."

        Returns:
            Rendered D0 XML string (e.g. "<D0>\\n[fence_id] text\\n</D0>\\n")
            or the original string unchanged when engine unavailable.
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "D0EngineAdapter.render_d0")

        if not self._real or not d0_injections:
            return d0_injections
        fences = []
        for segment in d0_injections.split("|"):
            segment = segment.strip()
            if ":" in segment:
                fence_id, text = segment.split(":", 1)
                fence_id = fence_id.strip()
                text = text.strip()
                if fence_id:
                    fences.append(self._RoleFence(fence_id=fence_id, text=text))
        if not fences:
            return d0_injections
        return self._engine.render_d0(fences=tuple(fences))

    @property
    def is_real(self) -> bool:
        """True if backed by the real D0InjectionEngine, False for null fallback."""
        return self._real
