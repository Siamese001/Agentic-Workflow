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
