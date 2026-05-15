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

from datetime import datetime
import os
import sqlite3
from pathlib import Path


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

    Uses ADG_REPO_ROOT env var if set, otherwise derives from this file's location.
    """
    if env_root := os.environ.get("ADG_REPO_ROOT"):
        return Path(env_root).resolve()
    # This file is at: tools/adg/shared_modules/path_resolver.py
    # Repo root is 4 levels up
    return Path(__file__).resolve().parents[3]


def get_adg_dir() -> Path:
    """Return ADG artifacts directory (artifacts/adg).

    Uses ADG_DIR env var if set, otherwise derives from repo root.
    """
    if env_dir := os.environ.get("ADG_DIR"):
        return Path(env_dir).resolve()
    return get_repo_root() / "artifacts" / "adg"


def _has_nodes_table(path: Path) -> bool:
    """Return True iff the SQLite file has a `nodes` base table.

    Stub/sentinel snapshots (e.g. adg_indexed_99999999_9999.sqlite or partial
    pipeline outputs) can be present in artifacts/adg/ without the nodes
    table. Picking such a stub by mtime would crash consumers with
    `sqlite3.OperationalError: no such table: nodes`.
    """
    try:
        with connect_adg_snapshot_readonly(path) as conn:
            row = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='nodes'"
            ).fetchone()
            return row is not None
    except Exception:  # noqa: BLE001
        return False


def latest_sqlite(require_nodes_table: bool = False) -> Path | None:
    """Return the most recent adg_indexed_*.sqlite file in ADG_DIR.

    Args:
        require_nodes_table: If True, skip files without a `nodes` table
            (filters out stub/sentinel snapshots even further).

    Returns None if no SQLite files found.
    """
    adg_dir = get_adg_dir()
    if not adg_dir.exists():
        return None

    files = list(adg_dir.glob("adg_indexed_*.sqlite"))
    if not files:
        return None

    def _is_valid_snapshot_file(path: Path) -> bool:
        snapshot_id = path.stem.replace("adg_indexed_", "")
        try:
            datetime.strptime(snapshot_id, "%m%d%Y_%H%M")
            return True
        except ValueError:
            return False

    valid_files = [p for p in files if _is_valid_snapshot_file(p)]
    if not valid_files:
        return None

    # Sort by mtime descending for selection
    sorted_files = sorted(valid_files, key=lambda p: p.stat().st_mtime, reverse=True)

    if require_nodes_table:
        for candidate in sorted_files:
            if _has_nodes_table(candidate):
                return candidate
        return None

    return sorted_files[0]


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
