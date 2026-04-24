"""Durable Redis-backed ``PassKStore`` for cross-host pass^k consistency.

Drop-in replacement for :class:`PassKStore` / :class:`SqlitePassKStore`
usable behind :class:`EvaluationPipeline`. Implements the same public
surface: ``record``, ``check``, ``history``, ``clear``.

Design
------

Each bucket is one Redis LIST keyed by the canonical bucket tuple:

    {prefix}:{trajectory_class}:{rubric_version}:
    {agent_version}:{policy_version}

Each list element is a single JSON-encoded :class:`TrialRecord`. Newest
entries are on the RIGHT (RPUSH); ``pass^k`` reads the last ``k`` with
``LRANGE -k -1``. Bucket length is bounded with ``LTRIM`` every write
to ``max_retained``, matching the in-memory store's semantics.

Why a list and not a sorted-set:

- LIST RPUSH + LTRIM is O(1) amortised for the write path and O(k) for
  the read path. That dominates for the realistic k ≤ 50 used by v4.
- Sorted sets would double storage (score + member) and only buy us
  range-by-score reads we do not need.

Fail-mode (per H8)
------------------

Any Redis RPC failure surfaces as :class:`StoreBackendError`; the
pipeline converts that to a HITL routing with
``CONSISTENCY_HISTORY_UNAVAILABLE`` — never a silent pass.

Connection
----------

Caller supplies an already-configured ``redis.Redis`` client. This
module does NOT handle TLS, retry, sentinel, or cluster details — those
are deployment concerns. Tests use ``fakeredis.FakeRedis`` so the CI
lane does not require a live server.
"""

from __future__ import annotations

import json
from threading import Lock
from typing import Any, Iterator

from agentic_core.L3_orchestration.exit_eval.consistency import (
    BucketKey,
    ConsistencyCheck,
    TrialRecord,
)


class StoreBackendError(RuntimeError):
    """Uniform backend error for pass^k stores.

    Subclass of ``RuntimeError`` so existing handlers in
    ``EvaluationPipeline`` that route ``RuntimeError`` to
    ``CONSISTENCY_HISTORY_UNAVAILABLE`` still catch it (the sqlite store
    raises bare ``RuntimeError`` — this class is the strict form). Do
    NOT swallow; route to HITL per H8.
    """

DEFAULT_KEY_PREFIX = "exit_eval:passk"


def _bucket_key(prefix: str, key: BucketKey) -> str:
    # Colons are meaningful Redis-side; sanitise with a safe replace.
    return ":".join(
        (
            prefix,
            key.trajectory_class.replace(":", "_"),
            key.rubric_version.replace(":", "_"),
            key.agent_version.replace(":", "_"),
            key.policy_version.replace(":", "_"),
        )
    )


def _encode(trial: TrialRecord) -> bytes:
    return json.dumps(
        {
            "run_id": trial.run_id,
            "passed": bool(trial.passed),
            "timestamp": float(trial.timestamp),
        },
        separators=(",", ":"),
    ).encode("utf-8")


def _decode(raw: bytes | str) -> TrialRecord:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    blob = json.loads(raw)
    return TrialRecord(
        run_id=str(blob["run_id"]),
        passed=bool(blob["passed"]),
        timestamp=float(blob["timestamp"]),
    )


class RedisPassKStore:
    """Redis-backed ``PassKStore``.

    Parameters
    ----------
    client:
        A ``redis.Redis`` (or compatible) instance. Must support
        ``rpush``, ``ltrim``, ``lrange``, ``llen``, and ``delete``.
    key_prefix:
        String prefixed to every bucket key. Defaults to
        ``"exit_eval:passk"``. Use one prefix per deployment tenant to
        avoid cross-tenant bucket collisions.

    Thread-safety is handled by Redis itself (single-threaded command
    processing). A local lock is kept only to keep the RPUSH+LTRIM pair
    atomic from this client's vantage when running under the fake
    in-memory Redis used in tests; with a real server, pipelines would
    be preferable.
    """

    def __init__(
        self,
        client: Any,
        *,
        key_prefix: str = DEFAULT_KEY_PREFIX,
    ) -> None:
        if client is None:
            raise ValueError("RedisPassKStore: client is required")
        self._client = client
        self._prefix = str(key_prefix)
        self._lock = Lock()

    # ------------------------------------------------------------- writes

    def record(
        self,
        key: BucketKey,
        trial: TrialRecord,
        *,
        max_retained: int = 100,
    ) -> None:
        if max_retained <= 0:
            raise ValueError("max_retained must be > 0")
        rk = _bucket_key(self._prefix, key)
        payload = _encode(trial)
        try:
            with self._lock:
                # Newest on the right; keep at most max_retained from the
                # right side (LTRIM start=-max stop=-1 trims to last N).
                self._client.rpush(rk, payload)
                self._client.ltrim(rk, -max_retained, -1)
        except Exception as exc:  # guardian: allow-broad -- redis client raises provider-specific errors (redis.ConnectionError, TimeoutError, ResponseError) we reclassify as StoreBackendError
            raise StoreBackendError(
                f"RedisPassKStore.record failed for bucket {rk!r}: {exc}"
            ) from exc

    # -------------------------------------------------------------- reads

    def check(
        self,
        key: BucketKey,
        *,
        k: int,
        theta: float,
    ) -> ConsistencyCheck:
        if k <= 0:
            raise ValueError("k must be > 0")
        if not 0.0 <= theta <= 1.0:
            raise ValueError("theta must be in [0, 1]")
        rk = _bucket_key(self._prefix, key)
        try:
            size = int(self._client.llen(rk))
            if size < k:
                return ConsistencyCheck(
                    passed=False,
                    pass_k=None,
                    k=k,
                    theta=theta,
                    has_history=False,
                    history_size=size,
                    reason="INSUFFICIENT_HISTORY",
                )
            raw_recent = self._client.lrange(rk, -k, -1)
        except Exception as exc:  # guardian: allow-broad -- redis error taxonomy is provider-defined; we uniformly reclassify as StoreBackendError
            raise StoreBackendError(
                f"RedisPassKStore.check failed for bucket {rk!r}: {exc}"
            ) from exc

        try:
            recent = [_decode(raw) for raw in raw_recent]
        except (ValueError, KeyError, TypeError) as exc:
            raise StoreBackendError(
                f"RedisPassKStore.check: corrupt payload in {rk!r}: {exc}"
            ) from exc

        successes = sum(1 for t in recent if t.passed)
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
        rk = _bucket_key(self._prefix, key)
        try:
            raw_all = self._client.lrange(rk, 0, -1)
        except Exception as exc:  # guardian: allow-broad -- redis provider-specific errors reclassified as StoreBackendError
            raise StoreBackendError(
                f"RedisPassKStore.history failed for bucket {rk!r}: {exc}"
            ) from exc
        try:
            return tuple(_decode(raw) for raw in raw_all)
        except (ValueError, KeyError, TypeError) as exc:
            raise StoreBackendError(
                f"RedisPassKStore.history: corrupt payload in {rk!r}: {exc}"
            ) from exc

    def clear(self, key: BucketKey) -> None:
        rk = _bucket_key(self._prefix, key)
        try:
            self._client.delete(rk)
        except Exception as exc:  # guardian: allow-broad -- redis provider-specific errors reclassified as StoreBackendError
            raise StoreBackendError(
                f"RedisPassKStore.clear failed for bucket {rk!r}: {exc}"
            ) from exc

    # ----------------------------------------------------------- admin

    def iter_buckets(self) -> Iterator[BucketKey]:
        """Yield every bucket present under this prefix. Admin-only.

        Uses SCAN for bounded memory. Malformed keys are skipped (the
        prefix disambiguates cleanly; only corruption produces them).
        """
        pattern = f"{self._prefix}:*"
        cursor = 0
        try:
            while True:
                cursor, keys = self._client.scan(cursor=cursor, match=pattern, count=200)
                for raw in keys:
                    if isinstance(raw, bytes):
                        raw = raw.decode("utf-8")
                    parts = raw.split(":", 5)  # prefix: + 4 tuple parts
                    # prefix may itself contain a colon (defaults to
                    # "exit_eval:passk"), so split on that prefix length.
                    if not raw.startswith(f"{self._prefix}:"):
                        continue
                    tail = raw[len(self._prefix) + 1 :]
                    parts = tail.split(":")
                    if len(parts) != 4:
                        continue
                    yield BucketKey(
                        trajectory_class=parts[0],
                        rubric_version=parts[1],
                        agent_version=parts[2],
                        policy_version=parts[3],
                    )
                if cursor == 0:
                    return
        except Exception as exc:  # guardian: allow-broad -- redis provider-specific errors reclassified as StoreBackendError
            raise StoreBackendError(
                f"RedisPassKStore.iter_buckets failed: {exc}"
            ) from exc


__all__ = ["DEFAULT_KEY_PREFIX", "RedisPassKStore", "StoreBackendError"]
