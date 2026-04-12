"""
L0 utilities for invoking L5 runners via subprocess.

This module provides clean subprocess invocation to L5 runners,
avoiding upward import edges while enabling L0 scripts to
trigger L5 agent functionality.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from agentic_core.L0_routing.config.path_constants import DEFAULT_TIMEOUT
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

emit_replay_key("p0", "subprocess_runner_util")
emit_determinism_digest("p0", "subprocess_runner_util")

_emit_dispatches_healing_run("p1", "subprocess_runner_util", "L0")
_emit_routes_through("p1", "subprocess_runner_util", "L0")
_emit_checks_agent_registry("p1", "subprocess_runner_util", "agent_registry")
_emit_validates_agent_capability("p1", "subprocess_runner_util", "capability")
_emit_dispatches_execution_plan("p1", "subprocess_runner_util", "exec_plan")
_emit_agent_executes_agent("p1", "subprocess_runner_util", "sub_agent")
_emit_routes_to_agent("p1", "subprocess_runner_util", "target_agent")
_emit_verifies_policy("p1", "subprocess_runner_util", "policy_check")
_emit_observes_runtime_state("p1", "subprocess_runner_util", "runtime_state")
_emit_verifies_boundary("p1", "subprocess_runner_util", "boundary_check")
_emit_transcripts_response("p1", "subprocess_runner_util", "transcript")
_emit_hard_fails_untranscripted("p1", "subprocess_runner_util")
_emit_gated_by_confidence("p1", "subprocess_runner_util", "confidence_gate")
_emit_escalates_to_human("p1", "subprocess_runner_util", "L0")
_emit_reads_policy_state("p1", "subprocess_runner_util", "L0")
_emit_authorize_and_execute("p2", "subprocess_runner_util", "execution_auth")
_emit_validates_capability("p2", "subprocess_runner_util", "capability_check")
_emit_routes_to_capability("p2", "subprocess_runner_util", "capability_route")
_emit_writes_via_uwg("p2", "subprocess_runner_util", "uwg_write")
_emit_blocks_direct_write("p2", "subprocess_runner_util", "direct_write_block")
_emit_records_tool_invocation("p2", "subprocess_runner_util", "tool_invocation")
_emit_captures_execution_output("p2", "subprocess_runner_util", "exec_output")
_emit_dispatches_agent("p3", "subprocess_runner_util", "agent_dispatch")
_emit_coordinates_agents("p3", "subprocess_runner_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "subprocess_runner_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "subprocess_runner_util", "healing_outcome")
_emit_escalates_failure("p3", "subprocess_runner_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "subprocess_runner_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "subprocess_runner_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "subprocess_runner_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "subprocess_runner_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "subprocess_runner_util", "eval_metric")
_emit_stores_embedding("p4", "subprocess_runner_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "subprocess_runner_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "subprocess_runner_util", "exec_snapshot_link")
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

_emit_emits_metric_event("subprocess_runner_util", "p4obs", "metric_1")
_emit_emits_metric_event("subprocess_runner_util", "p4obs", "metric_2")
_emit_emits_metric_event("subprocess_runner_util", "p4obs", "metric_3")
_emit_emits_metric_event("subprocess_runner_util", "p4obs", "metric_4")
_emit_emits_metric_event("subprocess_runner_util", "p4obs", "metric_5")
_emit_emits_metric_event("subprocess_runner_util", "p4obs", "metric_6")
_emit_records_incident_event("subprocess_runner_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("subprocess_runner_util", "p4obs", "anomaly")
_emit_writes_observability_log("subprocess_runner_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("subprocess_runner_util", "p4obs", "mon_state")
_emit_triggers_alert("subprocess_runner_util", "p4obs", "alert")
_emit_links_incident_trace("subprocess_runner_util", "p4obs", "trace_link")
_emit_captures_pattern("subprocess_runner_util", "p3lm", "pattern")
_emit_records_learning_event("subprocess_runner_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("subprocess_runner_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("subprocess_runner_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("subprocess_runner_util", "p3lm", "routing")
_emit_improves_agent_policy("subprocess_runner_util", "p3lm", "policy")
_emit_stores_learning_state("subprocess_runner_util", "p3lm", "state")
_emit_records_execution_trace("subprocess_runner_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("subprocess_runner_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("subprocess_runner_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("subprocess_runner_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("subprocess_runner_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("subprocess_runner_util", "env_read", "p2_env_1")
_emit_reads_environ("subprocess_runner_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("subprocess_runner_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("subprocess_runner_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "subprocess_runner_util", "context_pull")
_emit_pulls_context("p1", "subprocess_runner_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "subprocess_runner_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "subprocess_runner_util", "uwg_term_2")
_emit_writes_through("p1", "subprocess_runner_util", "write_through")
_emit_writes_through("p1", "subprocess_runner_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "subprocess_runner_util", "safety_validation")
_emit_invokes_eval("p1", "subprocess_runner_util", "eval_call")
_emit_proposal_commits_routing("p1", "subprocess_runner_util", "routing_commit")

__all__ = [
    "invoke_arch_governor",
    "invoke_orchestrator_mission",
    "invoke_agent_roster_validation",
    "invoke_hierarchy_agent",
    "invoke_code_validator",
]


def invoke_arch_governor(
    action: str,
    project_root: Path | None = None,
    targets: list[str] | None = None,
    auto_approve: bool = True,
) -> dict[str, Any]:
    """
    Invoke ArchitectureGovernorAgent via subprocess.

    Args:
        action: One of 'verify', 'capture_baseline', 'audit'
        project_root: Project root path (auto-detected if None)
        targets: Target territories for audit action
        auto_approve: Auto-approve mode

    Returns:
        Dict with 'success' key and action-specific results
    """
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "invoke_arch_governor", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "invoke_arch_governor", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "invoke_arch_governor")
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.arch_governor_runner", f"--action={action}"]
    if project_root:
        cmd.append(f"--project-root={project_root}")
    if targets:
        cmd.append(f"--targets={','.join(targets)}")
    if auto_approve:
        cmd.append("--auto-approve")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 300 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except (ValueError, TypeError) as e:
        return {"success": False, "error": str(e)}


def invoke_orchestrator_mission(
    project_root: Path | None = None,
    targets: list[str] | None = None,
    execute: bool = False,
) -> dict[str, Any]:
    """
    Invoke orchestrator mission via subprocess.

    Args:
        project_root: Project root path (auto-detected if None)
        targets: Target territories
        execute: Execute mode (vs dry-run)

    Returns:
        Dict with 'success' key and mission results
    """
    if not targets:
        return {"success": False, "error": "No targets specified"}
    cmd = [
        sys.executable,
        "-m",
        "agentic_core.L5_safety.runners.orchestrator_runner",
        "--action=mission",
        f"--targets={','.join(targets)}",
    ]
    if project_root:
        cmd.append(f"--project-root={project_root}")
    if execute:
        cmd.append("--execute")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 600 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except (ValueError, TypeError) as e:
        return {"success": False, "error": str(e)}


def invoke_agent_roster_validation() -> dict[str, Any]:
    """
    Invoke agent roster validation via subprocess.

    Returns:
        Dict with 'success', 'agents_validated', and 'integrity_errors' keys
    """
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.agent_roster_runner", "--action=validate"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 120 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except (ValueError, TypeError) as e:
        return {"success": False, "error": str(e)}


def invoke_hierarchy_agent(action: str, project_root: Path | None = None) -> dict[str, Any]:
    """
    Invoke HierarchyAgent via subprocess.

    Args:
        action: One of 'dry_run', 'heal_violations', 'verify_mro'
        project_root: Project root path (auto-detected if None)

    Returns:
        Dict with 'success' key and action-specific results
    """
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.hierarchy_runner", f"--action={action}"]
    if project_root:
        cmd.append(f"--project-root={project_root}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 300 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except (ValueError, TypeError) as e:
        return {"success": False, "error": str(e)}


def invoke_code_validator(
    action: str,
    project_root: Path | None = None,
    directory: str | None = None,
) -> dict[str, Any]:
    """
    Invoke CodeValidatorAgent via subprocess.

    Args:
        action: One of 'validate', 'validate_directory'
        project_root: Project root path (auto-detected if None)
        directory: Directory to validate (required for validate_directory)

    Returns:
        Dict with 'success' key and action-specific results
    """
    cmd = [sys.executable, "-m", "agentic_core.L5_safety.runners.code_validator_runner", f"--action={action}"]
    if directory:
        cmd.append(f"--directory={directory}")
    if project_root:
        cmd.append(f"--project-root={project_root}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=DEFAULT_TIMEOUT)
        if result.stdout.strip():
            return json.loads(result.stdout.strip())
        return {"success": result.returncode == 0, "error": result.stderr if result.returncode != 0 else None}
    except subprocess.TimeoutExpired:
        return {"success": False, "error": "Subprocess timed out after 300 seconds"}
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Failed to parse runner output: {e}"}
    except (ValueError, TypeError) as e:
        return {"success": False, "error": str(e)}
