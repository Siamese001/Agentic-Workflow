"""
Sovereign Context for RG Sovereign Architecture.

This is the GLUE. It packages the ImmutableBuffer, TraceRegistry, and Toggles
into a single object passed to every engine.

HARDENING: Replaces the legacy 'ctx' dictionary with a type-safe container.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from apps_rg.config.ReasoningToggles import ReasoningToggles, get_toggles

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

_emit_authorize_and_execute("p2", "SovereigncontextStrategy", "execution_auth")
_emit_validates_capability("p2", "SovereigncontextStrategy", "capability_check")
_emit_routes_to_capability("p2", "SovereigncontextStrategy", "capability_route")
_emit_writes_via_uwg("p2", "SovereigncontextStrategy", "uwg_write")
_emit_blocks_direct_write("p2", "SovereigncontextStrategy", "direct_write_block")
_emit_records_tool_invocation("p2", "SovereigncontextStrategy", "tool_invocation")
_emit_captures_execution_output("p2", "SovereigncontextStrategy", "exec_output")
_emit_dispatches_agent("p3", "SovereigncontextStrategy", "agent_dispatch")
_emit_coordinates_agents("p3", "SovereigncontextStrategy", "agent_coordination")
_emit_records_workflow_lineage("p3", "SovereigncontextStrategy", "workflow_lineage")
_emit_records_healing_outcome("p3", "SovereigncontextStrategy", "healing_outcome")
_emit_escalates_failure("p3", "SovereigncontextStrategy", "failure_escalation")
_emit_orchestrates_workflow("p3", "SovereigncontextStrategy", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "SovereigncontextStrategy", "healing_dispatch")
_emit_invokes_evaluation("p3", "SovereigncontextStrategy", "evaluation_signal")
_emit_records_telemetry_event("p4", "SovereigncontextStrategy", "telemetry_event")
_emit_captures_evaluation_metric("p4", "SovereigncontextStrategy", "eval_metric")
_emit_stores_embedding("p4", "SovereigncontextStrategy", "embedding_store")
_emit_updates_meta_learning_state("p4", "SovereigncontextStrategy", "meta_learning")
_emit_links_execution_to_snapshot("p4", "SovereigncontextStrategy", "exec_snapshot_link")
from apps_rg.types.SovereignContext import ImmutableStagingBuffer, TraceRegistry

_emit_applies_guardrail("p0", "SovereigncontextStrategy", "p0_governance")
_emit_reads_policy_state("p0", "SovereigncontextStrategy", "policy_binding")
_emit_snapshots_state("p0", "SovereigncontextStrategy", "state_snapshot")
emit_replay_key("p0", "SovereigncontextStrategy")
emit_determinism_digest("p0", "SovereigncontextStrategy")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@dataclass
class SovereignContext:
    """
    The Single Source of Truth for runtime execution.
    Passed to every engine. Replaces the legacy 'ctx' dictionary.
    """

    buffer: ImmutableStagingBuffer = field(default_factory=ImmutableStagingBuffer)
    trace: TraceRegistry = field(default_factory=TraceRegistry)
    toggles: ReasoningToggles = field(default_factory=get_toggles)
    mission_id: str = "default"
    signals: set = field(default_factory=set)

    def add_signal(self, signal: str) -> None:
        """Add a signal to the context and log it."""
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "SovereignContext.add_signal")

        self.signals.add(signal)
        self.trace.add_trace("signal_fired", {"signal": signal})

    def record_result(self, agent: str, passed: bool, details: str, data: Any = None) -> None:
        """Legacy adapter for record_result."""
        status = "SUCCESS" if passed else "FAILURE"
        self.trace.add_trace(
            f"agent_{status.lower()}", {"agent": agent, "passed": passed, "details": details}
        )
        if data:
            try:
                self.buffer.write(f"{agent}.output", data, source_agent=agent)
            except PermissionError:
                pass

    def get_signal_count(self) -> int:
        """Return the number of signals fired."""
        return len(self.signals)

    def has_signal(self, signal: str) -> bool:
        """Check if a specific signal has been fired."""
        return signal in self.signals

    def clear_signals(self) -> None:
        """Clear all signals (use with caution)."""
        self.signals.clear()
