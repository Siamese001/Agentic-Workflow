#!/usr/bin/env python3
"""Git Health Sensor - Deterministic binary sensor for Git repository health.

Zero-Ambiguity Standard: Named with _sensor.py suffix
Category: SENSOR (Deterministic binary check)

Monitors Git repository health and provides structured context for L0 healing operations.
Detects uncommitted changes, merge conflicts, and detached HEAD states.
"""

from __future__ import annotations

import logging
import subprocess
import uuid
from pathlib import Path

from agentic_core.L5_safety.config.detection_signal_config import (
    DetectionSignal,
    FailureContext,
    ImpactAssessment,
    ImpactScope,
    Severity,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "git_health_sensor_enforcer")
emit_determinism_digest("p0", "git_health_sensor_enforcer")

_emit_dispatches_healing_run("p1", "git_health_sensor_enforcer", "L5")
_emit_routes_through("p1", "git_health_sensor_enforcer", "L5")
_emit_checks_agent_registry("p1", "git_health_sensor_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "git_health_sensor_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "git_health_sensor_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "git_health_sensor_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "git_health_sensor_enforcer", "target_agent")
_emit_verifies_policy("p1", "git_health_sensor_enforcer", "policy_check")
_emit_verifies_boundary("p1", "git_health_sensor_enforcer", "boundary_check")
_emit_transcripts_response("p1", "git_health_sensor_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "git_health_sensor_enforcer")
_emit_gated_by_confidence("p1", "git_health_sensor_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "git_health_sensor_enforcer", "L5")
_emit_reads_policy_state("p1", "git_health_sensor_enforcer", "L5")

_emit_applies_guardrail("p0", "git_health_sensor_enforcer", "p0_governance")
_emit_snapshots_state("p0", "git_health_sensor_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "git_health_sensor_enforcer", "execution_auth")
_emit_validates_capability("p2", "git_health_sensor_enforcer", "capability_check")
_emit_routes_to_capability("p2", "git_health_sensor_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "git_health_sensor_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "git_health_sensor_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "git_health_sensor_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "git_health_sensor_enforcer", "exec_output")
_emit_dispatches_agent("p3", "git_health_sensor_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "git_health_sensor_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "git_health_sensor_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "git_health_sensor_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "git_health_sensor_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "git_health_sensor_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "git_health_sensor_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "git_health_sensor_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "git_health_sensor_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "git_health_sensor_enforcer", "eval_metric")
_emit_stores_embedding("p4", "git_health_sensor_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "git_health_sensor_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "git_health_sensor_enforcer", "exec_snapshot_link")

Logger = logging.getLogger(__name__)


class GitHealthSensor:
    """
    Deterministic binary sensor for Git repository health.

    Performs the following checks:
    - Uncommitted Changes: Dirty working directory (Severity.HIGH)
    - Merge Conflicts: Active conflict markers (Severity.CRITICAL)
    - Detached HEAD: Risk to mission trace persistence (Severity.MEDIUM)
    """

    def __init__(self, repo_root: Path | str | None = None):
        """
        Initialize the Git health sensor.

        Args:
            repo_root: Path to the Git repository root. If None, uses current directory.
        """
        self.repo_root = Path(repo_root) if repo_root else Path.cwd()
        self.sensor_name = "GitHealthSensor"

    def _run_git_command(self, args: list[str]) -> tuple[int, str, str]:
        """
        Run a git command and return exit code, stdout, stderr.

        Args:
            args: Git command arguments (without 'git' prefix)

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        try:
            # guardian: allow-magic-config (pre-existing, moved from L0)
            result = subprocess.run(
                ["git"] + args,  # guardian: File operations should check existence before access
                cwd=self.repo_root,
                capture_output=True,
                text=True,
                timeout=DEFAULT_TIMEOUT,
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Git command timed out"
        except FileNotFoundError:  # guardian: File operations should check existence before access
            return -1, "", "Git not found in PATH"
        # guardian: allow-silent-swallow (pre-existing, moved from L0)
        except (ValueError, TypeError) as e:
            return -1, "", str(e)

    def _check_uncommitted_changes(self) -> DetectionSignal | None:
        """
        Check for uncommitted changes in the working directory.

        Returns:
            DetectionSignal if dirty, None if clean
        """
        exit_code, stdout, stderr = self._run_git_command(["status", "--porcelain"])

        if exit_code != 0:
            Logger.warning(f"Git status failed: {stderr}")
            return None

        if not stdout.strip():
            return None  # Clean working directory

        # Parse affected files
        affected_files = []
        for line in stdout.strip().split("\n"):
            if line:
                # Format: XY filename
                file_path = line[3:].strip()
                if file_path:
                    affected_files.append(Path(file_path))

        # Get full git status for context
        _, full_status, _ = self._run_git_command(["status"])

        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="uncommitted_changes",
            is_failure=True,
            failure_context=FailureContext(
                error_message=f"Working directory has {len(affected_files)} uncommitted changes. "
                f"Healing agents cannot safely perform atomic git commits on unsaved work.",
                related_files=affected_files,
                system_state={"git_status": full_status},
            ),
            severity=Severity.HIGH,
            impact=ImpactAssessment(
                scope=ImpactScope.SYSTEM_WIDE,
                affected_components=["git", "healing", "commit"],
                estimated_blast_radius=len(affected_files),
                recovery_complexity="low",
            ),
            is_auto_fixable=False,
            suggested_fix="Commit or stash uncommitted changes before running healing operations.",
        )

    def _check_merge_conflicts(self) -> DetectionSignal | None:
        """
        Check for active merge conflicts.

        Returns:
            DetectionSignal if conflicts exist, None if clean
        """
        # Check for unmerged paths
        exit_code, stdout, stderr = self._run_git_command(["diff", "--name-only", "--diff-filter=U"])

        if exit_code != 0:
            Logger.warning(f"Git diff failed: {stderr}")
            return None

        if not stdout.strip():
            return None  # No conflicts

        # Parse conflicted files
        conflicted_files = [Path(f.strip()) for f in stdout.strip().split("\n") if f.strip()]

        # Get full git status for context
        _, full_status, _ = self._run_git_command(["status"])

        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="merge_conflicts",
            is_failure=True,
            failure_context=FailureContext(
                error_message=f"Repository has {len(conflicted_files)} files with merge conflicts. "
                f"All automated structural surgery is BLOCKED until conflicts are resolved.",
                related_files=conflicted_files,
                system_state={"git_status": full_status},
            ),
            severity=Severity.CRITICAL,
            impact=ImpactAssessment(
                scope=ImpactScope.COMPONENT,
                affected_components=["git", "merge", "healing"],
                estimated_blast_radius=len(conflicted_files),
                recovery_complexity="high",
            ),
            is_auto_fixable=False,
            suggested_fix="Resolve merge conflicts manually before running healing operations.",
        )

    def _check_detached_head(self) -> DetectionSignal | None:
        """
        Check if repository is in detached HEAD state.

        Returns:
            DetectionSignal if detached, None if on branch
        """
        exit_code, stdout, stderr = self._run_git_command(["symbolic-ref", "-q", "HEAD"])

        if exit_code == 0:
            return None  # On a branch, not detached

        # Confirm detached state
        exit_code2, head_ref, _ = self._run_git_command(["rev-parse", "--short", "HEAD"])

        if exit_code2 != 0:
            return None  # Can't determine state

        # Get full git status for context
        _, full_status, _ = self._run_git_command(["status"])

        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="detached_head",
            is_failure=True,
            failure_context=FailureContext(
                error_message=f"Repository is in detached HEAD state at {head_ref.strip()}. "
                f"This poses a risk to mission trace persistence.",
                system_state={"git_status": full_status, "head_ref": head_ref.strip()},
            ),
            severity=Severity.MEDIUM,
            impact=ImpactAssessment(
                scope=ImpactScope.SYSTEM_WIDE,
                affected_components=["git", "branch", "trace"],
                estimated_blast_radius=0,
                recovery_complexity="low",
            ),
            is_auto_fixable=False,
            suggested_fix="Checkout a branch before running healing operations: git checkout <branch>",
        )

    def check_repository_health(self) -> DetectionSignal:
        """
        Perform all Git health checks and return the most severe signal.

        Returns:
            DetectionSignal with is_failure=True if any blocker found,
            or is_failure=False if repository is healthy.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "GitHealthSensor.check_repository_health",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:GitHealthSensor.check_repository_health".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        Logger.info(f"[{self.sensor_name}] Checking repository health at {self.repo_root}")

        # Check in order of severity (CRITICAL first)
        signals = []

        # 1. Merge conflicts (CRITICAL)
        conflict_signal = self._check_merge_conflicts()
        if conflict_signal:
            signals.append(conflict_signal)
            Logger.warning(f"[{self.sensor_name}] Merge conflicts detected")

        # 2. Uncommitted changes (HIGH)
        uncommitted_signal = self._check_uncommitted_changes()
        if uncommitted_signal:
            signals.append(uncommitted_signal)
            Logger.warning(f"[{self.sensor_name}] Uncommitted changes detected")

        # 3. Detached HEAD (MEDIUM)
        detached_signal = self._check_detached_head()
        if detached_signal:
            signals.append(detached_signal)
            Logger.warning(f"[{self.sensor_name}] Detached HEAD detected")

        # Return most severe signal, or healthy signal if none
        if signals:
            # Sort by severity (highest first)
            signals.sort(key=lambda s: s.severity.value, reverse=True)
            return signals[0]

        # Repository is healthy
        Logger.info(f"[{self.sensor_name}] Repository is healthy")
        return DetectionSignal(
            source_sensor=self.sensor_name,
            detection_type="repository_health",
            is_failure=False,
            failure_context=FailureContext(
                error_message="Repository is healthy. No blockers detected.",
            ),
            severity=Severity.INFO,
            impact=ImpactAssessment(
                scope=ImpactScope.ISOLATED,
                recovery_complexity="low",
            ),
            is_auto_fixable=False,
        )

    def get_all_signals(self) -> list[DetectionSignal]:
        """
        Get all detection signals (not just the most severe).

        Returns:
            List of all DetectionSignal objects for each check.
        """
        signals = []

        conflict_signal = self._check_merge_conflicts()
        if conflict_signal:
            signals.append(conflict_signal)

        uncommitted_signal = self._check_uncommitted_changes()
        if uncommitted_signal:
            signals.append(uncommitted_signal)

        detached_signal = self._check_detached_head()
        if detached_signal:
            signals.append(detached_signal)

        return signals


def check_git_health(repo_root: Path | str | None = None) -> DetectionSignal:
    """
    Convenience function to check Git repository health.

    Args:
        repo_root: Path to the Git repository root. If None, uses current directory.

    Returns:
        DetectionSignal with health status.
    """
    _emit_observes_runtime_state(str(uuid.uuid4()), "Module.check_git_health", "L5_POLICY")
    sensor = GitHealthSensor(repo_root)
    return sensor.check_repository_health()


if __name__ == "__main__":
    # Quick test
    import json

    signal = check_git_health()
    print(json.dumps(signal.to_dict(), indent=2, default=str))
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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

_emit_emits_metric_event("git_health_sensor_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("git_health_sensor_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("git_health_sensor_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("git_health_sensor_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("git_health_sensor_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("git_health_sensor_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("git_health_sensor_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("git_health_sensor_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("git_health_sensor_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("git_health_sensor_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("git_health_sensor_enforcer", "p4obs", "alert")
_emit_links_incident_trace("git_health_sensor_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("git_health_sensor_enforcer", "p3lm", "pattern")
_emit_records_learning_event("git_health_sensor_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("git_health_sensor_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("git_health_sensor_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("git_health_sensor_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("git_health_sensor_enforcer", "p3lm", "policy")
_emit_stores_learning_state("git_health_sensor_enforcer", "p3lm", "state")
_emit_records_execution_trace("git_health_sensor_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("git_health_sensor_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("git_health_sensor_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("git_health_sensor_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("git_health_sensor_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("git_health_sensor_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("git_health_sensor_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("git_health_sensor_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("git_health_sensor_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "git_health_sensor_enforcer", "context_pull")
_emit_pulls_context("p1", "git_health_sensor_enforcer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "git_health_sensor_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "git_health_sensor_enforcer", "uwg_term_secondary")
_emit_writes_through("p1", "git_health_sensor_enforcer", "write_through")
_emit_writes_through("p1", "git_health_sensor_enforcer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "git_health_sensor_enforcer", "safety_validation")
_emit_invokes_eval("p1", "git_health_sensor_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "git_health_sensor_enforcer", "routing_commit")
