"""Shared path resolver for ADG tools — eliminates hardcoded Windows paths.

Usage:
    from tools.adg.shared_modules.path_resolver import get_adg_dir, latest_sqlite

    adg_dir = get_adg_dir()  # Path to artifacts/adg
    sqlite_path = latest_sqlite()  # Most recent adg_indexed_*.sqlite file
"""

from __future__ import annotations

import os
from pathlib import Path


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


def latest_sqlite() -> Path | None:
    """Return the most recent adg_indexed_*.sqlite file in ADG_DIR.

    Returns None if no SQLite files found.
    """
    adg_dir = get_adg_dir()
    if not adg_dir.exists():
        return None

    files = sorted(adg_dir.glob("adg_indexed_*.sqlite"))
    return files[-1] if files else None


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
