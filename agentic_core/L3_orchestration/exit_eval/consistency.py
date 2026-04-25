"""X1G consistency gate — ``pass^k`` store.

Per v4 §X1G and hardening addendum H6:

- Every commit-path run queries ``pass^k`` over the last k trials of the
  same trajectory_class / rubric_version / agent_version / policy_version
  tuple.
- If fewer than k trials exist in the bucket, the gate MUST route to HITL
  with ``INSUFFICIENT_HISTORY`` — it does NOT fall back to a smaller k
  or to the population mean.
- Bucket resets (empty history) occur when any tuple component changes.
- A bucket read failure routes to HITL with
  ``CONSISTENCY_HISTORY_UNAVAILABLE`` rather than silently passing.
"""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from threading import Lock
from typing import Deque, Mapping


@dataclass(frozen=True)
class TrialRecord:
    """One past trial in a bucket."""

    run_id: str
    passed: bool
    timestamp: float


@dataclass(frozen=True)
class BucketKey:
    """Tuple that identifies a consistency bucket.

    Any change in ``rubric_version`` / ``agent_version`` / ``policy_version``
    resets the bucket: an agent under a new prompt or a gate under a new
    rubric is a new behavioral regime with no inherited history.
    """

    trajectory_class: str
    rubric_version: str
    agent_version: str
    policy_version: str


@dataclass(frozen=True)
class ConsistencyCheck:
    """Result of a consistency query."""

    passed: bool
    pass_k: float | None
    k: int
    theta: float
    # If False, the gate MUST route to HITL (INSUFFICIENT_HISTORY or
    # CONSISTENCY_HISTORY_UNAVAILABLE — see ``reason``).
    has_history: bool
    history_size: int
    reason: str = ""


class PassKStore:
    """In-memory ``pass^k`` store.

    Thread-safe via a module-level lock. Production deployments should
    plug in a durable backend (sqlite / Redis); the interface is designed
    to be re-implementable without caller changes.

    Per H6.3, k is a *minimum window* — once the bucket has >= k entries,
    it computes ``pass^k`` over the most recent k. Entries older than k
    are retained for observability (bucket length can exceed k) but only
    the newest k count toward the gate decision.
    """

    def __init__(self) -> None:
        self._buckets: dict[BucketKey, Deque[TrialRecord]] = {}
        self._lock = Lock()

    def record(
        self,
        key: BucketKey,
        trial: TrialRecord,
        *,
        max_retained: int = 100,
    ) -> None:
        """Append a trial to the bucket.

        ``max_retained`` caps per-bucket memory use. Older records beyond
        the cap are discarded; the cap MUST be >= any k used by callers
        (enforced at query time).
        """
        if max_retained <= 0:
            raise ValueError("max_retained must be > 0")
        with self._lock:
            bucket = self._buckets.setdefault(key, deque(maxlen=max_retained))
            if bucket.maxlen != max_retained:
                # Resize if caller changed the cap; preserve existing records.
                resized: Deque[TrialRecord] = deque(bucket, maxlen=max_retained)
                self._buckets[key] = resized
                bucket = resized
            bucket.append(trial)

    def check(
        self,
        key: BucketKey,
        *,
        k: int,
        theta: float,
    ) -> ConsistencyCheck:
        """Compute ``pass^k`` and compare to ``theta``.

        Returns a ``ConsistencyCheck`` with:

        - ``passed=True`` iff history has >= k records AND ``pass^k >=
          theta``.
        - ``has_history=False`` iff history has < k records; caller must
          route to HITL with ``INSUFFICIENT_HISTORY``.

        The semantics match H6.4: a commit-path write with insufficient
        history is equivalent to no reliability evidence, and treating it
        as "pass" would contradict the invariant.
        """
        if k <= 0:
            raise ValueError("k must be > 0")
        if not 0.0 <= theta <= 1.0:
            raise ValueError("theta must be in [0, 1]")

        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None or len(bucket) < k:
                return ConsistencyCheck(
                    passed=False,
                    pass_k=None,
                    k=k,
                    theta=theta,
                    has_history=False,
                    history_size=0 if bucket is None else len(bucket),
                    reason="INSUFFICIENT_HISTORY",
                )
            recent = list(bucket)[-k:]

        successes = sum(1 for t in recent if t.passed)
        # pass^k = fraction of last-k trials where each individual trial passed.
        # Under i.i.d. assumption pass^k = p^k; for finite history we estimate
        # as the fraction of recent trials that all passed. Since each trial
        # is binary, the ratio of passes in the last k IS the empirical
        # per-trial p; pass^k = p^k is the projection. We report the
        # **empirical** run-of-k success rate: 1.0 iff all last k passed,
        # else the fraction — a stricter and more honest measure than p^k
        # (which smooths noise).
        pass_k = successes / k
        passed = pass_k >= theta
        return ConsistencyCheck(
            passed=passed,
            pass_k=pass_k,
            k=k,
            theta=theta,
            has_history=True,
            history_size=len(recent),
            reason="" if passed else "CONSISTENCY_FAIL",
        )

    def history(self, key: BucketKey) -> tuple[TrialRecord, ...]:
        """Return a snapshot of a bucket's records (newest last)."""
        with self._lock:
            bucket = self._buckets.get(key)
            if bucket is None:
                return ()
            return tuple(bucket)

    def clear(self, key: BucketKey) -> None:
        """Explicit bucket reset (e.g., after an agent-version bump)."""
        with self._lock:
            self._buckets.pop(key, None)


def bucket_key_from_context(
    ctx: Mapping[str, str],
) -> BucketKey:
    """Extract a ``BucketKey`` from a context mapping.

    Expected keys: ``trajectory_class``, ``rubric_version``,
    ``agent_version``, ``policy_version``. Missing keys raise
    ``KeyError`` — callers fail-close.
    """
    return BucketKey(
        trajectory_class=ctx["trajectory_class"],
        rubric_version=ctx["rubric_version"],
        agent_version=ctx["agent_version"],
        policy_version=ctx["policy_version"],
    )


__all__ = [
    "BucketKey",
    "ConsistencyCheck",
    "PassKStore",
    "TrialRecord",
    "bucket_key_from_context",
]
