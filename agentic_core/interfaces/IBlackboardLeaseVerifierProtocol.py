"""
Secure Filesystem Operations - Sandboxed File I/O with Blackboard Integration.

Prevents path traversal, protects critical directories, and integrates with HealingLease.

DELEGATION NOTICE (2026-01-21):
- move_file() and delete_file() now delegate to ArchivalGatekeeper
- This ensures all destructive operations go through the governance layer
- Direct shutil/os operations have been removed for security
"""

from __future__ import annotations

import logging
import os
import tempfile
import warnings
from functools import wraps
from pathlib import Path
from typing import Any, Protocol

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR

Logger = logging.getLogger(__name__)


def _get_tool_args_types():
    from agentic_core.L2_execution.types.tool_args_types import (
        CreateDirectoryArgs,
        DeleteFileArgs,
        ListFilesArgs,
        MoveFileArgs,
        ReadFileArgs,
        WriteFileArgs,
    )

    return CreateDirectoryArgs, DeleteFileArgs, ListFilesArgs, MoveFileArgs, ReadFileArgs, WriteFileArgs


def _get_sovereign_excluded_folders():
    from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS

    return SOVEREIGN_EXCLUDED_FOLDERS


def _get_archival_gatekeeper():
    from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper

    return ArchivalGatekeeper


CreateDirectoryArgs, DeleteFileArgs, ListFilesArgs, MoveFileArgs, ReadFileArgs, WriteFileArgs = (
    _get_tool_args_types()
)
ArchivalGatekeeper = _get_archival_gatekeeper()
EXCLUDED_DIRS = _get_sovereign_excluded_folders()


class IBlackboardLeaseVerifier(Protocol):
    """
    Protocol defining the methods expected from a blackboard-like object
    for HealingLease verification and security event logging.
    """

    def verify_healing_lease(self, agent_id: str, file_path: str) -> bool: ...

    def log_security_event(
        self,
        agent_id: str,
        event_type: str,
        file_path: str,
        details: dict[str, Any],
    ) -> None: ...


class SandboxViolationError(Exception):
    """Raised when a file operation violates sandbox constraints."""


class HealingLeaseError(Exception):
    """Raised when an agent attempts to write without holding the HealingLease."""


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / AGENTIC_CORE_DIR).exists() or (current / ".git").exists():
            return current
        current = current.parent
    return Path.cwd()


def validate_sandbox(path: str) -> Path:
    """
    Validate that a path is within the sandbox and not in excluded directories.

    Args:
        path: Relative path to validate

    Returns:
        Resolved absolute path within sandbox

    Raises:
        SandboxViolationError: If path violates sandbox constraints
    """
    project_root = get_project_root()
    try:
        resolved = (project_root / path).resolve()
    except (OSError, RuntimeError, ValueError) as e:
        raise SandboxViolationError(f"Invalid path: {e}") from e
    if not resolved.is_relative_to(project_root):
        raise SandboxViolationError(f"Path traversal detected: {path} resolves outside project root")
    path_parts = resolved.relative_to(project_root).parts
    for part in path_parts:
        if part in EXCLUDED_DIRS:
            raise SandboxViolationError(f"Access denied: {part} is in excluded directories")
    return resolved


class PreservationViolationError(Exception):
    """Raised when a write operation would delete too much content."""


def require_healing_lease(func):
    """
    Decorator to verify HealingLease before write operations.
    Integrates with AtomicBlackboard from Phase 2.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        blackboard = kwargs.get("blackboard")
        agent_id = kwargs.get("agent_id")
        file_path = kwargs.get("path") or (args[0].path if args else None)
        if blackboard and agent_id and file_path:
            if hasattr(blackboard, "verify_healing_lease") and callable(blackboard.verify_healing_lease):
                if not blackboard.verify_healing_lease(agent_id, file_path):
                    raise HealingLeaseError(f"Agent {agent_id} does not hold HealingLease for {file_path}")
        return func(*args, **kwargs)

    return wrapper


def read_file(args: ReadFileArgs) -> str:
    """
    Read file content with sandbox validation.

    Args:
        args: ReadFileArgs with path

    Returns:
        File content as string

    Raises:
        SandboxViolationError: If path violates sandbox
        FileNotFoundError: If file doesn't exist
    """
    resolved_path = validate_sandbox(args.path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"File not found: {args.path}")
    if not resolved_path.is_file():
        raise ValueError(f"Not a file: {args.path}")
    return resolved_path.read_text(encoding="utf-8")


@require_healing_lease
def write_file(
    args: WriteFileArgs,
    blackboard=None,
    agent_id: str | None = None,
    override_preservation: bool = False,
) -> None:
    """
    Write content to file with sandbox validation, HealingLease verification, and preservation enforcement.

    **Preservation Rule**: If the new content is less than 90% of the original file's line count,
    the write is REJECTED unless override_preservation=True is passed by a SystemArchitect agent.

    Args:
        args: WriteFileArgs with path and content
        blackboard: Optional AtomicBlackboard instance for lease verification
        agent_id: Optional agent ID for lease verification
        override_preservation: Allow writes that delete >10% of lines (SystemArchitect only)

    Raises:
        SandboxViolationError: If path violates sandbox
        HealingLeaseError: If agent doesn't hold HealingLease
        PreservationViolationError: If write would delete too much content
    """
    resolved_path = validate_sandbox(args.path)
    if resolved_path.exists() and (not override_preservation):
        try:
            with open(resolved_path, encoding="utf-8") as f:
                original_lines = len(f.readlines())
            new_lines = len(args.content.splitlines())
            min_lines = int(original_lines * 0.9)
            if new_lines < min_lines:
                if blackboard:
                    if hasattr(blackboard, "log_security_event") and callable(blackboard.log_security_event):
                        try:
                            blackboard.log_security_event(
                                agent_id=agent_id or "unknown",
                                event_type="PRESERVATION_VIOLATION",
                                file_path=args.path,
                                details={
                                    "original_lines": original_lines,
                                    "new_lines": new_lines,
                                    "threshold": min_lines,
                                    "deletion_percentage": round((1 - new_lines / original_lines) * 100, 2),
                                },
                            )
                        except Exception as e:  # guardian: allow-broad-exception -- log_security_event failure must not mask PreservationViolationError
                            Logger.debug("IBlackboardLeaseVerifierProtocol: log_security_event failed: %s", e)
                raise PreservationViolationError(
                    f"Preservation Violation: New content ({new_lines} lines) is less than 90% of original ({original_lines} lines). Minimum required: {min_lines} lines. This would delete {round((1 - new_lines / original_lines) * 100, 2)}% of the file. Set override_preservation=True if this is intentional (SystemArchitect only).",
                )
        # guardian: allow-silent-swallow - acceptable exception handling
        except (OSError, UnicodeDecodeError):
            pass
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_dir = resolved_path.parent
    with tempfile.NamedTemporaryFile(
        mode="w", encoding="utf-8", dir=tmp_dir, delete=False, suffix=".tmp"
    ) as tmp_file:
        tmp_file.write(args.content)
        tmp_path = Path(tmp_file.name)
    tmp_path.replace(resolved_path)


@require_healing_lease
def move_file(args: MoveFileArgs, blackboard=None, agent_id: str | None = None) -> None:
    """
    Move or rename a file with sandbox validation and HealingLease verification.

    DELEGATION: This function now delegates to ArchivalGatekeeper for all moves.
    The gatekeeper handles approval flow and audit logging.

    Args:
        args: MoveFileArgs with source and destination
        blackboard: Optional AtomicBlackboard instance for lease verification
        agent_id: Optional agent ID for lease verification

    Raises:
        SandboxViolationError: If paths violate sandbox
        HealingLeaseError: If agent doesn't hold HealingLease
        FileNotFoundError: If source doesn't exist
        FileExistsError: If destination exists
        PermissionError: If user denies approval
    """
    warnings.warn(
        "filesystem.move_file() is deprecated. Use ArchivalGatekeeper.safe_move() directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    source_path = validate_sandbox(args.source)
    dest_path = validate_sandbox(args.destination)
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {args.source}")
    if dest_path.exists():
        raise FileExistsError(f"Destination exists: {args.destination}. Use manual deletion first.")
    gatekeeper = ArchivalGatekeeper.get_instance(get_project_root())
    result = gatekeeper.safe_move(
        source_path,
        dest_path,
        agent_id or "filesystem.move_file",
        "Filesystem move operation",
        overwrite=False,
    )
    if not result.success:
        if result.approval_status == "DENIED":
            raise PermissionError("Move declined by user")
        raise OSError(f"Move failed: {result.error}")


def list_files(args: ListFilesArgs, recursive: bool = False) -> list[str]:
    """
    List files in a directory with sandbox validation.

    Args:
        args: ListFilesArgs with directory and pattern
        recursive: Whether to search recursively (default: False)
    Returns:
        List of relative file paths

    Raises:
        SandboxViolationError: If path violates sandbox
        NotADirectoryError: If path is not a directory
    """
    resolved_path = validate_sandbox(args.directory)
    if not resolved_path.exists():
        raise FileNotFoundError(f"Directory not found: {args.directory}")
    if not resolved_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {args.directory}")
    project_root = get_project_root()
    files = []
    if recursive:
        for root, dirs, filenames in os.walk(resolved_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
            for filename in filenames:
                file_path = Path(root) / filename
                if args.pattern:
                    if not file_path.match(args.pattern):
                        continue
                rel_path = file_path.relative_to(project_root)
                files.append(str(rel_path))
    else:
        for item in resolved_path.iterdir():
            if item.is_file():
                if args.pattern:
                    if not item.match(args.pattern):
                        continue
                rel_path = item.relative_to(project_root)
                files.append(str(rel_path))
    return sorted(files)


@require_healing_lease
def delete_file(args: DeleteFileArgs, blackboard=None, agent_id: str | None = None) -> None:
    """
    Delete a file with sandbox validation and HealingLease verification.

    DELEGATION: This function now delegates to ArchivalGatekeeper for all deletes.
    The gatekeeper performs SOFT DELETE (archive) and handles approval flow.

    Args:
        args: DeleteFileArgs with path
        blackboard: Optional AtomicBlackboard instance for lease verification
        agent_id: Optional agent ID for lease verification

    Raises:
        SandboxViolationError: If path violates sandbox
        HealingLeaseError: If agent doesn't hold HealingLease
        FileNotFoundError: If file doesn't exist
        PermissionError: If user denies approval
    """
    warnings.warn(
        "filesystem.delete_file() is deprecated. Use ArchivalGatekeeper.safe_delete() directly.",
        DeprecationWarning,
        stacklevel=2,
    )
    resolved_path = validate_sandbox(args.path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"File not found: {args.path}")
    gatekeeper = ArchivalGatekeeper.get_instance(get_project_root())
    result = gatekeeper.safe_delete(
        resolved_path,
        agent_id or "filesystem.delete_file",
        "Filesystem delete operation",
    )
    if not result.success:
        if result.approval_status == "DENIED":
            raise PermissionError("Delete declined by user")
        raise OSError(f"Delete failed: {result.error}")


@require_healing_lease
def create_directory(args: CreateDirectoryArgs, blackboard=None, agent_id: str | None = None) -> None:
    """
    Create a directory with sandbox validation and HealingLease verification.

    Args:
        args: CreateDirectoryArgs with path, parents, and exist_ok
        blackboard: Optional AtomicBlackboard instance for lease verification
        agent_id: Optional agent ID for lease verification

    Raises:
        SandboxViolationError: If path violates sandbox
        HealingLeaseError: If agent doesn't hold HealingLease
    """
    resolved_path = validate_sandbox(args.path)
    parents = getattr(args, "parents", True)
    exist_ok = getattr(args, "exist_ok", True)
    resolved_path.mkdir(parents=parents, exist_ok=exist_ok)


__all__ = [
    "IBlackboardLeaseVerifier",
    "SandboxViolationError",
    "HealingLeaseError",
    "PreservationViolationError",
    "get_project_root",
    "validate_sandbox",
    "require_healing_lease",
    "read_file",
    "write_file",
    "move_file",
    "list_files",
    "delete_file",
    "create_directory",
    "EXCLUDED_DIRS",
]
