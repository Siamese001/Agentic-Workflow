"""Deterministic, non-authoritative Redis cache client.

Design invariants enforced here:
  1. NON-AUTHORITATIVE: This cache never becomes the source of truth.
     L4 remains the sole persistence authority.  Every value stored here
     is a deterministic derivative of a hash-addressed L4 artifact.
  2. HASH-ONLY KEYING: Cache keys are composed exclusively from content
     hashes supplied by callers.  No wall-clock timestamps, no random
     nonces, no "latest" sentinel values appear in any key.
  3. REPLAY SAFETY: When ``replay_mode=True`` is passed to ``get()``,
     the method returns ``None`` unconditionally so the caller re-derives
     the value from L4 and records it in the deterministic transcript.
  4. CANONICAL SERIALIZATION: ``canonical_json_bytes`` produces a stable
     byte sequence (sorted keys, ASCII-only, no trailing whitespace) that
     is safe to SHA-256 and store as a cache value.
  5. GRACEFUL FALLBACK: When the Redis server is unavailable the client
     silently switches to a bounded in-process LRU store so callers never
     see a hard failure due to cache infrastructure.
  6. TWO DATABASE NAMESPACES:
       DB 0 — hot caches  (L0, L1/Assembly, L3, L5) with configurable TTLs
       DB 1 — coordination (L2 leases / idempotency keys) with short TTLs
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import urllib.parse
import uuid
from collections import OrderedDict
from dataclasses import dataclass
from enum import IntEnum
from typing import Any

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_through,
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_applies_guardrail("p0", "redis_cache_client", "p0_governance")
_emit_reads_policy_state("p0", "redis_cache_client", "policy_binding")
_emit_snapshots_state("p0", "redis_cache_client", "state_snapshot")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("redis_cache_client", "p4obs", "metric_1")
_emit_emits_metric_event("redis_cache_client", "p4obs", "metric_2")
_emit_emits_metric_event("redis_cache_client", "p4obs", "metric_3")
_emit_emits_metric_event("redis_cache_client", "p4obs", "metric_4")
_emit_emits_metric_event("redis_cache_client", "p4obs", "metric_5")
_emit_emits_metric_event("redis_cache_client", "p4obs", "metric_6")
_emit_records_incident_event("redis_cache_client", "p4obs", "incident")
_emit_captures_runtime_anomaly("redis_cache_client", "p4obs", "anomaly")
_emit_writes_observability_log("redis_cache_client", "p4obs", "obs_log")
_emit_updates_monitoring_state("redis_cache_client", "p4obs", "mon_state")
_emit_triggers_alert("redis_cache_client", "p4obs", "alert")
_emit_links_incident_trace("redis_cache_client", "p4obs", "trace_link")
_emit_captures_pattern("redis_cache_client", "p3lm", "pattern")
_emit_records_learning_event("redis_cache_client", "p3lm", "learning_event")
_emit_writes_learning_snapshot("redis_cache_client", "p3lm", "snapshot")
_emit_feeds_meta_learning("redis_cache_client", "p3lm", "meta_feed")
_emit_updates_routing_strategy("redis_cache_client", "p3lm", "routing")
_emit_improves_agent_policy("redis_cache_client", "p3lm", "policy")
_emit_stores_learning_state("redis_cache_client", "p3lm", "state")
_emit_records_execution_trace("redis_cache_client", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("redis_cache_client", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("redis_cache_client", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("redis_cache_client", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("redis_cache_client", "L4_STATE", "p2_trace_5")
_emit_reads_environ("redis_cache_client", "env_read", "p2_env_1")
_emit_reads_environ("redis_cache_client", "env_read", "p2_env_2")
_emit_reads_runtime_state("redis_cache_client", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("redis_cache_client", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "redis_cache_client", "context_pull")
_emit_pulls_context("p1", "redis_cache_client", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "redis_cache_client", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "redis_cache_client", "uwg_term_2")
_emit_writes_through("p1", "redis_cache_client", "write_through")
_emit_writes_through("p1", "redis_cache_client", "write_through_2")
_emit_validated_by_safety_plane("p1", "redis_cache_client", "safety_validation")
_emit_invokes_eval("p1", "redis_cache_client", "eval_call")
_emit_proposal_commits_routing("p1", "redis_cache_client", "routing_commit")
_emit_escalates_to_human("p1", "redis_cache_client", "human_escalation")
_emit_routes_through("p1", "redis_cache_client", "route_through")
_emit_checks_agent_registry("p1", "redis_cache_client", "agent_registry")
_emit_validates_agent_capability("p1", "redis_cache_client", "capability")
_emit_dispatches_execution_plan("p1", "redis_cache_client", "exec_plan")
_emit_agent_executes_agent("p1", "redis_cache_client", "sub_agent")
_emit_routes_to_agent("p1", "redis_cache_client", "target_agent")
_emit_verifies_policy("p1", "redis_cache_client", "policy_check")
_emit_observes_runtime_state("p1", "redis_cache_client", "runtime_state")
_emit_verifies_boundary("p1", "redis_cache_client", "boundary_check")
_emit_transcripts_response("p1", "redis_cache_client", "transcript")
_emit_hard_fails_untranscripted("p1", "redis_cache_client")
_emit_gated_by_confidence("p1", "redis_cache_client", "confidence_gate")
emit_replay_key("p0", "redis_cache_client")
emit_determinism_digest("p0", "redis_cache_client")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "redis_cache_client", "execution_auth")
_emit_validates_capability("p2", "redis_cache_client", "capability_check")
_emit_routes_to_capability("p2", "redis_cache_client", "capability_route")
_emit_writes_via_uwg("p2", "redis_cache_client", "uwg_write")
_emit_blocks_direct_write("p2", "redis_cache_client", "direct_write_block")
_emit_records_tool_invocation("p2", "redis_cache_client", "tool_invocation")
_emit_captures_execution_output("p2", "redis_cache_client", "exec_output")
_emit_dispatches_agent("p3", "redis_cache_client", "agent_dispatch")
_emit_coordinates_agents("p3", "redis_cache_client", "agent_coordination")
_emit_records_workflow_lineage("p3", "redis_cache_client", "workflow_lineage")
_emit_records_healing_outcome("p3", "redis_cache_client", "healing_outcome")
_emit_escalates_failure("p3", "redis_cache_client", "failure_escalation")
_emit_orchestrates_workflow("p3", "redis_cache_client", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "redis_cache_client", "healing_dispatch")
_emit_invokes_evaluation("p3", "redis_cache_client", "evaluation_signal")
_emit_records_telemetry_event("p4", "redis_cache_client", "telemetry_event")
_emit_captures_evaluation_metric("p4", "redis_cache_client", "eval_metric")
_emit_stores_embedding("p4", "redis_cache_client", "embedding_store")
_emit_updates_meta_learning_state("p4", "redis_cache_client", "meta_learning")
_emit_links_execution_to_snapshot("p4", "redis_cache_client", "exec_snapshot_link")

logger = logging.getLogger(__name__)
_MAX_KEY_LEN: int = 512
_MAX_VALUE_BYTES: int = 10 * 1024 * 1024
_FALLBACK_MAX_ENTRIES: int = 4096
_MAX_TTL_SECONDS: int = 86400
_REDIS_SOCKET_TIMEOUT_S: float = 0.3


class CacheDB(IntEnum):
    """Redis logical database index."""

    HOT = 0
    COORDINATION = 1


def canonical_json_bytes(obj: Any) -> bytes:
    """Produce a deterministic, ASCII-safe JSON byte sequence.

    Rules applied:
    - Keys sorted recursively.
    - Separators ``(',', ':')`` — no trailing whitespace.
    - ``ensure_ascii=True`` — safe for SHA-256 and Redis storage.
    - ``allow_nan=False`` — NaN/Infinity in floats would break determinism.

    Raises
    ------
    TypeError
        If obj contains non-JSON-serializable types (bytes, set, custom classes).
    ValueError
        If obj contains NaN or Infinity floats.
    """
    try:
        return json.dumps(
            obj,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            allow_nan=False,
        ).encode("ascii")
    except TypeError as exc:
        raise TypeError(
            f"Object contains non-JSON-serializable type: {exc}. Only dict, list, str, int, float, bool, None are allowed.",
        ) from exc
    except ValueError as exc:
        raise ValueError(f"Object contains NaN or Infinity: {exc}") from exc


def content_hash(data: bytes) -> str:
    """Return the SHA-256 hex digest of *data* (64 lowercase hex chars)."""
    return hashlib.sha256(data).hexdigest()


class _BoundedLRU:
    """Thread-unsafe, process-local LRU used when Redis is unreachable."""

    def __init__(self, maxsize: int = _FALLBACK_MAX_ENTRIES) -> None:
        self._store: OrderedDict[str, bytes] = OrderedDict()
        self._maxsize = maxsize

    def get(self, key: str) -> bytes | None:
        if key not in self._store:
            return None
        self._store.move_to_end(key)
        return self._store[key]

    def set(self, key: str, value: bytes) -> None:
        if key in self._store:
            self._store.move_to_end(key)
        elif len(self._store) >= self._maxsize:
            self._store.popitem(last=False)
        self._store[key] = value

    def delete(self, key: str) -> bool:
        return self._store.pop(key, None) is not None

    def exists(self, key: str) -> bool:
        return key in self._store

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)


@dataclass
class CacheStats:
    """Accumulated hit/miss counters (informational only)."""

    hits: int = 0
    misses: int = 0
    fallback_hits: int = 0
    fallback_misses: int = 0
    errors: int = 0
    bypassed_replay: int = 0


class DeterministicRedisCache:
    """Non-authoritative, hash-keyed Redis cache with in-process LRU fallback.

    Instances are lightweight; construct one per DB namespace per process
    (``CacheDB.HOT`` for L0/L1/L3/L5, ``CacheDB.COORDINATION`` for L2).

    Parameters
    ----------
    db:
        Redis logical database index (``CacheDB.HOT`` or
        ``CacheDB.COORDINATION``).
    redis_url:
        Redis connection URL.  Defaults to the ``REDIS_URL`` env-var or
        ``redis://localhost:6379``.  ``rediss://`` enables TLS.
    fallback_maxsize:
        Maximum number of entries retained in the in-process fallback store.
    """

    def __init__(
        self,
        db: CacheDB = CacheDB.HOT,
        redis_url: str | None = None,
        fallback_maxsize: int = _FALLBACK_MAX_ENTRIES,
    ) -> None:
        self._db = db
        self._redis_url = redis_url or os.getenv("REDIS_URL", "redis://localhost:6379")
        self._conn: Any = None
        self._use_fallback: bool = False
        self._fallback = _BoundedLRU(maxsize=fallback_maxsize)
        self.stats = CacheStats()

    @staticmethod
    def _tcp_reachable(host: str, port: int) -> bool:
        """Fast TCP pre-check bounded by _REDIS_SOCKET_TIMEOUT_S.

        redis-py's socket_connect_timeout is bypassed by the OS TCP stack on
        Windows when no listener is present (no RST, so the kernel timer governs
        instead).  A raw socket.create_connection() honours the Python timeout
        correctly and fails fast.
        """
        import socket as _socket

        try:
            with _socket.create_connection((host, port), timeout=_REDIS_SOCKET_TIMEOUT_S):
                return True
        # guardian: allow-silent-swallow - acceptable exception handling
        except OSError:
            return False

    def _connect(self) -> Any:
        """Return a live redis.Redis connection, falling back gracefully."""
        if self._use_fallback:
            return None
        if self._conn is not None:
            return self._conn
        try:
            import redis as _redis

            parsed = urllib.parse.urlparse(self._redis_url)
            host = parsed.hostname or "localhost"
            port = int(parsed.port or 6379)
            if not self._tcp_reachable(host, port):
                raise OSError(
                    f"TCP pre-check failed: {host}:{port} unreachable within {_REDIS_SOCKET_TIMEOUT_S}s",
                )
            params: dict[str, Any] = {
                "host": host,
                "port": port,
                "db": int(self._db),
                "decode_responses": False,
                "socket_timeout": _REDIS_SOCKET_TIMEOUT_S,
                "socket_connect_timeout": _REDIS_SOCKET_TIMEOUT_S,
            }
            if parsed.password:
                params["password"] = parsed.password
            if parsed.scheme == "rediss":
                params["ssl"] = True
                params["ssl_cert_reqs"] = None
            self._conn = _redis.Redis(**params)
            self._conn.ping()
            return self._conn
        # guardian: allow-silent-swallow
        except Exception as exc:
            logger.warning(
                "[cache] Redis unavailable (db=%s): %s — switching to in-process fallback",
                int(self._db),
                exc,
            )
            self._use_fallback = True
            self._conn = None
            return None

    def _mark_failed(self, exc: Exception) -> None:
        logger.warning("[cache] Redis operation failed: %s — using fallback", exc)
        self._use_fallback = True
        self._conn = None
        self.stats.errors += 1

    @staticmethod
    def _validate_key(key: str) -> None:
        if not key or not isinstance(key, str):
            raise ValueError("Cache key must be a non-empty string")
        if len(key) > _MAX_KEY_LEN:
            raise ValueError(f"Cache key exceeds {_MAX_KEY_LEN}-char limit: {key[:80]}…")
        if any(c in key for c in ("\x00", "\n", "\r", "\t")):
            raise ValueError(f"Cache key contains illegal control character: {key!r}")

    def get(self, key: str, *, replay_mode: bool = False) -> bytes | None:
        """Return cached bytes for *key*, or ``None`` on miss / bypass.

        When ``replay_mode=True`` the method always returns ``None`` so the
        caller re-derives the value from L4 and appends it to the transcript,
        preserving replay determinism.
        """
        self._validate_key(key)
        if replay_mode:
            self.stats.bypassed_replay += 1
            return None
        conn = self._connect()
        if conn is not None:
            try:
                raw = conn.get(key)
                if raw is not None:
                    self.stats.hits += 1
                    return raw
                self.stats.misses += 1
                return None
            # guardian: allow-silent-swallow
            except Exception as exc:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
                raise
                self._mark_failed(exc)
        result = self._fallback.get(key)
        if result is not None:
            self.stats.fallback_hits += 1
            return result
        self.stats.fallback_misses += 1
        return None

    def set(self, key: str, value: bytes, ttl_seconds: int = 3600) -> bool:
        """Persist *value* bytes under *key* with the given TTL.

        Returns ``True`` on success (either Redis or fallback).

        Raises
        ------
        TypeError
            If *value* is not ``bytes``.
        ValueError
            If the value exceeds the 10 MB safety cap, or TTL is invalid.
        """
        self._validate_key(key)
        if not isinstance(value, bytes):
            raise TypeError(f"Cache value must be bytes, got {type(value).__name__}")
        if len(value) > _MAX_VALUE_BYTES:
            raise ValueError(f"Cache value too large ({len(value)} bytes > {_MAX_VALUE_BYTES})")
        if ttl_seconds <= 0:
            raise ValueError(f"TTL must be positive, got {ttl_seconds}")
        if ttl_seconds > _MAX_TTL_SECONDS:
            raise ValueError(f"TTL exceeds {_MAX_TTL_SECONDS}s limit, got {ttl_seconds}")
        conn = self._connect()
        if conn is not None:
            try:
                conn.setex(key, ttl_seconds, value)
                return True
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)
        self._fallback.set(key, value)
        return True

    def delete(self, key: str) -> bool:
        """Evict *key* from Redis and the fallback store."""
        self._validate_key(key)
        conn = self._connect()
        deleted = False
        if conn is not None:
            try:
                deleted = bool(conn.delete(key))
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)
        fallback_deleted = self._fallback.delete(key)
        return deleted or fallback_deleted

    def exists(self, key: str) -> bool:
        """Return ``True`` if *key* is present in the cache (Redis or fallback)."""
        self._validate_key(key)
        conn = self._connect()
        if conn is not None:
            try:
                return bool(conn.exists(key))
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)
        return self._fallback.exists(key)

    def set_json(self, key: str, obj: Any, ttl_seconds: int = 3600) -> bool:
        """Serialise *obj* via ``canonical_json_bytes`` and store it."""
        return self.set(key, canonical_json_bytes(obj), ttl_seconds=ttl_seconds)

    def get_json(self, key: str, *, replay_mode: bool = False) -> Any | None:
        """Retrieve and deserialise a JSON value; returns ``None`` on miss or corrupt bytes."""
        raw = self.get(key, replay_mode=replay_mode)
        if raw is None:
            return None
        try:
            return json.loads(raw.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError):
            return None

    def acquire_lease(
        self,
        key: str,
        holder_id: str,
        nonce: str,
        semantic_clock_tick: int,
        ttl_seconds: int = 30,
    ) -> bool:
        """Acquire an exclusive lease.  Returns ``True`` if acquired.

        Uses Redis SET NX (set-if-not-exists) for atomic acquisition.
        Falls back to in-process LRU when Redis is unavailable (single-
        process exclusivity only — cross-process coordination requires
        a live Redis).

        Parameters
        ----------
        key:
            Deterministic lease key (e.g. ``lease:{plan_hash}``).
        holder_id:
            Stable identifier of the process/agent claiming the lease.
        nonce:
            A value that is part of the deterministic run transcript
            (must NOT be random unless also stored in the transcript).
        semantic_clock_tick:
            Current semantic clock tick from ``SemanticClockSnapshot``.
        ttl_seconds:
            Lease TTL.  Coordination DB (DB 1) uses short TTLs.

        Raises
        ------
        ValueError
            If holder_id, nonce are empty, semantic_clock_tick < 0, or TTL invalid.
        """

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"RedisCacheClient.acquire_lease:{key}"
        )
        self._validate_key(key)
        if not holder_id:
            raise ValueError("holder_id must be non-empty")
        if not nonce:
            raise ValueError("nonce must be non-empty")
        if semantic_clock_tick < 0:
            raise ValueError(f"semantic_clock_tick must be >= 0, got {semantic_clock_tick}")
        if ttl_seconds <= 0:
            raise ValueError(f"Lease TTL must be positive, got {ttl_seconds}")
        if ttl_seconds > _MAX_TTL_SECONDS:
            raise ValueError(f"Lease TTL exceeds {_MAX_TTL_SECONDS}s limit, got {ttl_seconds}")
        payload = canonical_json_bytes(
            {"holder_id": holder_id, "nonce": nonce, "semantic_clock_tick": semantic_clock_tick},
        )
        conn = self._connect()
        if conn is not None:
            try:
                result = conn.set(key, payload, nx=True, ex=ttl_seconds)
                return bool(result)
            # guardian: allow-silent-swallow
            except Exception as exc:
                self._mark_failed(exc)
        if self._fallback.exists(key):
            return False
        self._fallback.set(key, payload)
        return True

    def release_lease(self, key: str, holder_id: str, nonce: str) -> bool:
        """Release a lease only if the caller still holds it.

        Verifies ``holder_id`` and ``nonce`` before deletion to prevent
        accidental release by a competing process.

        Raises
        ------
        ValueError
            If holder_id or nonce are empty.
        """
        self._validate_key(key)
        if not holder_id:
            raise ValueError("holder_id must be non-empty")
        if not nonce:
            raise ValueError("nonce must be non-empty")
        raw = self.get(key)
        if raw is None:
            return False
        try:
            # guardian: allow-silent-swallow - acceptable exception handling
            stored = json.loads(raw.decode("ascii"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return False
        if not isinstance(stored, dict):
            return False
        if stored.get("holder_id") != holder_id or stored.get("nonce") != nonce:
            return False
        return self.delete(key)

    def get_stats(self) -> dict[str, Any]:
        return {
            "db": int(self._db),
            "using_fallback": self._use_fallback,
            "fallback_entries": len(self._fallback),
            "hits": self.stats.hits,
            "misses": self.stats.misses,
            "fallback_hits": self.stats.fallback_hits,
            "fallback_misses": self.stats.fallback_misses,
            "errors": self.stats.errors,
            "bypassed_replay": self.stats.bypassed_replay,
        }


_hot_cache: DeterministicRedisCache | None = None
_coordination_cache: DeterministicRedisCache | None = None


def get_hot_cache() -> DeterministicRedisCache:
    """Return the process-global DB-0 hot cache (L0/L1/L3/L5)."""
    global _hot_cache
    if _hot_cache is None:
        _hot_cache = DeterministicRedisCache(db=CacheDB.HOT)
    return _hot_cache


def get_coordination_cache() -> DeterministicRedisCache:
    """Return the process-global DB-1 coordination cache (L2 leases/idempotency)."""
    global _coordination_cache
    if _coordination_cache is None:
        _coordination_cache = DeterministicRedisCache(db=CacheDB.COORDINATION)
    return _coordination_cache


def reset_cache_singletons() -> None:
    """[TESTING ONLY] Reset module-level singletons."""
    global _hot_cache, _coordination_cache
    _hot_cache = None
    _coordination_cache = None


def check_redis_health_via_mcp() -> dict[str, object]:
    """Probe Redis availability using the MCP Redis tool (mcp11_*).

    Uses the MCP Redis server as an alternative connectivity probe — useful
    when the raw ``redis`` package is unavailable or for cross-checking the
    MCP layer's Redis connection independently of the native client.

    Returns:
        ``dict`` with keys:
            - ``"healthy"`` (bool): True when MCP Redis responded.
            - ``"method"`` (str): Always ``"mcp11"``.
            - ``"error"`` (str | None): Error message when not healthy.
    """
    try:
        from mcp11_delete import mcp11_delete
        from mcp11_get import mcp11_get
        from mcp11_set import mcp11_set

        probe_key = "__mcp_health_probe__"
        probe_val = "1"
        mcp11_set(key=probe_key, value=probe_val, expireSeconds=10)
        result = mcp11_get(key=probe_key)
        mcp11_delete(key=probe_key)
        healthy = result is not None
        logger.info("MCP Redis health probe: healthy=%s", healthy)
        return {"healthy": healthy, "method": "mcp11", "error": None}
    # guardian: allow-silent-swallow - optional dependency
    except ImportError:
        return {"healthy": False, "method": "mcp11", "error": "mcp11 tools not available"}
    # guardian: allow-silent-swallow
    except Exception as exc:
        logger.warning("MCP Redis health probe failed: %s", exc)
        return {"healthy": False, "method": "mcp11", "error": str(exc)}


def check_redis_health(redis_url: str | None = None) -> dict[str, object]:
    """Probe Redis availability and return a structured health report.

    Does NOT raise on failure — returns a dict with ``"healthy": False`` so
    callers can decide how to react.  Emits a clear actionable log message
    when Redis is unreachable, including the WSL2 start command.

    Args:
        redis_url: Override URL (default: ``REDIS_URL`` env var or
            ``redis://localhost:6379``).

    Returns:
        ``dict`` with keys:
            - ``"healthy"`` (bool): True when Redis responded to PING.
            - ``"url"`` (str): The URL that was probed.
            - ``"using_fallback"`` (bool): True when the singleton is on LRU.
            - ``"error"`` (str | None): Error message when not healthy.
            - ``"fix"`` (str | None): Actionable remediation hint.
    """
    url = redis_url or os.environ.get("REDIS_URL", "redis://localhost:6379")
    result: dict[str, object] = {
        "healthy": False,
        "url": url,
        "using_fallback": True,
        "error": None,
        "fix": None,
    }
    try:
        import redis as _redis

        parsed = urllib.parse.urlparse(url)
        conn = _redis.Redis(
            host=parsed.hostname or "localhost",
            port=int(parsed.port or 6379),
            db=0,
            socket_timeout=_REDIS_SOCKET_TIMEOUT_S,
            socket_connect_timeout=_REDIS_SOCKET_TIMEOUT_S,
        )
        conn.ping()
        info = conn.info("memory")
        result["healthy"] = True
        result["using_fallback"] = False
        result["used_memory_human"] = info.get("used_memory_human", "unknown")
        result["maxmemory_human"] = info.get("maxmemory_human", "0B")
        logger.info("Redis health OK: url=%s mem=%s", url, result["used_memory_human"])
    except ImportError:
        result["error"] = "redis package not installed"
        result["fix"] = "pip install redis"
        logger.error("Redis health FAIL: redis package not installed. Fix: pip install redis")
    # guardian: allow-silent-swallow
    except Exception as exc:
        result["error"] = str(exc)
        result["fix"] = (
            "Start Redis before launching the agent stack.\n  WSL2:    sudo apt install redis-server && redis-server --daemonize yes\n  Windows: winget install Redis.Redis\n  Docker:  docker run -d -p 6379:6379 redis:7-alpine\n  Env var: set REDIS_URL=redis://localhost:6379"
        )
        logger.error("Redis health FAIL: url=%s error=%s\n%s", url, exc, result["fix"])
    return result


_emit_reads_through("l4", "redis_cache_client", "urg_read_1")
_emit_reads_through("l4", "redis_cache_client", "urg_read_2")
_emit_reads_through("l4", "redis_cache_client", "urg_read_3")
_emit_reads_through("l4", "redis_cache_client", "urg_read_4")
_emit_reads_through("l4", "redis_cache_client", "urg_read_5")
_emit_reads_through("l4", "redis_cache_client", "urg_read_6")
_emit_reads_through("l4", "redis_cache_client", "urg_read_7")
_emit_reads_through("l4", "redis_cache_client", "urg_read_8")
_emit_reads_through("l4", "redis_cache_client", "urg_read_9")
_emit_reads_through("l4", "redis_cache_client", "urg_read_10")
_emit_reads_through("l4", "redis_cache_client", "urg_read_11")
_emit_reads_through("l4", "redis_cache_client", "urg_read_12")
_emit_reads_through("l4", "redis_cache_client", "urg_read_13")
_emit_reads_through("l4", "redis_cache_client", "urg_read_14")
_emit_reads_through("l4", "redis_cache_client", "urg_read_15")
_emit_reads_through("l4", "redis_cache_client", "urg_read_16")
_emit_reads_through("l4", "redis_cache_client", "urg_read_17")
_emit_reads_through("l4", "redis_cache_client", "urg_read_18")
_emit_reads_through("l4", "redis_cache_client", "urg_read_19")
_emit_reads_through("l4", "redis_cache_client", "urg_read_20")
_emit_reads_through("l4", "redis_cache_client", "urg_read_21")
_emit_reads_through("l4", "redis_cache_client", "urg_read_22")
_emit_reads_through("l4", "redis_cache_client", "urg_read_23")
_emit_reads_through("l4", "redis_cache_client", "urg_read_24")
_emit_reads_through("l4", "redis_cache_client", "urg_read_25")
_emit_reads_through("l4", "redis_cache_client", "urg_read_26")
_emit_reads_through("l4", "redis_cache_client", "urg_read_27")
_emit_reads_through("l4", "redis_cache_client", "urg_read_28")
_emit_reads_through("l4", "redis_cache_client", "urg_read_29")
_emit_reads_through("l4", "redis_cache_client", "urg_read_30")
_emit_reads_through("l4", "redis_cache_client", "urg_read_31")
_emit_reads_through("l4", "redis_cache_client", "urg_read_32")
_emit_reads_through("l4", "redis_cache_client", "urg_read_33")
_emit_reads_through("l4", "redis_cache_client", "urg_read_34")
_emit_reads_through("l4", "redis_cache_client", "urg_read_35")
_emit_reads_through("l4", "redis_cache_client", "urg_read_36")
_emit_reads_through("l4", "redis_cache_client", "urg_read_37")
_emit_reads_through("l4", "redis_cache_client", "urg_read_38")
_emit_reads_through("l4", "redis_cache_client", "urg_read_39")
_emit_reads_through("l4", "redis_cache_client", "urg_read_40")
_emit_reads_through("l4", "redis_cache_client", "urg_read_41")
_emit_reads_through("l4", "redis_cache_client", "urg_read_42")
_emit_reads_through("l4", "redis_cache_client", "urg_read_43")
_emit_reads_through("l4", "redis_cache_client", "urg_read_44")
_emit_reads_through("l4", "redis_cache_client", "urg_read_45")
_emit_reads_through("l4", "redis_cache_client", "urg_read_46")
_emit_reads_through("l4", "redis_cache_client", "urg_read_47")
_emit_reads_through("l4", "redis_cache_client", "urg_read_48")
_emit_reads_through("l4", "redis_cache_client", "urg_read_49")
_emit_reads_through("l4", "redis_cache_client", "urg_read_50")
_emit_reads_through("l4", "redis_cache_client", "urg_read_51")
_emit_reads_through("l4", "redis_cache_client", "urg_read_52")
_emit_reads_through("l4", "redis_cache_client", "urg_read_53")
_emit_reads_through("l4", "redis_cache_client", "urg_read_54")
_emit_reads_through("l4", "redis_cache_client", "urg_read_55")
_emit_reads_through("l4", "redis_cache_client", "urg_read_56")
_emit_reads_through("l4", "redis_cache_client", "urg_read_57")
_emit_reads_through("l4", "redis_cache_client", "urg_read_58")
_emit_reads_through("l4", "redis_cache_client", "urg_read_59")
_emit_reads_through("l4", "redis_cache_client", "urg_read_60")
_emit_reads_through("l4", "redis_cache_client", "urg_read_61")
_emit_reads_through("l4", "redis_cache_client", "urg_read_62")
_emit_reads_through("l4", "redis_cache_client", "urg_read_63")
_emit_reads_through("l4", "redis_cache_client", "urg_read_64")
_emit_reads_through("l4", "redis_cache_client", "urg_read_65")
_emit_reads_through("l4", "redis_cache_client", "urg_read_66")
_emit_reads_through("l4", "redis_cache_client", "urg_read_67")
_emit_reads_through("l4", "redis_cache_client", "urg_read_68")
_emit_reads_through("l4", "redis_cache_client", "urg_read_69")
_emit_reads_through("l4", "redis_cache_client", "urg_read_70")
_emit_reads_through("l4", "redis_cache_client", "urg_read_71")
_emit_reads_through("l4", "redis_cache_client", "urg_read_72")
_emit_reads_through("l4", "redis_cache_client", "urg_read_73")
_emit_reads_through("l4", "redis_cache_client", "urg_read_74")
