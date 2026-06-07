"""Resolve the newest ADG SQLite snapshot at runtime.

Replaces the previous pattern where ingest scripts hardcoded a specific
``artifacts/adg/adg_indexed_<timestamp>.sqlite`` filename. Hardcoded paths
go stale the moment ``tools/generate_full_adg.py`` is run again, leaving
ChromaDB populated with stale ``adg_node_id`` values.

W1.4 of the ChromaDB/BGE retrieval-hardening plan:
``docs/archive/windsurf/legacy-tree/plans/chromadb-bge-retrieval-hardening-e9aa09.md``.
"""

from __future__ import annotations

import os
from pathlib import Path

from agentic_core.L4_state.config.chroma_paths import repo_root

ENV_OVERRIDE = "ADG_SNAPSHOT_PATH"


def latest_adg_snapshot() -> Path | None:
    """Return the newest ``artifacts/adg/adg_indexed_*.sqlite`` path, or None.

    Resolution order:
        1. ``ADG_SNAPSHOT_PATH`` env var (absolute or repo-relative)
        2. Newest ``artifacts/adg/adg_indexed_*.sqlite`` by mtime
        3. ``None`` if the ``artifacts/adg/`` directory is absent/empty

    Returns ``None`` explicitly so callers can degrade gracefully rather
    than crashing on first-time repo clones with no ADG artifacts.
    """
    override = os.environ.get(ENV_OVERRIDE, "").strip()
    if override:
        p = Path(override)
        if not p.is_absolute():
            p = repo_root() / p
        p = p.resolve()
        return p if p.exists() else None

    adg_dir = repo_root() / "artifacts" / "adg"
    if not adg_dir.is_dir():
        return None
    candidates = sorted(
        adg_dir.glob("adg_indexed_*.sqlite"),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    return candidates[0] if candidates else None


__all__ = ["latest_adg_snapshot", "ENV_OVERRIDE"]
