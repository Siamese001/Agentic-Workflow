"""Shared path resolver for ADG tools — eliminates hardcoded Windows paths.

Usage:
    from tools.adg.shared_modules.path_resolver import get_adg_dir, latest_sqlite

    adg_dir = get_adg_dir()  # Path to artifacts/adg
    sqlite_path = latest_sqlite()  # Most recent adg_indexed_*.sqlite file

Related Tools:
    - ADG Generator: tools/generate/generate_full_adg.py (canonical)
    - Legacy shim: tools/adg/generate_full_adg.py (deprecated, redirects to canonical)
    - Redis Ingest: tools/adg/adg_redis_ingest.py
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
import sqlite3
from pathlib import Path
from typing import Literal

from tools.adg.shared_modules.snapshot_registry import (
    POINTER_FILENAMES,
    SnapshotPointerError,
    load_snapshot_pointer,
)


def connect_adg_snapshot_readonly(snapshot: Path, *, timeout: float = 5.0) -> sqlite3.Connection:
    """Open an ADG indexed snapshot read-only with immutable VFS.

    Read-write opens can rewrite SQLite headers / freelist metadata without
    changing logical row counts, which breaks DSSE file SHA attestations while
    leaving three-bucket digest checks green.
    """
    uri = f"file:{snapshot.resolve().as_posix()}?mode=ro&immutable=1"
    return sqlite3.connect(uri, uri=True, timeout=timeout)


def get_repo_root() -> Path:
    """Return repository root directory.

    Uses ADG_REPO_ROOT env var if set and resolved, otherwise derives from this
    file's location. Unexpanded MCP placeholders such as "${AGENTIC_REPO_ROOT}"
    are ignored so a bad launcher environment does not poison ADG resolution.
    """
    if env_root := os.environ.get("ADG_REPO_ROOT"):
        if "$" not in env_root:
            resolved = Path(env_root).resolve()
            if resolved.exists():
                return resolved
    # This file is at: tools/adg/shared_modules/path_resolver.py
    # Repo root is 4 levels up
    return Path(__file__).resolve().parents[3]


def _worktree_primary_root(repo_root: Path) -> Path | None:
    """Return the primary checkout root for a linked git worktree, if known.

    Codex often operates in a sibling worktree that intentionally does not
    carry heavy, gitignored ADG artifacts. The canonical snapshots remain in
    the primary checkout. Git records that relationship in the worktree's
    `.git` file:

        gitdir: C:/Git/Agentic-Workflow-FRESH/.git/worktrees/eval-harness

    Prefer the `commondir` file when present because it is Git's canonical
    pointer; fall back to the common `.git` parent for older layouts.
    """
    git_marker = repo_root / ".git"
    if not git_marker.is_file():
        return None
    try:
        raw = git_marker.read_text(encoding="utf-8").strip()
    except OSError:
        return None
    prefix = "gitdir:"
    if not raw.lower().startswith(prefix):
        return None
    gitdir = Path(raw[len(prefix) :].strip())
    if not gitdir.is_absolute():
        gitdir = (repo_root / gitdir).resolve()
    else:
        gitdir = gitdir.resolve()

    commondir_file = gitdir / "commondir"
    if commondir_file.exists():
        try:
            common_raw = commondir_file.read_text(encoding="utf-8").strip()
        except OSError:
            common_raw = ""
        if common_raw:
            common_dir = Path(common_raw)
            if not common_dir.is_absolute():
                common_dir = (gitdir / common_dir).resolve()
            else:
                common_dir = common_dir.resolve()
            if common_dir.name == ".git":
                return common_dir.parent

    # Common linked-worktree layout: <primary>/.git/worktrees/<name>
    try:
        if gitdir.parent.name == "worktrees" and gitdir.parent.parent.name == ".git":
            return gitdir.parent.parent.parent
    except IndexError:
        return None
    return None


def _adg_dir_has_snapshot(adg_dir: Path) -> bool:
    """Return True when `adg_dir` has at least one timestamp-valid ADG snapshot."""
    if not adg_dir.exists():
        return False
    for path in adg_dir.glob("adg_indexed_*.sqlite"):
        snapshot_id = path.stem.replace("adg_indexed_", "")
        try:
            datetime.strptime(snapshot_id, "%m%d%Y_%H%M")
            return True
        except ValueError:
            continue
    return False


def get_adg_dir() -> Path:
    """Return ADG artifacts directory (artifacts/adg).

    Uses ADG_DIR env var if set, otherwise derives from repo root. In linked
    worktrees, falls back to the primary checkout's `artifacts/adg` when the
    worktree has no snapshots. This keeps ADG MCP queryable from Codex worktrees
    without copying large gitignored SQLite artifacts into every worktree.
    """
    repo_root = get_repo_root()
    if env_dir := os.environ.get("ADG_DIR"):
        resolved = Path(env_dir).resolve()
        if os.environ.get("ADG_ALLOW_EXTERNAL_DIR") == "1":
            return resolved
        try:
            resolved.relative_to(repo_root)
            return resolved
        except ValueError:
            return repo_root / "artifacts" / "adg"
    local_adg_dir = repo_root / "artifacts" / "adg"
    if _adg_dir_has_snapshot(local_adg_dir):
        return local_adg_dir

    primary_root = _worktree_primary_root(repo_root)
    if primary_root is not None and primary_root != repo_root:
        primary_adg_dir = primary_root / "artifacts" / "adg"
        if _adg_dir_has_snapshot(primary_adg_dir):
            return primary_adg_dir

    return local_adg_dir


def _has_required_tables(path: Path, required_tables: tuple[str, ...]) -> bool:
    """Return True iff the SQLite file has all required tables.

    Stub/sentinel snapshots (e.g. adg_indexed_99999999_9999.sqlite or partial
    pipeline outputs) can be present in artifacts/adg/ without the materialized
    views consumers need. Picking such a stub by mtime would crash consumers
    with `sqlite3.OperationalError: no such table: ...`.
    """
    conn: sqlite3.Connection | None = None
    try:
        conn = connect_adg_snapshot_readonly(path)
        placeholders = ",".join("?" for _ in required_tables)
        rows = conn.execute(
            f"SELECT name FROM sqlite_master WHERE type='table' AND name IN ({placeholders})",  # noqa: S608
            required_tables,
        ).fetchall()
        present = {row[0] for row in rows}
        return set(required_tables).issubset(present)
    except (OSError, sqlite3.Error):
        return False
    finally:
        if conn is not None:
            conn.close()


def _has_nodes_table(path: Path) -> bool:
    """Return True iff the SQLite file has a `nodes` base table."""
    return _has_required_tables(path, ("nodes",))


SnapshotSelection = Literal["latest", "certified", "repair", "candidate"]


@dataclass(frozen=True)
class SnapshotResolution:
    """Resolved snapshot plus the provenance that authorized its use."""

    path: Path
    selection: SnapshotSelection
    snapshot_id: str
    certification_status: str
    artifact_status: str
    pointer_path: Path | None = None
    digest_verified: bool = False


def _is_valid_snapshot_file(path: Path) -> bool:
    snapshot_id = path.stem.replace("adg_indexed_", "")
    try:
        datetime.strptime(snapshot_id, "%m%d%Y_%H%M")
        return True
    except ValueError:
        return False


def _snapshot_search_dirs() -> tuple[Path, ...]:
    """Return local then primary-checkout directories for pointer resolution."""
    if os.environ.get("ADG_DIR"):
        return (get_adg_dir().resolve(),)

    repo_root = get_repo_root()
    directories = [repo_root / "artifacts" / "adg"]
    primary_root = _worktree_primary_root(repo_root)
    if primary_root is not None and primary_root != repo_root:
        directories.append(primary_root / "artifacts" / "adg")
    return tuple(dict.fromkeys(path.resolve() for path in directories))


def _latest_candidate(required_tables: tuple[str, ...]) -> Path | None:
    adg_dir = get_adg_dir()
    if not adg_dir.exists():
        return None
    candidates = [
        path
        for path in adg_dir.glob("adg_indexed_*.sqlite")
        if _is_valid_snapshot_file(path)
    ]
    for candidate in sorted(
        candidates,
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    ):
        if not required_tables or _has_required_tables(candidate, required_tables):
            return candidate
    return None


def resolve_snapshot(
    *,
    selection: SnapshotSelection = "latest",
    require_nodes_table: bool = False,
    required_tables: tuple[str, ...] | None = None,
    verify_digest: bool = False,
    strict: bool = False,
) -> SnapshotResolution | None:
    """Resolve an explicitly selected snapshot role without role fallback."""
    if selection not in {"latest", "certified", "repair", "candidate"}:
        raise ValueError(f"unsupported ADG snapshot selection: {selection!r}")

    requested = tuple(required_tables or ())
    tables = tuple(
        dict.fromkeys(
            requested + (("nodes",) if require_nodes_table else ())
        )
    )
    if selection == "latest":
        selected = _latest_candidate(tables)
        if selected is None:
            if strict:
                raise SnapshotPointerError("latest ADG snapshot is missing")
            return None
        return SnapshotResolution(
            path=selected,
            selection="latest",
            snapshot_id=selected.stem.replace("adg_indexed_", ""),
            certification_status="unknown",
            artifact_status="candidate",
        )

    role = selection
    for adg_dir in _snapshot_search_dirs():
        pointer_path = adg_dir / POINTER_FILENAMES[role]
        if not pointer_path.exists():
            continue
        try:
            pointer = load_snapshot_pointer(
                adg_dir,
                role,
                verify_digest=verify_digest,
            )
            if tables and not _has_required_tables(pointer.path, tables):
                raise SnapshotPointerError(
                    f"{role} snapshot missing required tables: "
                    + ", ".join(tables)
                )
        except SnapshotPointerError:
            if strict:
                raise
            return None
        return SnapshotResolution(
            path=pointer.path,
            selection=selection,
            snapshot_id=pointer.snapshot_id,
            certification_status=pointer.certification_status,
            artifact_status=pointer.artifact_status,
            pointer_path=pointer.pointer_path,
            digest_verified=pointer.digest_verified,
        )

    if strict:
        raise SnapshotPointerError(f"{role} snapshot pointer is missing")
    return None


def latest_sqlite(
    require_nodes_table: bool = False,
    required_tables: tuple[str, ...] | None = None,
    *,
    selection: SnapshotSelection = "latest",
    verify_digest: bool = False,
) -> Path | None:
    """Return the selected SQLite snapshot, retaining latest as the default."""
    resolved = resolve_snapshot(
        selection=selection,
        require_nodes_table=require_nodes_table,
        required_tables=required_tables,
        verify_digest=verify_digest,
    )
    return resolved.path if resolved else None


def get_reports_dir() -> Path:
    """Return ADG reports directory (artifacts/adg/reports)."""
    return get_adg_dir() / "reports"


def get_snapshots_dir() -> Path:
    """Return ADG snapshots directory (artifacts/adg/snapshots)."""
    return get_adg_dir() / "snapshots"


def resolve_sqlite(path: str | Path | None = None) -> Path | None:
    """Resolve SQLite path from string, Path, or auto-discover latest.

    Args:
        path: Explicit path string/Path, or None to auto-discover

    Returns:
        Resolved Path, or None if not found
    """
    if path is None:
        return latest_sqlite()

    p = Path(path)
    if p.exists():
        return p.resolve()

    # Try relative to ADG_DIR
    adg_relative = get_adg_dir() / p.name
    if adg_relative.exists():
        return adg_relative.resolve()

    return None


# Legacy aliases for backward compatibility
get_latest_sqlite = latest_sqlite
get_sqlite_path = resolve_sqlite
