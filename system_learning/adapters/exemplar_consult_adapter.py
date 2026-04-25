"""L0/L1 consult adapter for :mod:`system_learning.engines.trajectory_exemplar_store`.

Thin facade so planners can opt in to exemplar consultation without taking a
hard dependency on the store or its data types. The adapter:

- Owns a single process-wide :class:`TrajectoryExemplarStore` instance.
- Accepts seed loads from any producer (typically
  ``retrieval_case_embedder``'s post-eval output, or a test fixture).
- Exposes a minimal ``consult(query_text, k)`` that returns already-ranked
  opaque trajectories; planners never see exemplar internals.

Planners that have not opted in are unaffected — the adapter is additive.
"""

from __future__ import annotations

import threading
from typing import Any, Iterable, Mapping, Sequence

from system_learning.engines.trajectory_exemplar_store import (
    ExemplarHit,
    TrajectoryExemplar,
    TrajectoryExemplarStore,
)


_STORE: TrajectoryExemplarStore | None = None
_STORE_LOCK = threading.Lock()


def default_store(**init_kwargs: Any) -> TrajectoryExemplarStore:
    """Return the process-wide exemplar store, creating it lazily."""

    global _STORE
    with _STORE_LOCK:
        if _STORE is None:
            _STORE = TrajectoryExemplarStore(**init_kwargs)
        return _STORE


def reset_default_store() -> None:
    """Drop the singleton (tests, session boundaries)."""

    global _STORE
    with _STORE_LOCK:
        _STORE = None


def seed_exemplars(exemplars: Iterable[Mapping[str, Any]]) -> int:
    """Seed the store from raw mappings. Returns the number of entries added.

    Each mapping must have ``exemplar_id``, ``query_text``, ``trajectory``, and
    ``score``; all other fields are optional.
    """

    store = default_store()
    coerced: list[TrajectoryExemplar] = []
    for raw in exemplars:
        coerced.append(
            TrajectoryExemplar(
                exemplar_id=str(raw["exemplar_id"]),
                query_text=str(raw["query_text"]),
                trajectory=raw["trajectory"],
                score=float(raw["score"]),
                cost_tokens=int(raw.get("cost_tokens", 0)),
                tags=frozenset(raw.get("tags") or ()),
            )
        )
    return store.bulk_add(coerced)


def consult(
    query_text: str,
    *,
    k: int = 3,
    required_tags: Sequence[str] = (),
) -> list[ExemplarHit]:
    """Planner-facing consult — returns at most ``k`` ranked hits.

    Safe to call even if the store has never been seeded; returns ``[]`` in
    that case.
    """

    return default_store().consult(query_text, k=k, required_tags=required_tags)
