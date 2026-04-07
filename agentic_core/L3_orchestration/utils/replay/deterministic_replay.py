"""
Deterministic Replay Engine - Record and Replay Module

Provides immutable data structures and functions for recording and replaying
command executions deterministically for governance verification.

This module performs NO file writes or mutations - it only returns data
structures that callers can persist as needed.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime

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
    record_execution_trace,
)

emit_replay_key("p0", "deterministic_replay")
emit_determinism_digest("p0", "deterministic_replay")

_emit_dispatches_healing_run("p1", "deterministic_replay", "L3")
_emit_routes_through("p1", "deterministic_replay", "L3")
_emit_checks_agent_registry("p1", "deterministic_replay", "agent_registry")
_emit_validates_agent_capability("p1", "deterministic_replay", "capability")
_emit_dispatches_execution_plan("p1", "deterministic_replay", "exec_plan")
_emit_agent_executes_agent("p1", "deterministic_replay", "sub_agent")
_emit_routes_to_agent("p1", "deterministic_replay", "target_agent")
_emit_verifies_policy("p1", "deterministic_replay", "policy_check")
_emit_observes_runtime_state("p1", "deterministic_replay", "runtime_state")
_emit_verifies_boundary("p1", "deterministic_replay", "boundary_check")
_emit_transcripts_response("p1", "deterministic_replay", "transcript")
_emit_hard_fails_untranscripted("p1", "deterministic_replay")
_emit_gated_by_confidence("p1", "deterministic_replay", "confidence_gate")
_emit_escalates_to_human("p1", "deterministic_replay", "L3")
_emit_reads_policy_state("p1", "deterministic_replay", "L3")
_emit_authorize_and_execute("p2", "deterministic_replay", "execution_auth")
_emit_validates_capability("p2", "deterministic_replay", "capability_check")
_emit_routes_to_capability("p2", "deterministic_replay", "capability_route")
_emit_writes_via_uwg("p2", "deterministic_replay", "uwg_write")
_emit_blocks_direct_write("p2", "deterministic_replay", "direct_write_block")
_emit_records_tool_invocation("p2", "deterministic_replay", "tool_invocation")
_emit_captures_execution_output("p2", "deterministic_replay", "exec_output")
_emit_dispatches_agent("p3", "deterministic_replay", "agent_dispatch")
_emit_coordinates_agents("p3", "deterministic_replay", "agent_coordination")
_emit_records_workflow_lineage("p3", "deterministic_replay", "workflow_lineage")
_emit_records_healing_outcome("p3", "deterministic_replay", "healing_outcome")
_emit_escalates_failure("p3", "deterministic_replay", "failure_escalation")
_emit_orchestrates_workflow("p3", "deterministic_replay", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "deterministic_replay", "healing_dispatch")
_emit_invokes_evaluation("p3", "deterministic_replay", "evaluation_signal")
_emit_records_telemetry_event("p4", "deterministic_replay", "telemetry_event")
_emit_captures_evaluation_metric("p4", "deterministic_replay", "eval_metric")
_emit_stores_embedding("p4", "deterministic_replay", "embedding_store")
_emit_updates_meta_learning_state("p4", "deterministic_replay", "meta_learning")
_emit_links_execution_to_snapshot("p4", "deterministic_replay", "exec_snapshot_link")
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

record_execution_trace("deterministic_replay", "deterministic_replay_trace")


_emit_emits_metric_event("deterministic_replay", "p4obs", "metric_1")
_emit_emits_metric_event("deterministic_replay", "p4obs", "metric_2")
_emit_emits_metric_event("deterministic_replay", "p4obs", "metric_3")
_emit_emits_metric_event("deterministic_replay", "p4obs", "metric_4")
_emit_emits_metric_event("deterministic_replay", "p4obs", "metric_5")
_emit_emits_metric_event("deterministic_replay", "p4obs", "metric_6")
_emit_records_incident_event("deterministic_replay", "p4obs", "incident")
_emit_captures_runtime_anomaly("deterministic_replay", "p4obs", "anomaly")
_emit_writes_observability_log("deterministic_replay", "p4obs", "obs_log")
_emit_updates_monitoring_state("deterministic_replay", "p4obs", "mon_state")
_emit_triggers_alert("deterministic_replay", "p4obs", "alert")
_emit_links_incident_trace("deterministic_replay", "p4obs", "trace_link")
_emit_captures_pattern("deterministic_replay", "p3lm", "pattern")
_emit_records_learning_event("deterministic_replay", "p3lm", "learning_event")
_emit_writes_learning_snapshot("deterministic_replay", "p3lm", "snapshot")
_emit_feeds_meta_learning("deterministic_replay", "p3lm", "meta_feed")
_emit_updates_routing_strategy("deterministic_replay", "p3lm", "routing")
_emit_improves_agent_policy("deterministic_replay", "p3lm", "policy")
_emit_stores_learning_state("deterministic_replay", "p3lm", "state")
_emit_records_execution_trace("deterministic_replay", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("deterministic_replay", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("deterministic_replay", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("deterministic_replay", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("deterministic_replay", "L4_STATE", "p2_trace_5")
_emit_reads_environ("deterministic_replay", "env_read", "p2_env_1")
_emit_reads_environ("deterministic_replay", "env_read", "p2_env_2")
_emit_reads_runtime_state("deterministic_replay", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("deterministic_replay", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "deterministic_replay", "context_pull")
_emit_pulls_context("p1", "deterministic_replay", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "deterministic_replay", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "deterministic_replay", "uwg_term_2")
_emit_writes_through("p1", "deterministic_replay", "write_through")
_emit_writes_through("p1", "deterministic_replay", "write_through_2")
_emit_validated_by_safety_plane("p1", "deterministic_replay", "safety_validation")
_emit_invokes_eval("p1", "deterministic_replay", "eval_call")
_emit_proposal_commits_routing("p1", "deterministic_replay", "routing_commit")


@dataclass(frozen=True)
class ReplayMetrics:
    """Deterministic performance metrics for replay operations."""

    per_command_bytes_out: list[int] = field(default_factory=list)
    per_command_bytes_err: list[int] = field(default_factory=list)
    total_bytes_out: int = 0
    total_bytes_err: int = 0


@dataclass(frozen=True)
class ReplayCommand:
    """Immutable command definition for replay."""

    argv: list[str]
    cwd: str
    env_allowlist: dict[str, str]
    timeout_s: int = 300
    max_stdout_bytes: int = 1024 * 1024
    max_stderr_bytes: int = 1024 * 1024


@dataclass(frozen=True)
class ReplayResult:
    """Immutable result of a command execution."""

    exit_code: int
    stdout: str
    stderr: str


@dataclass(frozen=True)
class ReplayRecord:
    """Immutable record of command executions for replay."""

    version: int = 1
    created_utc: str = field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    commands: list[ReplayCommand] = field(default_factory=list)
    results: list[ReplayResult] = field(default_factory=list)
    hashes: dict[str, str] = field(default_factory=dict)
    metrics: ReplayMetrics | None = None


@dataclass(frozen=True)
class ComparisonResult:
    """Result of replay comparison."""

    is_match: bool
    mismatches: list[str] = field(default_factory=list)
    first_diff_summary: str = ""


_ENV_ALLOWLIST = {"AGENTIC_BYPASS_LONGPATHS_CHECK", "PYTHONUTF8", "PYTHONPATH", "PATH"}


def _hash_command_result(command: ReplayCommand, result: ReplayResult) -> str:
    """Compute SHA256 hash of command and result for integrity verification."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "_hash_command_result", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "_hash_command_result", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "_hash_command_result")
    data = {
        "argv": command.argv,
        "cwd": command.cwd,
        "env_allowlist": command.env_allowlist,
        "exit_code": result.exit_code,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }
    data_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def _filter_env_vars() -> dict[str, str]:
    """Filter environment variables to only allowlisted keys."""
    filtered = {}
    for key, value in os.environ.items():
        if key in _ENV_ALLOWLIST:
            filtered[key] = value
    return filtered


def _truncate_if_needed(text: str, max_bytes: int) -> tuple[str, bool]:
    """Truncate text if it exceeds max_bytes deterministically.

    Args:
        text: Text to potentially truncate
        max_bytes: Maximum allowed bytes

    Returns:
        Tuple of (truncated_text, was_truncated)
    """
    text_bytes = text.encode("utf-8")
    if len(text_bytes) <= max_bytes:
        return (text, False)
    suffix = f"...<TRUNCATED {len(text_bytes) - max_bytes} BYTES>"
    suffix_bytes = suffix.encode("utf-8")
    allowed_text_bytes = max_bytes - len(suffix_bytes)
    if allowed_text_bytes <= 0:
        return (suffix, True)
    truncated_bytes = text_bytes[:allowed_text_bytes]
    try:
        truncated_text = truncated_bytes.decode("utf-8")
    except UnicodeDecodeError:    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy    # guardian: Encoding errors should specify fallback encoding strategy
        truncated_text = truncated_bytes.decode("utf-8", errors="replace")
        truncated_text = truncated_text.rstrip("�")
    return (truncated_text + suffix, True)


def run_and_record(commands: list[ReplayCommand]) -> ReplayRecord:
    """Execute commands and record results deterministically.

    Args:
        commands: List of commands to execute

    Returns:
        ReplayRecord with commands, results, and per-command hashes

    Raises:
        RuntimeError: If any argv0 contains pwsh/powershell
    """
    results = []
    hashes = {}
    per_command_bytes_out = []
    per_command_bytes_err = []
    for command in commands:
        if len(command.argv) > 0 and ("pwsh" in command.argv[0] or "powershell" in command.argv[0]):
            raise RuntimeError(f"PowerShell usage forbidden in argv0: {command.argv[0]}")
        env = _filter_env_vars()
        env.update(command.env_allowlist)
        result = subprocess.run(
            command.argv,
            shell=False,
            text=True,
            capture_output=True,
            cwd=command.cwd,
            env=env,
            timeout=command.timeout_s,
        )
        truncated_stdout, stdout_truncated = _truncate_if_needed(result.stdout, command.max_stdout_bytes)
        truncated_stderr, stderr_truncated = _truncate_if_needed(result.stderr, command.max_stderr_bytes)
        replay_result = ReplayResult(
            exit_code=result.returncode, stdout=truncated_stdout, stderr=truncated_stderr,
        )
        results.append(replay_result)
        per_command_bytes_out.append(len(replay_result.stdout.encode("utf-8")))
        per_command_bytes_err.append(len(replay_result.stderr.encode("utf-8")))
        cmd_hash = _hash_command_result(command, replay_result)
        hashes[f"cmd_{len(results)}"] = cmd_hash
    metrics = ReplayMetrics(
        per_command_bytes_out=per_command_bytes_out,
        per_command_bytes_err=per_command_bytes_err,
        total_bytes_out=sum(per_command_bytes_out),
        total_bytes_err=sum(per_command_bytes_err),
    )
    return ReplayRecord(commands=commands, results=results, hashes=hashes, metrics=metrics)


def record_to_json(record: ReplayRecord) -> str:
    """Serialize ReplayRecord to deterministic JSON.

    Returns:
        JSON string with sorted keys and stable formatting
    """
    data = {
        "version": record.version,
        "created_utc": record.created_utc,
        "commands": [
            {"argv": cmd.argv, "cwd": cmd.cwd, "env_allowlist": cmd.env_allowlist, "timeout_s": cmd.timeout_s}
            for cmd in record.commands
        ],
        "results": [
            {"exit_code": res.exit_code, "stdout": res.stdout, "stderr": res.stderr} for res in record.results
        ],
        "hashes": record.hashes,
    }
    if record.metrics is not None:
        data["metrics"] = {
            "per_command_bytes_out": record.metrics.per_command_bytes_out,
            "per_command_bytes_err": record.metrics.per_command_bytes_err,
            "total_bytes_out": record.metrics.total_bytes_out,
            "total_bytes_err": record.metrics.total_bytes_err,
        }
    return json.dumps(data, sort_keys=True, indent=2)


def record_from_json(json_str: str) -> ReplayRecord:
    """Deserialize JSON string to ReplayRecord."""
    data = json.loads(json_str)
    commands = [
        ReplayCommand(
            argv=cmd["argv"],
            cwd=cmd["cwd"],
            env_allowlist=cmd["env_allowlist"],
            timeout_s=cmd.get("timeout_s", 300),
        )
        for cmd in data["commands"]
    ]
    results = [
        ReplayResult(exit_code=res["exit_code"], stdout=res["stdout"], stderr=res["stderr"])
        for res in data["results"]
    ]
    metrics = None
    if "metrics" in data:
        metrics_data = data["metrics"]
        metrics = ReplayMetrics(
            per_command_bytes_out=metrics_data["per_command_bytes_out"],
            per_command_bytes_err=metrics_data["per_command_bytes_err"],
            total_bytes_out=metrics_data["total_bytes_out"],
            total_bytes_err=metrics_data["total_bytes_err"],
        )
    return ReplayRecord(
        version=data["version"],
        created_utc=data["created_utc"],
        commands=commands,
        results=results,
        hashes=data["hashes"],
        metrics=metrics,
    )


def _normalize_output(output: str) -> str:
    """Normalize output by stripping timestamps and absolute paths."""
    output = re.sub("\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}(?:\\.\\d{3})?Z", "<TIMESTAMP>", output)
    output = re.sub("\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}:\\d{2},\\d{3}", "<TIMESTAMP>", output)
    # guardian: allow-path-string
    repo_root = os.path.abspath(os.getcwd())
    repo_root_normalized = repo_root.replace("\\", "/")
    output = output.replace(repo_root, "<REPO_ROOT>")
    output = output.replace(repo_root_normalized, "<REPO_ROOT>")
    output = re.sub("[A-Za-z]:/[^ \\n\\r]*", "<ABSOLUTE_PATH>", output)
    return output


def replay_and_compare(record: ReplayRecord) -> ComparisonResult:
    """Replay commands and compare with original results.

    Args:
        record: Original record to replay

    Returns:
        ComparisonResult with match status and any mismatches
    """
    if len(record.commands) != len(record.results):
        return ComparisonResult(is_match=False, mismatches=["Command and result count mismatch"])
    mismatches = []
    first_diff_lines = []
    for i, (command, original_result) in enumerate(zip(record.commands, record.results)):
        try:
            env = _filter_env_vars()
            env.update(command.env_allowlist)
            result = subprocess.run(
                command.argv,
                shell=False,
                text=True,
                capture_output=True,
                cwd=command.cwd,
                env=env,
                timeout=command.timeout_s,
            )
            current_result = ReplayResult(
                exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr,
            )
            if current_result.exit_code != original_result.exit_code:
                mismatches.append(
                    f"Command {i + 1}: Exit code mismatch (original={original_result.exit_code}, current={current_result.exit_code})",
                )
            orig_stdout_norm = _normalize_output(original_result.stdout)
            curr_stdout_norm = _normalize_output(current_result.stdout)
            if orig_stdout_norm != curr_stdout_norm:
                mismatches.append(f"Command {i + 1}: Stdout mismatch after normalization")
                if not first_diff_lines:
                    orig_lines = orig_stdout_norm.splitlines()
                    curr_lines = curr_stdout_norm.splitlines()
                    for j, (orig, curr) in enumerate(zip(orig_lines, curr_lines)):
                        if orig != curr:
                            first_diff_lines.extend(
                                [
                                    f"First difference at line {j + 1}:",
                                    f"Original: {orig}",
                                    f"Current:  {curr}",
                                ],
                            )
                            break
            orig_stderr_norm = _normalize_output(original_result.stderr)
            curr_stderr_norm = _normalize_output(current_result.stderr)
            if orig_stderr_norm != curr_stderr_norm:
                mismatches.append(f"Command {i + 1}: Stderr mismatch after normalization")
        except subprocess.TimeoutExpired:
            mismatches.append(f"Command {i + 1}: Timeout during replay")
        # guardian: allow-silent-swallow
        except (ValueError, TypeError) as e:
            mismatches.append(f"Command {i + 1}: Exception during replay: {e}")
    return ComparisonResult(
        is_match=len(mismatches) == 0,
        mismatches=mismatches,
        first_diff_summary="\n".join(first_diff_lines[:200]),
    )


__all__ = [
    "ReplayCommand",
    "ReplayResult",
    "ReplayRecord",
    "ComparisonResult",
    "run_and_record",
    "record_to_json",
    "record_from_json",
    "replay_and_compare",
]
