"""G-12-1 — Physical Mutation Prohibition for L0/L4/L6.

Every persistent write from L0, L4, or L6 MUST fail closed at runtime.
This module is the single source of truth for mutation prohibition enforcement.

Persistent writes include: Path.write_text/write_bytes, json.dump to file,
os.rename/remove/unlink, shutil.move/rmtree, and open(..., 'w'/'a').

Override: AGENTIC_ALLOW_MUTATION_FOR_TESTS=1 (env var, test-only).
"""

from __future__ import annotations

import logging
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Generator

from agentic_core.L2_execution.tools import write_gateway as _wg

logger = logging.getLogger(__name__)

# =============================================================================
# Constants
# =============================================================================

FORBIDDEN_WRITE_LAYERS: frozenset[str] = frozenset({"L0", "L4", "L6"})
_ENV_OVERRIDE_KEY = "AGENTIC_ALLOW_MUTATION_FOR_TESTS"


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
    _wg.write_text(Path(filepath), content, encoding=encoding)


def safe_write_bytes(
    filepath: Path | str,
    data: bytes,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded Path.write_bytes replacement."""
    assert_no_persistent_write(layer, "write_bytes", str(filepath), trace_id)
    _wg.write_bytes(Path(filepath), data)


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
    _wg.write_json(filepath, obj, indent=indent)


def safe_shutil_move(
    src: Path | str,
    dst: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded shutil.move replacement."""
    assert_no_persistent_write(layer, "shutil.move", str(dst), trace_id)
    _wg.move_path(str(src), str(dst))


def safe_shutil_rmtree(
    target: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded shutil.rmtree replacement."""
    assert_no_persistent_write(layer, "shutil.rmtree", str(target), trace_id)
    _wg.remove_tree(str(target))


def safe_os_remove(
    filepath: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded os.remove replacement."""
    assert_no_persistent_write(layer, "os.remove", str(filepath), trace_id)
    _wg.remove_file(filepath)


def safe_os_rename(
    src: Path | str,
    dst: Path | str,
    *,
    layer: str,
    trace_id: str | None = None,
) -> None:
    """Guarded os.rename replacement."""
    assert_no_persistent_write(layer, "os.rename", str(dst), trace_id)
    _wg.rename_path(src, dst)


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
