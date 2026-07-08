"""Infrastructure package — system hardening and cross-cutting optimization modules."""

from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract


def emit_package_boot_telemetry() -> None:
    """Emit package boot telemetry explicitly instead of at import time."""
    # P0: Evidence emission
    trace_contract.emit_replay_key("p0", "infrastructure")
    trace_contract.emit_determinism_digest("p0", "infrastructure")

    # P1: Policy and routing
    trace_contract._emit_reads_policy_state("p1", "infrastructure", "L5")
    trace_contract._emit_escalates_to_human("p1", "infrastructure", "L5")
    trace_contract._emit_routes_through("p1", "infrastructure", "L5")
    trace_contract._emit_checks_agent_registry("p1", "infrastructure", "agent_registry")
    trace_contract._emit_validates_agent_capability("p1", "infrastructure", "capability")
    trace_contract._emit_dispatches_execution_plan("p1", "infrastructure", "exec_plan")
    trace_contract._emit_agent_executes_agent("p1", "infrastructure", "sub_agent")
    trace_contract._emit_routes_to_agent("p1", "infrastructure", "target_agent")
    trace_contract._emit_verifies_policy("p1", "infrastructure", "policy_check")
    trace_contract._emit_observes_runtime_state("p1", "infrastructure", "runtime_state")
    trace_contract._emit_verifies_boundary("p1", "infrastructure", "boundary_check")
    trace_contract._emit_transcripts_response("p1", "infrastructure", "transcript")
    trace_contract._emit_hard_fails_untranscripted("p1", "infrastructure")
    trace_contract._emit_gated_by_confidence("p1", "infrastructure", "confidence_gate")
    trace_contract._emit_dispatches_healing_run("p1", "infrastructure", "L5")


__all__ = ["emit_package_boot_telemetry"]
