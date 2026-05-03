"""Cross-encoder reranker for apps_qna route ranking (W2.1).

Wave 2 phase 2.1 of ``apps-qna-dag-enhancements-e4c7b2``. The bi-encoder
path (spine ``classify_section_topic`` / BGE-M3) produces a point estimate
per route by computing the cosine between a single text embedding and each
route-descriptor embedding. This is cheap but has a well-known ceiling
because the two inputs never cross-attend.

A cross-encoder reads both inputs as a single sequence and produces a
relevance score directly. For a 9-route registry the added latency is
~10-80 ms (reranker already warm, 568M-param model on GPU), which is
acceptable for offline triage and eval work but inconvenient at real-time
speeds — the reranker is therefore an opt-in pass invoked ONLY on the
bi-encoder's top-K, not every route.

Design contract
---------------
* Wraps the spine ``BgeRerankerAdapter`` (BAAI/bge-reranker-v2-m3). All
  model weights, GPU device resolution, and FP16 loading are owned by
  ``agentic_core.knowledge.retrieval.bge_reranker_adapter``.
* Gracefully degrades when the cross-encoder is unavailable (missing
  sentence-transformers, missing weights, env gate disabled) — returns
  the input ranking unchanged so callers never have to branch.
* Emits the constitutional §29 paired ``ROUTER_DECISION:`` marker + an
  ``apps_qna_pack_lifecycle`` ledger row (``event_kind="rerank_pass"``)
  per reranker invocation, so downstream learning and audits can reason
  about rerank deltas without scraping logs.

This module does not implement a bandit; it is a pure reranker pass. The
W4.1 ``AppsQnaRouteBandit`` uses this module (W2.3) by passing a bi-encoder
top-K through ``rerank_routes`` and then handing the reranked top-N to its
Thompson-sampled posterior priors.
"""

from __future__ import annotations

import logging
import os
import uuid
from dataclasses import dataclass, replace
from typing import TYPE_CHECKING

from apps_qna.integrations.spine_adapter import emit_pack_lifecycle_event

if TYPE_CHECKING:
    from apps_qna.router.semantic_router import RouteScore

_log = logging.getLogger(__name__)

# §29 marker emission constants.
_ROUTER_LAYER: str = "L0"
_ROUTER_NAME: str = "apps_qna_reranker"

# Env gate: set ``APPS_QNA_RERANKER=1`` to opt into the cross-encoder
# pass at runtime. When unset, ``rerank_routes`` returns its input
# unchanged (and logs at debug). This keeps the bi-encoder hot path
# free of the ~10-80 ms cross-encoder cost unless a caller has explicitly
# opted in for depth (eval harness, W2.3 seeding, etc.).
_ENV_ENABLE_RERANKER: str = "APPS_QNA_RERANKER"


def _reranker_enabled() -> bool:
    """True iff ``APPS_QNA_RERANKER`` env flag is on."""
    return os.environ.get(_ENV_ENABLE_RERANKER, "").strip().lower() in {
        "1",
        "true",
        "yes",
    }


@dataclass(frozen=True)
class RerankOutcome:
    """Output of a reranker pass.

    ``reranked`` is the input ranking re-sorted by cross-encoder score
    (descending). ``mode`` indicates which path produced the final order:

      * ``"cross_encoder"`` — CE ran; order reflects CE scores.
      * ``"bi_encoder_passthrough"`` — CE unavailable/disabled; input
        order preserved so callers can treat the result identically.

    ``rerank_delta`` is the sum of rank-shifts (|old_rank - new_rank|)
    across the input routes — a simple scalar W2 ledger feature capturing
    how much the reranker disagreed with the bi-encoder. Zero under
    passthrough or when the orders coincide.
    """

    reranked: list["RouteScore"]
    mode: str
    rerank_delta: int
    decision_id: str


def _emit_rerank_decision_marker(
    *,
    decision_id: str,
    selected: str,
    mode: str,
    k: int,
    rerank_delta: int,
) -> None:
    """Constitutional §29 paired marker for a reranker pass."""
    print(
        f"ROUTER_DECISION: layer={_ROUTER_LAYER} router={_ROUTER_NAME} "
        f"decision_id={decision_id} selected={selected} mode={mode} "
        f"k={k} rerank_delta={rerank_delta}"
    )


def rerank_routes(
    *,
    query: str,
    candidates: list["RouteScore"],
    descriptors: dict[str, str],
    top_n: int | None = None,
) -> RerankOutcome:
    """Cross-encoder pass over a bi-encoder ranking.

    Args:
        query: The live question / signal to score against each candidate.
        candidates: Bi-encoder ranking (e.g. ``SemanticRouter.route`` output).
            Must be ordered by bi-encoder score descending; order is used
            to compute ``rerank_delta``.
        descriptors: ``{route_id: descriptor}`` map (same descriptors the
            bi-encoder scored against — pass the one from
            ``route_seeding.build_route_descriptor``).
        top_n: Optional cap on the returned list. When None, all input
            candidates are returned in reranked order.

    Returns:
        ``RerankOutcome`` — reranked list + mode + delta + decision_id.

    Fail-soft contract: any failure on the cross-encoder path (missing
    deps, missing weights, GPU OOM, unexpected exception) is logged at
    debug and the function returns the bi-encoder passthrough — callers
    never need to branch. §29 marker + ledger row are emitted in both
    paths so passthrough is visible in the telemetry stream.
    """
    decision_id = uuid.uuid4().hex
    k = len(candidates)
    if k == 0:
        _emit_rerank_decision_marker(
            decision_id=decision_id,
            selected="",
            mode="bi_encoder_passthrough",
            k=0,
            rerank_delta=0,
        )
        emit_pack_lifecycle_event(
            event_kind="rerank_pass",
            prediction={
                "query_length": len(query),
                "k": 0,
                "mode": "bi_encoder_passthrough",
                "rerank_delta": 0,
            },
            metadata={"decision_id": decision_id},
        )
        return RerankOutcome(
            reranked=[],
            mode="bi_encoder_passthrough",
            rerank_delta=0,
            decision_id=decision_id,
        )

    if not _reranker_enabled():
        _log.debug("reranker disabled via env; passthrough k=%d", k)
        out_list = candidates[:top_n] if top_n is not None else list(candidates)
        _emit_rerank_decision_marker(
            decision_id=decision_id,
            selected=out_list[0].route_id if out_list else "",
            mode="bi_encoder_passthrough",
            k=k,
            rerank_delta=0,
        )
        emit_pack_lifecycle_event(
            event_kind="rerank_pass",
            prediction={
                "query_length": len(query),
                "k": k,
                "mode": "bi_encoder_passthrough",
                "rerank_delta": 0,
                "top_route": out_list[0].route_id if out_list else "",
            },
            metadata={"decision_id": decision_id, "reason": "env_gate_off"},
        )
        return RerankOutcome(
            reranked=out_list,
            mode="bi_encoder_passthrough",
            rerank_delta=0,
            decision_id=decision_id,
        )

    try:
        from agentic_core.knowledge.retrieval.bge_reranker_adapter import (  # noqa: PLC0415
            BgeRerankerAdapter,
            CrossEncoderUnavailable,
        )
    except ImportError as exc:
        _log.debug("reranker import failed: %r — passthrough", exc)
        return _passthrough(query, candidates, top_n, decision_id, "import_error")

    adapter = BgeRerankerAdapter()
    texts = [descriptors.get(c.route_id, c.route_name) for c in candidates]
    try:
        raw_scores = adapter.score(query, texts)
    except CrossEncoderUnavailable as exc:
        _log.debug("cross-encoder unavailable: %r — passthrough", exc)
        return _passthrough(query, candidates, top_n, decision_id, "ce_unavailable")
    except (RuntimeError, ValueError, OSError) as exc:
        _log.debug("cross-encoder score failed: %r — passthrough", exc)
        return _passthrough(query, candidates, top_n, decision_id, "ce_error")

    # Rebind each candidate with the CE score, then sort descending.
    scored = [replace(c, score=float(s)) for c, s in zip(candidates, raw_scores)]
    scored.sort(key=lambda x: (x.score, x.route_id), reverse=True)

    # rerank_delta = sum of absolute rank shifts.
    orig_rank = {c.route_id: i for i, c in enumerate(candidates)}
    new_rank = {c.route_id: i for i, c in enumerate(scored)}
    rerank_delta = sum(abs(orig_rank[rid] - new_rank[rid]) for rid in orig_rank)

    out_list = scored[:top_n] if top_n is not None else scored
    _emit_rerank_decision_marker(
        decision_id=decision_id,
        selected=out_list[0].route_id if out_list else "",
        mode="cross_encoder",
        k=k,
        rerank_delta=rerank_delta,
    )
    emit_pack_lifecycle_event(
        event_kind="rerank_pass",
        prediction={
            "query_length": len(query),
            "k": k,
            "mode": "cross_encoder",
            "rerank_delta": rerank_delta,
            "top_route": out_list[0].route_id if out_list else "",
            "ce_scores": [float(s) for s in raw_scores],
        },
        score_numeric=float(out_list[0].score) if out_list else None,
        metadata={"decision_id": decision_id},
    )
    return RerankOutcome(
        reranked=out_list,
        mode="cross_encoder",
        rerank_delta=rerank_delta,
        decision_id=decision_id,
    )


def _passthrough(
    query: str,
    candidates: list["RouteScore"],
    top_n: int | None,
    decision_id: str,
    reason: str,
) -> RerankOutcome:
    """Bi-encoder passthrough with §29 emission."""
    out_list = candidates[:top_n] if top_n is not None else list(candidates)
    _emit_rerank_decision_marker(
        decision_id=decision_id,
        selected=out_list[0].route_id if out_list else "",
        mode="bi_encoder_passthrough",
        k=len(candidates),
        rerank_delta=0,
    )
    emit_pack_lifecycle_event(
        event_kind="rerank_pass",
        prediction={
            "query_length": len(query),
            "k": len(candidates),
            "mode": "bi_encoder_passthrough",
            "rerank_delta": 0,
            "top_route": out_list[0].route_id if out_list else "",
        },
        metadata={"decision_id": decision_id, "reason": reason},
    )
    return RerankOutcome(
        reranked=out_list,
        mode="bi_encoder_passthrough",
        rerank_delta=0,
        decision_id=decision_id,
    )


def rerank_candidate_scores(
    *,
    query: str,
    candidates: list[tuple[str, float, str]],
    descriptors: dict[str, str],
    top_n: int | None = None,
) -> tuple[list[tuple[str, float, str]], str, int]:
    """Tuple-based reranker entrypoint for ``rank_routes_by_signal`` (W2.3).

    Args:
        query: Signal/question to rerank against.
        candidates: ``[(route_id, score, mode), ...]`` ordered by bi-encoder
            score descending.
        descriptors: ``{route_id: descriptor}`` map.
        top_n: Optional cap on returned list length.

    Returns:
        ``(reranked_tuples, mode, rerank_delta)``.

    Fail-soft passthrough on every error path, same contract as
    ``rerank_routes``. §29 marker + ledger emission happen inside
    ``rerank_routes`` which this function delegates to via a lightweight
    adapter — constructed RouteScore objects are a transient implementation
    detail; callers see only tuples.
    """
    # Local import avoids a cycle: semantic_router imports this module
    # indirectly through route_seeding, so we defer the RouteScore import.
    from apps_qna.router.semantic_router import RouteScore  # noqa: PLC0415

    if not candidates:
        outcome = rerank_routes(
            query=query,
            candidates=[],
            descriptors=descriptors,
            top_n=top_n,
        )
        return ([], outcome.mode, outcome.rerank_delta)

    # Wrap tuples into RouteScore for the typed reranker surface.
    wrapped: list[RouteScore] = [
        RouteScore(
            route_id=rid,
            route_name=rid,
            primary_card="",
            score=float(score),
            mode=mode,
        )
        for rid, score, mode in candidates
    ]
    outcome = rerank_routes(
        query=query,
        candidates=wrapped,
        descriptors=descriptors,
        top_n=top_n,
    )
    # Restore the tuple shape; preserve each candidate's ORIGINAL mode
    # (bi-encoder/keyword label from classify_section_topic) since the
    # cross-encoder does not re-emit mode semantics.
    orig_mode = {rid: mode for rid, _, mode in candidates}
    out_tuples: list[tuple[str, float, str]] = [
        (rs.route_id, float(rs.score), orig_mode.get(rs.route_id, rs.mode))
        for rs in outcome.reranked
    ]
    return (out_tuples, outcome.mode, outcome.rerank_delta)


__all__ = ["RerankOutcome", "rerank_routes", "rerank_candidate_scores"]
