"""Single source of truth for ChromaDB persist paths.

Canonical store: ``data/cache/chromadb`` (relative to repo root).

Rationale:
    - Matches ``SovereignChromaClient.__init__`` default.
    - Matches ``L3SemanticRAG`` retrieval default.
    - Matches ``tools/generate/ingestion/validate_collection.CANONICAL_STORE``.
    - Previously, ``tools/ingestion/ingest_*.py`` defaulted to
      ``artifacts/chromadb``, creating a split-brain corpus. W1.2 of the
      ChromaDB/BGE retrieval-hardening plan unifies on this SSOT.

    Plan: ``.windsurf/plans/chromadb-bge-retrieval-hardening-e9aa09.md``.

Override via environment variable ``CHROMA_PERSIST_DIR`` (accepts absolute
or repo-relative paths). Env override exists purely for test isolation and
temporary migrations — production code MUST NOT set this.

Legacy path ``artifacts/chromadb`` is preserved on disk for historical
snapshots and is accessible via :func:`legacy_persist_dir` for migration
tooling only. New writes must use :func:`canonical_persist_dir`.
"""

from __future__ import annotations

import os
from pathlib import Path

# Repo root: this file lives at agentic_core/L4_state/config/chroma_paths.py
# ─── so repo_root = parents[3].
_REPO_ROOT = Path(__file__).resolve().parents[3]

CANONICAL_SUBDIR = "data/cache/chromadb"
LEGACY_SUBDIR = "artifacts/chromadb"

ENV_OVERRIDE = "CHROMA_PERSIST_DIR"


def repo_root() -> Path:
    """Return the repository root resolved from this file's location."""
    return _REPO_ROOT


def canonical_persist_dir() -> Path:
    """Return the canonical ChromaDB persist directory (absolute Path).

    Resolves the ``CHROMA_PERSIST_DIR`` env var if set (absolute or
    repo-relative), else returns ``<repo_root>/data/cache/chromadb``.

    The directory is NOT created here; callers that write should call
    ``path.mkdir(parents=True, exist_ok=True)`` before use.
    """
    override = os.environ.get(ENV_OVERRIDE, "").strip()
    if override:
        override_path = Path(override)
        if not override_path.is_absolute():
            override_path = _REPO_ROOT / override_path
        return override_path.resolve()
    return (_REPO_ROOT / CANONICAL_SUBDIR).resolve()


def canonical_persist_dir_str() -> str:
    """String form of :func:`canonical_persist_dir` for APIs that require str."""
    return str(canonical_persist_dir())


def legacy_persist_dir() -> Path:
    """Return the legacy ``artifacts/chromadb`` path for migration tooling only.

    Production code MUST NOT use this. It exists for migration scripts that
    read from the legacy store and write to the canonical store during the
    W5 consolidation wave.
    """
    return (_REPO_ROOT / LEGACY_SUBDIR).resolve()


__all__ = [
    "CANONICAL_SUBDIR",
    "LEGACY_SUBDIR",
    "ENV_OVERRIDE",
    "canonical_persist_dir",
    "canonical_persist_dir_str",
    "legacy_persist_dir",
    "repo_root",
]
