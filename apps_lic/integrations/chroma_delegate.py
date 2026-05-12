"""
apps_lic sanctioned ChromaDB integration delegate.

This is the ONLY file in apps_lic permitted to import SovereignChromaClient
from agentic_core.L4_state. All other apps_lic modules that need ChromaDB
access MUST go through this delegate.

Invariants (W1 — chroma-graphrag-lic-rg-research-f4a2e9):
- apps_lic/types/ MUST NOT import from agentic_core.L4_state directly.
- apps_lic/integrations/chroma_delegate.py is the sanctioned import site.
- This module exposes only what apps_lic legitimately needs: client
  construction and collection access.
- semantic cache (R1B / check_d2_semantic_cache) is NOT exposed here.
  apps_lic must never call check_d2_semantic_cache() or emit SEMANTIC_CACHE_HIT.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


def get_sovereign_chroma_client(persist_dir: str) -> Any:
    """Return a SovereignChromaClient for the given persist directory.

    Deferred import so that ChromaDB is only required when actually
    instantiated, not at module load time (matches original lazy pattern
    in LICVectorMemory.initialize()).

    Raises ImportError if chromadb is not installed — callers should
    handle this gracefully (fail-soft to MockVectorMemory).
    """
    from agentic_core.L4_state.utils.client.chroma_client import (  # noqa: PLC0415
        SovereignChromaClient,
    )

    return SovereignChromaClient(persist_dir=persist_dir)
