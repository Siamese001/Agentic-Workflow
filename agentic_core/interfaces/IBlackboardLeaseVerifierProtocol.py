"""
Secure filesystem operations with sandbox validation and healing lease checks.
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
    def verify_healing_lease(self, agent_id: str, file_path: str) -> bool: ...

    def log_security_event(
        self,
        agent_id: str,
        event_type: str,
        file_path: str,
        details: dict[str, Any] | None = None,
    ) -> None: ...


class SandboxViolationError(Exception):
    """Raised when a file operation violates sandbox constraints."""


class HealingLeaseError(Exception):
    """Raised when an agent attempts to write without holding the HealingLease."""


def get_project_root() -> Path:
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / AGENTIC_CORE_DIR).exists() or (current / ".git").exists():
            return current
        current = current.parent
    raise RuntimeError("Project root not found.")


def validate_sandbox(path: str) -> Path:
    project_root = get_project_root()
    try:
        resolved = (project_root / path).resolve()
        resolved.relative_to(project_root)
    except (OSError, RuntimeError, ValueError) as exc:
        raise SandboxViolationError(f"Invalid sandbox path {path!r}: {exc}") from exc

    for part in resolved.relative_to(project_root).parts:
        if part in EXCLUDED_DIRS:
            raise SandboxViolationError(f"Access denied: {part} is in excluded directories")
    return resolved


class PreservationViolationError(Exception):
    """Raised when a write operation would delete too much content."""


def require_healing_lease(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        blackboard = kwargs.get("blackboard")
        agent_id = kwargs.get("agent_id")
        file_path = kwargs.get("path") or (args[0].path if args else None)
        if blackboard and agent_id and file_path:
            verifier = getattr(blackboard, "verify_healing_lease", None)
            if callable(verifier) and not verifier(agent_id, file_path):
                raise HealingLeaseError(f"Agent {agent_id} does not hold HealingLease for {file_path}")
        return func(*args, **kwargs)

    return wrapper


def read_file(args: ReadFileArgs) -> str:
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
    resolved_path = validate_sandbox(args.path)
    if resolved_path.exists() and not override_preservation:
        try:
            original_lines = len(resolved_path.read_text(encoding="utf-8").splitlines())
            new_lines = len(args.content.splitlines())
            min_lines = int(original_lines * 0.9)
            if new_lines < min_lines:
                logger = getattr(blackboard, "log_security_event", None)
                if callable(logger):
                    try:
                        logger(
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
                    except Exception as exc:  # guardian: allow-broad-exception -- log_security_event failure must not mask PreservationViolationError
                        Logger.debug("Security logging failed: %s", exc)
                raise PreservationViolationError(
                    "Preservation violation: replacement content would delete too much of the file."
                )
        except (OSError, UnicodeDecodeError) as exc:
            Logger.debug("Preservation pre-check skipped for %s: %s", args.path, exc)
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
