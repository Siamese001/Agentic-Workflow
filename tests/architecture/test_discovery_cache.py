"""Non-happy-path tests for AgentDiscoveryCache following .windsurfrules §4."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


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
    assert True  # no-exception contract


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
