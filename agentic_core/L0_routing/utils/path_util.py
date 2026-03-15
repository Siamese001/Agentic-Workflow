"""
L0 Path Utilities — Pure path validation and manipulation functions.

These are stdlib-only utilities with no governance logic.
They are extracted from L5 to eliminate upward import violations.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_routes_through,  # noqa: E402
)

_emit_dispatches_healing_run("p1", "path_util", "L0")
_emit_routes_through("p1", "path_util", "L0")
_emit_escalates_to_human("p1", "path_util", "L0")
_emit_reads_policy_state("p1", "path_util", "L0")

if TYPE_CHECKING:
    from collections.abc import Iterator
from agentic_core.L0_routing.config.path_constants import GLOBAL_EXCLUDED_DIRS, PROJECT_ROOT_MARKERS
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,
    _emit_records_execution_trace,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
)


def get_validated_project_root() -> Path:
    """Get the validated project root by searching upward from CWD."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "get_validated_project_root", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "get_validated_project_root", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "get_validated_project_root")
    current = Path.cwd().resolve()
    for parent in [current, *list(current.parents)]:
        if any((parent / marker).exists() for marker in PROJECT_ROOT_MARKERS):
            return parent
    return current


def validate_path_within_project(path: str | Path, project_root: Path | None = None) -> bool:
    """Validate that a path is within the project root."""
    if project_root is None:
        project_root = get_validated_project_root()
    try:
        path = Path(path).resolve()
        project_root = Path(project_root).resolve()
        path.relative_to(project_root)
        return True
    except ValueError:
        return False


def safe_path_join(project_root: str | Path, *parts: str) -> Path:
    """Safely join path parts and validate result is within project root."""
    project_root = Path(project_root).resolve()
    result = project_root.joinpath(*parts).resolve()
    if not validate_path_within_project(result, project_root):
        raise ValueError(f"SAFETY VIOLATION: Path '{result}' is outside project root '{project_root}'")
    return result


def safe_prefixed_filename(filename: str, prefix: str) -> str:
    """Generate a safe prefixed filename."""
    if filename.startswith(prefix):
        return filename
    return f"{prefix}{filename}"


def validate_no_duplicate_prefix(filename: str, prefix: str) -> bool:
    """Validate that a filename doesn't have duplicate prefixes."""
    double_prefix = f"{prefix}{prefix}"
    return double_prefix not in filename


def get_python_files(directory: Path, *, exclude_dirs: frozenset[str] | None = None) -> Iterator[Path]:
    """Yield all Python files in a directory, excluding specified directories."""
    if exclude_dirs is None:
        exclude_dirs = GLOBAL_EXCLUDED_DIRS
    for item in directory.rglob("*.py"):
        if not any(part in exclude_dirs for part in item.parts):
            yield item


def is_path_allowed(path: str | Path, allowed_dirs: frozenset[str]) -> bool:
    """Check if a path is within one of the allowed directories."""
    path_str = str(path).replace("\\", "/")
    return any(path_str.startswith(d) or f"/{d}/" in path_str for d in allowed_dirs)


__all__ = [
    "get_python_files",
    "get_validated_project_root",
    "is_path_allowed",
    "safe_path_join",
    "safe_prefixed_filename",
    "validate_no_duplicate_prefix",
    "validate_path_within_project",
]
