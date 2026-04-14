"""Infrastructure package — system hardening and cross-cutting optimization modules."""

from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_observes_runtime_state,
    _emit_reads_policy_state,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_transcripts_response,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    emit_determinism_digest,
    emit_replay_key,
)


def emit_package_boot_telemetry() -> None:
    """Emit package boot telemetry explicitly instead of at import time."""
    # P0: Evidence emission
    emit_replay_key("p0", "infrastructure")
    emit_determinism_digest("p0", "infrastructure")

    # P1: Policy and routing
    _emit_reads_policy_state("p1", "infrastructure", "L5")
    _emit_escalates_to_human("p1", "infrastructure", "L5")
    _emit_routes_through("p1", "infrastructure", "L5")
    _emit_checks_agent_registry("p1", "infrastructure", "agent_registry")
    _emit_validates_agent_capability("p1", "infrastructure", "capability")
    _emit_dispatches_execution_plan("p1", "infrastructure", "exec_plan")
    _emit_agent_executes_agent("p1", "infrastructure", "sub_agent")
    _emit_routes_to_agent("p1", "infrastructure", "target_agent")
    _emit_verifies_policy("p1", "infrastructure", "policy_check")
    _emit_observes_runtime_state("p1", "infrastructure", "runtime_state")
    _emit_verifies_boundary("p1", "infrastructure", "boundary_check")
    _emit_transcripts_response("p1", "infrastructure", "transcript")
    _emit_hard_fails_untranscripted("p1", "infrastructure")
    _emit_gated_by_confidence("p1", "infrastructure", "confidence_gate")
    _emit_dispatches_healing_run("p1", "infrastructure", "L5")


__all__ = ["emit_package_boot_telemetry"]
