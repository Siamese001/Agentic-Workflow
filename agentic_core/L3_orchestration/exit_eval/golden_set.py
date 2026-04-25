"""Golden-set candidate surface (v6 §S2D / §S4A — golden-set comparisons).

This module reads the X1G consistency store and surfaces buckets that have
demonstrated stable, high pass-rate behavior over a sufficiently long
window — the candidates a system-learning operator (or §S4A gauntlet)
might promote to the golden set for future-run regression checks.

It is a **read-only** observer per v6 §1 OBSERVER LAW:
- It does not mutate the PassKStore.
- It does not write L4.
- It does not publish BUS U.
- It does not change live thresholds.

The selection rule is deliberately simple and overridable:

    promotable iff history_size >= min_history
              AND last_n_pass_rate(n=min_history) >= pass_rate_threshold
              AND no failed trial within the last `recency_window` records

Callers may compose this with additional filters (e.g. exclude buckets
whose ``policy_version`` is below an org-wide floor).

The contract returns ``CandidateRecord`` rather than raw ``BucketKey`` so
the gauntlet sees pass-rate, sample size, and the exact tuple — every
inputs the auditor needs to defend the promotion choice in §S4D ledger
proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    PassKStore,
)


@dataclass(frozen=True)
class CandidateRecord:
    """One golden-set promotion candidate.

    Attributes:
        key: Bucket identity (trajectory_class + version tuple).
        history_size: Total trials retained for the bucket.
        recent_pass_rate: Pass rate computed over the most-recent
            ``min_history`` trials (the same window used by the X1G
            check). 1.0 means every recent trial passed.
        had_recent_failure: True iff any of the most-recent
            ``recency_window`` trials failed; this short-circuits
            promotion regardless of pass rate.
    """

    key: BucketKey
    history_size: int
    recent_pass_rate: float
    had_recent_failure: bool


@dataclass(frozen=True)
class GoldenSetPolicy:
    """Selection thresholds applied to PassKStore buckets.

    All thresholds are inclusive (``>=`` / ``<=``) unless noted. The
    defaults are intentionally conservative: a candidate must clear a
    20-trial history with 100% pass rate AND zero failures in the last 5
    trials. Operators may relax these for capability tracks or tighten
    them for regression tracks.
    """

    min_history: int = 20
    pass_rate_threshold: float = 1.0
    recency_window: int = 5

    def __post_init__(self) -> None:
        if self.min_history <= 0:
            raise ValueError("min_history must be > 0")
        if not 0.0 <= self.pass_rate_threshold <= 1.0:
            raise ValueError("pass_rate_threshold must be in [0, 1]")
        if self.recency_window <= 0:
            raise ValueError("recency_window must be > 0")
        if self.recency_window > self.min_history:
            raise ValueError(
                "recency_window cannot exceed min_history "
                "(window must lie within the evaluated history)",
            )


def _evaluate_bucket(
    store: PassKStore,
    key: BucketKey,
    policy: GoldenSetPolicy,
) -> CandidateRecord | None:
    """Return a CandidateRecord iff ``key`` meets ``policy``; else None."""
    history = store.history(key)  # newest last
    if len(history) < policy.min_history:
        return None
    recent = history[-policy.min_history :]
    passes = sum(1 for t in recent if t.passed)
    pass_rate = passes / policy.min_history
    if pass_rate < policy.pass_rate_threshold:
        return None
    tail = history[-policy.recency_window :]
    had_recent_failure = any(not t.passed for t in tail)
    if had_recent_failure:
        return None
    return CandidateRecord(
        key=key,
        history_size=len(history),
        recent_pass_rate=pass_rate,
        had_recent_failure=False,
    )


def select_candidates(
    store: PassKStore,
    keys: Iterable[BucketKey],
    *,
    policy: GoldenSetPolicy | None = None,
) -> tuple[CandidateRecord, ...]:
    """Surface golden-set candidates from ``store`` for ``keys``.

    Read-only: this function does not mutate the store. The returned
    tuple is sorted by ``(key.trajectory_class, key.rubric_version)`` for
    deterministic downstream consumption (BUS U snapshots are content-
    addressed; identical input must produce identical output).

    Args:
        store: A ``PassKStore`` instance. Live or replayed-from-snapshot;
            this surface is agnostic.
        keys: Bucket identities to evaluate. Callers must supply the
            list explicitly because PassKStore does not enumerate (a
            production backend may shard buckets across stores).
        policy: Selection thresholds. Defaults to ``GoldenSetPolicy()``.

    Returns:
        Tuple of ``CandidateRecord`` for every bucket that passes the
        policy, sorted deterministically. Empty tuple if none qualify.
    """
    pol = policy or GoldenSetPolicy()
    seen: set[BucketKey] = set()
    results: list[CandidateRecord] = []
    for key in keys:
        if key in seen:
            continue
        seen.add(key)
        record = _evaluate_bucket(store, key, pol)
        if record is not None:
            results.append(record)
    results.sort(
        key=lambda r: (
            r.key.trajectory_class,
            r.key.rubric_version,
            r.key.agent_version,
            r.key.policy_version,
        )
    )
    return tuple(results)


__all__ = [
    "CandidateRecord",
    "GoldenSetPolicy",
    "select_candidates",
]
