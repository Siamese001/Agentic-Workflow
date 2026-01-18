from __future__ import annotations
"""
Secure Filesystem Operations - Sandboxed File I/O with Blackboard Integration
Prevents path traversal, protects critical directories, and integrates with HealingLease.
"""
import logging
import os
import re
from functools import wraps
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol, Set

# [SSOT IMPORT] Structure blueprint is the single source of truth
from agentic_core.L5_safety.validators.structure_blueprint_1 import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

from agentic_core.L2_execution.ToolRegistry.definitions import (
    CreateDirectoryArgs,
    DeleteFileArgs,
    ListFilesArgs,
    MoveFileArgs,
    ReadFileArgs,
    WriteFileArgs,
)


# Define a Protocol for the Blackboard interface required by this module
# NAMING FIXED: BlackboardLeaseVerifier → blackboard_lease_verifier
class blackboard_lease_verifier(Protocol):
    """
    Protocol defining the methods expected from a blackboard-like object
    for HealingLease verification and security event logging.
    """
    def verify_healing_lease(self, agent_id: str, file_path: str) -> bool:
                    
        ...
    def log_security_event(self, agent_id: str, event_type: str, file_path: str, details: Dict[str, Any]) -> None:
                    
        ...


EXCLUDED_DIRS: Set[str] = {
    '.git',
    '__pycache__',
    '.pytest_cache',
    'node_modules',
    '.venv',
    'venv',
    'env',
    'archives',
    'data',
    '.idea',
    '.vscode',
    'build',
    'dist',
    'eggs',
}


# NAMING FIXED: SandboxViolationError → sandbox_violation_error
class sandbox_violation_error(Exception):
    """Raised when a file operation violates sandbox constraints."""


# NAMING FIXED: HealingLeaseError → healing_lease_error
class healing_lease_error(Exception):
    """Raised when an agent attempts to write without holding the HealingLease."""


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).resolve()
    while current.parent != current:
        if (current / 'agentic_core').exists() or (current / '.git').exists():
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
    except Exception as e:
        raise SandboxViolationError(f"Invalid path: {e}")
    
    if not str(resolved).startswith(str(project_root)):
        raise SandboxViolationError(
            f"Path traversal detected: {path} resolves outside project root"
        )
    
    path_parts = resolved.relative_to(project_root).parts
    for part in path_parts:
        if part in EXCLUDED_DIRS:
            raise SandboxViolationError(
                f"Access denied: {part} is in excluded directories"
            )
    
    return resolved


# NAMING FIXED: PreservationViolationError → preservation_violation_error
class preservation_violation_error(Exception):
    """Raised when a write operation would delete too much content."""


def require_healing_lease(func):
    """
    Decorator to verify HealingLease before write operations.
    Integrates with AtomicBlackboard from Phase 2.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
                    
        blackboard = kwargs.get('blackboard')
        agent_id = kwargs.get('agent_id')
        file_path = kwargs.get('path') or (args[0].path if args else None)
        
        if blackboard and agent_id and file_path:
            # Removed direct import of AtomicBlackboard to avoid architectural Violation.
            # Instead, check if the provided blackboard object has the required method (duck typing).
            if hasattr(blackboard, 'verify_healing_lease') and callable(blackboard.verify_healing_lease):
                if not blackboard.verify_healing_lease(agent_id, file_path):
                    raise HealingLeaseError(
                        f"Agent {agent_id} does not hold HealingLease for {file_path}"
                    )
        
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
    
    with open(resolved_path, 'r', encoding='utf-8') as f:
        return f.read()


@require_healing_lease
def write_file(
    args: WriteFileArgs,
    blackboard=None,
    agent_id: Optional[str] = None,
    override_preservation: bool = False
) -> None:
    """
    Write content to file with sandbox validation, HealingLease verification, and preservation enforcement.
    
    **Preservation Rule**: If the new content is less than 90% of the original file's line count,
    the write is REJECTED unless override_preservation=True is passed by a SystemArchitect agent.
    
    Args:
        args: WriteFileArgs with path, content, and options
        blackboard: Optional AtomicBlackboard instance for lease verification
        agent_id: Optional agent ID for lease verification
        override_preservation: Allow writes that delete >10% of lines (SystemArchitect only)
        
    Raises:
        SandboxViolationError: If path violates sandbox
        HealingLeaseError: If agent doesn't hold HealingLease
        PreservationViolationError: If write would delete too much content
    """
    resolved_path = validate_sandbox(args.path)
    
    # Preservation enforcement: Check line count if file exists
    if resolved_path.exists() and not override_preservation:
        try:
            with open(resolved_path, 'r', encoding='utf-8') as f:
                original_lines = len(f.readlines())
            
            new_lines = len(args.content.splitlines())
            
            # Require at least 90% of original line count
            min_lines = int(original_lines * 0.9)
            
            if new_lines < min_lines:
                # Log to AtomicBlackboard if available and has the method
                if blackboard:
                    if hasattr(blackboard, 'log_security_event') and callable(blackboard.log_security_event):
                        try:
                            blackboard.log_security_event(
                                agent_id=agent_id or "unknown",
                                event_type="PRESERVATION_VIOLATION",
                                file_path=args.path,
                                details={
                                    "original_lines": original_lines,
                                    "new_lines": new_lines,
                                    "threshold": min_lines,
                                    "deletion_percentage": round((1 - new_lines/original_lines) * 100, 2)
                                }
                            )
                        except Exception:
                            # Catch any errors during logging itself
                            pass
                
                raise PreservationViolationError(
                    f"Preservation Violation: New content ({new_lines} lines) is less than 90% "
                    f"of original ({original_lines} lines). Minimum required: {min_lines} lines. "
                    f"This would delete {round((1 - new_lines/original_lines) * 100, 2)}% of the file. "
                    f"Set override_preservation=True if this is intentional (SystemArchitect only)."
                )
        except (IOError, UnicodeDecodeError):
            # If we can't read the file, allow the write
            pass
    
    if args.create_dirs:
        resolved_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(resolved_path, 'w', encoding='utf-8') as f:
        f.write(args.content)


@require_healing_lease
def move_file(
    args: MoveFileArgs,
    blackboard=None,
    agent_id: Optional[str] = None
) -> None:
    """
    Move or rename a file with sandbox validation and HealingLease verification.
    
    Args:
        args: MoveFileArgs with source, destination, and options
        blackboard: Optional AtomicBlackboard instance for lease verification
        agent_id: Optional agent ID for lease verification
        
    Raises:
        SandboxViolationError: If paths violate sandbox
        HealingLeaseError: If agent doesn't hold HealingLease
        FileNotFoundError: If source doesn't exist
        FileExistsError: If destination exists and overwrite=False
    """
    source_path = validate_sandbox(args.source)
    dest_path = validate_sandbox(args.destination)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source not found: {args.source}")
    
    if dest_path.exists() and not args.overwrite:
        raise FileExistsError(
            f"Destination exists: {args.destination}. Set overwrite=True to replace."
        )
    
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), str(dest_path))


def list_files(args: ListFilesArgs) -> List[str]:
    """
    List files in a directory with sandbox validation.
    
    Args:
        args: ListFilesArgs with path, pattern, and options
    Returns:
        List of relative file paths
        
    Raises:
        SandboxViolationError: If path violates sandbox
        NotADirectoryError: If path is not a directory
    """
    resolved_path = validate_sandbox(args.path)
    
    if not resolved_path.exists():
        raise FileNotFoundError(f"Directory not found: {args.path}")
    
    if not resolved_path.is_dir():
        raise NotADirectoryError(f"Not a directory: {args.path}")
    
    project_root = get_project_root()
    files = []
    
    if args.recursive:
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
def delete_file(
    args: DeleteFileArgs,
    blackboard=None,
    agent_id: Optional[str] = None
) -> None:
    """
    Delete a file with sandbox validation and HealingLease verification.
    
    Args:
        args: DeleteFileArgs with path
        blackboard: Optional AtomicBlackboard instance for lease verification
        agent_id: Optional agent ID for lease verification
        
    Raises:
        SandboxViolationError: If path violates sandbox
        HealingLeaseError: If agent doesn't hold HealingLease
        FileNotFoundError: If file doesn't exist
    """
    resolved_path = validate_sandbox(args.path)
    
    if not resolved_path.exists():
        raise FileNotFoundError(f"File not found: {args.path}")
    
    if resolved_path.is_dir():
        raise IsADirectoryError(f"Cannot delete directory with delete_file: {args.path}")
    
    resolved_path.unlink()


def create_directory(args: CreateDirectoryArgs) -> None:
    """
    Create a directory with sandbox validation.
    
    Args:
        args: CreateDirectoryArgs with path and options
        
    Raises:
        SandboxViolationError: If path violates sandbox
    """
    resolved_path = validate_sandbox(args.path)
    resolved_path.mkdir(parents=args.parents, exist_ok=True)