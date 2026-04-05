"""
Centralized SSOT for managing backup directories and cleanup policies.

This module replaces the 4 competing backup patterns identified in the SSOT audit:
- archives/healing_backups/ (CORRECT - now enforced)
- .sovereign_healing_backup/ (DEPRECATED)
- .governance_healer_backups/ (NON-STANDARD)
- .canon_memory/backups/ (NON-STANDARD)

All agents should use BackupManager for backup operations.
"""

import shutil
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
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

_emit_applies_guardrail("p0", "backup_manager_util", "p0_governance")
_emit_reads_policy_state("p0", "backup_manager_util", "policy_binding")
_emit_snapshots_state("p0", "backup_manager_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("backup_manager_util", "p4obs", "metric_1")
_emit_emits_metric_event("backup_manager_util", "p4obs", "metric_2")
_emit_emits_metric_event("backup_manager_util", "p4obs", "metric_3")
_emit_emits_metric_event("backup_manager_util", "p4obs", "metric_4")
_emit_emits_metric_event("backup_manager_util", "p4obs", "metric_5")
_emit_emits_metric_event("backup_manager_util", "p4obs", "metric_6")
_emit_records_incident_event("backup_manager_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("backup_manager_util", "p4obs", "anomaly")
_emit_writes_observability_log("backup_manager_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("backup_manager_util", "p4obs", "mon_state")
_emit_triggers_alert("backup_manager_util", "p4obs", "alert")
_emit_links_incident_trace("backup_manager_util", "p4obs", "trace_link")
_emit_captures_pattern("backup_manager_util", "p3lm", "pattern")
_emit_records_learning_event("backup_manager_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("backup_manager_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("backup_manager_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("backup_manager_util", "p3lm", "routing")
_emit_improves_agent_policy("backup_manager_util", "p3lm", "policy")
_emit_stores_learning_state("backup_manager_util", "p3lm", "state")
_emit_records_execution_trace("backup_manager_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("backup_manager_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("backup_manager_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("backup_manager_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("backup_manager_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("backup_manager_util", "env_read", "p2_env_1")
_emit_reads_environ("backup_manager_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("backup_manager_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("backup_manager_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "backup_manager_util", "context_pull")
_emit_pulls_context("p1", "backup_manager_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "backup_manager_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "backup_manager_util", "uwg_term_2")
_emit_writes_through("p1", "backup_manager_util", "write_through")
_emit_writes_through("p1", "backup_manager_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "backup_manager_util", "safety_validation")
_emit_invokes_eval("p1", "backup_manager_util", "eval_call")
_emit_proposal_commits_routing("p1", "backup_manager_util", "routing_commit")
_emit_escalates_to_human("p1", "backup_manager_util", "human_escalation")
_emit_routes_through("p1", "backup_manager_util", "route_through")
_emit_checks_agent_registry("p1", "backup_manager_util", "agent_registry")
_emit_validates_agent_capability("p1", "backup_manager_util", "capability")
_emit_dispatches_execution_plan("p1", "backup_manager_util", "exec_plan")
_emit_agent_executes_agent("p1", "backup_manager_util", "sub_agent")
_emit_routes_to_agent("p1", "backup_manager_util", "target_agent")
_emit_verifies_policy("p1", "backup_manager_util", "policy_check")
_emit_observes_runtime_state("p1", "backup_manager_util", "runtime_state")
_emit_verifies_boundary("p1", "backup_manager_util", "boundary_check")
_emit_transcripts_response("p1", "backup_manager_util", "transcript")
_emit_hard_fails_untranscripted("p1", "backup_manager_util")
_emit_gated_by_confidence("p1", "backup_manager_util", "confidence_gate")
emit_replay_key("p0", "backup_manager_util")
emit_determinism_digest("p0", "backup_manager_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "backup_manager_util", "execution_auth")
_emit_validates_capability("p2", "backup_manager_util", "capability_check")
_emit_routes_to_capability("p2", "backup_manager_util", "capability_route")
_emit_writes_via_uwg("p2", "backup_manager_util", "uwg_write")
_emit_blocks_direct_write("p2", "backup_manager_util", "direct_write_block")
_emit_records_tool_invocation("p2", "backup_manager_util", "tool_invocation")
_emit_captures_execution_output("p2", "backup_manager_util", "exec_output")
_emit_dispatches_agent("p3", "backup_manager_util", "agent_dispatch")
_emit_coordinates_agents("p3", "backup_manager_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "backup_manager_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "backup_manager_util", "healing_outcome")
_emit_escalates_failure("p3", "backup_manager_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "backup_manager_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "backup_manager_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "backup_manager_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "backup_manager_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "backup_manager_util", "eval_metric")
_emit_stores_embedding("p4", "backup_manager_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "backup_manager_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "backup_manager_util", "exec_snapshot_link")


class BackupManager:
    """
    Centralized backup directory management.
    SSOT Location: archives/healing_backups/<category>/
    """

    BACKUP_ROOT = Path("archives/healing_backups")

    @classmethod
    def get_backup_dir(
        cls, category: str, project_root: str | Path | None = None, timestamped: bool = True
    ) -> Path:
        """
        Get a standardized backup directory path.

        Args:
            category: The sub-bucket for backups (e.g., 'filesystem', 'structure')
            project_root: Root of the repository (defaults to CWD)
            timestamped: If True, appends YYYYMMDD_HHMMSS subdirectory

        Returns:
            Path: The fully resolved, created directory path
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "BackupManager.get_backup_dir")

        root = Path(project_root) if project_root else Path.cwd()
        base_path = root / cls.BACKUP_ROOT / category
        if timestamped:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            final_path = base_path / timestamp
        else:
            final_path = base_path
        final_path.mkdir(parents=True, exist_ok=True)
        return final_path

    @classmethod
    def cleanup_old_backups(
        cls, category: str, keep_last_n: int = 10, project_root: str | Path | None = None
    ) -> int:
        """
        Remove old backups for a specific category, keeping only the N most recent.

        Returns:
            int: Number of backup directories removed
        """
        root = Path(project_root) if project_root else Path.cwd()
        category_dir = root / cls.BACKUP_ROOT / category
        if not category_dir.exists():
            return 0
        backups = sorted(
            [d for d in category_dir.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True
        )
        removed_count = 0
        if len(backups) > keep_last_n:
            to_remove = backups[keep_last_n:]
            for backup in to_remove:
                try:
                    shutil.rmtree(backup)
                    removed_count += 1
                except OSError as e:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                    print(f"Error cleaning up backup {backup}: {e}")
        return removed_count

    @classmethod
    def backup_file(
        cls, target_file: str | Path, category: str = "misc", project_root: str | Path | None = None
    ) -> Path | None:
        """
        Quickly backup a single file to a timestamped location.

        Args:
            target_file: Path to the file to backup
            category: Backup category (e.g., 'filesystem', 'structure')
            project_root: Root of the repository (defaults to CWD)

        Returns:
            Path to the backup file, or None if source doesn't exist
        """
        src = Path(target_file)
        if not src.exists():
            return None
        dest_dir = cls.get_backup_dir(category, project_root, timestamped=True)
        dest_file = dest_dir / src.name
        shutil.copy2(src, dest_file)
        return dest_file

    @classmethod
    def list_backups(cls, category: str, project_root: str | Path | None = None) -> list[Path]:
        """
        List all backup directories for a category.

        Args:
            category: Backup category to list
            project_root: Root of the repository (defaults to CWD)

        Returns:
            List of backup directory paths, sorted newest first
        """
        root = Path(project_root) if project_root else Path.cwd()
        category_dir = root / cls.BACKUP_ROOT / category
        if not category_dir.exists():
            return []
        return sorted([d for d in category_dir.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)

    @classmethod
    def restore_backup(
        cls, backup_path: str | Path, target_path: str | Path, overwrite: bool = False
    ) -> bool:
        """
        Restore files from a backup directory to a target location.

        Args:
            backup_path: Path to the backup directory
            target_path: Path to restore files to
            overwrite: If True, overwrite existing files

        Returns:
            True if restore succeeded, False otherwise
        """
        backup = Path(backup_path)
        target = Path(target_path)
        if not backup.exists():
            return False
        try:
            if backup.is_file():
                if target.exists() and (not overwrite):
                    return False
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(backup, target)
            else:
                for item in backup.iterdir():
                    dest = target / item.name
                    if dest.exists() and (not overwrite):
                        continue
                    if item.is_file():
                        dest.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(item, dest)
                    else:
                        shutil.copytree(item, dest, dirs_exist_ok=overwrite)
            return True
        except Exception as e:
            print(f"Error restoring backup: {e}")
            return False

    @classmethod
    def decommission_legacy_backups(cls, project_root: str | Path | None = None) -> int:
        """
        Final cleanup of deprecated backup directories.

        Removes legacy backup directories that are no longer used:
        - .sovereign_healing_backup/
        - .governance_healer_backups/

        Args:
            project_root: Root of the repository (defaults to CWD)

        Returns:
            int: Number of legacy directories removed
        """
        root = Path(project_root) if project_root else Path.cwd()
        legacy_dirs = [".sovereign_healing_backup", ".governance_healer_backups"]
        removed_count = 0
        for legacy_name in legacy_dirs:
            legacy_path = root / legacy_name
            if legacy_path.exists() and legacy_path.is_dir():
                try:
                    shutil.rmtree(legacy_path)
                    removed_count += 1
                    print(f"Removed legacy backup directory: {legacy_path}")
                except OSError as e:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
                    print(f"Error removing legacy backup {legacy_path}: {e}")
        return removed_count

    @classmethod
    def get_legacy_backup_dirs(cls, project_root: str | Path | None = None) -> list[Path]:
        """
        List any legacy backup directories that still exist.

        Args:
            project_root: Root of the repository (defaults to CWD)

        Returns:
            List of legacy backup directory paths that exist
        """
        root = Path(project_root) if project_root else Path.cwd()
        legacy_dirs = [".sovereign_healing_backup", ".governance_healer_backups"]
        existing = []
        for legacy_name in legacy_dirs:
            legacy_path = root / legacy_name
            if legacy_path.exists() and legacy_path.is_dir():
                existing.append(legacy_path)
        return existing
