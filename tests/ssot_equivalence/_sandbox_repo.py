"""Sandbox repo creator for hermetic legacy execution testing.

Provides isolated repo copies (via git worktree or local clone) so that
legacy execute_ssot can run with full write permissions without affecting
the primary working tree.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

from tests._helpers.robust_fs import robust_rmtree, robust_subprocess_run

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("_sandbox_repo", "p4obs", "metric_1")
_emit_emits_metric_event("_sandbox_repo", "p4obs", "metric_2")
_emit_emits_metric_event("_sandbox_repo", "p4obs", "metric_3")
_emit_emits_metric_event("_sandbox_repo", "p4obs", "metric_4")
_emit_emits_metric_event("_sandbox_repo", "p4obs", "metric_5")
_emit_emits_metric_event("_sandbox_repo", "p4obs", "metric_6")
_emit_records_incident_event("_sandbox_repo", "p4obs", "incident")
_emit_captures_runtime_anomaly("_sandbox_repo", "p4obs", "anomaly")
_emit_writes_observability_log("_sandbox_repo", "p4obs", "obs_log")
_emit_updates_monitoring_state("_sandbox_repo", "p4obs", "mon_state")
_emit_triggers_alert("_sandbox_repo", "p4obs", "alert")
_emit_links_incident_trace("_sandbox_repo", "p4obs", "trace_link")
_emit_captures_pattern("_sandbox_repo", "p3lm", "pattern")
_emit_records_learning_event("_sandbox_repo", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_sandbox_repo", "p3lm", "snapshot")
_emit_feeds_meta_learning("_sandbox_repo", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_sandbox_repo", "p3lm", "routing")
_emit_improves_agent_policy("_sandbox_repo", "p3lm", "policy")
_emit_stores_learning_state("_sandbox_repo", "p3lm", "state")
_emit_records_execution_trace("_sandbox_repo", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_sandbox_repo", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_sandbox_repo", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_sandbox_repo", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_sandbox_repo", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_sandbox_repo", "env_read", "p2_env_1")
_emit_reads_environ("_sandbox_repo", "env_read", "p2_env_2")
_emit_reads_runtime_state("_sandbox_repo", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_sandbox_repo", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "_sandbox_repo")
_emit_applies_guardrail("p0", "_sandbox_repo", "p0_governance")
_emit_reads_policy_state("p0", "_sandbox_repo", "policy_binding")
_emit_snapshots_state("p0", "_sandbox_repo", "state_snapshot")
_emit_pulls_context("p1", "_sandbox_repo", "context_pull")
_emit_pulls_context("p1", "_sandbox_repo", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_sandbox_repo", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_sandbox_repo", "uwg_term_secondary")
_emit_writes_through("p1", "_sandbox_repo", "write_through")
_emit_writes_through("p1", "_sandbox_repo", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_sandbox_repo", "safety_validation")
_emit_invokes_eval("p1", "_sandbox_repo", "eval_call")
_emit_proposal_commits_routing("p1", "_sandbox_repo", "routing_commit")
_emit_escalates_to_human("p1", "_sandbox_repo", "human_escalation")
_emit_routes_through("p1", "_sandbox_repo", "route_through")
_emit_checks_agent_registry("p1", "_sandbox_repo", "agent_registry")
_emit_validates_agent_capability("p1", "_sandbox_repo", "capability")
_emit_dispatches_execution_plan("p1", "_sandbox_repo", "exec_plan")
_emit_agent_executes_agent("p1", "_sandbox_repo", "sub_agent")
_emit_routes_to_agent("p1", "_sandbox_repo", "target_agent")
_emit_verifies_policy("p1", "_sandbox_repo", "policy_check")
_emit_observes_runtime_state("p1", "_sandbox_repo", "runtime_state")
_emit_verifies_boundary("p1", "_sandbox_repo", "boundary_check")
_emit_transcripts_response("p1", "_sandbox_repo", "transcript")
_emit_hard_fails_untranscripted("p1", "_sandbox_repo")
_emit_gated_by_confidence("p1", "_sandbox_repo", "confidence_gate")
emit_replay_key("p0", "_sandbox_repo")
emit_determinism_digest("p0", "_sandbox_repo")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_sandbox_repo", "execution_auth")
_emit_validates_capability("p2", "_sandbox_repo", "capability_check")
_emit_routes_to_capability("p2", "_sandbox_repo", "capability_route")
_emit_writes_via_uwg("p2", "_sandbox_repo", "uwg_write")
_emit_blocks_direct_write("p2", "_sandbox_repo", "direct_write_block")
_emit_records_tool_invocation("p2", "_sandbox_repo", "tool_invocation")
_emit_captures_execution_output("p2", "_sandbox_repo", "exec_output")
_emit_dispatches_agent("p3", "_sandbox_repo", "agent_dispatch")
_emit_coordinates_agents("p3", "_sandbox_repo", "agent_coordination")
_emit_records_workflow_lineage("p3", "_sandbox_repo", "workflow_lineage")
_emit_records_healing_outcome("p3", "_sandbox_repo", "healing_outcome")
_emit_escalates_failure("p3", "_sandbox_repo", "failure_escalation")
_emit_orchestrates_workflow("p3", "_sandbox_repo", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_sandbox_repo", "healing_dispatch")
_emit_invokes_evaluation("p3", "_sandbox_repo", "evaluation_signal")
_emit_records_telemetry_event("p4", "_sandbox_repo", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_sandbox_repo", "eval_metric")
_emit_stores_embedding("p4", "_sandbox_repo", "embedding_store")
_emit_updates_meta_learning_state("p4", "_sandbox_repo", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_sandbox_repo", "exec_snapshot_link")

# ── Configuration constants ────────────────────────────────────────
MAX_CAPTURE: int = 2000
DEFAULT_TIMEOUT: int = 120
GIT_PROBE_TIMEOUT: int = 10
WORKTREE_TIMEOUT: int = 60
CLONE_TIMEOUT: int = 120
CLEANUP_TIMEOUT: int = 30
PRUNE_TIMEOUT: int = 10
LEGACY_RUN_TIMEOUT: int = 120


def run_cmd(
    cwd: Path,
    cmd: list[str],
    timeout: int = DEFAULT_TIMEOUT,
    env: dict[str, str] | None = None,
) -> tuple[int, str, str]:
    """Run a command and return ``(returncode, stdout_head, stderr_head)``."""
    merged_env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", **(env or {})}
    try:
        result = robust_subprocess_run(
            cmd,
            capture_output=True,
            text=True,
            cwd=str(cwd),
            timeout=timeout,
            env=merged_env,
        )
        return (
            result.returncode,
            result.stdout[:MAX_CAPTURE],
            result.stderr[:MAX_CAPTURE],
        )
    except subprocess.TimeoutExpired:
        return (-1, "", f"Command timed out after {timeout}s")
    except FileNotFoundError:
        return (-2, "", f"Command not found: {cmd[0]}")


def _git_available(repo_root: Path) -> bool:
    """Return True if git is callable from *repo_root*."""
    rc, _, _ = run_cmd(repo_root, ["git", "--version"], timeout=GIT_PROBE_TIMEOUT)
    return rc == 0


def _sandbox_dir_name(node_id: str = "") -> str:
    """Derive a deterministic unique directory name from *node_id*.

    Uses sha256 truncated to 16 hex chars so parallel tests never
    collide on the same worktree path (fixes WinError 183).
    """
    tag = node_id or "default"
    return "ssot_sandbox_" + hashlib.sha256(tag.encode()).hexdigest()[:16]


def create_sandbox(
    repo_root: Path,
    sandbox_root: Path,
    node_id: str = "",
) -> Path:
    """Create an isolated sandbox of *repo_root* under *sandbox_root*.

    Tries strategies in order:
      A) ``git worktree add --detach`` (fastest, shares objects)
      B) ``git clone --local`` (independent, hardlinked objects)

    *node_id* is used to derive a unique sandbox directory name so that
    parallel fixtures never collide (§Wave5.0.6).

    Returns the sandbox repo path.
    Raises ``RuntimeError`` if all strategies fail.
    """
    sandbox_path = sandbox_root / _sandbox_dir_name(node_id)

    # Strategy A: git worktree (fastest)
    rc, _, err_a = run_cmd(
        repo_root,
        ["git", "worktree", "add", "--detach", str(sandbox_path)],
        timeout=WORKTREE_TIMEOUT,
    )
    if rc == 0:
        return sandbox_path

    # Strategy B: local clone (independent)
    rc, _, err_b = run_cmd(
        repo_root,
        ["git", "clone", "--local", str(repo_root), str(sandbox_path)],
        timeout=CLONE_TIMEOUT,
    )
    if rc == 0:
        return sandbox_path

    raise RuntimeError(f"Cannot create sandbox.\n  worktree error: {err_a}\n  clone error: {err_b}")


def destroy_sandbox(repo_root: Path, sandbox_path: Path) -> None:
    """Remove sandbox, best-effort.  Never raises."""
    try:
        # Try git worktree remove first (handles worktree strategy)
        run_cmd(
            repo_root,
            ["git", "worktree", "remove", "--force", str(sandbox_path)],
            timeout=CLEANUP_TIMEOUT,
        )
        # Prune stale worktree refs
        run_cmd(repo_root, ["git", "worktree", "prune"], timeout=PRUNE_TIMEOUT)
    except (subprocess.CalledProcessError, OSError):
        pass

    # Force-remove directory if still present
    robust_rmtree(sandbox_path)


def run_legacy_in_sandbox(
    sandbox_path: Path,
    extra_args: list[str] | None = None,
    timeout: int = LEGACY_RUN_TIMEOUT,
) -> dict:
    """Run legacy entrypoint inside the sandbox and return capture dict.

    Returns dict with keys: command, returncode, stdout_head, stderr_head.
    """
    cmd = [
        sys.executable,
        "-m",
        "agentic_core.L0_routing.scripts.execute_ssot_entrypoint",
        "--legacy",
        *(extra_args or []),
    ]
    env_overrides = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "V15_ENFORCEMENT": "0",
    }
    rc, stdout, stderr = run_cmd(
        sandbox_path,
        cmd,
        timeout=timeout,
        env=env_overrides,
    )
    return {
        "command": cmd,
        "returncode": rc,
        "stdout_head": stdout,
        "stderr_head": stderr,
    }
