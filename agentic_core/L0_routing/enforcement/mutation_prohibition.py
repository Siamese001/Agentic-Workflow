"""G-12-1 — Physical Mutation Prohibition for L0/L4/L6.

Every persistent write from L0, L4, or L6 MUST fail closed at runtime.
This module is the single source of truth for mutation prohibition enforcement.

Persistent writes include: Path.write_text/write_bytes, json.dump to file,
os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').

Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    TESTS_DIR,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "mutation_prohibition")
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

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

FORBIDDEN_WRITE_LAYERS: frozenset[str] = frozenset({"L0", "L4", "L6"})
_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"


# =============================================================================
# Protected-Root Enforcement (Wave 2+)
# =============================================================================


class SourceMutationBlocked(RuntimeError):
    """Raised when attempting to mutate a protected root directory."""

    pass


@dataclass
class ProtectedRootBlockEvent:
    """Event record for blocked protected-root write attempts."""

    ts_utc: str  # ISO8601, seconds precision
    target: str  # Normalized path string
    matched_root: str  # Name of the immutable root that matched
    caller: str  # module:function best-effort


@dataclass
class ProtectedRootPolicy:
    """Policy contract for protected-root enforcement.

    This defines which roots are immutable and where block events are logged.
    Pure dataclass with no side effects.
    """

    immutable_roots: tuple[str, ...]  # Root names (e.g., "agentic_core", "tests", ".github")
    log_path: str  # JSONL log destination for block events


def get_default_protected_root_policy() -> ProtectedRootPolicy:
    """Get the default protected-root policy (pure; constant return).

    Returns:
        ProtectedRootPolicy with canonical immutable roots and log path
    """
    return ProtectedRootPolicy(
        immutable_roots=(AGENTIC_CORE_DIR, TESTS_DIR, ".github", ".windsurfrules"),
        log_path="logs/ssot_protected_root_blocks.jsonl",
    )


def _emit_block_event(
    target: Path, matched_root: str, log_path: str, ts_utc_override: str | None = None
) -> None:
    """Emit a deterministic JSONL event for a blocked write attempt.

    Args:
        target: Normalized path that was blocked
        matched_root: Name of the immutable root that matched
        log_path: Path to JSONL log file
        ts_utc_override: Optional fixed timestamp for deterministic replay (tests only)

    Failures are swallowed to avoid masking the block exception.
    """
    try:
        # Create event record (deterministic: stable field order via dataclass)
        if ts_utc_override is not None:
            ts = ts_utc_override
        else:
            ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

        event = ProtectedRootBlockEvent(
            ts_utc=ts,
            target=str(target),
            matched_root=matched_root,
            caller="mutation_prohibition:enforce_protected_root",
        )

        # Write to JSONL log (deterministic: sorted keys, newline-terminated)
        log_file = Path(log_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)

        with open(log_file, "a", encoding="utf-8") as f:
            json.dump(asdict(event), f, sort_keys=True)
            f.write("\n")
    except (OSError, TypeError) as e:
        # Swallow logging failures to avoid masking the block exception
        print(f"Failed to log mutation event: {e}")


def _get_repo_root() -> Path:
    """Get repository root directory."""
    return Path(__file__).resolve().parents[3]


# Backward compatibility: IMMUTABLE_ROOTS derived from default policy
def _get_immutable_roots() -> tuple[Path, ...]:
    """Get immutable root paths from default policy (for backward compatibility)."""
    policy = get_default_protected_root_policy()
    repo_root = _get_repo_root()
    return tuple(repo_root / root_name for root_name in policy.immutable_roots)


IMMUTABLE_ROOTS = _get_immutable_roots()


def enforce_protected_root(
    target_path: Path, *, allow_override: bool, policy: ProtectedRootPolicy | None = None
) -> None:
    """Block writes to protected root directories unless explicitly overridden.

    Args:
        target_path: Path being written to
        allow_override: If True, bypass the protection (audited CLI override)
        policy: Optional policy override (for tests only). If None, uses default policy.

    Raises:
        SourceMutationBlocked: If target_path is under a protected root and override is disabled
    """
    if allow_override:
        return

    # Use provided policy or default
    if policy is None:
        policy = get_default_protected_root_policy()

    # Resolve immutable roots from policy
    repo_root = _get_repo_root()
    immutable_roots = tuple(repo_root / root_name for root_name in policy.immutable_roots)

    # Resolve path without requiring existence
    try:
        resolved = target_path.resolve(strict=False)
    # guardian: allow-silent-swallow - acceptable exception handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling    # guardian: Multiple exceptions (OSError, RuntimeError) need specific handling
    except (OSError, RuntimeError):
        # If resolution fails, use the original path
        resolved = target_path

    # Check if path is under any immutable root
    for immutable_root in immutable_roots:
        try:
            if resolved.is_relative_to(immutable_root):
                _emit_block_event(resolved, immutable_root.name, policy.log_path)
                raise SourceMutationBlocked(
                    f"Protected root mutation blocked: target={resolved} matched_root={immutable_root.name}"
                )
        except AttributeError:
            # Fallback for Python < 3.9
            try:
                resolved.relative_to(immutable_root)
                _emit_block_event(resolved, immutable_root.name, policy.log_path)
                raise SourceMutationBlocked(
                    f"Protected root mutation blocked: target={resolved} matched_root={immutable_root.name}"
                )
            except ValueError:
                pass


# =============================================================================
# Core guard
# =============================================================================


def _is_override_active() -> bool:
    """Check if the test-only mutation override env var is set."""
    return os.environ.get(_ENV_OVERRIDE_KEY) == "1"


def assert_no_persistent_write(
    layer: str,
    op: str,
    path: str | None = None,
    trace_id: str | None = None,
) -> None:
    """Fail-closed guard: raises PermissionError if layer is forbidden.

    Args:
        layer: Calling layer identifier (e.g. "L0", "L4", "L6").
        op: Operation name (e.g. "write_text", "json.dump", "shutil.move").
        path: Optional target path for the write.
        trace_id: Optional trace identifier for deterministic diagnostics.

    Raises:
        PermissionError: If layer is in FORBIDDEN_WRITE_LAYERS and override inactive.
    """
    if layer not in FORBIDDEN_WRITE_LAYERS:
        return
    if _is_override_active():
        return

    msg_parts = [
        f"MUTATION_PROHIBITED:layer={layer}",
        f"op={op}",
    ]
    if path is not None:
        msg_parts.append(f"path={path}")
    if trace_id is not None:
        msg_parts.append(f"trace_id={trace_id}")

    msg = "|".join(msg_parts)
    logger.error("MUTATION_PROHIBITION DENY: %s", msg)

    # Record prohibition hit for loop detection (RCA Phase 5)
    if path is not None:
        try:
            from agentic_core.L2_execution.utils.write_gateway import (
                record_prohibition_hit,
            )

            record_prohibition_hit(layer, op, path)
        # guardian: allow-silent-swallow - optional dependency
        except ImportError:
            pass  # Gateway not available; skip signal

    raise PermissionError(msg)


# =============================================================================
# Safe wrappers — drop-in replacements for dangerous primitives
# =============================================================================


def safe_write_text(
    filepath: Path | str,
    content: str,
    *,
    layer: str,
    trace_id: str | None = None,
    encoding: str = "utf-8",
) -> None:
    """Guarded Path.write_text replacement."""
    assert_no_persistent_write(layer, "write_text", str(filepath), trace_id)
    Path(filepath).write_text(content, encoding=encoding)


def safe_write_bytes(
    filepath: Path | str,
    data: bytes,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded Path.write_bytes replacement."""
    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
    Path(filepath).write_bytes(data)


def safe_json_dump(
    obj: Any,
    filepath: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
    indent: int | None = 2,
    sort_keys: bool = True,
    **kwargs: Any,
) -> None:
    """Guarded json.dump-to-file replacement."""
    assert_no_persistent_write(layer, "json.dump", str(filepath), trace_id)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent, sort_keys=sort_keys, **kwargs)


def safe_shutil_move(
    src: Path | str,
    dst: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded shutil.move replacement."""
    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
    shutil.move(str(src), str(dst))


def safe_shutil_rmtree(
    target: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded shutil.rmtree replacement."""
    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
    shutil.rmtree(str(target))


def safe_os_remove(
    filepath: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded os.remove replacement."""
    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
    os.remove(filepath)


def safe_os_rename(
    src: Path | str,
    dst: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded os.rename replacement."""
    assert_no_persistent_write(layer, "os.rename", str(dst), trace_id)
    os.rename(src, dst)


def safe_open_write(
    filepath: Path | str,
    mode: str = "w",
    *,
    layer: str,
    trace_id: str | None = None,
    encoding: str | None = "utf-8",
) -> Any:
    """Guarded open(..., 'w'/'a') replacement. Returns file handle."""
    assert_no_persistent_write(layer, f"open({mode})", str(filepath), trace_id)
    return open(filepath, mode, encoding=encoding)


# =============================================================================
# Context manager for scoped enforcement
# =============================================================================


@contextmanager
def mutation_guard(layer: str) -> Generator[None, None, None]:
    """Context manager that asserts no mutation is in progress for the layer.

    Raises PermissionError on entry if layer is forbidden.
    Useful for wrapping code blocks that should never write.
    """
    assert_no_persistent_write(layer, "mutation_guard_enter")
    yield


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "FORBIDDEN_WRITE_LAYERS",
    "assert_no_persistent_write",
    "mutation_guard",
    "safe_json_dump",
    "safe_open_write",
    "safe_os_remove",
    "safe_os_rename",
    "safe_shutil_move",
    "safe_shutil_rmtree",
    "safe_write_bytes",
    "safe_write_text",
]
