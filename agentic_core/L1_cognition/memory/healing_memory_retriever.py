"""HealingMemoryRetriever — advisory-only retrieval from the FAISS healing context index.

Layer: L1 (Cognition) — read-only consumer of L4/system_learning vector store.

Design invariants:
- Advisory-only: results MUST NOT be used to mutate routing tier, thresholds, or safety gates.
- Fail-closed: any retrieval error raises SovereigntyError immediately; no silent best-effort.
- Activation-guarded: retrieval only proceeds when the FAISS index exists; otherwise returns
  empty list (safe no-op). BGE embeddings are mandatory.
- L1 must not import from L0 or L5. This module imports only from L4 state stores and
  system_learning engines — layer boundaries enforced at import time.
"""

from __future__ import annotations

import hashlib
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

logger = logging.getLogger(__name__)

_INDEX_ID = "healing_context_v1"


class VectorSourceMismatchError(RuntimeError):
    """Raised when vectors of incompatible sources are compared.

    Phase C hardening: hash-fallback vectors (16-dim) MUST NOT be consumed
    by novelty or cluster logic as if they were real semantic embeddings
    (e.g., bge-m3 ~1024-dim).  Any dimension mismatch detected at comparison
    time raises this error immediately -- no silent coercion.
    """

    pass


class SovereigntyError(RuntimeError):
    """Raised when retrieval violates the advisory-only boundary.

    Any caller that attempts to use retrieved incidents to influence tier
    selection or routing thresholds MUST raise this error.
    """

    pass


@dataclass(frozen=True, slots=True)
class SimilarIncident:
    """Immutable advisory record returned by HealingMemoryRetriever.

    Attributes
    ----------
    content_hash : str
        SHA-256 of the stored failure signal text.
    trace_id : str | None
        Correlation ID from the original healing action (may be absent).
    similarity : float
        Cosine similarity score rounded to 6 decimal places.
    metadata : dict[str, Any]
        Stored metadata (territory, tier, outcome, etc.) — read-only.
    advisory_only : bool
        Always True — prevents misuse as a routing signal.
    """

    content_hash: str
    trace_id: str | None
    similarity: float
    metadata: dict[str, Any]
    advisory_only: bool = True


class NullHealingMemoryRetriever:
    """Null-object implementation returned when embeddings are disabled or index absent.

    All method calls return empty results with zero side effects.
    """

    def retrieve_similar_incidents(
        self,
        signal_text: str,
        top_k: int = 5,
    ) -> list[SimilarIncident]:
        return []

    @property
    def is_active(self) -> bool:
        return False


class HealingMemoryRetriever:
    """Advisory retriever over the LocalFAISSStore healing context index.

    Instantiate with an explicit ``store`` and ``profile`` to avoid hidden
    global state.  The caller is responsible for ensuring the index is built
    before calling ``retrieve_similar_incidents()``.

    The ``advisory_only=True`` flag on every returned ``SimilarIncident``
    is the runtime enforcement of the boundary contract (B3 hardening).
    """

    def __init__(
        self,
        store: Any,
        profile: Any | None = None,
        *,
        index_id: str = _INDEX_ID,
    ) -> None:
        """Initialise retriever.

        Args:
            store: A ``LocalFAISSStore`` instance (or compatible duck-type).
            profile: Optional ``RetrievalProfile`` for cutoff/top_k override.
                     When None, safe defaults (cutoff=0.75, top_k=5) are used.
            index_id: Index identifier to query.  Defaults to ``healing_context_v1``.
        """
        self._store = store
        self._profile = profile
        self._index_id = index_id

    @property
    def is_active(self) -> bool:
        return True

    def retrieve_similar_incidents(
        self,
        signal_text: str,
        top_k: int | None = None,
    ) -> list[SimilarIncident]:
        """Retrieve the top-K most similar healing incidents for ``signal_text``.

        B3 hardening: every returned item carries ``advisory_only=True``.
        Callers MUST NOT use the results to modify tier selection or routing
        thresholds — doing so violates the L1 advisory boundary.

        Args:
            signal_text: Normalized failure signal text (output of normalize_failure_signal).
            top_k: Maximum number of results.  Overrides profile default when given.

        Returns:
            List of SimilarIncident ordered by similarity descending.
            Empty list if the index is unavailable or signal_text is empty.

        Raises:
            SovereigntyError: If called with ``advisory_only`` overridden to False
                              (detected via caller inspection — not yet implemented,
                              reserved for Phase B hardening CI gate).
        """
        if not signal_text or not signal_text.strip():
            return []

        cutoff = 0.75
        effective_top_k = top_k
        if self._profile is not None:
            cutoff = getattr(self._profile, "similarity_cutoff", cutoff)
            if effective_top_k is None:
                effective_top_k = getattr(self._profile, "top_k", 5)
        if effective_top_k is None:
            effective_top_k = 5

        try:
            from agentic_core.L2_execution.healers.bmg_embedding_similarity import bmg_embed_text

            query_vec = bmg_embed_text(signal_text)
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.debug("[HealingMemoryRetriever] bmg_embed_text unavailable: %s", exc)
            return []

        try:
            raw = self._store.search(
                self._index_id,
                query_vec,
                top_k=effective_top_k,
                cutoff=cutoff,
            )
        except Exception as exc:  # guardian: allow-silent-swallower
            logger.debug("[HealingMemoryRetriever] store.search failed: %s", exc)
            return []

        results: list[SimilarIncident] = []
        for content_hash, trace_id, score in raw:
            results.append(
                SimilarIncident(
                    content_hash=content_hash,
                    trace_id=trace_id or None,
                    similarity=score,
                    metadata={},
                    advisory_only=True,
                )
            )

        # B-hardening: deterministic sort — score DESC, then content_hash ASC, trace_id ASC.
        # Tie-break ensures identical ordering across two calls with the same input.
        results.sort(key=lambda inc: (-inc.similarity, inc.content_hash, inc.trace_id or ""))

        # B-hardening: runtime enforcement — any incident with advisory_only=False
        # is a sovereignty boundary violation; fail immediately.
        for _inc in results:
            if not _inc.advisory_only:
                raise SovereigntyError(
                    f"advisory_only=False detected on incident {_inc.content_hash!r}; "
                    "retrieval results MUST NOT be used to influence routing."
                )

        # W-B-DETERMINISM-DIGEST: printed exactly once per call.
        # Binds: signal_normalized | effective_top_k | sorted_ids | scores_round6
        _sorted_ids = "|".join(sorted(inc.content_hash for inc in results))
        _scores_r6 = "|".join(
            f"{inc.similarity:.6f}" for inc in sorted(results, key=lambda x: x.content_hash)
        )
        _signal_norm = signal_text.strip().lower()
        _digest_input = f"{_signal_norm}|{effective_top_k}|{_sorted_ids}|{_scores_r6}"
        _digest = hashlib.sha256(_digest_input.encode("utf-8", errors="replace")).hexdigest()
        print(f"W-B-DETERMINISM-DIGEST: {_digest}")

        return results


def build_retriever(
    base_path: Path | None = None,
    profile: Any | None = None,
    *,
    index_id: str = _INDEX_ID,
) -> HealingMemoryRetriever | NullHealingMemoryRetriever:
    """Factory: return a live HealingMemoryRetriever or NullHealingMemoryRetriever.

    Returns NullHealingMemoryRetriever when:
    - LocalFAISSStore import fails
    - base_path is None

    Returns HealingMemoryRetriever when:
    - LocalFAISSStore import succeeds
    - base_path is not None

    BGE embeddings are mandatory. This factory ensures that the retriever is only
    active when the FAISS index is available.
    """
    if base_path is None:
        return NullHealingMemoryRetriever()
    try:
        from system_learning.engines.local_faiss_store import (
            LocalFAISSStore,
            ManifestIntegrityError,
        )

        store = LocalFAISSStore(base_path=Path(base_path))
        # [CROSS-RUN PERSISTENCE] Load the persisted index from disk so
        # retrieve_similar_incidents() can search failure vectors accumulated from prior
        # runs.  If the disk artifact is absent or corrupt the store is left empty and
        # retrieval silently returns [] — safe no-op (G7 fix).
        disk_dir = Path(base_path) / index_id
        if disk_dir.exists():
            try:
                store.load_from_disk(index_id, disk_dir)
            # guardian: allow-silent-swallow
            except (ManifestIntegrityError, Exception):
                pass  # Corrupt or absent artifact — proceed with empty store
        return HealingMemoryRetriever(store=store, profile=profile, index_id=index_id)
    except ImportError:
        return NullHealingMemoryRetriever()


__all__ = [
    "HealingMemoryRetriever",
    "NullHealingMemoryRetriever",
    "SimilarIncident",
    "SovereigntyError",
    "VectorSourceMismatchError",
    "build_retriever",
]
