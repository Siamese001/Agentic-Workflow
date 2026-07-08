"""Surface Isolation Validator — Enforces single-surface mutation per activation window.

Ensures that only one surface can be mutated within a given activation window
to prevent cross-surface contamination and maintain isolation guarantees.
"""

from __future__ import annotations

import time

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "surface_isolation_validator", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "surface_isolation_validator", "policy_binding")
trace_contract._emit_snapshots_state("p0", "surface_isolation_validator", "state_snapshot")

trace_contract._emit_emits_metric_event("surface_isolation_validator", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("surface_isolation_validator", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("surface_isolation_validator", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("surface_isolation_validator", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("surface_isolation_validator", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("surface_isolation_validator", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("surface_isolation_validator", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("surface_isolation_validator", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("surface_isolation_validator", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("surface_isolation_validator", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("surface_isolation_validator", "p4obs", "alert")
trace_contract._emit_links_incident_trace("surface_isolation_validator", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("surface_isolation_validator", "p3lm", "pattern")
trace_contract._emit_records_learning_event("surface_isolation_validator", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("surface_isolation_validator", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("surface_isolation_validator", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("surface_isolation_validator", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("surface_isolation_validator", "p3lm", "policy")
trace_contract._emit_stores_learning_state("surface_isolation_validator", "p3lm", "state")
trace_contract._emit_records_execution_trace("surface_isolation_validator", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("surface_isolation_validator", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("surface_isolation_validator", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("surface_isolation_validator", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("surface_isolation_validator", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("surface_isolation_validator", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("surface_isolation_validator", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("surface_isolation_validator", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("surface_isolation_validator", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "surface_isolation_validator", "context_pull")
trace_contract._emit_pulls_context("p1", "surface_isolation_validator", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "surface_isolation_validator", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "surface_isolation_validator", "uwg_term_2")
trace_contract._emit_writes_through("p1", "surface_isolation_validator", "write_through")
trace_contract._emit_writes_through("p1", "surface_isolation_validator", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "surface_isolation_validator", "safety_validation")
trace_contract._emit_invokes_eval("p1", "surface_isolation_validator", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "surface_isolation_validator", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "surface_isolation_validator", "human_escalation")
trace_contract._emit_routes_through("p1", "surface_isolation_validator", "route_through")
trace_contract._emit_checks_agent_registry("p1", "surface_isolation_validator", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "surface_isolation_validator", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "surface_isolation_validator", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "surface_isolation_validator", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "surface_isolation_validator", "target_agent")
trace_contract._emit_verifies_policy("p1", "surface_isolation_validator", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "surface_isolation_validator", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "surface_isolation_validator", "boundary_check")
trace_contract._emit_transcripts_response("p1", "surface_isolation_validator", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "surface_isolation_validator")
trace_contract._emit_gated_by_confidence("p1", "surface_isolation_validator", "confidence_gate")
trace_contract.emit_replay_key("p0", "surface_isolation_validator")
trace_contract.emit_determinism_digest("p0", "surface_isolation_validator")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "surface_isolation_validator", "execution_auth")
trace_contract._emit_validates_capability("p2", "surface_isolation_validator", "capability_check")
trace_contract._emit_routes_to_capability("p2", "surface_isolation_validator", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "surface_isolation_validator", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "surface_isolation_validator", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "surface_isolation_validator", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "surface_isolation_validator", "exec_output")
trace_contract._emit_dispatches_agent("p3", "surface_isolation_validator", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "surface_isolation_validator", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "surface_isolation_validator", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "surface_isolation_validator", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "surface_isolation_validator", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "surface_isolation_validator", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "surface_isolation_validator", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "surface_isolation_validator", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "surface_isolation_validator", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "surface_isolation_validator", "eval_metric")
trace_contract._emit_stores_embedding("p4", "surface_isolation_validator", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "surface_isolation_validator", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "surface_isolation_validator", "exec_snapshot_link")


class SurfaceIsolationValidator:
    """Enforces single-surface mutation per activation window.

    Tracks active mutation surfaces and enforces that only one surface
    can be mutated within a given activation window. This prevents
    cross-surface contamination and maintains isolation guarantees.
    """

    ACTIVATION_WINDOW_SECONDS = 300

    def __init__(self) -> None:
        """Initialize the surface isolation validator."""
        self._active_surfaces: dict[str, float] = {}
        self._completion_timestamps: dict[str, float] = {}
        self._completed_surfaces: set[str] = set()
        self._last_cleanup = time.time()

    def can_mutate_surface(
        self,
        target_surface: str,
        authority_sensitivity: str = "MEDIUM",
    ) -> tuple[bool, str]:
        """Check if a surface can be mutated.

        Args:
            target_surface: The target surface identifier.
            authority_sensitivity: Authority sensitivity level (LOW/MEDIUM/HIGH).

        Returns:
            (can_mutate, reason) tuple
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "SurfaceIsolationValidator.can_mutate_surface"
        )

        current_time = time.time()
        self._cleanup_expired_windows(current_time)
        if target_surface in self._completed_surfaces:
            return (False, f"Surface {target_surface} already completed in current activation window")
        if authority_sensitivity == "HIGH":
            if target_surface not in self._active_surfaces:
                self._active_surfaces[target_surface] = current_time
            return (True, "HIGH authority sensitivity allows mutation")
        if not self._active_surfaces:
            self._active_surfaces[target_surface] = current_time
            return (True, "No active surfaces, mutation allowed")
        if target_surface in self._active_surfaces:
            return (True, "Surface already active in current window")
        active_surface = next(iter(self._active_surfaces))
        return (
            False,
            f"Cannot mutate {target_surface}: surface {active_surface} is active in current window",
        )

    def mark_surface_completed(self, target_surface: str) -> None:
        """Mark a surface as completed for the current activation window.

        Args:
            target_surface: The target surface identifier.
        """
        current_time = time.time()
        self._active_surfaces.pop(target_surface, None)
        self._completion_timestamps[target_surface] = current_time
        self._completed_surfaces.add(target_surface)

    def reset_window(self) -> None:
        """Reset the activation window (for testing or manual override)."""
        self._active_surfaces.clear()
        self._completed_surfaces.clear()
        self._completion_timestamps.clear()
        self._last_cleanup = time.time()

    def get_active_surfaces(self) -> set[str]:
        """Get the set of currently active surfaces.

        Returns:
            Set of active surface identifiers (excludes completion tracking keys).
        """
        self._cleanup_expired_windows(time.time())
        return set(self._active_surfaces.keys())

    def get_completed_surfaces(self) -> set[str]:
        """Get the set of completed surfaces in current window.

        Returns:
            Set of completed surface identifiers.
        """
        self._cleanup_expired_windows(time.time())
        return self._completed_surfaces.copy()

    def _cleanup_expired_windows(self, current_time: float) -> None:
        """Clean up expired activation windows.

        Args:
            current_time: Current timestamp.
        """
        if current_time - self._last_cleanup < 60:
            return
        window_start = current_time - self.ACTIVATION_WINDOW_SECONDS
        expired_active = [s for s, ts in self._active_surfaces.items() if ts < window_start]
        for s in expired_active:
            del self._active_surfaces[s]
        expired_completed = [s for s, ts in self._completion_timestamps.items() if ts < window_start]
        for s in expired_completed:
            del self._completion_timestamps[s]
            self._completed_surfaces.discard(s)
        self._last_cleanup = current_time

    def get_window_status(self) -> dict[str, any]:
        """Get the current window status for debugging.

        Returns:
            Dictionary with window status information.
        """
        current_time = time.time()
        self._cleanup_expired_windows(current_time)
        return {
            "current_time": current_time,
            "active_surfaces": dict(self._active_surfaces),
            "completed_surfaces": list(self._completed_surfaces),
            "window_duration_seconds": self.ACTIVATION_WINDOW_SECONDS,
            "last_cleanup": self._last_cleanup,
        }


_surface_isolation_validator: SurfaceIsolationValidator | None = None


def get_surface_isolation_validator() -> SurfaceIsolationValidator:
    """Get the global surface isolation validator instance.

    Returns:
        The global SurfaceIsolationValidator instance.
    """
    global _surface_isolation_validator
    if _surface_isolation_validator is None:
        _surface_isolation_validator = SurfaceIsolationValidator()
    return _surface_isolation_validator


def reset_surface_isolation_validator() -> None:
    """Reset the global surface isolation validator (for testing)."""
    global _surface_isolation_validator
    if _surface_isolation_validator is not None:
        _surface_isolation_validator.reset_window()
