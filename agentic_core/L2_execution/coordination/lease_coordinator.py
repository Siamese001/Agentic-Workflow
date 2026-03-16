"""L2 Execution — Redis-backed lease coordinator and idempotency store.

Two concerns are handled here:

  LeaseCoordinator
      Provides cross-process mutual exclusion for plan execution.
      Uses Redis DB 1 (CacheDB.COORDINATION) with short TTLs.
      Falls back to in-process LRU when Redis is unavailable (single-
      process exclusivity only — cross-process requires a live Redis).

  IdempotencyStore
      Records the exact stdout/exit-code bytes returned by a tool call
      so that retried calls return the same result without re-executing.
      Keyed by ``tool_call_hash`` (SHA-256 of canonical-JSON tool args).

Hard rules for determinism
--------------------------
* In ``replay_mode=True`` ALL reads from both stores return ``None`` /
  ``False`` so the caller re-derives the result from first principles.
  This ensures the replay transcript is self-contained.
* Neither store is a source of truth — L4 / UWG remains the mutation
  authority.  Both stores contain *coordination* records and *derived*
  outputs only.
* ``nonce`` in lease entries must be drawn from the deterministic
  transcript of the current run (not ``secrets.token_hex``), unless the
  nonce is itself stored in the transcript so replay can reconstruct it.
"""

from __future__ import annotations

import logging
from typing import Any

from agentic_core.cache.cache_key_builders import build_lease_key, build_tool_result_key
from agentic_core.cache.redis_cache_client import (
    DeterministicRedisCache,
    get_coordination_cache,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
    _emit_applies_guardrail,  # noqa: E402
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_to_human,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_routes_through,  # noqa: E402
    _emit_signs_execution_trace,
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

emit_replay_key("p0", "lease_coordinator")
emit_determinism_digest("p0", "lease_coordinator")

_emit_dispatches_healing_run("p1", "lease_coordinator", "L2")
_emit_routes_through("p1", "lease_coordinator", "L2")
_emit_escalates_to_human("p1", "lease_coordinator", "L2")
_emit_reads_policy_state("p1", "lease_coordinator", "L2")

_emit_applies_guardrail("p0", "lease_coordinator", "p0_governance")
_emit_snapshots_state("p0", "lease_coordinator", "state_snapshot")

logger = logging.getLogger(__name__)

_DEFAULT_LEASE_TTL: int = 30  # seconds — short for coordination safety
_DEFAULT_IDEMPOTENCY_TTL: int = 300  # 5 minutes


class LeaseCoordinator:
    """Cross-process execution-lease manager (DB 1, short TTLs).

    Usage pattern::

        lc = LeaseCoordinator()
        acquired = lc.acquire("plan-abc123", holder_id="worker-1",
                               nonce="<transcript-nonce>",
                               semantic_clock_tick=42)
        if acquired:
            try:
                ...run plan...
            finally:
                lc.release("plan-abc123", holder_id="worker-1",
                            nonce="<transcript-nonce>")

    Parameters
    ----------
    lease_ttl_seconds:
        How long a lease is valid before automatic expiry.
    cache:
        Override the coordination-cache instance (useful for testing).
    """

    def __init__(
        self,
        lease_ttl_seconds: int = _DEFAULT_LEASE_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = lease_ttl_seconds
        self._cache = cache or get_coordination_cache()

    def acquire(
        self,
        plan_hash: str,
        holder_id: str,
        nonce: str,
        semantic_clock_tick: int,
        *,
        replay_mode: bool = False,
    ) -> bool:
        """Attempt to acquire the lease for *plan_hash*.

        Returns ``True`` if the lease was acquired; ``False`` if another
        holder currently holds it.  Always returns ``False`` in
        ``replay_mode=True`` — callers should treat replay as lease-free
        (no coordination needed for read-only transcript reconstruction).
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "LeaseCoordinator.acquire")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:LeaseCoordinator.acquire".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if replay_mode:
            return False

        key = build_lease_key(plan_hash)
        return self._cache.acquire_lease(
            key,
            holder_id=holder_id,
            nonce=nonce,
            semantic_clock_tick=semantic_clock_tick,
            ttl_seconds=self._ttl,
        )

    def release(
        self,
        plan_hash: str,
        holder_id: str,
        nonce: str,
    ) -> bool:
        """Release the lease for *plan_hash* held by *holder_id* / *nonce*.

        Returns ``True`` if the lease was successfully released; ``False``
        if the caller did not hold the lease or it had already expired.
        """
        key = build_lease_key(plan_hash)
        return self._cache.release_lease(key, holder_id=holder_id, nonce=nonce)

    def is_held(self, plan_hash: str) -> bool:
        """Return ``True`` if any holder currently holds the lease."""
        key = build_lease_key(plan_hash)
        return self._cache.exists(key)

    def holder_info(self, plan_hash: str) -> dict[str, Any] | None:
        """Return the lease payload dict (holder_id, nonce, clock tick) or None."""
        key = build_lease_key(plan_hash)
        return self._cache.get_json(key)


class IdempotencyStore:
    """Records exact tool-call outputs for deduplication (DB 1).

    When a tool call identified by ``tool_call_hash`` has already been
    executed, its raw output bytes are stored here so that a retry returns
    the same bytes without re-executing the tool.

    Rules
    -----
    * Only store outputs for tools that are **strictly input-hashed** (the
      same hash always produces the same output).  Do NOT store outputs for
      tools with side effects unless those side effects are idempotent.
    * In ``replay_mode=True`` all reads return ``None`` — the transcript
      already contains the canonical output.

    Parameters
    ----------
    ttl_seconds:
        TTL for idempotency records.
    cache:
        Override the coordination-cache instance (useful for testing).
    """

    def __init__(
        self,
        ttl_seconds: int = _DEFAULT_IDEMPOTENCY_TTL,
        cache: DeterministicRedisCache | None = None,
    ) -> None:
        self._ttl = ttl_seconds
        self._cache = cache or get_coordination_cache()

    def get(
        self,
        tool_call_hash: str,
        *,
        replay_mode: bool = False,
    ) -> bytes | None:
        """Return stored tool-output bytes or ``None`` on miss/bypass."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "IdempotencyStore.get")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:IdempotencyStore.get".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        key = build_tool_result_key(tool_call_hash)
        return self._cache.get(key, replay_mode=replay_mode)

    def set(
        self,
        tool_call_hash: str,
        output_bytes: bytes,
    ) -> None:
        """Record *output_bytes* as the canonical output for *tool_call_hash*."""
        key = build_tool_result_key(tool_call_hash)
        self._cache.set(key, output_bytes, ttl_seconds=self._ttl)

    def exists(self, tool_call_hash: str) -> bool:
        """Return ``True`` if a recorded result exists for *tool_call_hash*."""
        key = build_tool_result_key(tool_call_hash)
        return self._cache.exists(key)

    def invalidate(self, tool_call_hash: str) -> None:
        """Evict the idempotency record (e.g. after a forced retry)."""
        key = build_tool_result_key(tool_call_hash)
        self._cache.delete(key)


# ---------------------------------------------------------------------------
# Module-level convenience singletons
# ---------------------------------------------------------------------------

_lease_coordinator: LeaseCoordinator | None = None
_idempotency_store: IdempotencyStore | None = None


def get_lease_coordinator() -> LeaseCoordinator:
    """Return the process-global ``LeaseCoordinator`` instance."""
    global _lease_coordinator
    if _lease_coordinator is None:
        _lease_coordinator = LeaseCoordinator()
    return _lease_coordinator


def get_idempotency_store() -> IdempotencyStore:
    """Return the process-global ``IdempotencyStore`` instance."""
    global _idempotency_store
    if _idempotency_store is None:
        _idempotency_store = IdempotencyStore()
    return _idempotency_store
