"""Backfill seeder for :mod:`system_learning.engines.trajectory_exemplar_store`.

Turns post-eval retrieval case records into ``TrajectoryExemplar`` entries so
the exemplar consult adapter has a non-empty corpus on first use. Designed to
run either as a one-time backfill at deployment or as a nightly job keyed on a
timestamp window.

Design:

- **Pure transformation**: takes an iterable of eval case records (any mapping
  shape with the required fields) and emits typed
  ``TrajectoryExemplar`` objects. No embedding, no DB — that is
  ``retrieval_case_embedder``'s job.
- **Scoring floor**: records whose composite score is below the store's
  ``min_score`` are silently dropped (the store would reject them too).
- **Cost-tokens inference**: if a record lacks an explicit ``cost_tokens``,
  falls back to ``total_tokens`` or ``0``.
- **Idempotency**: relies on the exemplar store's own ``exemplar_id``
  dedup — safe to re-run.

Not in scope (yet): direct wiring into L0/L1 planners (planners opt in via
:mod:`system_learning.adapters.exemplar_consult_adapter.consult`).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from .exemplar_consult_adapter import default_store
from agentic_core.L6_system_learning.engines.trajectory_exemplar_store import (
    TrajectoryExemplar,
    TrajectoryExemplarStore,
)

_REQUIRED_KEYS = ("exemplar_id", "query_text", "trajectory", "score")


@dataclass(frozen=True)
class SeedResult:
    """Return value of :func:`seed_from_cases`.

    - ``considered``: total input records evaluated
    - ``malformed``: records missing required fields
    - ``below_floor``: records whose score was below the store's min_score
    - ``added``: records successfully added to the store
    - ``duplicates``: records rejected due to duplicate exemplar_id
    """

    considered: int
    malformed: int
    below_floor: int
    added: int
    duplicates: int


def _coerce_record(raw: Mapping[str, Any]) -> TrajectoryExemplar | None:
    """Convert a raw case record to a :class:`TrajectoryExemplar`.

    Returns ``None`` when required keys are missing.
    """

    for key in _REQUIRED_KEYS:
        if key not in raw:
            return None

    cost_tokens = int(raw.get("cost_tokens") or raw.get("total_tokens") or 0)
    tags_raw = raw.get("tags") or ()
    if isinstance(tags_raw, str):
        tags_iterable = [tags_raw]
    else:
        tags_iterable = list(tags_raw)

    try:
        score = float(raw["score"])
    except (
        TypeError,
        ValueError,
    ):  # guardian: allow-return-none-swallow -- exemplar-seed loader skips malformed rows (non-numeric or missing 'score') by returning None; the caller iterates and filters None to keep the seeder resilient against partially-corrupt JSONL inputs
        return None

    return TrajectoryExemplar(
        exemplar_id=str(raw["exemplar_id"]),
        query_text=str(raw["query_text"]),
        trajectory=raw["trajectory"],
        score=score,
        cost_tokens=cost_tokens,
        tags=frozenset(str(t) for t in tags_iterable),
    )


def seed_from_cases(
    cases: Iterable[Mapping[str, Any]],
    *,
    store: TrajectoryExemplarStore | None = None,
) -> SeedResult:
    """Seed ``store`` (default: the process-wide adapter store) from raw cases."""

    target = store if store is not None else default_store()

    considered = 0
    malformed = 0
    below_floor = 0
    added = 0
    duplicates = 0

    for raw in cases:
        considered += 1
        exemplar = _coerce_record(raw)
        if exemplar is None:
            malformed += 1
            continue
        if exemplar.score < target._min_score:  # noqa: SLF001 — tight coupling by design
            below_floor += 1
            continue
        ok = target.add(exemplar)
        if ok:
            added += 1
        else:
            duplicates += 1

    return SeedResult(
        considered=considered,
        malformed=malformed,
        below_floor=below_floor,
        added=added,
        duplicates=duplicates,
    )


__all__ = ["SeedResult", "seed_from_cases"]
