"""
L2 Write Gateway — Centralized durable mutation authority.

All filesystem writes, directory creation, file copies, moves, and deletions
MUST be routed through this gateway. Non-L2 layers (L3–L6) call these
functions instead of using direct mutation primitives.

Tool ID Prefix: ACT-010
"""

from __future__ import annotations

import csv
import json
import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Sequence

Logger: Any = logging.getLogger("L2.WriteGateway")

# =============================================================================
# Source Root Fence — Prevent self-mutation during SSOT heal runs
# =============================================================================

_REPO_ROOT: Path | None = None


def _get_repo_root() -> Path:
    """Lazily resolve repo root (parent of agentic_core)."""
    global _REPO_ROOT
    if _REPO_ROOT is None:
        _REPO_ROOT = Path(__file__).resolve().parents[3]
    return _REPO_ROOT


_SOURCE_ROOTS_RELATIVE: frozenset[str] = frozenset(
    {
        "agentic_core",
        "prompt_governance",
        "tests",
        "ops_scripts",
        "apps_shared",
    }
)

_SAFE_OUTPUT_PREFIXES: tuple[str, ...] = (
    "docs/evidence",
    "docs/reports",
    "archives/healing_backups",
    "runtime_state.json",
    ".backup",
)


def _deny_writes_into_source_roots(path: Path) -> None:
    """Raise RuntimeError if path is under a tracked source root."""
    if os.environ.get("AGENTIC_DENY_SOURCE_MUTATION") != "1":
        return
    repo_root = _get_repo_root()
    try:
        rel = path.resolve().relative_to(repo_root)
        rel_str = str(rel).replace("\\", "/")
    except ValueError:
        return
    for safe_prefix in _SAFE_OUTPUT_PREFIXES:
        if rel_str.startswith(safe_prefix):
            return
    top_dir = rel.parts[0] if rel.parts else ""
    if top_dir in _SOURCE_ROOTS_RELATIVE:
        raise RuntimeError(
            f"SOURCE_MUTATION_BLOCKED: Write to tracked source prohibited during SSOT heal. path={rel_str}"
        )


def write_text(path: str | Path, content: str, encoding: str = "utf-8") -> str:
    """Write text content to a file, creating parent dirs as needed."""
    p = Path(path)
    _deny_writes_into_source_roots(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding=encoding)
    Logger.debug(f"[WriteGateway] write_text: {p}")
    return str(p)


def write_bytes(path: str | Path, data: bytes) -> str:
    """Write binary content to a file, creating parent dirs as needed."""
    p = Path(path)
    _deny_writes_into_source_roots(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(data)
    Logger.debug(f"[WriteGateway] write_bytes: {p}")
    return str(p)


def write_json(path: str | Path, obj: Any, indent: int = 2) -> str:
    """Serialize obj as JSON and write to file."""
    p = Path(path)
    _deny_writes_into_source_roots(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=indent)
    Logger.debug(f"[WriteGateway] write_json: {p}")
    return str(p)


def append_text(path: str | Path, content: str, encoding: str = "utf-8") -> str:
    """Append text to a file, creating parent dirs as needed."""
    p = Path(path)
    _deny_writes_into_source_roots(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "a", encoding=encoding) as f:
        f.write(content)
    Logger.debug(f"[WriteGateway] append_text: {p}")
    return str(p)


def open_write(path: str | Path, content: str, encoding: str = "utf-8") -> str:
    """Open file in write mode and write content."""
    p = Path(path)
    _deny_writes_into_source_roots(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding=encoding) as f:
        f.write(content)
    Logger.debug(f"[WriteGateway] open_write: {p}")
    return str(p)


def ensure_dir(path: str | Path) -> Path:
    """Create directory (and parents) if it does not exist."""
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    Logger.debug(f"[WriteGateway] ensure_dir: {p}")
    return p


def remove_file(path: str | Path, missing_ok: bool = True) -> None:
    """Remove a file."""
    p = Path(path)
    if missing_ok and not p.exists():
        return
    p.unlink(missing_ok=missing_ok)
    Logger.debug(f"[WriteGateway] remove_file: {p}")


def remove_dir(path: str | Path) -> None:
    """Remove an empty directory."""
    p = Path(path)
    if p.exists():
        p.rmdir()
    Logger.debug(f"[WriteGateway] remove_dir: {p}")


def remove_tree(path: str | Path) -> None:
    """Recursively remove a directory tree."""
    p = Path(path)
    if p.exists():
        shutil.rmtree(p)
    Logger.debug(f"[WriteGateway] remove_tree: {p}")


def copy_file(src: str | Path, dst: str | Path) -> str:
    """Copy a file preserving metadata."""
    s, d = Path(src), Path(dst)
    _deny_writes_into_source_roots(d)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(s, d)
    Logger.debug(f"[WriteGateway] copy_file: {s} -> {d}")
    return str(d)


def move_path(src: str | Path, dst: str | Path) -> str:
    """Move/rename a file or directory."""
    s, d = Path(src), Path(dst)
    _deny_writes_into_source_roots(d)
    d.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(s), str(d))
    Logger.debug(f"[WriteGateway] move_path: {s} -> {d}")
    return str(d)


def rename_path(src: str | Path, dst: str | Path) -> Path:
    """Rename a file or directory."""
    s, d = Path(src), Path(dst)
    _deny_writes_into_source_roots(d)
    s.rename(d)
    Logger.debug(f"[WriteGateway] rename_path: {s} -> {d}")
    return d


def touch_file(path: str | Path) -> Path:
    """Create an empty file or update its timestamp."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.touch()
    Logger.debug(f"[WriteGateway] touch_file: {p}")
    return p


def copy_tree(src: str | Path, dst: str | Path) -> str:
    """Recursively copy a directory tree."""
    s, d = Path(src), Path(dst)
    shutil.copytree(str(s), str(d), dirs_exist_ok=True)
    Logger.debug(f"[WriteGateway] copy_tree: {s} -> {d}")
    return str(d)


def makedirs(path: str | Path, exist_ok: bool = True) -> str:
    """Create directories (os.makedirs equivalent)."""
    os.makedirs(str(path), exist_ok=exist_ok)
    Logger.debug(f"[WriteGateway] makedirs: {path}")
    return str(path)


def write_json_atomic(
    path: str | Path,
    obj: Any,
    indent: int = 2,
) -> str:
    """Serialize obj as JSON via temp file + atomic rename."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(
        dir=str(p.parent),
        suffix=".tmp",
        prefix=f".{p.stem}_",
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(obj, f, indent=indent)
        # Atomic replace (Windows needs target removed first)
        if os.name == "nt" and p.exists():
            p.unlink()
        Path(tmp).replace(p)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    Logger.debug(f"[WriteGateway] write_json_atomic: {p}")
    return str(p)


def init_csv(
    path: str | Path,
    header: Sequence[str],
) -> str:
    """Create a CSV file with a header row, creating parent dirs."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(header)
    Logger.debug(f"[WriteGateway] init_csv: {p}")
    return str(p)


def append_csv_row(
    path: str | Path,
    row: Sequence[str],
) -> str:
    """Append a single row to an existing CSV file."""
    p = Path(path)
    with open(p, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow(row)
    Logger.debug(f"[WriteGateway] append_csv_row: {p}")
    return str(p)


__all__ = [
    "write_text",
    "write_bytes",
    "write_json",
    "append_text",
    "open_write",
    "ensure_dir",
    "remove_file",
    "remove_dir",
    "remove_tree",
    "copy_file",
    "move_path",
    "rename_path",
    "touch_file",
    "copy_tree",
    "makedirs",
    "write_json_atomic",
    "init_csv",
    "append_csv_row",
]
