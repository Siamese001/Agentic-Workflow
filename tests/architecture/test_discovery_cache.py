"""Non-happy-path tests for AgentDiscoveryCache following .windsurfrules §4."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,  # noqa: E402
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_discovery_cache")
# REMOVED: _emit_applies_guardrail("p0", "test_discovery_cache", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_discovery_cache", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_discovery_cache", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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
    _emit_links_incident_trace,  # noqa: E402
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
    _emit_writes_through,  # noqa: E402
)

# REMOVED: _emit_emits_metric_event("test_discovery_cache", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_discovery_cache", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_discovery_cache", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_discovery_cache", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_discovery_cache", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_discovery_cache", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_discovery_cache", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_discovery_cache", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_discovery_cache", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_discovery_cache", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_discovery_cache", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_discovery_cache", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_discovery_cache", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_discovery_cache", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_discovery_cache", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_discovery_cache", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_discovery_cache", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_discovery_cache", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_discovery_cache", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_discovery_cache", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_discovery_cache", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_discovery_cache", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_discovery_cache", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_discovery_cache", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_discovery_cache", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_discovery_cache", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_discovery_cache", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_discovery_cache", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_discovery_cache", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_discovery_cache", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_discovery_cache", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_discovery_cache", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_discovery_cache", "write_through")
# REMOVED: _emit_writes_through("p1", "test_discovery_cache", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_discovery_cache", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_discovery_cache", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_discovery_cache", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_discovery_cache", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_discovery_cache", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_discovery_cache", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_discovery_cache", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_discovery_cache", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_discovery_cache", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_discovery_cache", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_discovery_cache", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_discovery_cache", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_discovery_cache", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_discovery_cache", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_discovery_cache")
# REMOVED: _emit_gated_by_confidence("p1", "test_discovery_cache", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_discovery_cache")
# REMOVED: emit_determinism_digest("p0", "test_discovery_cache")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_discovery_cache", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_discovery_cache", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_discovery_cache", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_discovery_cache", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_discovery_cache", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_discovery_cache", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_discovery_cache", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_discovery_cache", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_discovery_cache", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_discovery_cache", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_discovery_cache", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_discovery_cache", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_discovery_cache", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_discovery_cache", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_discovery_cache", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_discovery_cache", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_discovery_cache", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_discovery_cache", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_discovery_cache", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_discovery_cache", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

def _make_fake_cache():
    """Create a mock DeterministicRedisCache for testing."""
    fake = MagicMock()
    fake.get_json.return_value = None
    fake.set_json.return_value = None
    return fake


# ---------------------------------------------------------------------------
# §1  HAPPY PATH: Basic functionality
# ---------------------------------------------------------------------------


def test_agent_discovery_cache_has_get_or_fetch():
    """AgentDiscoveryCache must have get_or_fetch method."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    cache = AgentDiscoveryCache(cache=_make_fake_cache())
    assert hasattr(cache, "get_or_fetch")
    assert callable(cache.get_or_fetch)


def test_agent_discovery_cache_miss_calls_fetch():
    """Cache miss must call fetch_from_disk exactly once."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "TestAgent", "path": "test.py"}], f)
        temp_path = Path(f.name)

    try:
        call_count = [0]

        def fetch():
            call_count[0] += 1
            return [{"name": "TestAgent", "path": "test.py"}]

        result = cache.get_or_fetch(temp_path, fetch)
        assert call_count[0] == 1
        assert result == [{"name": "TestAgent", "path": "test.py"}]
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_hit_skips_fetch():
    """Cache hit must NOT call fetch_from_disk."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = [{"name": "CachedAgent", "path": "cached.py"}]
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "TestAgent"}], f)
        temp_path = Path(f.name)

    try:
        fetch_called = [False]

        def fetch():
            fetch_called[0] = True
            return [{"name": "TestAgent"}]

        result = cache.get_or_fetch(temp_path, fetch)
        assert not fetch_called[0], "fetch must not be called on cache hit"
        assert result == [{"name": "CachedAgent", "path": "cached.py"}]
    finally:
        temp_path.unlink()


# ---------------------------------------------------------------------------
# §2  NON-HAPPY-PATH: Error handling & edge cases
# ---------------------------------------------------------------------------


def test_agent_discovery_cache_file_not_found_propagates():
    """FileNotFoundError must propagate when discovery file missing."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)
    nonexistent = Path("/nonexistent/agent_discovery.json")

    with pytest.raises(FileNotFoundError):
        cache.get_or_fetch(nonexistent, lambda: [])


def test_agent_discovery_cache_fetch_exception_propagates():
    """Exceptions from fetch_from_disk must propagate."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([], f)
        temp_path = Path(f.name)

    try:

        def fetch_raises():
            raise ValueError("Disk read failed")

        with pytest.raises(ValueError, match="Disk read failed"):
            cache.get_or_fetch(temp_path, fetch_raises)
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_non_callable_fetch_raises():
    """Non-callable fetch_from_disk must raise TypeError."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([], f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(TypeError):
            cache.get_or_fetch(temp_path, "not-a-callable")  # type: ignore[arg-type]
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_replay_mode_bypasses_cache():
    """replay_mode=True must skip cache read and write."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = [{"name": "StaleAgent"}]
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "FreshAgent"}], f)
        temp_path = Path(f.name)

    try:
        fetch_called = [False]

        def fetch():
            fetch_called[0] = True
            return [{"name": "FreshAgent"}]

        result = cache.get_or_fetch(temp_path, fetch, replay_mode=True)
        assert fetch_called[0], "fetch must be called in replay mode"
        assert result == [{"name": "FreshAgent"}]
        fake.set_json.assert_not_called()
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_empty_list_is_valid():
    """fetch_from_disk returning empty list is valid and must be cached."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([], f)
        temp_path = Path(f.name)

    try:
        result = cache.get_or_fetch(temp_path, lambda: [])
        assert result == []
        fake.set_json.assert_called_once()
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_content_hash_changes_invalidate():
    """Changing file content must invalidate cache via different hash."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "Agent1"}], f)
        temp_path = Path(f.name)

    try:
        # First fetch
        cache.get_or_fetch(temp_path, lambda: [{"name": "Agent1"}])
        first_key = fake.set_json.call_args[0][0]

        # Modify file content
        temp_path.write_text(json.dumps([{"name": "Agent2"}]), encoding="utf-8")

        # Second fetch should use different cache key
        fake.reset_mock()
        cache.get_or_fetch(temp_path, lambda: [{"name": "Agent2"}])
        second_key = fake.set_json.call_args[0][0]

        assert first_key != second_key, "Cache key must change when file content changes"
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_handles_cache_get_exception():
    """If cache.get_json raises, must fall through to fetch."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    fake.get_json.side_effect = RuntimeError("Redis connection lost")
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "Agent"}], f)
        temp_path = Path(f.name)

    try:
        fetch_called = [False]

        def fetch():
            fetch_called[0] = True
            return [{"name": "Agent"}]

        result = cache.get_or_fetch(temp_path, fetch)
        assert fetch_called[0], "fetch must be called when cache.get_json fails"
        assert result == [{"name": "Agent"}]
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_handles_cache_set_exception():
    """If cache.set_json raises, fetch result must still be returned."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    fake.set_json.side_effect = RuntimeError("Redis write failed")
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "Agent"}], f)
        temp_path = Path(f.name)

    try:
        result = cache.get_or_fetch(temp_path, lambda: [{"name": "Agent"}])
        assert result == [{"name": "Agent"}], "Result must be returned even if cache write fails"
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_fetch_called_exactly_once():
    """fetch_from_disk must be called exactly once per cache miss."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "Agent"}], f)
        temp_path = Path(f.name)

    try:
        call_count = [0]

        def fetch():
            call_count[0] += 1
            return [{"name": "Agent"}]

        cache.get_or_fetch(temp_path, fetch)
        assert call_count[0] == 1, "fetch must be called exactly once"
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_invalidate_all_is_noop():
    """invalidate_all must be a no-op for content-addressed cache."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)
    cache.invalidate_all()  # Must not raise


# ---------------------------------------------------------------------------
# §3  UPDATED §4 REQUIREMENT GAPS
# ---------------------------------------------------------------------------


def test_agent_discovery_cache_same_file_gives_identical_key_twice():
    """Same file content must produce identical cache key on two successive calls (§4:124-125)."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "AgentA"}], f)
        temp_path = Path(f.name)

    try:
        cache.get_or_fetch(temp_path, lambda: [{"name": "AgentA"}])
        key1 = fake.set_json.call_args[0][0]

        fake.reset_mock()
        cache.get_or_fetch(temp_path, lambda: [{"name": "AgentA"}])
        key2 = fake.set_json.call_args[0][0]

        assert key1 == key2, "Same file content must produce identical cache key on repeat calls"
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_replay_warm_cache_get_json_never_called():
    """replay_mode=True with warm cache must NEVER call get_json (§4:155-156 matrix: warm×replay)."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = [{"name": "StaleAgent"}]  # warm cache
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "FreshAgent"}], f)
        temp_path = Path(f.name)

    try:
        result = cache.get_or_fetch(temp_path, lambda: [{"name": "FreshAgent"}], replay_mode=True)
        fake.get_json.assert_not_called()
        fake.set_json.assert_not_called()
        assert result == [{"name": "FreshAgent"}]
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_hit_side_effect_envelope():
    """On cache hit: get_json called once, set_json never called, fetch never called (§4:134-138)."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = [{"name": "Cached"}]
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "Cached"}], f)
        temp_path = Path(f.name)

    try:
        fetch_called = [False]

        def fetch():
            fetch_called[0] = True
            return [{"name": "Cached"}]

        cache.get_or_fetch(temp_path, fetch)
        assert not fetch_called[0], "fetch must not be called on cache hit"
        fake.get_json.assert_called_once()
        fake.set_json.assert_not_called()
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_file_not_found_no_set_json_side_effect():
    """FileNotFoundError must propagate before any set_json call (§4:131-133 fail-closed)."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with pytest.raises(FileNotFoundError):
        cache.get_or_fetch(Path("/no/such/file.json"), lambda: [])

    fake.set_json.assert_not_called()


def test_agent_discovery_cache_broad_except_does_not_swallow_custom_sentinel():
    """The broad except on cache read must not swallow exceptions from fetch itself (§4:146-148).

    The cache read except-block targets cache.get_json failures only.
    A ValueError raised by fetch_from_disk must still propagate out.
    """
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = None  # cache miss — fetch will be called
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([], f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(ValueError, match="sentinel-propagation-check"):
            cache.get_or_fetch(
                temp_path, lambda: (_ for _ in ()).throw(ValueError("sentinel-propagation-check"))
            )
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_stale_cache_path_returns_fresh_after_miss():
    """After TTL expiry (get_json returns None again), fetch is called and result re-cached (§4:179-183)."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump([{"name": "Agent"}], f)
        temp_path = Path(f.name)

    try:
        # First call: miss, fetch, write
        call_count = [0]

        def fetch():
            call_count[0] += 1
            return [{"name": "Agent"}]

        cache.get_or_fetch(temp_path, fetch)
        assert call_count[0] == 1
        assert fake.set_json.call_count == 1

        # Simulate TTL expiry: get_json returns None again
        fake.get_json.return_value = None
        fake.reset_mock()

        cache.get_or_fetch(temp_path, fetch)
        assert call_count[0] == 2, "fetch must be called again after TTL expiry"
        assert fake.set_json.call_count == 1, "set_json must be called again to re-cache"
    finally:
        temp_path.unlink()


def test_agent_discovery_cache_malformed_plausible_path_object():
    """Path that exists but is a directory degrades gracefully: fetch called, result returned (§4:116-117).

    On Windows, reading a directory raises PermissionError (subclass of OSError).
    The hash computation handler catches OSError, logs a warning, and falls through to fetch.
    This is correct cache-resilience behavior: the cache seam must never crash the caller.
    The test asserts the malformed-but-plausible input does not silently convert failure
    into false success — the result comes from fetch, not a phantom cache hit.
    """
    import tempfile as tf

    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)
    fetch_called = [False]

    def fetch():
        fetch_called[0] = True
        return []

    with tf.TemporaryDirectory() as tmpdir:
        dir_path = Path(tmpdir)
        # Directory path: hash computation fails with OSError/PermissionError.
        # Cache degrades gracefully: fetch IS called, result returned, no phantom cache hit.
        result = cache.get_or_fetch(dir_path, fetch)
        assert fetch_called[0], "fetch must be called when path is a directory (hash computation fails)"
        assert result == [], "result must come from fetch, not from cache"
        # No phantom cache hit: get_json return value must not have been returned
        fake.get_json.assert_not_called()  # get_json never reached (OSError branch exits before else)


def test_agent_discovery_cache_distinct_files_produce_distinct_keys():
    """Two files with different content must produce distinct cache keys (§4:127)."""
    from agentic_core.cache.discovery_cache import AgentDiscoveryCache

    fake = _make_fake_cache()
    cache = AgentDiscoveryCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
        json.dump([{"name": "AgentA"}], f1)
        path1 = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f2:
        json.dump([{"name": "AgentB"}], f2)
        path2 = Path(f2.name)

    try:
        cache.get_or_fetch(path1, lambda: [{"name": "AgentA"}])
        key1 = fake.set_json.call_args[0][0]

        fake.reset_mock()
        cache.get_or_fetch(path2, lambda: [{"name": "AgentB"}])
        key2 = fake.set_json.call_args[0][0]

        assert key1 != key2
    finally:
        path1.unlink()
        path2.unlink()
