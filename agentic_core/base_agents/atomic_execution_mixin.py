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
from typing import Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class FileBackup:
    """Record of a backed-up file for potential rollback."""

    original_path: Path
    backup_path: Path
    timestamp: datetime = field(default_factory=datetime.utcnow)
    content_hash: Optional[str] = None


@dataclass
class AtomicTransaction:
    """Transaction context for atomic operations."""

    transaction_id: str
    started_at: datetime = field(default_factory=datetime.utcnow)
    backups: List[FileBackup] = field(default_factory=list)
    modified_files: Set[Path] = field(default_factory=set)
    created_files: Set[Path] = field(default_factory=set)
    committed: bool = False
    rolled_back: bool = False
    error: Optional[str] = None


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

    _active_transactions: Dict[str, AtomicTransaction] = {}
    _backup_dir: Optional[Path] = None

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

    def _compute_file_hash(self, file_path: Path) -> Optional[str]:
        """Compute content hash for a file."""
        import hashlib

        if not file_path.exists():
            return None
        try:
            content = file_path.read_bytes()
            return hashlib.sha256(content).hexdigest()[:16]
        except Exception:
            # HARDENING: Log specific error for observability
            logger.warning(f"Failed to compute hash for {file_path}", exc_info=True)
            return None

    def _backup_file(self, txn: AtomicTransaction, file_path: Path) -> Optional[FileBackup]:
        """Create a backup of a file before modification."""
        if not file_path.exists():
            return None

        # Skip if already backed up in this transaction
        for backup in txn.backups:
            if backup.original_path == file_path:
                return backup

        backup_dir = self._get_backup_dir() / txn.transaction_id
        backup_dir.mkdir(parents=True, exist_ok=True)

        # Create unique backup filename
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
        except Exception as e:
            logger.error(f"Failed to backup {file_path}: {e}")
            raise AtomicExecutionError(
                f"Backup failed for {file_path}: {e}",
                txn.transaction_id,
            )

    def _rollback_transaction(self, txn: AtomicTransaction) -> None:
        """Rollback all changes in a transaction."""
        logger.warning(f"Rolling back transaction {txn.transaction_id}")

        errors = []

        # Restore backed-up files
        for backup in reversed(txn.backups):
            try:
                if backup.backup_path.exists():
                    shutil.copy2(backup.backup_path, backup.original_path)
                    logger.debug(f"Restored {backup.original_path} from backup")
            except Exception as e:
                errors.append(f"Failed to restore {backup.original_path}: {e}")

        # Remove created files
        for created_path in txn.created_files:
            try:
                if created_path.exists() and created_path not in [
                    b.original_path for b in txn.backups
                ]:
                    created_path.unlink()
                    logger.debug(f"Removed created file {created_path}")
            except Exception as e:
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
        except Exception as e:
            logger.warning(f"Failed to cleanup transaction {txn.transaction_id}: {e}")

        # Remove from active transactions
        if txn.transaction_id in self._active_transactions:
            del self._active_transactions[txn.transaction_id]

    @contextmanager
    def atomic_transaction(
        self,
        operation_name: str,
        cleanup_on_success: bool = True,
    ):
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
        txn_id = self._generate_transaction_id()
        txn = AtomicTransaction(transaction_id=txn_id)
        self._active_transactions[txn_id] = txn

        logger.info(f"Starting atomic transaction {txn_id} for '{operation_name}'")

        try:
            yield txn

            # Commit on success
            txn.committed = True
            logger.info(
                f"Transaction {txn_id} committed successfully. "
                f"Modified: {len(txn.modified_files)}, Created: {len(txn.created_files)}"
            )

            if cleanup_on_success:
                self._cleanup_transaction(txn)

        except Exception as e:
            txn.error = str(e)
            logger.error(f"Transaction {txn_id} failed: {e}")

            # Rollback
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

        # Backup existing file
        if file_path.exists():
            self._backup_file(txn, file_path)
            txn.modified_files.add(file_path)
        else:
            txn.created_files.add(file_path)

        # Write new content
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding=encoding)
            logger.debug(f"Atomic write to {file_path}")
        except Exception as e:
            raise AtomicExecutionError(
                f"Write failed for {file_path}: {e}",
                txn.transaction_id,
            ) from e

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

        # Backup before delete
        self._backup_file(txn, file_path)
        txn.modified_files.add(file_path)

        try:
            file_path.unlink()
            logger.debug(f"Atomic delete of {file_path}")
        except Exception as e:
            raise AtomicExecutionError(
                f"Delete failed for {file_path}: {e}",
                txn.transaction_id,
            ) from e

    def atomic_rename(
        self,
        txn: AtomicTransaction,
        src_path: Path,
        dst_path: Path,
    ) -> None:
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
            raise AtomicExecutionError(
                f"Source file does not exist: {src_path}",
                txn.transaction_id,
            )

        # Backup source
        self._backup_file(txn, src_path)
        txn.modified_files.add(src_path)

        # Backup destination if exists
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

    def get_active_transactions(self) -> Dict[str, AtomicTransaction]:
        """Get all active transactions for monitoring."""
        return dict(self._active_transactions)


__all__ = [
    "AtomicExecutionMixin",
    "AtomicExecutionError",
    "AtomicTransaction",
    "FileBackup",
]
