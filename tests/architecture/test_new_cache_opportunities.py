"""Non-happy-path tests for new cache opportunities (tool embeddings, schema validators, policy registry, config files).

Following .windsurfrules §4 to ensure comprehensive error coverage.
"""

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
    fake.delete.return_value = None
    return fake


# ---------------------------------------------------------------------------
# §1  TOOL EMBEDDING CACHE TESTS
# ---------------------------------------------------------------------------


def test_tool_embedding_cache_has_get_or_fetch():
    """ToolEmbeddingCache must have get_or_fetch method."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    cache = ToolEmbeddingCache(cache=_make_fake_cache())
    assert hasattr(cache, "get_or_fetch")
    assert callable(cache.get_or_fetch)


def test_tool_embedding_cache_miss_calls_fetch():
    """Cache miss must call fetch_embeddings exactly once."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "tool1", "description": "desc1", "tags": ["tag1"]}]
    call_count = [0]

    def fetch():
        call_count[0] += 1
        return [[0.1, 0.2]], ["tool1"]

    embeddings, names = cache.get_or_fetch(tools, fetch)
    assert call_count[0] == 1
    assert embeddings == [[0.1, 0.2]]
    assert names == ["tool1"]


def test_tool_embedding_cache_empty_tools_raises():
    """Empty tool definitions list must raise ValueError."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)

    with pytest.raises(ValueError, match="must not be empty"):
        cache.get_or_fetch([], lambda: ([], []))


def test_tool_embedding_cache_replay_mode_bypasses():
    """replay_mode=True must skip cache read and write."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"embeddings": [[0.9]], "tool_names": ["stale"]}
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "fresh", "description": "desc", "tags": []}]

    embeddings, names = cache.get_or_fetch(tools, lambda: ([[0.1]], ["fresh"]), replay_mode=True)
    assert embeddings == [[0.1]]
    assert names == ["fresh"]
    fake.set_json.assert_not_called()


def test_tool_embedding_cache_handles_cache_exception():
    """Cache exceptions must not propagate, must fall through to fetch."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    fake.get_json.side_effect = RuntimeError("Redis down")
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "tool1", "description": "desc", "tags": []}]

    embeddings, names = cache.get_or_fetch(tools, lambda: ([[0.5]], ["tool1"]))
    assert embeddings == [[0.5]]
    assert names == ["tool1"]


def test_tool_embedding_cache_fingerprint_changes_invalidate():
    """Changing tool set must invalidate cache via different fingerprint."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)

    tools1 = [{"name": "tool1", "description": "desc1", "tags": []}]
    cache.get_or_fetch(tools1, lambda: ([[0.1]], ["tool1"]))
    key1 = fake.set_json.call_args[0][0]

    tools2 = [{"name": "tool2", "description": "desc2", "tags": []}]
    fake.reset_mock()
    cache.get_or_fetch(tools2, lambda: ([[0.2]], ["tool2"]))
    key2 = fake.set_json.call_args[0][0]

    assert key1 != key2, "Cache key must change when tool set changes"


# ---------------------------------------------------------------------------
# §2  SCHEMA VALIDATOR CACHE TESTS
# ---------------------------------------------------------------------------


def test_schema_validator_cache_has_get_or_fetch():
    """SchemaValidatorCache must have get_or_fetch method."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    cache = SchemaValidatorCache(cache=_make_fake_cache())
    assert hasattr(cache, "get_or_fetch")
    assert callable(cache.get_or_fetch)


def test_schema_validator_cache_miss_calls_fetch():
    """Cache miss must call fetch_validator exactly once."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    cache = SchemaValidatorCache(cache=fake)
    schema = {"type": "object", "properties": {"name": {"type": "string"}}}
    call_count = [0]

    def fetch():
        call_count[0] += 1
        return {"compiled": True}

    result = cache.get_or_fetch(schema, fetch)
    assert call_count[0] == 1
    assert result == {"compiled": True}


def test_schema_validator_cache_empty_schema_raises():
    """Empty schema dict must raise ValueError."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    cache = SchemaValidatorCache(cache=fake)

    with pytest.raises(ValueError, match="must not be empty"):
        cache.get_or_fetch({}, lambda: None)


def test_schema_validator_cache_replay_mode_bypasses():
    """replay_mode=True must skip cache read and write."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"stale": True}
    cache = SchemaValidatorCache(cache=fake)
    schema = {"type": "string"}

    result = cache.get_or_fetch(schema, lambda: {"fresh": True}, replay_mode=True)
    assert result == {"fresh": True}
    fake.set_json.assert_not_called()


def test_schema_validator_cache_schema_changes_invalidate():
    """Changing schema must invalidate cache via different hash."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    cache = SchemaValidatorCache(cache=fake)

    schema1 = {"type": "string"}
    cache.get_or_fetch(schema1, lambda: {"v": 1})
    key1 = fake.set_json.call_args[0][0]

    schema2 = {"type": "number"}
    fake.reset_mock()
    cache.get_or_fetch(schema2, lambda: {"v": 2})
    key2 = fake.set_json.call_args[0][0]

    assert key1 != key2, "Cache key must change when schema changes"


def test_schema_validator_cache_handles_cache_exception():
    """Cache exceptions must not propagate."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    fake.get_json.side_effect = RuntimeError("Redis down")
    cache = SchemaValidatorCache(cache=fake)
    schema = {"type": "boolean"}

    result = cache.get_or_fetch(schema, lambda: {"ok": True})
    assert result == {"ok": True}


# ---------------------------------------------------------------------------
# §3  POLICY REGISTRY CACHE TESTS
# ---------------------------------------------------------------------------


def test_policy_registry_cache_has_get_or_fetch():
    """PolicyRegistryCache must have get_or_fetch method."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    cache = PolicyRegistryCache(cache=_make_fake_cache())
    assert hasattr(cache, "get_or_fetch")
    assert callable(cache.get_or_fetch)


def test_policy_registry_cache_miss_calls_fetch():
    """Cache miss must call fetch_policy exactly once."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)
    call_count = [0]

    def fetch():
        call_count[0] += 1
        return {"id": "GOV-001", "severity": "CRITICAL"}

    result = cache.get_or_fetch("GOV-001", fetch)
    assert call_count[0] == 1
    assert result["id"] == "GOV-001"


def test_policy_registry_cache_empty_policy_id_raises():
    """Empty policy ID must raise ValueError."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)

    with pytest.raises(ValueError, match="must not be empty"):
        cache.get_or_fetch("", lambda: {})

    with pytest.raises(ValueError, match="must not be empty"):
        cache.get_or_fetch("   ", lambda: {})


def test_policy_registry_cache_replay_mode_bypasses():
    """replay_mode=True must skip cache read and write."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"stale": True}
    cache = PolicyRegistryCache(cache=fake)

    result = cache.get_or_fetch("GOV-002", lambda: {"fresh": True}, replay_mode=True)
    assert result == {"fresh": True}
    fake.set_json.assert_not_called()


def test_policy_registry_cache_invalidate_calls_delete():
    """invalidate must call cache.delete with correct key."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)

    cache.invalidate("GOV-003")
    fake.delete.assert_called_once_with("policy:GOV-003")


def test_policy_registry_cache_handles_cache_exception():
    """Cache exceptions must not propagate."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    fake.get_json.side_effect = RuntimeError("Redis down")
    cache = PolicyRegistryCache(cache=fake)

    result = cache.get_or_fetch("GOV-004", lambda: {"ok": True})
    assert result == {"ok": True}


# ---------------------------------------------------------------------------
# §4  CONFIG FILE CACHE TESTS
# ---------------------------------------------------------------------------


def test_config_file_cache_has_get_or_fetch():
    """ConfigFileCache must have get_or_fetch method."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    cache = ConfigFileCache(cache=_make_fake_cache())
    assert hasattr(cache, "get_or_fetch")
    assert callable(cache.get_or_fetch)


def test_config_file_cache_miss_calls_fetch():
    """Cache miss must call fetch_from_disk exactly once."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"key": "value"}, f)
        temp_path = Path(f.name)

    try:
        call_count = [0]

        def fetch():
            call_count[0] += 1
            return {"key": "value"}

        result = cache.get_or_fetch(temp_path, fetch)
        assert call_count[0] == 1
        assert result == {"key": "value"}
    finally:
        temp_path.unlink()


def test_config_file_cache_file_not_found_propagates():
    """FileNotFoundError must propagate when config file missing."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    cache = ConfigFileCache(cache=fake)
    nonexistent = Path("/nonexistent/config.yaml")

    with pytest.raises(FileNotFoundError):
        cache.get_or_fetch(nonexistent, lambda: {})


def test_config_file_cache_replay_mode_bypasses():
    """replay_mode=True must skip cache read and write."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"stale": True}
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"fresh": True}, f)
        temp_path = Path(f.name)

    try:
        result = cache.get_or_fetch(temp_path, lambda: {"fresh": True}, replay_mode=True)
        assert result == {"fresh": True}
        fake.set_json.assert_not_called()
    finally:
        temp_path.unlink()


def test_config_file_cache_content_changes_invalidate():
    """Changing file content must invalidate cache via different hash."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"v": 1}, f)
        temp_path = Path(f.name)

    try:
        cache.get_or_fetch(temp_path, lambda: {"v": 1})
        key1 = fake.set_json.call_args[0][0]

        temp_path.write_text(json.dumps({"v": 2}), encoding="utf-8")
        fake.reset_mock()
        cache.get_or_fetch(temp_path, lambda: {"v": 2})
        key2 = fake.set_json.call_args[0][0]

        assert key1 != key2, "Cache key must change when file content changes"
    finally:
        temp_path.unlink()


def test_config_file_cache_handles_cache_exception():
    """Cache exceptions must not propagate."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    fake.get_json.side_effect = RuntimeError("Redis down")
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"ok": True}, f)
        temp_path = Path(f.name)

    try:
        result = cache.get_or_fetch(temp_path, lambda: {"ok": True})
        assert result == {"ok": True}
    finally:
        temp_path.unlink()


def test_config_file_cache_handles_set_exception():
    """Cache write exceptions must not propagate."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    fake.set_json.side_effect = RuntimeError("Redis write failed")
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"ok": True}, f)
        temp_path = Path(f.name)

    try:
        result = cache.get_or_fetch(temp_path, lambda: {"ok": True})
        assert result == {"ok": True}, "Result must be returned even if cache write fails"
    finally:
        temp_path.unlink()
