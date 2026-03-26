"""Redis integration tests — REQUIRES LIVE REDIS SERVER.

These tests skip (not hang) when Redis is not running, and FAIL when
Redis is running but misbehaving.  No mocks — every assertion hits
real Redis.

Run with:
    pytest tests/integration/agentic_core/test_redis_integration.py -v
"""

from __future__ import annotations

import time

import pytest

#  # MOVED: from agentic_core.cache.redis_cache_client import (
    CacheDB,
    DeterministicRedisCache,
    check_redis_health,
    get_coordination_cache,
    get_hot_cache,
    reset_cache_singletons,
)
#  # MOVED: from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,  # noqa: E402
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_redis_integration", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_redis_integration", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_redis_integration", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_redis_integration", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_redis_integration", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_redis_integration", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_redis_integration", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_redis_integration", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_redis_integration", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_redis_integration", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_redis_integration", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_redis_integration", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_redis_integration", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_redis_integration", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_redis_integration", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_redis_integration", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_redis_integration", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_redis_integration", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_redis_integration", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_redis_integration", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_redis_integration", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_redis_integration", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_redis_integration", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_redis_integration", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_redis_integration", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_redis_integration", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_redis_integration", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_redis_integration", "runtime_state", "p2_rt_2")

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_redis_integration")
# REMOVED: _emit_applies_guardrail("p0", "test_redis_integration", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_redis_integration", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_redis_integration", "state_snapshot")
# REMOVED: _emit_pulls_context("p1", "test_redis_integration", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_redis_integration", "context_pull_secondary")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_redis_integration", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_redis_integration", "uwg_term_secondary")
# REMOVED: _emit_writes_through("p1", "test_redis_integration", "write_through")
# REMOVED: _emit_writes_through("p1", "test_redis_integration", "write_through_secondary")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_redis_integration", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_redis_integration", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_redis_integration", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_redis_integration", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_redis_integration", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_redis_integration", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_redis_integration", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_redis_integration", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_redis_integration", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_redis_integration", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_redis_integration", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_redis_integration", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_redis_integration", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_redis_integration", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_redis_integration")
# REMOVED: _emit_gated_by_confidence("p1", "test_redis_integration", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_redis_integration")
# REMOVED: emit_determinism_digest("p0", "test_redis_integration")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_redis_integration", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_redis_integration", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_redis_integration", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_redis_integration", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_redis_integration", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_redis_integration", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_redis_integration", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_redis_integration", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_redis_integration", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_redis_integration", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_redis_integration", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_redis_integration", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_redis_integration", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_redis_integration", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_redis_integration", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_redis_integration", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_redis_integration", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_redis_integration", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_redis_integration", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_redis_integration", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


# ---------------------------------------------------------------------------
# Module-level fast probe — skips the whole file in <0.3 s if Redis is down
# ---------------------------------------------------------------------------

_health = check_redis_health()
if not _health["healthy"]:
    pytest.fail(
        f"Redis not running — integration suite cannot execute.\n"
        f"Error: {_health['error']}\nFix:   {_health['fix']}\n"
        f"Redis is a mandatory dependency (pyproject.toml redis>=5.0.0). "
        f"Start Redis before running this suite or set REDIS_URL.",
    )

pytestmark = pytest.mark.integration_full_deps


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _raw_conn(cache: DeterministicRedisCache):
    """Return a live redis.Redis connection from the cache (never None here)."""
    conn = cache._connect()
    assert conn is not None, "Redis must be reachable; got None from _connect()"
    return conn


def _flush_db(db: CacheDB) -> None:
    c = DeterministicRedisCache(db=db)
    _raw_conn(c).flushdb()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module", autouse=True)
def flush_dbs_around_module():
    """Flush test DBs before and after the entire module to avoid cross-test pollution."""
    _flush_db(CacheDB.HOT)
    _flush_db(CacheDB.COORDINATION)
    yield
    reset_cache_singletons()
    _flush_db(CacheDB.HOT)
    _flush_db(CacheDB.COORDINATION)


@pytest.fixture
def hot():
    """Fresh HOT-DB cache — guaranteed NOT in fallback mode."""
    cache = DeterministicRedisCache(db=CacheDB.HOT)
    conn = _raw_conn(cache)
    conn.flushdb()
    assert cache._use_fallback is False, "Cache must NOT be in fallback mode for integration tests"
    yield cache
    _raw_conn(cache).flushdb()


@pytest.fixture
def coord():
    """Fresh COORDINATION-DB cache — guaranteed NOT in fallback mode."""
    cache = DeterministicRedisCache(db=CacheDB.COORDINATION)
    conn = _raw_conn(cache)
    conn.flushdb()
    assert cache._use_fallback is False
    yield cache
    _raw_conn(cache).flushdb()


# ---------------------------------------------------------------------------
# 1. Connection hygiene
# ---------------------------------------------------------------------------


class TestRedisConnection:
    def test_health_check_reports_healthy(self):
        from agentic_core.cache.redis_cache_client import (
        from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    """Test health_check_reports_healthy contract compliance."""
    # Arrange
    # TODO: Set up test data
    test_data = {}  # Replace with actual test data

    # Act
    # TODO: Validate schema
    validation_result = None  # Replace with actual validation

    # Assert - Schema Contract
    assert validation_result is not None, "Schema validation should produce a result"
    assert isinstance(validation_result, (bool, dict)), "Validation result should be structured"
    # TODO: Add specific schema validation assertions
    # assert validation_result.get("valid", False), "Data should conform to schema"
        assert len(hot._fallback) == 0, "Data went to in-memory fallback instead of Redis"

    def test_ping_succeeds(self, hot):
        assert _raw_conn(hot).ping() is True


# ---------------------------------------------------------------------------
# 2. Basic read / write / delete
# ---------------------------------------------------------------------------


class TestRedisBasicOps:
    def test_set_get_roundtrip(self, hot):
        hot.set("rw:roundtrip", b"hello_redis", ttl_seconds=30)
        assert hot.get("rw:roundtrip") == b"hello_redis"

    def test_get_missing_key_returns_none(self, hot):
        assert hot.get("rw:definitely:missing:xyz") is None

    def test_delete_removes_key(self, hot):
        hot.set("rw:delete_me", b"gone", ttl_seconds=30)
        assert hot.get("rw:delete_me") == b"gone"
        hot.delete("rw:delete_me")
        assert hot.get("rw:delete_me") is None

    def test_overwrite_updates_value(self, hot):
        hot.set("rw:overwrite", b"original", ttl_seconds=30)
        hot.set("rw:overwrite", b"updated", ttl_seconds=30)
        assert hot.get("rw:overwrite") == b"updated"

    def test_five_independent_keys(self, hot):
        pairs = {f"rw:multi:{i}": f"val_{i}".encode() for i in range(5)}
        for k, v in pairs.items():
            hot.set(k, v, ttl_seconds=30)
        for k, v in pairs.items():
            assert hot.get(k) == v

    def test_set_returns_true_on_success(self, hot):
        result = hot.set("rw:return", b"v", ttl_seconds=30)
        assert result is True


# ---------------------------------------------------------------------------
# 3. TTL enforcement — actual expiry in Redis, not mocked
# ---------------------------------------------------------------------------


class TestRedisTTL:
    def test_key_expires_after_ttl(self, hot):
        hot.set("ttl:expires", b"ephemeral", ttl_seconds=1)
        assert hot.get("ttl:expires") == b"ephemeral"
        time.sleep(DEFAULT_SLEEP)
        assert hot.get("ttl:expires") is None, "Key must have expired in Redis after TTL"

    def test_key_survives_within_ttl(self, hot):
        hot.set("ttl:survives", b"durable", ttl_seconds=30)
        time.sleep(DEFAULT_SLEEP)
        assert hot.get("ttl:survives") == b"durable"

    def test_redis_ttl_command_reflects_set_value(self, hot):
        """TTL remaining as reported by Redis must be close to what we set."""
        hot.set("ttl:cmd", b"v", ttl_seconds=20)
        remaining = _raw_conn(hot).ttl("ttl:cmd")
        assert 18 <= remaining <= 20, f"Expected ~20s TTL, Redis reports {remaining}s"

    def test_max_ttl_stored_correctly(self, hot):
        hot.set("ttl:max", b"v", ttl_seconds=86400)
        remaining = _raw_conn(hot).ttl("ttl:max")
        assert remaining > 86390, f"Expected ~86400s TTL, Redis reports {remaining}s"


# ---------------------------------------------------------------------------
# 4. Edge cases — binary, large values
# ---------------------------------------------------------------------------


class TestRedisEdgeCases:
    def test_binary_data_with_null_bytes(self, hot):
        val = b"\x00\x01\x02\xff\xfe\xfd\x00"
        hot.set("edge:binary", val, ttl_seconds=30)
        assert hot.get("edge:binary") == val

    def test_large_value_1mb(self, hot):
        val = b"x" * (1024 * 1024)
        hot.set("edge:large", val, ttl_seconds=30)
        assert hot.get("edge:large") == val

    def test_overwrite_with_smaller_value(self, hot):
        hot.set("edge:shrink", b"large_original_value", ttl_seconds=30)
        hot.set("edge:shrink", b"tiny", ttl_seconds=30)
        assert hot.get("edge:shrink") == b"tiny"


# ---------------------------------------------------------------------------
# 5. Namespace isolation — HOT vs COORDINATION DBs are separate
# ---------------------------------------------------------------------------


class TestRedisNamespaces:
    def test_hot_and_coordination_dbs_isolated(self, hot, coord):
        key = "ns:isolation"
        hot.set(key, b"hot_value", ttl_seconds=30)
        coord.set(key, b"coord_value", ttl_seconds=30)
        assert hot.get(key) == b"hot_value"
        assert coord.get(key) == b"coord_value"

    def test_delete_in_hot_does_not_affect_coordination(self, hot, coord):
        key = "ns:delete_isolation"
        hot.set(key, b"h", ttl_seconds=30)
        coord.set(key, b"c", ttl_seconds=30)
        hot.delete(key)
        assert hot.get(key) is None
        assert coord.get(key) == b"c"

    def test_singleton_factories_use_correct_dbs(self, flush_dbs_around_module):
        reset_cache_singletons()
        h = get_hot_cache()
        c = get_coordination_cache()
        assert h._db == CacheDB.HOT
        assert c._db == CacheDB.COORDINATION
        assert h is not c


# ---------------------------------------------------------------------------
# 6. Stats — counters incremented by real Redis operations
# ---------------------------------------------------------------------------


class TestRedisStats:
    def test_hit_increments_hits(self, hot):
        hot.set("stats:hit", b"v", ttl_seconds=30)
        before = hot.stats.hits
        hot.get("stats:hit")
        assert hot.stats.hits == before + 1

    def test_miss_increments_misses(self, hot):
        before = hot.stats.misses
        hot.get("stats:definitely_missing_xyz")
        assert hot.stats.misses == before + 1

    def test_get_stats_reflects_live_state(self, hot):
        hot.set("stats:k", b"v", ttl_seconds=30)
        hot.get("stats:k")  # hit
        hot.get("stats:missing")  # miss
        s = hot.get_stats()
        assert s["using_fallback"] is False
        assert s["hits"] >= 1
        assert s["misses"] >= 1
        assert s["db"] == int(CacheDB.HOT)


# ---------------------------------------------------------------------------
# 7. Replay mode — real Redis, replay bypasses it unconditionally
# ---------------------------------------------------------------------------


class TestRedisReplayMode:
    def test_replay_mode_bypasses_real_redis(self, hot):
        hot.set("replay:key", b"cached", ttl_seconds=30)
        assert hot.get("replay:key") == b"cached"  # normal path hits Redis
        assert hot.get("replay:key", replay_mode=True) is None  # replay must bypass

    def test_replay_does_not_evict_key_from_redis(self, hot):
        """replay_mode=True bypasses but must not delete the cached value."""
        hot.set("replay:persist", b"still_here", ttl_seconds=30)
        hot.get("replay:persist", replay_mode=True)
        assert hot.get("replay:persist") == b"still_here"

    def test_replay_increments_bypassed_counter(self, hot):
        hot.set("replay:counter", b"v", ttl_seconds=30)
        before = hot.stats.bypassed_replay
        hot.get("replay:counter", replay_mode=True)
        assert hot.stats.bypassed_replay == before + 1
