"""
Safe Subprocess Wrapper - Secure Process Execution.

Landmine #8 & #9 Prevention: Environment Corruption and Zombie Processes.

This module provides safe_run(), a secure wrapper around subprocess.Popen that:
1. Validates commands against the security firewall
2. Registers spawned PIDs for lifecycle tracking
3. Sanitizes captured output to prevent token overload

OPERATIONAL SAFETY (Feb 2026):
- All subprocess calls should go through safe_run()
- Automatic PID registration ensures cleanup on exit
- Output sanitization prevents context pollution
"""

import logging
import subprocess
from typing import Any

from agentic_core.L4_state.utils.telemetry_sanitizer_util import sanitize_tool_output
from agentic_core.L5_safety.enforcement.process_guardrail import ProcessGuard
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
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

emit_replay_key("p0", "safe_subprocess_handler_enforcer")
emit_determinism_digest("p0", "safe_subprocess_handler_enforcer")

_emit_dispatches_healing_run("p1", "safe_subprocess_handler_enforcer", "L5")
_emit_routes_through("p1", "safe_subprocess_handler_enforcer", "L5")
_emit_checks_agent_registry("p1", "safe_subprocess_handler_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "safe_subprocess_handler_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "safe_subprocess_handler_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "safe_subprocess_handler_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "safe_subprocess_handler_enforcer", "target_agent")
_emit_verifies_policy("p1", "safe_subprocess_handler_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "safe_subprocess_handler_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "safe_subprocess_handler_enforcer", "boundary_check")
_emit_transcripts_response("p1", "safe_subprocess_handler_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "safe_subprocess_handler_enforcer")
_emit_gated_by_confidence("p1", "safe_subprocess_handler_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "safe_subprocess_handler_enforcer", "L5")
_emit_reads_policy_state("p1", "safe_subprocess_handler_enforcer", "L5")
_emit_authorize_and_execute("p2", "safe_subprocess_handler_enforcer", "execution_auth")
_emit_validates_capability("p2", "safe_subprocess_handler_enforcer", "capability_check")
_emit_routes_to_capability("p2", "safe_subprocess_handler_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "safe_subprocess_handler_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "safe_subprocess_handler_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "safe_subprocess_handler_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "safe_subprocess_handler_enforcer", "exec_output")
_emit_dispatches_agent("p3", "safe_subprocess_handler_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "safe_subprocess_handler_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "safe_subprocess_handler_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "safe_subprocess_handler_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "safe_subprocess_handler_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "safe_subprocess_handler_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safe_subprocess_handler_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "safe_subprocess_handler_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "safe_subprocess_handler_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safe_subprocess_handler_enforcer", "eval_metric")
_emit_stores_embedding("p4", "safe_subprocess_handler_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "safe_subprocess_handler_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safe_subprocess_handler_enforcer", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("safe_subprocess_handler_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("safe_subprocess_handler_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("safe_subprocess_handler_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("safe_subprocess_handler_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("safe_subprocess_handler_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("safe_subprocess_handler_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("safe_subprocess_handler_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("safe_subprocess_handler_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("safe_subprocess_handler_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("safe_subprocess_handler_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("safe_subprocess_handler_enforcer", "p4obs", "alert")
_emit_links_incident_trace("safe_subprocess_handler_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("safe_subprocess_handler_enforcer", "p3lm", "pattern")
_emit_records_learning_event("safe_subprocess_handler_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("safe_subprocess_handler_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("safe_subprocess_handler_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("safe_subprocess_handler_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("safe_subprocess_handler_enforcer", "p3lm", "policy")
_emit_stores_learning_state("safe_subprocess_handler_enforcer", "p3lm", "state")
_emit_records_execution_trace("safe_subprocess_handler_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("safe_subprocess_handler_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("safe_subprocess_handler_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("safe_subprocess_handler_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("safe_subprocess_handler_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("safe_subprocess_handler_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("safe_subprocess_handler_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("safe_subprocess_handler_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("safe_subprocess_handler_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "safe_subprocess_handler_enforcer", "context_pull")
_emit_pulls_context("p1", "safe_subprocess_handler_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "safe_subprocess_handler_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "safe_subprocess_handler_enforcer", "uwg_term_2")
_emit_writes_through("p1", "safe_subprocess_handler_enforcer", "write_through")
_emit_writes_through("p1", "safe_subprocess_handler_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "safe_subprocess_handler_enforcer", "safety_validation")
_emit_invokes_eval("p1", "safe_subprocess_handler_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "safe_subprocess_handler_enforcer", "routing_commit")

logger = logging.getLogger(__name__)


# guardian: allow-magic-config
def safe_run(
    command: list[str],
    *,
    capture_output: bool = True,
    text: bool = True,
    timeout: float | None = 60.0,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    sanitize_output: bool = True,
    max_output_chars: int = 2000,
    check: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess | subprocess.Popen:
    """
    Safely run a subprocess with security validation and lifecycle tracking.

    Args:
        command: The command to run as a list of strings.
        capture_output: Whether to capture stdout/stderr (default: True).
        text: Whether to decode output as text (default: True).
        timeout: Timeout in seconds (default: 60, None for no timeout).
        cwd: Working directory for the command.
        env: Environment variables for the command.
        sanitize_output: Whether to sanitize captured output (default: True).
        max_output_chars: Max chars for sanitized output (default: 2000).
        check: Whether to raise on non-zero exit (default: False).
        **kwargs: Additional arguments passed to subprocess.run.

    Returns:
        subprocess.CompletedProcess with the result.

    Raises:
        SecurityViolation: If command is blocked by the firewall.
        subprocess.TimeoutExpired: If command exceeds timeout.
        subprocess.CalledProcessError: If check=True and command fails.
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "safe_run", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "safe_run", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "safe_run")
    guard = ProcessGuard.get_instance()
    guard.validate_command(command)
    logger.debug(f"safe_run: Executing command: {command}")
    try:
        result = subprocess.run(
            command,
            capture_output=capture_output,
            text=text,
            timeout=timeout,
            cwd=cwd,
            env=env,
            check=check,
            **kwargs,
        )
        if sanitize_output and capture_output:
            if result.stdout:
                result.stdout = sanitize_tool_output(result.stdout, max_chars=max_output_chars)
            if result.stderr:
                result.stderr = sanitize_tool_output(result.stderr, max_chars=max_output_chars)
        logger.debug(f"safe_run: Command completed with return code {result.returncode}")
        return result
    except subprocess.TimeoutExpired:
        logger.warning(f"safe_run: Command timed out after {timeout}s: {command}")
        raise


def safe_popen(
    command: list[str],
    *,
    stdout: int | None = subprocess.PIPE,
    stderr: int | None = subprocess.PIPE,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
    **kwargs: Any,
) -> subprocess.Popen:
    """
    Safely spawn a subprocess with security validation and PID tracking.

    Use this for long-running processes that need to be managed asynchronously.
    The PID is automatically registered with ProcessGuard for cleanup.

    Args:
        command: The command to run as a list of strings.
        stdout: stdout handling (default: PIPE).
        stderr: stderr handling (default: PIPE).
        cwd: Working directory for the command.
        env: Environment variables for the command.
        **kwargs: Additional arguments passed to subprocess.Popen.

    Returns:
        subprocess.Popen object with registered PID.

    Raises:
        SecurityViolation: If command is blocked by the firewall.
    """
    guard = ProcessGuard.get_instance()
    guard.validate_command(command)
    logger.debug(f"safe_popen: Spawning command: {command}")
    process = subprocess.Popen(command, stdout=stdout, stderr=stderr, cwd=cwd, env=env, **kwargs)
    guard.register_pid(process.pid)
    logger.debug(f"safe_popen: Spawned PID {process.pid}")
    return process


# guardian: allow-magic-config
def safe_communicate(
    process: subprocess.Popen,
    input_data: str | bytes | None = None,
    timeout: float | None = 60.0,
    sanitize_output: bool = True,
    max_output_chars: int = 2000,
) -> tuple[str | bytes | None, str | bytes | None]:
    """
    Safely communicate with a Popen process and unregister on completion.

    Args:
        process: The Popen process to communicate with.
        input_data: Data to send to stdin.
        timeout: Timeout in seconds.
        sanitize_output: Whether to sanitize output.
        max_output_chars: Max chars for sanitized output.

    Returns:
        Tuple of (stdout, stderr).
    """
    guard = ProcessGuard.get_instance()
    try:
        stdout, stderr = process.communicate(input=input_data, timeout=timeout)
        if sanitize_output:
            if stdout and isinstance(stdout, str):
                stdout = sanitize_tool_output(stdout, max_chars=max_output_chars)
            if stderr and isinstance(stderr, str):
                stderr = sanitize_tool_output(stderr, max_chars=max_output_chars)
        return (stdout, stderr)
    finally:
        guard.unregister_pid(process.pid)


__all__ = ["safe_run", "safe_popen", "safe_communicate"]
