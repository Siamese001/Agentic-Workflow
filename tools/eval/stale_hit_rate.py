"""Stale Hit Rate — measures how often retrieval returns outdated/stale chunks.

Implements the G8 eval axis: "stale-hit rate".  When documents are updated
or re-chunked, old chunk IDs may linger in the index.  This tool measures
the fraction of retrieved chunks that are stale (i.e. their content hash
no longer matches the canonical source).

Design:
  - ``StaleHitResult`` captures per-query stale-hit metrics.
  - ``StaleHitAnalyzer`` compares retrieved chunk IDs against a freshness
    manifest (mapping chunk_id → content_hash) to detect stale hits.
  - Intended for CI: fail if stale-hit rate exceeds threshold.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# StaleHitResult — per-query stale-hit metrics
# ---------------------------------------------------------------------------


@dataclass
class StaleHitResult:
    """Stale-hit metrics for a single query.

    Attributes
    ----------
    query : str
        The query string.
    retrieved_ids : list[str]
        Chunk IDs returned by retrieval.
    stale_ids : list[str]
        Chunk IDs that are stale (hash mismatch or missing from manifest).
    fresh_ids : list[str]
        Chunk IDs that are fresh (hash matches manifest).
    stale_rate : float
        Fraction of retrieved IDs that are stale (0–1).
    """

    query: str
    retrieved_ids: list[str]
    stale_ids: list[str] = field(default_factory=list)
    fresh_ids: list[str] = field(default_factory=list)
    stale_rate: float = 0.0


# ---------------------------------------------------------------------------
# StaleHitReport — aggregate stale-hit across all queries
# ---------------------------------------------------------------------------


@dataclass
class StaleHitReport:
    """Aggregate stale-hit report.

    Attributes
    ----------
    total_queries : int
        Number of queries analyzed.
    total_chunks_retrieved : int
        Total chunks across all queries.
    total_stale : int
        Total stale chunks across all queries.
    avg_stale_rate : float
        Average stale rate across queries.
    max_stale_rate : float
        Worst single-query stale rate.
    queries_above_threshold : list[str]
        Queries where stale_rate > threshold.
    """

    total_queries: int = 0
    total_chunks_retrieved: int = 0
    total_stale: int = 0
    avg_stale_rate: float = 0.0
    max_stale_rate: float = 0.0
    queries_above_threshold: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# StaleHitAnalyzer
# ---------------------------------------------------------------------------


class StaleHitAnalyzer:
    """Analyzes stale-hit rate by comparing retrieval results against a
    freshness manifest.

    Args:
        stale_rate_threshold : float
            Above this stale rate, a query is flagged.
    """

    def __init__(self, stale_rate_threshold: float = 0.1) -> None:
        if not 0.0 <= stale_rate_threshold <= 1.0:
            raise ValueError(f"stale_rate_threshold must be in [0, 1], got {stale_rate_threshold}")
        self._stale_rate_threshold = stale_rate_threshold

    def compute_stale_hit(
        self,
        query: str,
        retrieved_ids: list[str],
        freshness_manifest: dict[str, str],
        current_hashes: dict[str, str],
    ) -> StaleHitResult:
        """Compute stale-hit for a single query.

        Args:
            query: The query string.
            retrieved_ids: Chunk IDs returned by retrieval.
            freshness_manifest: Mapping chunk_id → expected content_hash
                (the "ground truth" from the last index build).
            current_hashes: Mapping chunk_id → current content_hash
                (from the canonical source right now).

        Returns:
            ``StaleHitResult`` with stale/fresh classification.
        """
        if not isinstance(retrieved_ids, list):
            raise TypeError(f"retrieved_ids must be list, got {type(retrieved_ids).__name__}")
        if not isinstance(freshness_manifest, dict):
            raise TypeError(f"freshness_manifest must be dict, got {type(freshness_manifest).__name__}")
        if not isinstance(current_hashes, dict):
            raise TypeError(f"current_hashes must be dict, got {type(current_hashes).__name__}")
        stale: list[str] = []
        fresh: list[str] = []

        for cid in retrieved_ids:
            if cid not in freshness_manifest:
                # Not in manifest at all — treat as stale (orphan)
                stale.append(cid)
                continue
            expected_hash = freshness_manifest[cid]
            current_hash = current_hashes.get(cid)
            if current_hash is None:
                # In manifest but missing from current source — stale
                stale.append(cid)
            elif current_hash != expected_hash:
                stale.append(cid)
            else:
                fresh.append(cid)

        total = len(retrieved_ids)
        stale_rate = len(stale) / total if total > 0 else 0.0

        return StaleHitResult(
            query=query,
            retrieved_ids=retrieved_ids,
            stale_ids=stale,
            fresh_ids=fresh,
            stale_rate=stale_rate,
        )

    def compute_report(
        self,
        results: list[StaleHitResult],
    ) -> StaleHitReport:
        """Aggregate stale-hit results into a report."""
        if not results:
            return StaleHitReport()

        n = len(results)
        total_chunks = sum(len(r.retrieved_ids) for r in results)
        total_stale = sum(len(r.stale_ids) for r in results)
        avg_rate = sum(r.stale_rate for r in results) / n
        max_rate = max(r.stale_rate for r in results)
        above = [
            r.query
            for r in results
            if r.stale_rate > self._stale_rate_threshold
        ]

        return StaleHitReport(
            total_queries=n,
            total_chunks_retrieved=total_chunks,
            total_stale=total_stale,
            avg_stale_rate=avg_rate,
            max_stale_rate=max_rate,
            queries_above_threshold=above,
        )
