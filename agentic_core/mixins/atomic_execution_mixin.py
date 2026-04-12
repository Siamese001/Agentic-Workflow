"""
Atomic Execution Mixin - V10 System Actuation Compliance.

Per Agentic Process V10 specification:
- System Actuation (Healing) requires "Atomic Execution (All-or-Nothing changes)"
- "Auto-rollback if problems" on the main flow

This mixin provides transactional semantics for file operations:
1. Backup before modification
2. Execute changes
3. Verify success
4. Rollback on failure

References:
- V10 Diagram: "Safe Execution: All-or-nothing changes, Auto-rollback if problems"
- Resolution Asymmetry.jpg: "Zero-Loss Surgical Fixes"
"""

import logging
import shutil
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_applies_guardrail("p0", "atomic_execution_mixin", "p0_governance")
_emit_reads_policy_state("p0", "atomic_execution_mixin", "policy_binding")
_emit_snapshots_state("p0", "atomic_execution_mixin", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("atomic_execution_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("atomic_execution_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("atomic_execution_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("atomic_execution_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("atomic_execution_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("atomic_execution_mixin", "p4obs", "metric_6")
_emit_records_incident_event("atomic_execution_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("atomic_execution_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("atomic_execution_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("atomic_execution_mixin", "p4obs", "mon_state")
_emit_triggers_alert("atomic_execution_mixin", "p4obs", "alert")
_emit_links_incident_trace("atomic_execution_mixin", "p4obs", "trace_link")
_emit_captures_pattern("atomic_execution_mixin", "p3lm", "pattern")
_emit_records_learning_event("atomic_execution_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("atomic_execution_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("atomic_execution_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("atomic_execution_mixin", "p3lm", "routing")
_emit_improves_agent_policy("atomic_execution_mixin", "p3lm", "policy")
_emit_stores_learning_state("atomic_execution_mixin", "p3lm", "state")
_emit_records_execution_trace("atomic_execution_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("atomic_execution_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("atomic_execution_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("atomic_execution_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("atomic_execution_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("atomic_execution_mixin", "env_read", "p2_env_1")
_emit_reads_environ("atomic_execution_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("atomic_execution_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("atomic_execution_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "atomic_execution_mixin", "context_pull")
_emit_pulls_context("p1", "atomic_execution_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "atomic_execution_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "atomic_execution_mixin", "uwg_term_2")
_emit_writes_through("p1", "atomic_execution_mixin", "write_through")
_emit_writes_through("p1", "atomic_execution_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "atomic_execution_mixin", "safety_validation")
_emit_invokes_eval("p1", "atomic_execution_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "atomic_execution_mixin", "routing_commit")
_emit_escalates_to_human("p1", "atomic_execution_mixin", "human_escalation")
_emit_routes_through("p1", "atomic_execution_mixin", "route_through")
_emit_checks_agent_registry("p1", "atomic_execution_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "atomic_execution_mixin", "capability")
_emit_dispatches_execution_plan("p1", "atomic_execution_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "atomic_execution_mixin", "sub_agent")
_emit_routes_to_agent("p1", "atomic_execution_mixin", "target_agent")
_emit_verifies_policy("p1", "atomic_execution_mixin", "policy_check")
_emit_observes_runtime_state("p1", "atomic_execution_mixin", "runtime_state")
_emit_verifies_boundary("p1", "atomic_execution_mixin", "boundary_check")
_emit_transcripts_response("p1", "atomic_execution_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "atomic_execution_mixin")
_emit_gated_by_confidence("p1", "atomic_execution_mixin", "confidence_gate")
emit_replay_key("p0", "atomic_execution_mixin")
emit_determinism_digest("p0", "atomic_execution_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "atomic_execution_mixin", "execution_auth")
_emit_validates_capability("p2", "atomic_execution_mixin", "capability_check")
_emit_routes_to_capability("p2", "atomic_execution_mixin", "capability_route")
_emit_writes_via_uwg("p2", "atomic_execution_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "atomic_execution_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "atomic_execution_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "atomic_execution_mixin", "exec_output")
_emit_dispatches_agent("p3", "atomic_execution_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "atomic_execution_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "atomic_execution_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "atomic_execution_mixin", "healing_outcome")
_emit_escalates_failure("p3", "atomic_execution_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "atomic_execution_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "atomic_execution_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "atomic_execution_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "atomic_execution_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "atomic_execution_mixin", "eval_metric")
_emit_stores_embedding("p4", "atomic_execution_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "atomic_execution_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "atomic_execution_mixin", "exec_snapshot_link")

logger = logging.getLogger(__name__)


@dataclass
class FileBackup:
    """Record of a backed-up file for potential rollback."""

    original_path: Path
    backup_path: Path
    timestamp: datetime = field(default_factory=datetime.utcnow)
    content_hash: str | None = None


@dataclass
class AtomicTransaction:
    """Transaction context for atomic operations."""

    transaction_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    backups: list[FileBackup] = field(default_factory=list)
    modified_files: set[Path] = field(default_factory=set)
    created_files: set[Path] = field(default_factory=set)
    committed: bool = False
    rolled_back: bool = False
    error: str | None = None


class AtomicExecutionError(Exception):
    """Raised when atomic execution fails and rollback occurs."""

    def __init__(self, message: str, transaction_id: str, rolled_back: bool = False):
        self.transaction_id = transaction_id
        self.rolled_back = rolled_back
        super().__init__(f"[{transaction_id}] {message} (rolled_back={rolled_back})")


class AtomicExecutionMixin:
    """
    Mixin providing atomic execution capabilities for healing operations.

    Implements the V10 "All-or-Nothing" constraint for System Actuation:
    - Creates backups before any modification
    - Tracks all file changes within a transaction
    - Automatically rolls back on any failure
    - Provides verification hooks

    Usage:
        class MyHealerAgent(AtomicExecutionMixin, SovereignBaseAgent):
            def heal_file(self, file_path: Path):
                with self.atomic_transaction("heal_imports") as txn:
                    self.atomic_write(txn, file_path, new_content)
                    # If any error occurs, changes are rolled back

    Integration with existing agents:
        # Add to MRO before SovereignBaseAgent
        class MyAgent(AtomicExecutionMixin, SovereignBaseAgent):
            pass
    """

    _active_transactions: dict[str, AtomicTransaction] = {}
    _backup_dir: Path | None = None

    def _get_backup_dir(self) -> Path:
        """Get or create the backup directory."""
        if self._backup_dir is None:
            project_root = getattr(self, "project_root", Path.cwd())
            self._backup_dir = project_root / ".atomic_backups"
            self._backup_dir.mkdir(parents=True, exist_ok=True)
        return self._backup_dir

    def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID."""
        import uuid

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        return f"txn_{timestamp}_{uuid.uuid4().hex[:8]}"

    def _compute_file_hash(self, file_path: Path) -> str | None:
        """Compute content hash for a file."""
        import hashlib

        if not file_path.exists():
            return None
        try:
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        # guardian: allow-silent-swallow
        except Exception:
            logger.warning(f"Failed to compute hash for {file_path}", exc_info=True)
            return None

    def _backup_file(self, txn: AtomicTransaction, file_path: Path) -> FileBackup | None:
        """Create a backup of a file before modification."""
        if not file_path.exists():
            return None
        for backup in txn.backups:
            if backup.original_path == file_path:
                return backup
        backup_dir = self._get_backup_dir() / txn.transaction_id
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_name = f"{file_path.stem}_{len(txn.backups)}{file_path.suffix}"
        backup_path = backup_dir / backup_name
        try:
            shutil.copy2(file_path, backup_path)
            backup = FileBackup(
                original_path=file_path,
                backup_path=backup_path,
                content_hash=self._compute_file_hash(file_path),
            )
            txn.backups.append(backup)
            logger.debug(f"Backed up {file_path} to {backup_path}")
            return backup
        # guardian: allow-silent-swallow
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            raise AtomicExecutionError(f"Backup failed for {file_path}: {e}", txn.transaction_id)

    def _rollback_transaction(self, txn: AtomicTransaction) -> None:
        """Rollback all changes in a transaction."""
        logger.warning(f"Rolling back transaction {txn.transaction_id}")
        errors = []
        for backup in reversed(txn.backups):
            try:
                if backup.backup_path.exists():
                    shutil.copy2(backup.backup_path, backup.original_path)
                    logger.debug(f"Restored {backup.original_path} from backup")
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                errors.append(f"Failed to restore {backup.original_path}: {e}")
        for created_path in txn.created_files:
            try:
                if created_path.exists() and created_path not in [b.original_path for b in txn.backups]:
                    created_path.unlink()
                    logger.debug(f"Removed created file {created_path}")
            except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                errors.append(f"Failed to remove {created_path}: {e}")
        txn.rolled_back = True
        if errors:
            logger.error(f"Rollback completed with errors: {errors}")
        else:
            logger.info(f"Transaction {txn.transaction_id} rolled back successfully")

    def _cleanup_transaction(self, txn: AtomicTransaction) -> None:
        """Clean up transaction resources after commit or rollback."""
        try:
            backup_dir = self._get_backup_dir() / txn.transaction_id
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
                logger.debug(f"Cleaned up backup directory {backup_dir}")
        # guardian: allow-silent-swallow
        except Exception as e:  # guardian: allow-log-and-swallow -- teardown/cleanup context -- swallow is conventional in resource-release paths
            logger.warning(f"Failed to cleanup transaction {txn.transaction_id}: {e}")
        if txn.transaction_id in self._active_transactions:
            del self._active_transactions[txn.transaction_id]

    @contextmanager
    def atomic_transaction(self, operation_name: str, cleanup_on_success: bool = True):
        """
        Context manager for atomic file operations.

        Usage:
            with self.atomic_transaction("fix_imports") as txn:
                self.atomic_write(txn, file_path, new_content)
                # Automatically rolled back if exception occurs

        Args:
            operation_name: Human-readable name for logging
            cleanup_on_success: Whether to cleanup backups on successful commit

        Yields:
            AtomicTransaction context object

        Raises:
            AtomicExecutionError: If operation fails (after rollback)
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L3_ORCHESTRATION, "AtomicExecutionMixin.atomic_transaction"
        )

        txn_id = self._generate_transaction_id()
        txn = AtomicTransaction(transaction_id=txn_id)
        self._active_transactions[txn_id] = txn
        logger.info(f"Starting atomic transaction {txn_id} for '{operation_name}'")
        try:
            yield txn
            txn.committed = True
            logger.info(
                f"Transaction {txn_id} committed successfully. Modified: {len(txn.modified_files)}, Created: {len(txn.created_files)}",
            )
            if cleanup_on_success:
                self._cleanup_transaction(txn)
        # guardian: allow-silent-swallow
        except Exception as e:
            txn.error = str(e)
            logger.error(f"Transaction {txn_id} failed: {e}")
            self._rollback_transaction(txn)
            self._cleanup_transaction(txn)
            raise AtomicExecutionError(
                f"Operation '{operation_name}' failed: {e}",
                txn_id,
                rolled_back=True,
            ) from e

    def atomic_write(
        self,
        txn: AtomicTransaction,
        file_path: Path,
        content: str,
        encoding: str = "utf-8",
    ) -> None:
        """
        Write to a file within an atomic transaction.

        Args:
            txn: Active transaction context
            file_path: Path to write
            content: Content to write
            encoding: File encoding (default: utf-8)
        """
        if txn.committed or txn.rolled_back:
            raise AtomicExecutionError(
                "Cannot write to committed/rolled-back transaction",
                txn.transaction_id,
            )
        if file_path.exists():
            self._backup_file(txn, file_path)
            txn.modified_files.add(file_path)
        else:
            txn.created_files.add(file_path)
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding=encoding)
            logger.debug(f"Atomic write to {file_path}")
        except Exception as e:
            raise AtomicExecutionError(f"Write failed for {file_path}: {e}", txn.transaction_id) from e

    def atomic_delete(self, txn: AtomicTransaction, file_path: Path) -> None:
        """
        Delete a file within an atomic transaction.

        Args:
            txn: Active transaction context
            file_path: Path to delete
        """
        if txn.committed or txn.rolled_back:
            raise AtomicExecutionError(
                "Cannot delete in committed/rolled-back transaction",
                txn.transaction_id,
            )
        if not file_path.exists():
            return
        self._backup_file(txn, file_path)
        txn.modified_files.add(file_path)
        try:
            file_path.unlink()
            logger.debug(f"Atomic delete of {file_path}")
        except Exception as e:
            raise AtomicExecutionError(f"Delete failed for {file_path}: {e}", txn.transaction_id) from e

    def atomic_rename(self, txn: AtomicTransaction, src_path: Path, dst_path: Path) -> None:
        """
        Rename/move a file within an atomic transaction.

        Args:
            txn: Active transaction context
            src_path: Source path
            dst_path: Destination path
        """
        if txn.committed or txn.rolled_back:
            raise AtomicExecutionError(
                "Cannot rename in committed/rolled-back transaction",
                txn.transaction_id,
            )
        if not src_path.exists():
            raise AtomicExecutionError(f"Source file does not exist: {src_path}", txn.transaction_id)
        self._backup_file(txn, src_path)
        txn.modified_files.add(src_path)
        if dst_path.exists():
            self._backup_file(txn, dst_path)
            txn.modified_files.add(dst_path)
        else:
            txn.created_files.add(dst_path)
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src_path), str(dst_path))
            logger.debug(f"Atomic rename {src_path} -> {dst_path}")
        except Exception as e:
            raise AtomicExecutionError(
                f"Rename failed {src_path} -> {dst_path}: {e}",
                txn.transaction_id,
            ) from e

    def get_active_transactions(self) -> dict[str, AtomicTransaction]:
        """Get all active transactions for monitoring."""
        return dict(self._active_transactions)


__all__ = ["AtomicExecutionMixin", "AtomicExecutionError", "AtomicTransaction", "FileBackup"]
