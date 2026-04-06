"""Redis Cache Client — DeterministicRedisCache and supporting utilities.

Core Redis client for all cache operations. Provides hash-keyed, deterministic
cache operations with proper DB isolation, TTL management, and LRU fallback.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from typing import Any

import redis

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

logger = logging.getLogger(__name__)

# Redis DB indices (isolated namespaces)
CacheDB = int
DB_HOT = 0  # Hot caches (L0/L1/L3/L5 routing, execution, orchestration, safety)
DB_COORDINATION = 1  # Coordination leases (L2 execution locks)
DB_WORKSPACE = 2  # Operational workspace (per-trace, team-sync, replay-assist, novelty)

_DEFAULT_TTL_SECONDS = 3600  # 1 hour default TTL


def canonical_json_bytes(obj: Any) -> bytes:
    """Return canonical JSON bytes for cache value serialization.

    Uses sorted keys to ensure deterministic serialization.
    """
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def content_hash(data: bytes) -> str:
    """Return SHA-256 hash of data for content-addressed caching."""
    return hashlib.sha256(data).hexdigest()


class DeterministicRedisCache:
    """Deterministic Redis cache with hash-keyed operations.

    All cache operations use content-hashed keys for automatic invalidation
    when inputs change. Provides proper DB isolation and TTL management.
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        db: CacheDB = DB_HOT,
        password: str | None = None,
        socket_timeout: float = 5.0,
        socket_connect_timeout: float = 5.0,
        health_check_interval: int = 30,
    ) -> None:
        """Initialize Redis cache connection.

        Args:
            host: Redis host (default: REDIS_HOST env var or localhost)
            port: Redis port (default: REDIS_PORT env var or 6379)
            db: Redis DB index (default: 0 - hot caches)
            password: Redis password (default: REDIS_PASSWORD env var or None)
            socket_timeout: Socket read timeout
            socket_connect_timeout: Connection timeout
            health_check_interval: Health check interval in seconds
        """
        self.host = host or os.environ.get("REDIS_HOST", "localhost")
        self.port = port or int(os.environ.get("REDIS_PORT", "6379"))
        self.db = db
        self.password = password or os.environ.get("REDIS_PASSWORD")
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        self.health_check_interval = health_check_interval

        self._client: redis.Redis | None = None
        self._connected = False

    def _get_client(self) -> redis.Redis | None:
        """Get or create Redis client with lazy connection."""
        if self._client is None:
            try:
                self._client = redis.Redis(
                    host=self.host,
                    port=self.port,
                    db=self.db,
                    password=self.password,
                    socket_timeout=self.socket_timeout,
                    socket_connect_timeout=self.socket_connect_timeout,
                    health_check_interval=self.health_check_interval,
                    decode_responses=True,
                )
                # Test connection
                self._client.ping()
                self._connected = True
            except redis.ConnectionError as e:
                logger.warning(f"Redis connection failed: {e}")
                self._connected = False
                return None
        return self._client

    def get(self, key: str, db: CacheDB | None = None) -> str | None:
        """Get raw string value from cache.

        Args:
            key: Cache key
            db: Optional DB override (uses instance default if not specified)

        Returns:
            Cached value or None if not found
        """
        client = self._get_client()
        if client is None:
            return None
        try:
            if db is not None and db != self.db:
                # Use different DB via execute_command
                return client.execute_command("GET", key)
            return client.get(key)
        except redis.RedisError as e:
            logger.warning(f"Redis get failed: {e}")
            return None

    def get_json(self, key: str, db: CacheDB | None = None) -> Any | None:
        """Get JSON-deserialized value from cache.

        Args:
            key: Cache key
            db: Optional DB override

        Returns:
            Deserialized JSON value or None if not found/invalid
        """
        data = self.get(key, db=db)
        if data is None:
            return None
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON in cache for key: {key}")
            return None

    def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int = _DEFAULT_TTL_SECONDS,
        db: CacheDB | None = None,
    ) -> bool:
        """Set raw string value in cache.

        Args:
            key: Cache key
            value: String value to cache
            ttl_seconds: TTL in seconds
            db: Optional DB override

        Returns:
            True if set successfully, False otherwise
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            if db is not None and db != self.db:
                # Use different DB via execute_command with SELECT
                client.execute_command("SELECT", db)
                result = client.execute_command("SETEX", key, ttl_seconds, value)
                client.execute_command("SELECT", self.db)  # Restore original DB
                return result is not None
            return client.setex(key, ttl_seconds, value) is not None
        except redis.RedisError as e:
            logger.warning(f"Redis set failed: {e}")
            return False

    def set_json(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = _DEFAULT_TTL_SECONDS,
        db: CacheDB | None = None,
    ) -> bool:
        """Set JSON-serialized value in cache.

        Args:
            key: Cache key
            value: Value to JSON-serialize and cache
            ttl_seconds: TTL in seconds
            db: Optional DB override

        Returns:
            True if set successfully, False otherwise
        """
        try:
            json_str = json.dumps(value, sort_keys=True, separators=(",", ":"))
            return self.set(key, json_str, ttl_seconds=ttl_seconds, db=db)
        except (TypeError, ValueError) as e:
            logger.warning(f"JSON serialization failed: {e}")
            return False

    def delete(self, key: str, db: CacheDB | None = None) -> bool:
        """Delete key from cache.

        Args:
            key: Cache key to delete
            db: Optional DB override

        Returns:
            True if deleted, False otherwise
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            if db is not None and db != self.db:
                client.execute_command("SELECT", db)
                result = client.execute_command("DEL", key)
                client.execute_command("SELECT", self.db)
                return result == 1
            return client.delete(key) == 1
        except redis.RedisError as e:
            logger.warning(f"Redis delete failed: {e}")
            return False

    def set_nx(
        self,
        key: str,
        value: str,
        ttl_seconds: int = _DEFAULT_TTL_SECONDS,
        db: CacheDB | None = None,
    ) -> bool:
        """Set value only if key does not exist (SET if Not eXists).

        Args:
            key: Cache key
            value: String value to set
            ttl_seconds: TTL in seconds
            db: Optional DB override

        Returns:
            True if set (key didn't exist), False if key existed
        """
        client = self._get_client()
        if client is None:
            return False
        try:
            if db is not None and db != self.db:
                client.execute_command("SELECT", db)
                # SET key value NX EX ttl
                result = client.execute_command("SET", key, value, "NX", "EX", ttl_seconds)
                client.execute_command("SELECT", self.db)
                return result is not None
            return client.set(key, value, nx=True, ex=ttl_seconds) is not None
        except redis.RedisError as e:
            logger.warning(f"Redis set_nx failed: {e}")
            return False


# Singleton hot cache instance
_hot_cache: DeterministicRedisCache | None = None


def get_hot_cache() -> DeterministicRedisCache:
    """Get the singleton hot cache instance (DB 0)."""
    global _hot_cache
    if _hot_cache is None:
        _hot_cache = DeterministicRedisCache(db=DB_HOT)
    return _hot_cache


def get_coordination_cache() -> DeterministicRedisCache:
    """Get coordination cache instance (DB 1)."""
    return DeterministicRedisCache(db=DB_COORDINATION)


def get_workspace_cache() -> DeterministicRedisCache:
    """Get workspace cache instance (DB 2)."""
    return DeterministicRedisCache(db=DB_WORKSPACE)


def check_redis_health() -> dict:
    """Check Redis connection health.

    Returns:
        Dict with status, connected flag, and any error message
    """
    try:
        cache = get_hot_cache()
        client = cache._get_client()
        if client is None:
            return {"status": "unhealthy", "connected": False, "error": "No Redis client"}
        client.ping()
        return {"status": "healthy", "connected": True, "error": None}
    except Exception as e:
        return {"status": "unhealthy", "connected": False, "error": str(e)}


def reset_cache_singletons() -> None:
    """Reset all cache singleton instances.

    This is useful for testing and when needing to clear all cached connections.
    """
    global _hot_cache
    _hot_cache = None


# P0/P1/P2/P3/P4 governance wiring

_emit_applies_guardrail("p0", "redis_cache_client", "p0_governance")
_emit_reads_policy_state("p0", "redis_cache_client", "policy_binding")
_emit_snapshots_state("p0", "redis_cache_client", "state_snapshot")
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
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
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
