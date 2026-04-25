"""Trajectory exemplar store — G6 (plan ``system-learning-waves-7b3c91`` D1).

In-process retrieval corpus of **successful** past trajectories, consulted at
plan time by L0/L1 planners so every run does not re-derive plans from zero.

Derived from arXiv 2505.17716 ("Get Experience from Practice: LLM Agents with
Record & Replay"). Successful trajectories become a retrievable experience
asset alongside the RAG corpus; hits cut cost and variance.

Design:

- Index keyed on ``query_shape`` — a cheap normalized form of the user
  request (downcased, whitespace-collapsed, length-bucketed) plus a
  small set of feature tokens. Not a full embedding — that belongs to
  ``retrieval_case_embedder`` (seed source; see adapter).
- Each exemplar carries: ``exemplar_id``, ``trajectory`` (opaque blob), a
  ``score`` in ``[0, 1]`` (post-eval composite), ``cost_tokens``,
  ``created_at``, plus optional ``tags``.
- Retrieval returns up to ``k`` exemplars ranked by (score, -cost_tokens,
  -recency) with a hard floor on ``min_score`` so the planner never sees
  marginal examples.
- Pure in-memory; persistence is a follow-on (seed from
  ``retrieval_case_embedder`` via
  :mod:`system_learning.adapters.exemplar_consult_adapter`).

The store is intentionally *dumb* — planners call it through the adapter;
no planner takes a hard dependency on this module.
"""

from __future__ import annotations

import re
import threading
import time
from dataclasses import dataclass, field, replace
from typing import Any, Iterable, Mapping, Sequence


_WHITESPACE = re.compile(r"\s+")
_NON_WORD = re.compile(r"[^a-z0-9\s]+")


def _normalize_query(text: str) -> str:
    """Cheap, deterministic query normalization for keying.

    Downcase, strip non-word characters, collapse whitespace. Keeps the
    store platform-agnostic (no tokenizer dependency).
    """

    lowered = text.lower()
    stripped = _NON_WORD.sub(" ", lowered)
    collapsed = _WHITESPACE.sub(" ", stripped).strip()
    return collapsed


def _length_bucket(text: str) -> str:
    n = len(text)
    if n < 32:
        return "xs"
    if n < 128:
        return "s"
    if n < 512:
        return "m"
    if n < 2048:
        return "l"
    return "xl"


def _query_shape(text: str) -> str:
    return f"{_length_bucket(text)}::{_normalize_query(text)[:256]}"


@dataclass(frozen=True)
class TrajectoryExemplar:
    """One entry in the exemplar store."""

    exemplar_id: str
    query_text: str
    trajectory: Mapping[str, Any]
    score: float
    cost_tokens: int = 0
    created_at: float = field(default_factory=time.time)
    tags: frozenset[str] = field(default_factory=frozenset)

    @property
    def query_shape(self) -> str:
        return _query_shape(self.query_text)


@dataclass(frozen=True)
class ExemplarHit:
    """A retrieval result ranked by the store."""

    exemplar: TrajectoryExemplar
    rank: int
    score: float
    reason: str


class TrajectoryExemplarStore:
    """Thread-safe in-memory exemplar index."""

    def __init__(
        self,
        *,
        min_score: float = 0.75,
        max_entries: int = 10_000,
    ) -> None:
        if not (0.0 <= min_score <= 1.0):
            raise ValueError("min_score must be in [0, 1]")
        self._min_score = min_score
        self._max_entries = max_entries
        self._by_shape: dict[str, list[TrajectoryExemplar]] = {}
        self._by_id: dict[str, TrajectoryExemplar] = {}
        self._lock = threading.Lock()

    @property
    def size(self) -> int:
        with self._lock:
            return len(self._by_id)

    def clear(self) -> None:
        with self._lock:
            self._by_shape.clear()
            self._by_id.clear()

    def add(self, exemplar: TrajectoryExemplar) -> bool:
        """Add ``exemplar`` to the index.

        Returns ``True`` if the exemplar was stored, ``False`` if it was
        filtered out because its score was below ``min_score`` or the store
        already contains an exemplar with the same id (idempotent add).
        """

        if exemplar.score < self._min_score:
            return False
        with self._lock:
            if exemplar.exemplar_id in self._by_id:
                return False
            if len(self._by_id) >= self._max_entries:
                # Evict lowest-scoring existing entry deterministically.
                worst = min(self._by_id.values(), key=lambda e: (e.score, e.created_at))
                self._remove_locked(worst.exemplar_id)
            self._by_id[exemplar.exemplar_id] = exemplar
            self._by_shape.setdefault(exemplar.query_shape, []).append(exemplar)
            return True

    def _remove_locked(self, exemplar_id: str) -> None:
        existing = self._by_id.pop(exemplar_id, None)
        if existing is None:
            return
        bucket = self._by_shape.get(existing.query_shape, [])
        self._by_shape[existing.query_shape] = [e for e in bucket if e.exemplar_id != exemplar_id]
        if not self._by_shape[existing.query_shape]:
            self._by_shape.pop(existing.query_shape, None)

    def bulk_add(self, exemplars: Iterable[TrajectoryExemplar]) -> int:
        added = 0
        for exemplar in exemplars:
            if self.add(exemplar):
                added += 1
        return added

    def consult(
        self,
        query_text: str,
        *,
        k: int = 3,
        required_tags: Sequence[str] = (),
    ) -> list[ExemplarHit]:
        """Return up to ``k`` ranked exemplars matching ``query_text``.

        Ranking: exact ``query_shape`` bucket first, then any exemplar whose
        normalized text shares all tokens with the query (bag-of-words
        containment). Within a group, ordering is (score desc, cost asc,
        recency desc).
        """

        shape = _query_shape(query_text)
        normalized_query_tokens = set(_normalize_query(query_text).split())
        with self._lock:
            exact_bucket = list(self._by_shape.get(shape, []))
            # Candidate pool for fuzzy match = all entries whose query tokens
            # are a subset of the query tokens (query covers the exemplar).
            fuzzy_bucket: list[TrajectoryExemplar] = []
            for exemplar in self._by_id.values():
                if exemplar.query_shape == shape:
                    continue  # already in exact_bucket
                exemplar_tokens = set(_normalize_query(exemplar.query_text).split())
                if exemplar_tokens and exemplar_tokens.issubset(normalized_query_tokens):
                    fuzzy_bucket.append(exemplar)

        if required_tags:
            required_set = frozenset(required_tags)
            exact_bucket = [e for e in exact_bucket if required_set.issubset(e.tags)]
            fuzzy_bucket = [e for e in fuzzy_bucket if required_set.issubset(e.tags)]

        def sort_key(exemplar: TrajectoryExemplar) -> tuple[float, int, float]:
            return (-exemplar.score, exemplar.cost_tokens, -exemplar.created_at)

        exact_bucket.sort(key=sort_key)
        fuzzy_bucket.sort(key=sort_key)

        hits: list[ExemplarHit] = []
        for idx, exemplar in enumerate(exact_bucket[:k]):
            hits.append(
                ExemplarHit(
                    exemplar=exemplar,
                    rank=idx,
                    score=exemplar.score,
                    reason="exact_shape_match",
                )
            )
        remaining = k - len(hits)
        if remaining > 0:
            for idx, exemplar in enumerate(fuzzy_bucket[:remaining]):
                hits.append(
                    ExemplarHit(
                        exemplar=exemplar,
                        rank=len(hits),
                        score=exemplar.score,
                        reason="token_subset_match",
                    )
                )
        return hits

    def demote(self, exemplar_id: str, new_score: float) -> bool:
        """Lower an exemplar's score in place (e.g., after a bad replay)."""

        if not (0.0 <= new_score <= 1.0):
            raise ValueError("new_score must be in [0, 1]")
        with self._lock:
            existing = self._by_id.get(exemplar_id)
            if existing is None:
                return False
            updated = replace(existing, score=new_score)
            self._by_id[exemplar_id] = updated
            bucket = self._by_shape.get(existing.query_shape, [])
            self._by_shape[existing.query_shape] = [
                updated if e.exemplar_id == exemplar_id else e for e in bucket
            ]
            # If it fell below the min_score threshold, evict.
            if new_score < self._min_score:
                self._remove_locked(exemplar_id)
            return True
