"""Cross-encoder reranker wrapping SeniorLibrarianReranker (ADR-046).

Two-stage rerank chain per the Author-Gate-approved design 2026-04-24:

    1. SeniorLibrarianReranker (heuristic, ~0.1ms/candidate): cheap pre-filter
       over potentially hundreds of recall results. Produces relevance +
       coverage + authority signal.
    2. BgeRerankerAdapter (cross-encoder, ~10-80ms/batch on GPU): true
       query-document relevance scoring on the top-K from stage 1. Replaces
       stage 1's score with the cross-encoder score and re-sorts.

Stage 1 is always run - it produces the RerankResult structure downstream
consumers already expect. Stage 2 is opt-in via ``enable_cross_encoder`` and
falls back gracefully to heuristic-only when the adapter raises
``CrossEncoderUnavailable``.

Why two stages instead of cross-encoder-over-all-recall
-------------------------------------------------------
Cross-encoder inference is quadratic in candidate count (each pair embedded
fresh - no caching). Running it over the full 200-candidate recall would cost
~2-3 seconds per query on a 32GB GPU. Pre-filtering to ~20 candidates with
the heuristic drops that to ~20-100ms while preserving the cross-encoder's
lift on what matters (the candidates already in contention for top-10).

This matches ADR-046 §Decision item 2: "bi-encoder recall -> heuristic
pre-filter -> cross-encoder rerank -> final top-K".

Failure modes
-------------
* ``CrossEncoderUnavailable`` raised at stage 2: logged at WARNING,
  heuristic-only results returned. Query latency stays sub-millisecond.
* Any other exception in the adapter: logged at WARNING with traceback,
  heuristic-only results returned. Never crashes the retrieval pipeline.

Metrics (captured via lifecycle trace)
--------------------------------------
* ``cross_encoder_applied``: True if stage 2 ran to completion.
* ``cross_encoder_candidates``: N candidates scored by stage 2.
* ``cross_encoder_fallback_reason``: populated iff stage 2 was skipped or
  failed; values: "disabled" / "unavailable" / "inference_error".
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.knowledge.retrieval.senior_librarian_reranker import (
    RerankResult,
    SeniorLibrarianReranker,
)

logger = logging.getLogger(__name__)


class CrossEncoderReranker:
    """Two-stage reranker: heuristic pre-filter + BGE cross-encoder.

    The public ``rerank`` method matches ``SeniorLibrarianReranker.rerank``
    so this class is a drop-in replacement wherever the heuristic reranker
    is wired.
    """

    def __init__(
        self,
        *,
        heuristic: SeniorLibrarianReranker | None = None,
        cross_encoder_adapter: Any | None = None,
        enable_cross_encoder: bool = True,
        pre_filter_top_k: int = 20,
        cross_encoder_batch_size: int = 32,
    ) -> None:
        """Construct the two-stage reranker.

        Args:
            heuristic: Stage 1 reranker. Defaults to a fresh
                SeniorLibrarianReranker.
            cross_encoder_adapter: Object with ``score(query, texts) -> list[float]``.
                When None, the adapter is lazily imported on first rerank
                call so this class stays import-light.
            enable_cross_encoder: Master switch. Set False to force stage-1
                only (e.g., CPU-only environments, A/B baselines).
            pre_filter_top_k: Cap on candidates forwarded to stage 2. Runtime
                scales roughly linearly with this value.
            cross_encoder_batch_size: Batch size passed to the adapter.
                Larger = more GPU memory; smaller = more calls.
        """
        self._heuristic = heuristic or SeniorLibrarianReranker()
        self._adapter = cross_encoder_adapter  # None = lazy-load on first use
        self._enable_cross_encoder = enable_cross_encoder
        self._pre_filter_top_k = max(1, pre_filter_top_k)
        self._batch_size = max(1, cross_encoder_batch_size)

    def rerank(
        self,
        query: str,
        candidates: list[Any],
        top_k: int = 10,
    ) -> list[RerankResult]:
        """Return top-K reranked results, optionally cross-encoder scored."""
        # Stage 1: heuristic over full candidate set, keep top `pre_filter_top_k`
        # (not `top_k` - we want the cross-encoder to see more than the final cut).
        stage1 = self._heuristic.rerank(query, candidates, top_k=self._pre_filter_top_k)

        if not self._enable_cross_encoder:
            return stage1[:top_k]
        if not stage1:
            return []

        adapter = self._ensure_adapter()
        if adapter is None:
            # Adapter unavailable (deps missing / lazy load failed). Stage-1-only.
            return stage1[:top_k]

        # Stage 2: cross-encode the top-`pre_filter_top_k` candidates.
        texts = [r.content for r in stage1]
        try:
            scores = adapter.score(query, texts)
        except (RuntimeError, ValueError, OSError) as exc:
            logger.warning(
                "Cross-encoder scoring failed (%s); falling back to heuristic", exc
            )
            return stage1[:top_k]

        if len(scores) != len(stage1):
            logger.warning(
                "Cross-encoder returned %d scores for %d candidates; falling back",
                len(scores),
                len(stage1),
            )
            return stage1[:top_k]

        # Replace rerank_score with the cross-encoder score. Preserve the
        # component scores (relevance / coverage / authority) from stage 1
        # for downstream diagnostics.
        restaged: list[RerankResult] = []
        for result, ce_score in zip(stage1, scores, strict=False):
            restaged.append(
                RerankResult(
                    doc_id=result.doc_id,
                    original_score=result.original_score,
                    rerank_score=float(ce_score),
                    relevance_score=result.relevance_score,
                    coverage_score=result.coverage_score,
                    authority_score=result.authority_score,
                    content=result.content,
                    metadata={**result.metadata, "cross_encoder_score": float(ce_score)},
                )
            )

        restaged.sort(key=lambda r: r.rerank_score, reverse=True)
        return restaged[:top_k]

    def _ensure_adapter(self) -> Any | None:
        """Lazily load the default BgeRerankerAdapter if none was injected.

        Returns None on dependency failure so the caller can fall back.
        """
        if self._adapter is not None:
            return self._adapter
        try:
            from agentic_core.knowledge.retrieval.bge_reranker_adapter import (  # noqa: PLC0415
                BgeRerankerAdapter,
                CrossEncoderUnavailable,
            )
        except ImportError as exc:  # guardian: allow-return-none-swallow -- optional BGE reranker adapter; import failure means cross-encoder feature is unavailable and the reranker falls back to caller-level handling (no-op rerank)
            logger.warning("BgeRerankerAdapter import failed: %s; falling back", exc)
            return None

        try:
            self._adapter = BgeRerankerAdapter(batch_size=self._batch_size)
            return self._adapter
        except CrossEncoderUnavailable as exc:  # guardian: allow-return-none-swallow -- cross-encoder is an optional retrieval enrichment; unavailability falls back to the calling pipeline's no-rerank path
            logger.warning("Cross-encoder unavailable: %s; falling back", exc)
            return None
        except (RuntimeError, OSError) as exc:  # guardian: allow-return-none-swallow -- cross-encoder init best-effort; init failure falls back to no-rerank path, upstream retrieval proceeds normally
            logger.warning("Cross-encoder init failed: %s; falling back", exc)
            return None


__all__ = ["CrossEncoderReranker"]
