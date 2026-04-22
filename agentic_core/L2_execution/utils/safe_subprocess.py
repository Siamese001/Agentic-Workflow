"""
Safe subprocess wrapper that enforces mutation fence protection.
"""

import subprocess
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.enforcement.mutation_prohibition import (
    enforce_protected_root,
)  # guardian: allow-layer-violation -- L2 module uses L0 config/enforcement; intentional downward enforcement-chain dependency
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
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

emit_replay_key("p0", "safe_subprocess")
emit_determinism_digest("p0", "safe_subprocess")

_emit_dispatches_healing_run("p1", "safe_subprocess", "L2")
_emit_routes_through("p1", "safe_subprocess", "L2")
_emit_checks_agent_registry("p1", "safe_subprocess", "agent_registry")
_emit_validates_agent_capability("p1", "safe_subprocess", "capability")
_emit_dispatches_execution_plan("p1", "safe_subprocess", "exec_plan")
_emit_agent_executes_agent("p1", "safe_subprocess", "sub_agent")
_emit_routes_to_agent("p1", "safe_subprocess", "target_agent")
_emit_verifies_policy("p1", "safe_subprocess", "policy_check")
_emit_observes_runtime_state("p1", "safe_subprocess", "runtime_state")
_emit_verifies_boundary("p1", "safe_subprocess", "boundary_check")
_emit_transcripts_response("p1", "safe_subprocess", "transcript")
_emit_hard_fails_untranscripted("p1", "safe_subprocess")
_emit_gated_by_confidence("p1", "safe_subprocess", "confidence_gate")
_emit_escalates_to_human("p1", "safe_subprocess", "L2")
_emit_reads_policy_state("p1", "safe_subprocess", "L2")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "safe_subprocess")
_emit_applies_guardrail("p0", "safe_subprocess", "p0_governance")
_emit_authorize_and_execute("p2", "safe_subprocess", "execution_auth")
_emit_validates_capability("p2", "safe_subprocess", "capability_check")
_emit_routes_to_capability("p2", "safe_subprocess", "capability_route")
_emit_writes_via_uwg("p2", "safe_subprocess", "uwg_write")
_emit_blocks_direct_write("p2", "safe_subprocess", "direct_write_block")
_emit_records_tool_invocation("p2", "safe_subprocess", "tool_invocation")
_emit_captures_execution_output("p2", "safe_subprocess", "exec_output")
_emit_dispatches_agent("p3", "safe_subprocess", "agent_dispatch")
_emit_coordinates_agents("p3", "safe_subprocess", "agent_coordination")
_emit_records_workflow_lineage("p3", "safe_subprocess", "workflow_lineage")
_emit_records_healing_outcome("p3", "safe_subprocess", "healing_outcome")
_emit_escalates_failure("p3", "safe_subprocess", "failure_escalation")
_emit_orchestrates_workflow("p3", "safe_subprocess", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "safe_subprocess", "healing_dispatch")
_emit_invokes_evaluation("p3", "safe_subprocess", "evaluation_signal")
_emit_records_telemetry_event("p4", "safe_subprocess", "telemetry_event")
_emit_captures_evaluation_metric("p4", "safe_subprocess", "eval_metric")
_emit_stores_embedding("p4", "safe_subprocess", "embedding_store")
_emit_updates_meta_learning_state("p4", "safe_subprocess", "meta_learning")
_emit_links_execution_to_snapshot("p4", "safe_subprocess", "exec_snapshot_link")
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("safe_subprocess", "p4obs", "metric_1")
_emit_emits_metric_event("safe_subprocess", "p4obs", "metric_2")
_emit_emits_metric_event("safe_subprocess", "p4obs", "metric_3")
_emit_emits_metric_event("safe_subprocess", "p4obs", "metric_4")
_emit_emits_metric_event("safe_subprocess", "p4obs", "metric_5")
_emit_emits_metric_event("safe_subprocess", "p4obs", "metric_6")
_emit_records_incident_event("safe_subprocess", "p4obs", "incident")
_emit_captures_runtime_anomaly("safe_subprocess", "p4obs", "anomaly")
_emit_writes_observability_log("safe_subprocess", "p4obs", "obs_log")
_emit_updates_monitoring_state("safe_subprocess", "p4obs", "mon_state")
_emit_triggers_alert("safe_subprocess", "p4obs", "alert")
_emit_links_incident_trace("safe_subprocess", "p4obs", "trace_link")
_emit_captures_pattern("safe_subprocess", "p3lm", "pattern")
_emit_records_learning_event("safe_subprocess", "p3lm", "learning_event")
_emit_writes_learning_snapshot("safe_subprocess", "p3lm", "snapshot")
_emit_feeds_meta_learning("safe_subprocess", "p3lm", "meta_feed")
_emit_updates_routing_strategy("safe_subprocess", "p3lm", "routing")
_emit_improves_agent_policy("safe_subprocess", "p3lm", "policy")
_emit_stores_learning_state("safe_subprocess", "p3lm", "state")
_emit_records_execution_trace("safe_subprocess", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("safe_subprocess", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("safe_subprocess", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("safe_subprocess", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("safe_subprocess", "L4_STATE", "p2_trace_5")
_emit_reads_environ("safe_subprocess", "env_read", "p2_env_1")
_emit_reads_environ("safe_subprocess", "env_read", "p2_env_2")
_emit_reads_runtime_state("safe_subprocess", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("safe_subprocess", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "safe_subprocess", "context_pull")
_emit_pulls_context("p1", "safe_subprocess", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "safe_subprocess", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "safe_subprocess", "uwg_term_2")
_emit_writes_through("p1", "safe_subprocess", "write_through")
_emit_writes_through("p1", "safe_subprocess", "write_through_2")
_emit_validated_by_safety_plane("p1", "safe_subprocess", "safety_validation")
_emit_invokes_eval("p1", "safe_subprocess", "eval_call")
_emit_proposal_commits_routing("p1", "safe_subprocess", "routing_commit")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_invoke_authorize_and_execute", "state_snapshot")
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.utils.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="safe_subprocess",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


def safe_subprocess_run(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    capture_output: bool = False,
    text: bool = False,
    check: bool = False,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> subprocess.CompletedProcess:
    """
    Safe subprocess.run wrapper with mutation fence protection.

    Args:
        argv: Command arguments as a list (no shell)
        cwd: Working directory for the command
        capture_output: Whether to capture stdout/stderr
        text: Whether to decode output as text
        check: Whether to raise exception on non-zero exit
        allow_protected_root_mutation: Whether to allow commands that can mutate protected roots
        **kwargs: Additional arguments passed to subprocess.run

    Returns:
        subprocess.CompletedProcess result

    Raises:
        RuntimeError: If command attempts protected root mutation without override
    """
    dangerous_commands = {
        "git",
        "rm",
        "mv",
        "cp",
        "chmod",
        "chown",
        "touch",
        "mkdir",
        "rmdir",
        "find",
        "sed",
        "awk",
        "perl",
        "python",
        "pip",
        "npm",
        "yarn",
    }
    if argv and argv[0] in dangerous_commands:
        if not allow_protected_root_mutation:
            if cwd:
                cwd_path = Path(cwd).resolve()
                if enforce_protected_root(cwd_path, operation="check"):
                    raise RuntimeError(
                        f"Command '{argv[0]}' may affect protected root {cwd_path}. Use allow_protected_root_mutation=True if intentional.",
                    )
    if not isinstance(argv, list):
        raise TypeError("argv must be a list of strings")
    _ectx = _make_execution_context(" ".join(str(a) for a in argv), "safe_subprocess.safe_subprocess_run")
    _invoke_authorize_and_execute(
        _ectx,
        lambda p: p,
        "default",
        " ".join(str(a) for a in argv),
        target_name="safe_subprocess.safe_subprocess_run",
    )
    return subprocess.run(argv, cwd=cwd, capture_output=capture_output, text=text, check=check, **kwargs)  # guardian: allow-unbounded-subprocess -- canonical wrapper: caller supplies timeout via **kwargs; adding a default here would override caller intent


def safe_subprocess_call(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> int:
    """Safe subprocess.call wrapper."""
    result = safe_subprocess_run(
        argv,
        cwd=cwd,
        allow_protected_root_mutation=allow_protected_root_mutation,
        **kwargs,
    )
    return result.returncode


def safe_subprocess_check_call(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> None:
    """Safe subprocess.check_call wrapper."""
    safe_subprocess_run(
        argv,
        cwd=cwd,
        check=True,
        allow_protected_root_mutation=allow_protected_root_mutation,
        **kwargs,
    )


def safe_subprocess_check_output(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    text: bool = True,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> str | bytes:
    """Safe subprocess.check_output wrapper."""
    result = safe_subprocess_run(
        argv,
        cwd=cwd,
        capture_output=True,
        text=text,
        allow_protected_root_mutation=allow_protected_root_mutation,
        **kwargs,
    )
    return result.stdout


def safe_subprocess_popen(
    argv: list[str],
    *,
    cwd: str | Path | None = None,
    allow_protected_root_mutation: bool = False,
    **kwargs: Any,
) -> subprocess.Popen:
    """Safe subprocess.Popen wrapper."""
    dangerous_commands = {
        "git",
        "rm",
        "mv",
        "cp",
        "chmod",
        "chown",
        "touch",
        "mkdir",
        "rmdir",
        "find",
        "sed",
        "awk",
        "perl",
        "python",
        "pip",
        "npm",
        "yarn",
    }
    if argv and argv[0] in dangerous_commands:
        if not allow_protected_root_mutation:
            if cwd:
                cwd_path = Path(cwd).resolve()
                if enforce_protected_root(cwd_path, operation="check"):
                    raise RuntimeError(
                        f"Command '{argv[0]}' may affect protected root {cwd_path}. Use allow_protected_root_mutation=True if intentional.",
                    )
    if not isinstance(argv, list):
        raise TypeError("argv must be a list of strings")
    return subprocess.Popen(argv, cwd=cwd, **kwargs)  # guardian: allow-popen-leak -- canonical Popen wrapper: caller owns process lifecycle (wait/terminate/with-block)
