from __future__ import annotations

# ruff: noqa: E501, E402

"""
ArchivalGatekeeper - Centralized Service for Destructive File Operations

This module provides a singleton service that handles ALL destructive file operations
(move, delete, archive) across the entire codebase. This prevents "God Object" creation
by centralizing file operation logic while keeping agents focused on their domain.

DESIGN PRINCIPLES:
1. Singleton/Static Service - Single point of control for all file operations
2. Safe Deletion - 'delete' actually moves to timestamped archive (soft delete)
3. Audit Logging - Every operation is logged with full context
4. No Hard Deletes - Hard delete is banned; all removals go to archive

USAGE:

    gatekeeper = ArchivalGatekeeper.get_instance(project_root)
    result = gatekeeper.safe_move(src, dst, "MyAgent", "Relocating to correct territory")
    result = gatekeeper.safe_archive(src, "MyAgent", "File violates depth rules")
    result = gatekeeper.safe_delete(src, "MyAgent", "Duplicate file removal")

Territory: agentic_core/L5_safety/enforcement/
"""


import json
import logging
import os
import shutil
import threading
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from agentic_core.L5_safety.config.structure_blueprint_config import ARCHIVES_DIR

# Configure module logger
logging.basicConfig(level=logging.INFO)
Logger = logging.getLogger(__name__)

# Environment variable for batch mode (auto-approve all operations)
ARCHIVE_BATCH_ACCEPT_ENV = "ARCHIVE_BATCH_ACCEPT"


class ArchivalOperation(Enum):
    """Types of archival operations."""

    MOVE = "MOVE"
    ARCHIVE = "ARCHIVE"
    DELETE = "DELETE"  # Soft delete - actually archives


@dataclass
class ArchivalResult:
    """Result of an archival operation."""

    success: bool
    operation: ArchivalOperation
    source_path: Path
    destination_path: Path | None = None
    requester_agent: str = ""
    reason: str = ""
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    error: str | None = None
    approval_status: str = "PENDING"  # PENDING, APPROVED, DENIED, BATCH_APPROVED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "success": self.success,
            "operation": self.operation.value,
            "source_path": str(self.source_path),
            "destination_path": str(self.destination_path) if self.destination_path else None,
            "requester_agent": self.requester_agent,
            "reason": self.reason,
            "timestamp": self.timestamp,
            "error": self.error,
            "approval_status": self.approval_status,
        }


class ArchivalGatekeeper:
    """
    Singleton service for all destructive file operations.

    This gatekeeper ensures:
    - All file moves/deletes/archives go through a single point
    - Every operation is logged with full audit trail
    - 'Delete' operations are soft deletes (move to archive)
    - Hard deletes are banned to prevent data loss

    Thread-safe singleton implementation.
    """

    _instance: ArchivalGatekeeper | None = None
    _lock: threading.Lock = threading.Lock()
    _log_lock: threading.Lock = threading.Lock()

    # Archive folder structure - uses .healing_backups/ (gitignored, not indexed)
    # [REFACTOR 2026-02-05] Changed from archives/ to .healing_backups/
    ARCHIVE_ROOT_NAME = ARCHIVES_DIR  # Now resolves to ".healing_backups"
    ARCHIVE_SUBDIR = "gatekeeper"  # Subdirectory within archives for gatekeeper operations
    AUDIT_LOG_NAME = "archival_audit.jsonl"

    def __init__(self, project_root: Path):
        """
        Initialize the gatekeeper.

        NOTE: Use get_instance() instead of direct instantiation.

        Args:
            project_root: Root directory of the project
        """
        self.project_root = Path(project_root).resolve()
        # Use .healing_backups/gatekeeper path (gitignored, not indexed)
        self.archive_root = self.project_root / self.ARCHIVE_ROOT_NAME / self.ARCHIVE_SUBDIR
        self.audit_log_path = self.archive_root / self.AUDIT_LOG_NAME
        self._operation_count = 0

        # Governance settings
        self._require_approval = True  # Can be disabled for testing
        self._input_func: Callable[[str], str] = input  # Mockable for testing
        self._l4_ledger_hook: Callable[[ArchivalResult], None] | None = None

        # Ensure archive directory exists
        self.archive_root.mkdir(parents=True, exist_ok=True)

        Logger.info(f"[ArchivalGatekeeper] Initialized with project_root: {self.project_root}")
        Logger.info(f"[ArchivalGatekeeper] Archive root: {self.archive_root}")

    @classmethod
    def get_instance(cls, project_root: Path | None = None) -> ArchivalGatekeeper:
        """
        Get the singleton instance of ArchivalGatekeeper.

        Args:
            project_root: Root directory (required on first call)

        Returns:
            The singleton ArchivalGatekeeper instance

        Raises:
            ValueError: If project_root not provided on first call
        """
        with cls._lock:
            if cls._instance is None:
                if project_root is None:
                    raise ValueError("project_root must be provided on first call to get_instance()")
                cls._instance = cls(project_root)
            return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        """Reset the singleton instance (primarily for testing)."""
        with cls._lock:
            cls._instance = None

    def _get_archive_path(self, source_path: Path) -> Path:
        """
        Generate archive path for a file.

        Structure: .archive/{YYYY-MM-DD}/{original_relative_path}

        Args:
            source_path: Original file path

        Returns:
            Path in archive directory
        """
        date_folder = datetime.now().strftime("%Y-%m-%d")

        # Get relative path from project root
        try:
            rel_path = source_path.relative_to(self.project_root)
        except ValueError:
            # File is outside project root, use full path
            rel_path = Path(str(source_path).replace(":", "_").lstrip("/\\"))

        archive_path = self.archive_root / date_folder / rel_path
        return archive_path

    def _log_operation(self, result: ArchivalResult) -> None:
        """
        Log operation to audit log (JSONL format).

        Thread-safe: Uses _log_lock to prevent log corruption from concurrent writes.

        Args:
            result: The operation result to log
        """
        with self._log_lock:
            try:
                with open(self.audit_log_path, "a", encoding="utf-8") as f:
                    f.write(json.dumps(result.to_dict()) + "\n")
            except Exception as e:
                Logger.error(f"[ArchivalGatekeeper] Failed to write audit log: {e}")

            # Also log to standard logger
            status = "SUCCESS" if result.success else "FAILED"
            Logger.info(
                f"[ArchivalGatekeeper] [{status}] {result.operation.value}: "
                f"{result.source_path} -> {result.destination_path} "
                f"(requester: {result.requester_agent}, reason: {result.reason})",
            )

    def _validate_path(self, path: Path, operation: str, allow_archive: bool = False) -> str | None:
        """
        Validate a path before operation.

        Args:
            path: Path to validate
            operation: Name of operation for error message
            allow_archive: If True, allow operations on archive directory (for restore)

        Returns:
            Error message if invalid, None if valid
        """
        # Check if path exists (for source operations)
        if not path.exists():
            return f"Source path does not exist: {path}"

        # Prevent operations on archive directory itself (unless restoring)
        if not allow_archive:
            try:
                path.relative_to(self.archive_root)
                return f"Cannot {operation} files within archive directory: {path}"
            except ValueError:
                pass  # Path is not in archive, which is good

        # Prevent operations on critical system files
        critical_patterns = [".git", "__pycache__", ".venv", "venv", "node_modules"]
        for pattern in critical_patterns:
            if pattern in path.parts:
                return f"Cannot {operation} files in protected directory ({pattern}): {path}"

        return None

    # ========================================================================
    # GOVERNANCE LAYER - Approval Flow & L4 Ledger Integration
    # ========================================================================

    def _is_batch_mode(self) -> bool:
        """
        Check if batch mode is enabled via environment variable.

        [PHASE 33j] Checks both ARCHIVE_BATCH_ACCEPT and SOVEREIGN_AUTO_APPROVE.
        When either is set to "1", all operations are auto-approved without prompts.

        Returns:
            True if batch mode is enabled
        """
        return (
            os.environ.get(ARCHIVE_BATCH_ACCEPT_ENV, "").strip() == "1"
            or os.environ.get("SOVEREIGN_AUTO_APPROVE") == "1"
        )

    def _request_approval(self, result: ArchivalResult) -> bool:
        """
        Request user approval for a destructive operation.

        Displays operation details and waits for (y/n) input.
        Auto-approves if ARCHIVE_BATCH_ACCEPT=1 is set.

        Args:
            result: The pending operation result (pre-populated with details)

        Returns:
            True if approved, False if denied
        """
        # Check batch mode first
        if self._is_batch_mode():
            result.approval_status = "BATCH_APPROVED"
            Logger.info(f"[ArchivalGatekeeper] BATCH_APPROVED: {result.operation.value} {result.source_path}")
            return True

        # Skip approval if disabled (for testing without mocking input)
        if not self._require_approval:
            result.approval_status = "APPROVED"
            return True

        # Display operation details
        print("\n" + "=" * 70)
        print("🔒 ARCHIVAL GATEKEEPER - APPROVAL REQUIRED")
        print("=" * 70)
        print(f"  Operation:   {result.operation.value}")
        print(f"  Requester:   {result.requester_agent}")
        print(f"  Source:      {result.source_path}")
        if result.destination_path:
            print(f"  Destination: {result.destination_path}")
        print(f"  Reason:      {result.reason}")
        print("=" * 70)

        # Get user input
        try:
            response = self._input_func("Approve this operation? (y/n): ").strip().lower()
            approved = response in ("y", "yes")

            if approved:
                result.approval_status = "APPROVED"
                Logger.info(
                    f"[ArchivalGatekeeper] User APPROVED: {result.operation.value} {result.source_path}",
                )
            else:
                result.approval_status = "DENIED"
                Logger.info(
                    f"[ArchivalGatekeeper] User DENIED: {result.operation.value} {result.source_path}",
                )

            return approved

        except (EOFError, KeyboardInterrupt):
            # Handle non-interactive environments gracefully
            result.approval_status = "DENIED"
            Logger.warning(
                f"[ArchivalGatekeeper] Non-interactive environment, DENIED: {result.operation.value}",
            )
            return False

    def set_l4_ledger_hook(self, hook: Callable[[ArchivalResult], None]) -> None:
        """
        Register a callback for L4 Ledger integration.

        The hook will be called after each operation with the full result,
        allowing the L4 Ledger to capture before/after state.

        Args:
            hook: Callable that receives ArchivalResult
        """
        self._l4_ledger_hook = hook
        Logger.info("[ArchivalGatekeeper] L4 Ledger hook registered")

    def _notify_l4_ledger(self, result: ArchivalResult) -> None:
        """
        Notify L4 Ledger of an operation (if hook is registered).

        This captures the "before" and "after" state as mandated by
        the Rationalization Report.

        Args:
            result: The completed operation result
        """
        if self._l4_ledger_hook is not None:
            try:
                self._l4_ledger_hook(result)
                Logger.debug(f"[ArchivalGatekeeper] L4 Ledger notified: {result.operation.value}")
            except Exception as e:
                Logger.error(f"[ArchivalGatekeeper] L4 Ledger hook failed: {e}")

    def set_input_function(self, func: Callable[[str], str]) -> None:
        """
        Set a custom input function (for testing).

        Args:
            func: Function that takes a prompt string and returns user input
        """
        self._input_func = func

    def set_require_approval(self, require: bool) -> None:
        """
        Enable or disable approval requirement.

        Args:
            require: If True, require user approval for operations
        """
        self._require_approval = require

    def safe_move(
        self,
        source: str | Path,
        destination: str | Path,
        requester_agent: str,
        reason: str,
        create_parents: bool = True,
        overwrite: bool = False,
    ) -> ArchivalResult:
        """
        Safely move a file or directory.

        Args:
            source: Source path
            destination: Destination path
            requester_agent: Name of the agent requesting the operation
            reason: Reason for the move
            create_parents: Create parent directories if needed
            overwrite: If False (default), fail if destination exists. Prevents silent overwrites.

        Returns:
            ArchivalResult with operation details
        """
        source = Path(source).resolve()
        destination = Path(destination).resolve()

        # Validate source
        error = self._validate_path(source, "move")
        if error:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.MOVE,
                source_path=source,
                destination_path=destination,
                requester_agent=requester_agent,
                reason=reason,
                error=error,
            )
            self._log_operation(result)
            return result

        # GOVERNANCE: Request approval BEFORE any file system changes
        pending_result = ArchivalResult(
            success=False,
            operation=ArchivalOperation.MOVE,
            source_path=source,
            destination_path=destination,
            requester_agent=requester_agent,
            reason=reason,
        )

        if not self._request_approval(pending_result):
            pending_result.error = "User denied approval"
            self._log_operation(pending_result)
            self._notify_l4_ledger(pending_result)
            return pending_result

        try:
            # Check destination existence to prevent silent overwrite
            if destination.exists() and not overwrite:
                raise FileExistsError(f"Destination already exists: {destination}")

            # Create parent directories if needed
            if create_parents:
                destination.parent.mkdir(parents=True, exist_ok=True)

            # If overwrite is True and dest exists, explicitly remove it
            # because shutil.move behavior varies (might nest directories)
            if destination.exists() and overwrite:
                if destination.is_dir():
                    shutil.rmtree(str(destination))
                else:
                    destination.unlink()

            # Perform the move
            shutil.move(str(source), str(destination))
            self._operation_count += 1

            result = ArchivalResult(
                success=True,
                operation=ArchivalOperation.MOVE,
                source_path=source,
                destination_path=destination,
                requester_agent=requester_agent,
                reason=reason,
                approval_status=pending_result.approval_status,
            )

        except Exception as e:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.MOVE,
                source_path=source,
                destination_path=destination,
                requester_agent=requester_agent,
                reason=reason,
                error=str(e),
                approval_status=pending_result.approval_status,
            )

        self._log_operation(result)
        self._notify_l4_ledger(result)
        return result

    def safe_archive(
        self,
        source: str | Path,
        requester_agent: str,
        reason: str,
    ) -> ArchivalResult:
        """
        Safely archive a file or directory.

        Moves the file to: .archive/{YYYY-MM-DD}/{original_relative_path}

        Args:
            source: Source path to archive
            requester_agent: Name of the agent requesting the operation
            reason: Reason for archiving

        Returns:
            ArchivalResult with operation details
        """
        source = Path(source).resolve()

        # Validate source
        error = self._validate_path(source, "archive")
        if error:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.ARCHIVE,
                source_path=source,
                requester_agent=requester_agent,
                reason=reason,
                error=error,
            )
            self._log_operation(result)
            return result

        # Generate archive path
        archive_path = self._get_archive_path(source)

        # GOVERNANCE: Request approval BEFORE any file system changes
        pending_result = ArchivalResult(
            success=False,
            operation=ArchivalOperation.ARCHIVE,
            source_path=source,
            destination_path=archive_path,
            requester_agent=requester_agent,
            reason=reason,
        )

        if not self._request_approval(pending_result):
            pending_result.error = "User denied approval"
            self._log_operation(pending_result)
            self._notify_l4_ledger(pending_result)
            return pending_result

        try:
            # Create parent directories
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle collision - add timestamp suffix if file exists
            if archive_path.exists():
                timestamp_suffix = datetime.now().strftime("_%H%M%S")
                stem = archive_path.stem
                suffix = archive_path.suffix
                archive_path = archive_path.parent / f"{stem}{timestamp_suffix}{suffix}"

            # Perform the archive (move to archive directory)
            shutil.move(str(source), str(archive_path))
            self._operation_count += 1

            result = ArchivalResult(
                success=True,
                operation=ArchivalOperation.ARCHIVE,
                source_path=source,
                destination_path=archive_path,
                requester_agent=requester_agent,
                reason=reason,
                approval_status=pending_result.approval_status,
            )

        except Exception as e:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.ARCHIVE,
                source_path=source,
                destination_path=archive_path,
                requester_agent=requester_agent,
                reason=reason,
                approval_status=pending_result.approval_status,
                error=str(e),
            )

        self._log_operation(result)
        self._notify_l4_ledger(result)
        return result

    def safe_delete(
        self,
        source: str | Path,
        requester_agent: str,
        reason: str,
    ) -> ArchivalResult:
        """
        Safely 'delete' a file or directory.

        NOTE: This is a SOFT DELETE - the file is moved to archive, not permanently deleted.
        Hard deletes are banned to prevent data loss.

        Args:
            source: Source path to delete
            requester_agent: Name of the agent requesting the operation
            reason: Reason for deletion

        Returns:
            ArchivalResult with operation details
        """
        source = Path(source).resolve()

        # Validate source
        error = self._validate_path(source, "delete")
        if error:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.DELETE,
                source_path=source,
                requester_agent=requester_agent,
                reason=reason,
                error=error,
            )
            self._log_operation(result)
            return result

        # Soft delete = archive with DELETE operation type
        archive_path = self._get_archive_path(source)

        # GOVERNANCE: Request approval BEFORE any file system changes
        pending_result = ArchivalResult(
            success=False,
            operation=ArchivalOperation.DELETE,
            source_path=source,
            destination_path=archive_path,
            requester_agent=requester_agent,
            reason=f"[SOFT DELETE] {reason}",
        )

        if not self._request_approval(pending_result):
            pending_result.error = "User denied approval"
            self._log_operation(pending_result)
            self._notify_l4_ledger(pending_result)
            return pending_result

        try:
            # Create parent directories
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Handle collision
            if archive_path.exists():
                timestamp_suffix = datetime.now().strftime("_%H%M%S")
                stem = archive_path.stem
                suffix = archive_path.suffix
                archive_path = archive_path.parent / f"{stem}{timestamp_suffix}{suffix}"

            # Perform soft delete (move to archive)
            shutil.move(str(source), str(archive_path))
            self._operation_count += 1

            result = ArchivalResult(
                success=True,
                operation=ArchivalOperation.DELETE,
                source_path=source,
                destination_path=archive_path,
                requester_agent=requester_agent,
                reason=f"[SOFT DELETE] {reason}",
                approval_status=pending_result.approval_status,
            )

        except Exception as e:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.DELETE,
                source_path=source,
                destination_path=archive_path,
                requester_agent=requester_agent,
                approval_status=pending_result.approval_status,
                reason=reason,
                error=str(e),
            )

        self._log_operation(result)
        self._notify_l4_ledger(result)
        return result

    def get_audit_log(self, limit: int = 100) -> list[dict[str, Any]]:
        """
        Get recent entries from the audit log.

        Args:
            limit: Maximum number of entries to return

        Returns:
            List of audit log entries (most recent first)
        """
        entries = []

        if not self.audit_log_path.exists():
            return entries

        try:
            with open(self.audit_log_path, encoding="utf-8") as f:
                lines = f.readlines()

            # Get last N entries
            for line in reversed(lines[-limit:]):
                try:
                    entries.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue

        except Exception as e:
            Logger.error(f"[ArchivalGatekeeper] Failed to read audit log: {e}")

        return entries

    def get_operation_count(self) -> int:
        """Get total number of operations performed."""
        return self._operation_count

    def restore_from_archive(
        self,
        archived_path: str | Path,
        requester_agent: str,
        reason: str,
    ) -> ArchivalResult:
        """
        Restore a file from the archive to its original location.

        Args:
            archived_path: Path to the archived file
            requester_agent: Name of the agent requesting the restore
            reason: Reason for restoration

        Returns:
            ArchivalResult with operation details
        """
        archived_path = Path(archived_path).resolve()

        # Verify file is in archive
        try:
            rel_to_archive = archived_path.relative_to(self.archive_root)
        except ValueError:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.MOVE,
                source_path=archived_path,
                requester_agent=requester_agent,
                reason=reason,
                error=f"File is not in archive directory: {archived_path}",
            )
            self._log_operation(result)
            return result

        # Extract original path (skip date folder)
        parts = rel_to_archive.parts
        if len(parts) < 2:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.MOVE,
                source_path=archived_path,
                requester_agent=requester_agent,
                reason=reason,
                error=f"Invalid archive path structure: {archived_path}",
            )
            self._log_operation(result)
            return result

        # Reconstruct original path (skip date folder)
        original_rel_path = Path(*parts[1:])
        original_path = self.project_root / original_rel_path

        # Direct restore (bypass normal validation since source is in archive)
        try:
            original_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(archived_path), str(original_path))
            self._operation_count += 1

            result = ArchivalResult(
                success=True,
                operation=ArchivalOperation.MOVE,
                source_path=archived_path,
                destination_path=original_path,
                requester_agent=requester_agent,
                reason=f"[RESTORE] {reason}",
            )
        except Exception as e:
            result = ArchivalResult(
                success=False,
                operation=ArchivalOperation.MOVE,
                source_path=archived_path,
                destination_path=original_path,
                requester_agent=requester_agent,
                reason=f"[RESTORE] {reason}",
                error=str(e),
            )

        self._log_operation(result)
        return result
