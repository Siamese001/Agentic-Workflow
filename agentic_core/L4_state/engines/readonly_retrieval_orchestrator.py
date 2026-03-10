"""
Phase 6 — Read-Only Retrieval Orchestrator.

Canonical retrieval entrypoint that:
1. Enters read_only_retrieval_scope() before any L4 query.
2. Produces a RetrievalBoundarySnapshot (non-mutating).
3. Returns AnchoredResult list + snapshot.

Any persistent mutation attempted inside this path raises RetrievalMutationViolation.
"""

from __future__ import annotations

from typing import Any

from agentic_core.L4_state.enforcement.readonly_retrieval_scope import (
    read_only_retrieval_scope,
)
from agentic_core.L4_state.types.retrieval_anchor_types import AnchoredResult
from agentic_core.L4_state.types.retrieval_boundary_snapshot_types import (
    AnchorEntry,
    RetrievalBoundarySnapshot,
    create_retrieval_boundary_snapshot,
)


def retrieve_with_readonly_guarantee(
    mission_id: str,
    query: str,
    top_k: int,
    domain: str,
    active_config_hashes: dict[str, str],
    created_at_utc: str,
    *,
    _query_fn: Any = None,
) -> tuple[list[AnchoredResult], RetrievalBoundarySnapshot]:
    """
    Execute a retrieval inside a read-only scope and return results + snapshot.

    Parameters
    ----------
    mission_id           : str  — mission identifier
    query                : str  — retrieval query text
    top_k                : int  — maximum results to return
    domain               : str  — retrieval domain
    active_config_hashes : dict — L4 active config hashes (policy/routing/model/budget)
    created_at_utc       : str  — stable UTC timestamp for the snapshot
    _query_fn            : callable | None
        Injected query function (for testing / real L4 backend).
        Signature: (query: str, top_k: int, domain: str) -> list[AnchoredResult]
        If None, returns an empty result list (safe default for wiring tests).

    Returns
    -------
    (results, snapshot)
        results  : list[AnchoredResult]
        snapshot : RetrievalBoundarySnapshot  (non-mutating, stable hash)
    """
    with read_only_retrieval_scope():
        if _query_fn is not None:
            results: list[AnchoredResult] = _query_fn(query, top_k, domain)
        else:
            results = []

        anchor_entries = [
            AnchorEntry(
                chunk_id=r.anchor.chunk_id,
                version_hash=r.anchor.version_hash,
            )
            for r in results
        ]

        snapshot = create_retrieval_boundary_snapshot(
            mission_id=mission_id,
            query=query,
            top_k=top_k,
            domain=domain,
            active_config_hashes=active_config_hashes,
            anchors=anchor_entries,
            created_at_utc=created_at_utc,
        )

    return results, snapshot
