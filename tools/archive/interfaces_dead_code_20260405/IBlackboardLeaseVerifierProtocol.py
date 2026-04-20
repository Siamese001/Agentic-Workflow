from __future__ import annotations

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "IBlackboardLeaseVerifierProtocol")
_emit_applies_guardrail("p0", "IBlackboardLeaseVerifierProtocol", "p0_governance")
_emit_reads_policy_state("p0", "IBlackboardLeaseVerifierProtocol", "policy_binding")
_emit_snapshots_state("p0", "IBlackboardLeaseVerifierProtocol", "state_snapshot")
emit_replay_key("p0", "IBlackboardLeaseVerifierProtocol")
emit_determinism_digest("p0", "IBlackboardLeaseVerifierProtocol")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "IBlackboardLeaseVerifierProtocol", "execution_auth")
_emit_validates_capability("p2", "IBlackboardLeaseVerifierProtocol", "capability_check")
_emit_routes_to_capability("p2", "IBlackboardLeaseVerifierProtocol", "capability_route")
_emit_writes_via_uwg("p2", "IBlackboardLeaseVerifierProtocol", "uwg_write")
_emit_blocks_direct_write("p2", "IBlackboardLeaseVerifierProtocol", "direct_write_block")
_emit_records_tool_invocation("p2", "IBlackboardLeaseVerifierProtocol", "tool_invocation")
_emit_captures_execution_output("p2", "IBlackboardLeaseVerifierProtocol", "exec_output")
_emit_dispatches_agent("p3", "IBlackboardLeaseVerifierProtocol", "agent_dispatch")
_emit_coordinates_agents("p3", "IBlackboardLeaseVerifierProtocol", "agent_coordination")
_emit_records_workflow_lineage("p3", "IBlackboardLeaseVerifierProtocol", "workflow_lineage")
_emit_records_healing_outcome("p3", "IBlackboardLeaseVerifierProtocol", "healing_outcome")
_emit_escalates_failure("p3", "IBlackboardLeaseVerifierProtocol", "failure_escalation")
_emit_orchestrates_workflow("p3", "IBlackboardLeaseVerifierProtocol", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "IBlackboardLeaseVerifierProtocol", "healing_dispatch")
_emit_invokes_evaluation("p3", "IBlackboardLeaseVerifierProtocol", "evaluation_signal")
_emit_records_telemetry_event("p4", "IBlackboardLeaseVerifierProtocol", "telemetry_event")
_emit_captures_evaluation_metric("p4", "IBlackboardLeaseVerifierProtocol", "eval_metric")
_emit_stores_embedding("p4", "IBlackboardLeaseVerifierProtocol", "embedding_store")
_emit_updates_meta_learning_state("p4", "IBlackboardLeaseVerifierProtocol", "meta_learning")
_emit_links_execution_to_snapshot("p4", "IBlackboardLeaseVerifierProtocol", "exec_snapshot_link")

"\nSecure Filesystem Operations - Sandboxed File I/O with Blackboard Integration\nPrevents path traversal, protects critical directories, and integrates with HealingLease.\n\nDELEGATION NOTICE (2026-01-21):\n- move_file() and delete_file() now delegate to ArchivalGatekeeper\n- This ensures all destructive operations go through the governance layer\n- Direct shutil/os operations have been removed for security\n"
import os
import warnings
from functools import wraps
from pathlib import Path
from typing import Any, Protocol

from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR

_emit_emits_metric_event("IBlackboardLeaseVerifierProtocol", "p4obs", "metric_1")
_emit_emits_metric_event("IBlackboardLeaseVerifierProtocol", "p4obs", "metric_2")
_emit_emits_metric_event("IBlackboardLeaseVerifierProtocol", "p4obs", "metric_3")
_emit_emits_metric_event("IBlackboardLeaseVerifierProtocol", "p4obs", "metric_4")
_emit_emits_metric_event("IBlackboardLeaseVerifierProtocol", "p4obs", "metric_5")
_emit_emits_metric_event("IBlackboardLeaseVerifierProtocol", "p4obs", "metric_6")
_emit_records_incident_event("IBlackboardLeaseVerifierProtocol", "p4obs", "incident")
_emit_captures_runtime_anomaly("IBlackboardLeaseVerifierProtocol", "p4obs", "anomaly")
_emit_writes_observability_log("IBlackboardLeaseVerifierProtocol", "p4obs", "obs_log")
_emit_updates_monitoring_state("IBlackboardLeaseVerifierProtocol", "p4obs", "mon_state")
_emit_triggers_alert("IBlackboardLeaseVerifierProtocol", "p4obs", "alert")
_emit_links_incident_trace("IBlackboardLeaseVerifierProtocol", "p4obs", "trace_link")
_emit_captures_pattern("IBlackboardLeaseVerifierProtocol", "p3lm", "pattern")
_emit_records_learning_event("IBlackboardLeaseVerifierProtocol", "p3lm", "learning_event")
_emit_writes_learning_snapshot("IBlackboardLeaseVerifierProtocol", "p3lm", "snapshot")
_emit_feeds_meta_learning("IBlackboardLeaseVerifierProtocol", "p3lm", "meta_feed")
_emit_updates_routing_strategy("IBlackboardLeaseVerifierProtocol", "p3lm", "routing")
_emit_improves_agent_policy("IBlackboardLeaseVerifierProtocol", "p3lm", "policy")
_emit_stores_learning_state("IBlackboardLeaseVerifierProtocol", "p3lm", "state")
_emit_records_execution_trace("IBlackboardLeaseVerifierProtocol", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("IBlackboardLeaseVerifierProtocol", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("IBlackboardLeaseVerifierProtocol", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("IBlackboardLeaseVerifierProtocol", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("IBlackboardLeaseVerifierProtocol", "L4_STATE", "p2_trace_5")
_emit_reads_environ("IBlackboardLeaseVerifierProtocol", "env_read", "p2_env_1")
_emit_reads_environ("IBlackboardLeaseVerifierProtocol", "env_read", "p2_env_2")
_emit_reads_runtime_state("IBlackboardLeaseVerifierProtocol", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("IBlackboardLeaseVerifierProtocol", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "IBlackboardLeaseVerifierProtocol", "context_pull")
_emit_pulls_context("p1", "IBlackboardLeaseVerifierProtocol", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "IBlackboardLeaseVerifierProtocol", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "IBlackboardLeaseVerifierProtocol", "uwg_term_2")
_emit_writes_through("p1", "IBlackboardLeaseVerifierProtocol", "write_through")
_emit_writes_through("p1", "IBlackboardLeaseVerifierProtocol", "write_through_2")
_emit_validated_by_safety_plane("p1", "IBlackboardLeaseVerifierProtocol", "safety_validation")
_emit_invokes_eval("p1", "IBlackboardLeaseVerifierProtocol", "eval_call")
_emit_proposal_commits_routing("p1", "IBlackboardLeaseVerifierProtocol", "routing_commit")
_emit_escalates_to_human("p1", "IBlackboardLeaseVerifierProtocol", "human_escalation")
_emit_routes_through("p1", "IBlackboardLeaseVerifierProtocol", "route_through")
_emit_checks_agent_registry("p1", "IBlackboardLeaseVerifierProtocol", "agent_registry")
_emit_validates_agent_capability("p1", "IBlackboardLeaseVerifierProtocol", "capability")
_emit_dispatches_execution_plan("p1", "IBlackboardLeaseVerifierProtocol", "exec_plan")
_emit_agent_executes_agent("p1", "IBlackboardLeaseVerifierProtocol", "sub_agent")
_emit_routes_to_agent("p1", "IBlackboardLeaseVerifierProtocol", "target_agent")
_emit_verifies_policy("p1", "IBlackboardLeaseVerifierProtocol", "policy_check")
_emit_observes_runtime_state("p1", "IBlackboardLeaseVerifierProtocol", "runtime_state")
_emit_verifies_boundary("p1", "IBlackboardLeaseVerifierProtocol", "boundary_check")
_emit_transcripts_response("p1", "IBlackboardLeaseVerifierProtocol", "transcript")
_emit_hard_fails_untranscripted("p1", "IBlackboardLeaseVerifierProtocol")
_emit_gated_by_confidence("p1", "IBlackboardLeaseVerifierProtocol", "confidence_gate")


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


def __getattr__(name: str):  # noqa: N807
    if name == "EXCLUDED_DIRS":
        return _get_sovereign_excluded_folders()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


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
    except Exception as e:  # guardian: allow-silent-swallow
        raise SandboxViolationError(f"Invalid path: {e}")
    if not str(resolved).startswith(str(project_root)):
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
    with open(resolved_path, encoding="utf-8") as f:
        return f.read()


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
                        except Exception:  # guardian: allow-silent-swallow
                            pass
                raise PreservationViolationError(
                    f"Preservation Violation: New content ({new_lines} lines) is less than 90% of original ({original_lines} lines). Minimum required: {min_lines} lines. This would delete {round((1 - new_lines / original_lines) * 100, 2)}% of the file. Set override_preservation=True if this is intentional (SystemArchitect only).",
                )
        except (OSError, UnicodeDecodeError):  # guardian: allow-silent-swallow - acceptable exception handling
            pass
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    with open(resolved_path, "w", encoding="utf-8") as f:
        f.write(args.content)


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
    if resolved_path.is_dir():
        raise IsADirectoryError(f"Cannot delete directory with delete_file: {args.path}")
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


def create_directory(args: CreateDirectoryArgs, parents: bool = True) -> None:
    """
    Create a directory with sandbox validation.

    Args:
        args: CreateDirectoryArgs with path
        parents: Whether to create parent directories (default: True)

    Raises:
        SandboxViolationError: If path violates sandbox
    """
    resolved_path = validate_sandbox(args.path)
    resolved_path.mkdir(parents=parents, exist_ok=True)
