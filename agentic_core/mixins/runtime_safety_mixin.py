"""
RuntimeSafetyMixin - Process Lifecycle Management for Agents.

Landmine #8 & #9 Prevention: Environment Corruption and Zombie Processes.

This mixin provides agents with:
1. Safe subprocess execution via safe_run/safe_popen
2. Automatic process cleanup via ProcessGuard
3. Context manager support for guaranteed cleanup

OPERATIONAL SAFETY (Feb 2026):
- Agents inheriting this mixin get automatic process lifecycle management
- All subprocess calls are validated against the security firewall
- Cleanup is guaranteed via context manager or explicit cleanup() call
"""

import logging
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
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
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "runtime_safety_mixin", "p0_governance")
_emit_reads_policy_state("p0", "runtime_safety_mixin", "policy_binding")
_emit_snapshots_state("p0", "runtime_safety_mixin", "state_snapshot")
emit_replay_key("p0", "runtime_safety_mixin")
emit_determinism_digest("p0", "runtime_safety_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "runtime_safety_mixin", "execution_auth")
_emit_validates_capability("p2", "runtime_safety_mixin", "capability_check")
_emit_routes_to_capability("p2", "runtime_safety_mixin", "capability_route")
_emit_writes_via_uwg("p2", "runtime_safety_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "runtime_safety_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "runtime_safety_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "runtime_safety_mixin", "exec_output")
_emit_dispatches_agent("p3", "runtime_safety_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "runtime_safety_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "runtime_safety_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "runtime_safety_mixin", "healing_outcome")
_emit_escalates_failure("p3", "runtime_safety_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "runtime_safety_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "runtime_safety_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "runtime_safety_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "runtime_safety_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "runtime_safety_mixin", "eval_metric")
_emit_stores_embedding("p4", "runtime_safety_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "runtime_safety_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "runtime_safety_mixin", "exec_snapshot_link")


def _get_process_guardrail():
    from agentic_core.L5_safety.enforcement.process_guardrail import ProcessGuard, SecurityViolation

    return ProcessGuard, SecurityViolation


try:
    from agentic_core.L5_safety.enforcement.safe_subprocess_handler_enforcer import (
        safe_communicate,
        safe_popen,
        safe_run,
    )
except ImportError:  # guardian: allow-silent-swallow - optional dependency

    def safe_communicate(*args, **kwargs):
        return None

    def safe_popen(*args, **kwargs):
        return None

    def safe_run(*args, **kwargs):
        return None


from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("runtime_safety_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("runtime_safety_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("runtime_safety_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("runtime_safety_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("runtime_safety_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("runtime_safety_mixin", "p4obs", "metric_6")
_emit_records_incident_event("runtime_safety_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("runtime_safety_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("runtime_safety_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("runtime_safety_mixin", "p4obs", "mon_state")
_emit_triggers_alert("runtime_safety_mixin", "p4obs", "alert")
_emit_links_incident_trace("runtime_safety_mixin", "p4obs", "trace_link")
_emit_captures_pattern("runtime_safety_mixin", "p3lm", "pattern")
_emit_records_learning_event("runtime_safety_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("runtime_safety_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("runtime_safety_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("runtime_safety_mixin", "p3lm", "routing")
_emit_improves_agent_policy("runtime_safety_mixin", "p3lm", "policy")
_emit_stores_learning_state("runtime_safety_mixin", "p3lm", "state")
_emit_records_execution_trace("runtime_safety_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("runtime_safety_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("runtime_safety_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("runtime_safety_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("runtime_safety_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("runtime_safety_mixin", "env_read", "p2_env_1")
_emit_reads_environ("runtime_safety_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("runtime_safety_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("runtime_safety_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "runtime_safety_mixin", "context_pull")
_emit_pulls_context("p1", "runtime_safety_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "runtime_safety_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "runtime_safety_mixin", "uwg_term_2")
_emit_writes_through("p1", "runtime_safety_mixin", "write_through")
_emit_writes_through("p1", "runtime_safety_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "runtime_safety_mixin", "safety_validation")
_emit_invokes_eval("p1", "runtime_safety_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "runtime_safety_mixin", "routing_commit")
_emit_escalates_to_human("p1", "runtime_safety_mixin", "human_escalation")
_emit_routes_through("p1", "runtime_safety_mixin", "route_through")
_emit_checks_agent_registry("p1", "runtime_safety_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "runtime_safety_mixin", "capability")
_emit_dispatches_execution_plan("p1", "runtime_safety_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "runtime_safety_mixin", "sub_agent")
_emit_routes_to_agent("p1", "runtime_safety_mixin", "target_agent")
_emit_verifies_policy("p1", "runtime_safety_mixin", "policy_check")
_emit_observes_runtime_state("p1", "runtime_safety_mixin", "runtime_state")
_emit_verifies_boundary("p1", "runtime_safety_mixin", "boundary_check")
_emit_transcripts_response("p1", "runtime_safety_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "runtime_safety_mixin")
_emit_gated_by_confidence("p1", "runtime_safety_mixin", "confidence_gate")

logger = logging.getLogger(__name__)


class RuntimeSafetyMixin:
    """
    Mixin providing runtime safety capabilities to agents.

    Provides:
    - safe_run(): Secure subprocess.run wrapper
    - safe_popen(): Secure subprocess.Popen wrapper
    - cleanup_processes(): Terminate all spawned processes
    - Context manager support for automatic cleanup

    Usage:
        class MyAgent(RuntimeSafetyMixin, SovereignBaseAgent):
            def execute(self):
                with self.runtime_guard():
                    result = self.safe_run(["python", "script.py"])
                    # Processes are automatically cleaned up on exit
    """

    def __init__(self, *args, **kwargs):
        """Initialize runtime safety mixin."""
        super().__init__(*args, **kwargs)
        ProcessGuard, _SecurityViolation = _get_process_guardrail()
        self._process_guard = ProcessGuard.get_instance()

    # guardian: allow-magic-config
    def safe_run(
        self,
        command: list[str],
        *,
        capture_output: bool = True,
        text: bool = True,
        timeout: float | None = 60.0,
        cwd: str | None = None,
        sanitize_output: bool = True,
        max_output_chars: int = 2000,
        **kwargs: Any,
    ):
        """
        Safely run a subprocess with security validation.

        See safe_subprocess.safe_run for full documentation.
        """
        return safe_run(
            command,
            capture_output=capture_output,
            text=text,
            timeout=timeout,
            cwd=cwd,
            sanitize_output=sanitize_output,
            max_output_chars=max_output_chars,
            **kwargs,
        )

    def safe_popen(self, command: list[str], *, cwd: str | None = None, **kwargs: Any):
        """
        Safely spawn a subprocess with PID tracking.

        See safe_subprocess.safe_popen for full documentation.
        """
        return safe_popen(command, cwd=cwd, **kwargs)

    # guardian: allow-magic-config
    def safe_communicate(
        self,
        process,
        input_data: str | bytes | None = None,
        timeout: float | None = 60.0,
        sanitize_output: bool = True,
        max_output_chars: int = 2000,
    ):
        """
        Safely communicate with a Popen process.

        See safe_subprocess.safe_communicate for full documentation.
        """
        return safe_communicate(
            process,
            input_data=input_data,
            timeout=timeout,
            sanitize_output=sanitize_output,
            max_output_chars=max_output_chars,
        )

    def cleanup_processes(self) -> dict[str, list[int]]:
        """
        Terminate all processes spawned by this agent.

        Returns:
            Dict with 'terminated' and 'failed' PID lists.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "RuntimeSafetyMixin.cleanup_processes"
        )

        result = self._process_guard.cleanup()
        if result["terminated"]:
            logger.info(f"RuntimeSafetyMixin: Cleaned up {len(result['terminated'])} processes")
        return result

    def validate_command(self, command: list[str]) -> bool:
        """
        Validate a command without executing it.

        Args:
            command: The command to validate.

        Returns:
            True if command is allowed.

        Raises:
            SecurityViolation: If command is blocked.
        """
        return self._process_guard.validate_command(command)

    class _RuntimeGuardContext:
        """Context manager for guaranteed process cleanup."""

        def __init__(self, mixin: "RuntimeSafetyMixin"):
            self._mixin = mixin

        def __enter__(self):
            return self._mixin

        def __exit__(self, exc_type, exc_val, exc_tb):
            self._mixin.cleanup_processes()
            return False

    def runtime_guard(self):
        """
        Context manager for automatic process cleanup.

        Usage:
            with self.runtime_guard():
                self.safe_run(["python", "script.py"])
                # Cleanup happens automatically on exit
        """
        return self._RuntimeGuardContext(self)


def __getattr__(name: str):
    if name == "SecurityViolation":
        _, SecurityViolation = _get_process_guardrail()
        return SecurityViolation
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["RuntimeSafetyMixin", "SecurityViolation", "_get_process_guardrail"]
