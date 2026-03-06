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


# ---------------------------------------------------------------------------
# §5  UPDATED §4 GAPS — TOOL EMBEDDING CACHE
# ---------------------------------------------------------------------------


def test_tool_embedding_cache_same_tools_identical_key_twice():
    """Same tool set must produce identical fingerprint on two successive calls (§4:124-125)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "tool1", "description": "desc1", "tags": ["t1"]}]

    cache.get_or_fetch(tools, lambda: ([[0.1]], ["tool1"]))
    key1 = fake.set_json.call_args[0][0]

    fake.reset_mock()
    cache.get_or_fetch(tools, lambda: ([[0.1]], ["tool1"]))
    key2 = fake.set_json.call_args[0][0]

    assert key1 == key2, "Same tool set must produce identical fingerprint on repeat calls"


def test_tool_embedding_cache_input_order_invariant():
    """Tool set in different input order must produce identical fingerprint (§4:126, normalization)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)

    tools_ab = [
        {"name": "alpha", "description": "d1", "tags": []},
        {"name": "beta", "description": "d2", "tags": []},
    ]
    tools_ba = [
        {"name": "beta", "description": "d2", "tags": []},
        {"name": "alpha", "description": "d1", "tags": []},
    ]

    cache.get_or_fetch(tools_ab, lambda: ([[0.1], [0.2]], ["alpha", "beta"]))
    key_ab = fake.set_json.call_args[0][0]

    fake.reset_mock()
    # Provide warm cache miss again
    fake.get_json.return_value = None
    cache.get_or_fetch(tools_ba, lambda: ([[0.2], [0.1]], ["beta", "alpha"]))
    key_ba = fake.set_json.call_args[0][0]

    assert key_ab == key_ba, "Tool input order must not affect fingerprint"


def test_tool_embedding_cache_near_miss_different_description_distinct_key():
    """Tool with same name but different description must produce distinct fingerprint (§4:127)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)

    tools_v1 = [{"name": "tool1", "description": "version-one", "tags": []}]
    tools_v2 = [{"name": "tool1", "description": "version-two", "tags": []}]

    cache.get_or_fetch(tools_v1, lambda: ([[0.1]], ["tool1"]))
    key1 = fake.set_json.call_args[0][0]

    fake.reset_mock()
    cache.get_or_fetch(tools_v2, lambda: ([[0.2]], ["tool1"]))
    key2 = fake.set_json.call_args[0][0]

    assert key1 != key2, "Near-miss: same name + different description must give distinct key"


def test_tool_embedding_cache_replay_warm_get_json_never_called():
    """replay_mode=True with warm cache must NEVER call get_json (§4:155-156 matrix: warm×replay)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"embeddings": [[0.9]], "tool_names": ["stale"]}
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "fresh", "description": "d", "tags": []}]

    embeddings, names = cache.get_or_fetch(tools, lambda: ([[0.1]], ["fresh"]), replay_mode=True)
    fake.get_json.assert_not_called()
    fake.set_json.assert_not_called()
    assert embeddings == [[0.1]]


def test_tool_embedding_cache_hit_side_effect_envelope():
    """On cache hit: get_json once, set_json never, fetch never (§4:134-138)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"embeddings": [[0.5]], "tool_names": ["cached_tool"]}
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "cached_tool", "description": "d", "tags": []}]

    fetch_called = [False]

    def fetch():
        fetch_called[0] = True
        return [[0.5]], ["cached_tool"]

    cache.get_or_fetch(tools, fetch)
    assert not fetch_called[0], "fetch must not be called on cache hit"
    fake.get_json.assert_called_once()
    fake.set_json.assert_not_called()


def test_tool_embedding_cache_empty_tools_no_cache_side_effect():
    """ValueError from empty tools must propagate before any cache operation (§4:131-133)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)

    with pytest.raises(ValueError):
        cache.get_or_fetch([], lambda: ([], []))

    fake.get_json.assert_not_called()
    fake.set_json.assert_not_called()


def test_tool_embedding_cache_malformed_tool_missing_name_key():
    """Tool dict missing 'name' key must still produce a stable (empty-name) fingerprint (§4:116-117)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)
    # Malformed-but-plausible: tool has description but no name
    tools = [{"description": "no-name-tool", "tags": []}]

    result_embeddings, result_names = cache.get_or_fetch(tools, lambda: ([[0.3]], ["no-name-tool"]))
    assert result_embeddings == [[0.3]]
    fake.set_json.assert_called_once()


def test_tool_embedding_cache_stale_path_refetch_on_miss():
    """After TTL expiry simulation (get_json→None), fetch and re-cache (§4:179-183)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "t", "description": "d", "tags": []}]
    call_count = [0]

    def fetch():
        call_count[0] += 1
        return [[0.1]], ["t"]

    cache.get_or_fetch(tools, fetch)
    assert call_count[0] == 1

    # Simulate TTL expiry
    fake.get_json.return_value = None
    fake.reset_mock()
    cache.get_or_fetch(tools, fetch)
    assert call_count[0] == 2
    assert fake.set_json.call_count == 1


def test_tool_embedding_cache_broad_except_does_not_swallow_fetch_error():
    """Broad except on cache read must not swallow errors from fetch (§4:146-148)."""
    from agentic_core.cache.tool_embedding_cache import ToolEmbeddingCache

    fake = _make_fake_cache()
    fake.get_json.return_value = None
    cache = ToolEmbeddingCache(cache=fake)
    tools = [{"name": "t", "description": "d", "tags": []}]

    with pytest.raises(RuntimeError, match="fetch-sentinel"):
        cache.get_or_fetch(tools, lambda: (_ for _ in ()).throw(RuntimeError("fetch-sentinel")))


# ---------------------------------------------------------------------------
# §6  UPDATED §4 GAPS — SCHEMA VALIDATOR CACHE
# ---------------------------------------------------------------------------


def test_schema_validator_cache_same_schema_identical_key_twice():
    """Same schema must produce identical hash on two successive calls (§4:124-125)."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    cache = SchemaValidatorCache(cache=fake)
    schema = {"type": "object", "properties": {"x": {"type": "integer"}}}

    cache.get_or_fetch(schema, lambda: {"ok": 1})
    key1 = fake.set_json.call_args[0][0]

    fake.reset_mock()
    cache.get_or_fetch(schema, lambda: {"ok": 1})
    key2 = fake.set_json.call_args[0][0]

    assert key1 == key2


def test_schema_validator_cache_key_order_invariant():
    """Schema dicts with same keys in different order must produce identical hash (§4:126)."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    cache = SchemaValidatorCache(cache=fake)

    # Python dicts preserve insertion order; JSON sort_keys normalises them
    schema_ab = {"b": 2, "a": 1}
    schema_ba = {"a": 1, "b": 2}

    cache.get_or_fetch(schema_ab, lambda: {"v": 1})
    key_ab = fake.set_json.call_args[0][0]

    fake.reset_mock()
    fake.get_json.return_value = None
    cache.get_or_fetch(schema_ba, lambda: {"v": 1})
    key_ba = fake.set_json.call_args[0][0]

    assert key_ab == key_ba, "Key ordering must not affect schema hash"


def test_schema_validator_cache_near_miss_added_field_distinct_key():
    """Schema with one extra field must produce distinct hash from original (§4:127)."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    cache = SchemaValidatorCache(cache=fake)

    schema1 = {"type": "string"}
    schema2 = {"type": "string", "minLength": 1}

    cache.get_or_fetch(schema1, lambda: {"v": 1})
    key1 = fake.set_json.call_args[0][0]

    fake.reset_mock()
    cache.get_or_fetch(schema2, lambda: {"v": 2})
    key2 = fake.set_json.call_args[0][0]

    assert key1 != key2


def test_schema_validator_cache_replay_warm_get_json_never_called():
    """replay_mode=True with warm cache must NEVER call get_json (§4:155-156)."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"stale": True}
    cache = SchemaValidatorCache(cache=fake)

    result = cache.get_or_fetch({"type": "integer"}, lambda: {"fresh": True}, replay_mode=True)
    fake.get_json.assert_not_called()
    fake.set_json.assert_not_called()
    assert result == {"fresh": True}


def test_schema_validator_cache_hit_side_effect_envelope():
    """On cache hit: get_json once, set_json never, fetch never (§4:134-138)."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"cached": True}
    cache = SchemaValidatorCache(cache=fake)

    fetch_called = [False]

    def fetch():
        fetch_called[0] = True
        return {"fresh": True}

    cache.get_or_fetch({"type": "string"}, fetch)
    assert not fetch_called[0]
    fake.get_json.assert_called_once()
    fake.set_json.assert_not_called()


def test_schema_validator_cache_empty_schema_no_cache_side_effect():
    """ValueError from empty schema must propagate before any cache operation (§4:131-133)."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    cache = SchemaValidatorCache(cache=fake)

    with pytest.raises(ValueError):
        cache.get_or_fetch({}, lambda: None)

    fake.get_json.assert_not_called()
    fake.set_json.assert_not_called()


def test_schema_validator_cache_broad_except_does_not_swallow_fetch_error():
    """Broad except on cache read must not swallow errors from fetch (§4:146-148)."""
    from agentic_core.cache.schema_validator_cache import SchemaValidatorCache

    fake = _make_fake_cache()
    fake.get_json.return_value = None
    cache = SchemaValidatorCache(cache=fake)

    with pytest.raises(KeyError, match="fetch-sentinel"):
        cache.get_or_fetch({"type": "object"}, lambda: (_ for _ in ()).throw(KeyError("fetch-sentinel")))


# ---------------------------------------------------------------------------
# §7  UPDATED §4 GAPS — POLICY REGISTRY CACHE
# ---------------------------------------------------------------------------


def test_policy_registry_cache_same_id_identical_key_twice():
    """Same policy ID must produce identical cache key on two successive calls (§4:124-125)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)

    cache.get_or_fetch("GOV-001", lambda: {"id": "GOV-001"})
    key1 = fake.set_json.call_args[0][0]

    fake.reset_mock()
    cache.get_or_fetch("GOV-001", lambda: {"id": "GOV-001"})
    key2 = fake.set_json.call_args[0][0]

    assert key1 == key2


def test_policy_registry_cache_distinct_ids_distinct_keys():
    """Two different policy IDs must produce distinct cache keys (§4:127)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)

    cache.get_or_fetch("GOV-001", lambda: {"id": "GOV-001"})
    key1 = fake.set_json.call_args[0][0]

    fake.reset_mock()
    cache.get_or_fetch("GOV-002", lambda: {"id": "GOV-002"})
    key2 = fake.set_json.call_args[0][0]

    assert key1 != key2


def test_policy_registry_cache_replay_warm_get_json_never_called():
    """replay_mode=True with warm cache must NEVER call get_json (§4:155-156)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"stale": True}
    cache = PolicyRegistryCache(cache=fake)

    result = cache.get_or_fetch("GOV-005", lambda: {"fresh": True}, replay_mode=True)
    fake.get_json.assert_not_called()
    fake.set_json.assert_not_called()
    assert result == {"fresh": True}


def test_policy_registry_cache_hit_side_effect_envelope():
    """On cache hit: get_json once, set_json never, fetch never (§4:134-138)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"id": "GOV-001", "cached": True}
    cache = PolicyRegistryCache(cache=fake)

    fetch_called = [False]

    def fetch():
        fetch_called[0] = True
        return {"id": "GOV-001"}

    cache.get_or_fetch("GOV-001", fetch)
    assert not fetch_called[0]
    fake.get_json.assert_called_once()
    fake.set_json.assert_not_called()


def test_policy_registry_cache_empty_id_no_cache_side_effect():
    """ValueError from empty policy ID must propagate before any cache op (§4:131-133)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)

    with pytest.raises(ValueError):
        cache.get_or_fetch("", lambda: {})

    fake.get_json.assert_not_called()
    fake.set_json.assert_not_called()


def test_policy_registry_cache_whitespace_id_no_cache_side_effect():
    """Whitespace-only policy ID must raise before any cache op (§4:107-108)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)

    with pytest.raises(ValueError):
        cache.get_or_fetch("   ", lambda: {})

    fake.get_json.assert_not_called()
    fake.set_json.assert_not_called()


def test_policy_registry_cache_stale_path_refetch_on_miss():
    """After TTL expiry simulation, fetch and re-cache (§4:179-183)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    cache = PolicyRegistryCache(cache=fake)
    call_count = [0]

    def fetch():
        call_count[0] += 1
        return {"id": "GOV-001"}

    cache.get_or_fetch("GOV-001", fetch)
    assert call_count[0] == 1

    fake.get_json.return_value = None
    fake.reset_mock()
    cache.get_or_fetch("GOV-001", fetch)
    assert call_count[0] == 2
    assert fake.set_json.call_count == 1


def test_policy_registry_cache_broad_except_does_not_swallow_fetch_error():
    """Broad except on cache read must not swallow errors from fetch (§4:146-148)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    fake.get_json.return_value = None
    cache = PolicyRegistryCache(cache=fake)

    with pytest.raises(LookupError, match="fetch-sentinel"):
        cache.get_or_fetch("GOV-001", lambda: (_ for _ in ()).throw(LookupError("fetch-sentinel")))


def test_policy_registry_cache_invalidate_exception_does_not_propagate():
    """invalidate must swallow cache.delete exceptions without propagating (§4:141-144)."""
    from agentic_core.cache.policy_registry_cache import PolicyRegistryCache

    fake = _make_fake_cache()
    fake.delete.side_effect = RuntimeError("Redis unavailable")
    cache = PolicyRegistryCache(cache=fake)

    cache.invalidate("GOV-001")  # Must not raise


# ---------------------------------------------------------------------------
# §8  UPDATED §4 GAPS — CONFIG FILE CACHE
# ---------------------------------------------------------------------------


def test_config_file_cache_same_file_identical_key_twice():
    """Same file content must produce identical cache key on two successive calls (§4:124-125)."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"v": 1}, f)
        temp_path = Path(f.name)

    try:
        cache.get_or_fetch(temp_path, lambda: {"v": 1})
        key1 = fake.set_json.call_args[0][0]

        fake.reset_mock()
        cache.get_or_fetch(temp_path, lambda: {"v": 1})
        key2 = fake.set_json.call_args[0][0]

        assert key1 == key2
    finally:
        temp_path.unlink()


def test_config_file_cache_replay_warm_get_json_never_called():
    """replay_mode=True with warm cache must NEVER call get_json (§4:155-156)."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"stale": True}
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"fresh": True}, f)
        temp_path = Path(f.name)

    try:
        result = cache.get_or_fetch(temp_path, lambda: {"fresh": True}, replay_mode=True)
        fake.get_json.assert_not_called()
        fake.set_json.assert_not_called()
        assert result == {"fresh": True}
    finally:
        temp_path.unlink()


def test_config_file_cache_hit_side_effect_envelope():
    """On cache hit: get_json once, set_json never, fetch never (§4:134-138)."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    fake.get_json.return_value = {"cached": True}
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"cached": True}, f)
        temp_path = Path(f.name)

    try:
        fetch_called = [False]

        def fetch():
            fetch_called[0] = True
            return {"cached": True}

        cache.get_or_fetch(temp_path, fetch)
        assert not fetch_called[0]
        fake.get_json.assert_called_once()
        fake.set_json.assert_not_called()
    finally:
        temp_path.unlink()


def test_config_file_cache_file_not_found_no_set_json_side_effect():
    """FileNotFoundError must propagate before any set_json call (§4:131-133)."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    cache = ConfigFileCache(cache=fake)

    with pytest.raises(FileNotFoundError):
        cache.get_or_fetch(Path("/no/such/config.yaml"), lambda: {})

    fake.set_json.assert_not_called()


def test_config_file_cache_stale_path_refetch_on_miss():
    """After TTL expiry simulation, fetch and re-cache (§4:179-183)."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"v": 1}, f)
        temp_path = Path(f.name)

    try:
        call_count = [0]

        def fetch():
            call_count[0] += 1
            return {"v": 1}

        cache.get_or_fetch(temp_path, fetch)
        assert call_count[0] == 1

        fake.get_json.return_value = None
        fake.reset_mock()
        cache.get_or_fetch(temp_path, fetch)
        assert call_count[0] == 2
        assert fake.set_json.call_count == 1
    finally:
        temp_path.unlink()


def test_config_file_cache_broad_except_does_not_swallow_fetch_error():
    """Broad except on cache read must not swallow errors from fetch (§4:146-148)."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    fake.get_json.return_value = None
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({}, f)
        temp_path = Path(f.name)

    try:
        with pytest.raises(OSError, match="fetch-sentinel"):
            cache.get_or_fetch(temp_path, lambda: (_ for _ in ()).throw(OSError("fetch-sentinel")))
    finally:
        temp_path.unlink()


def test_config_file_cache_distinct_files_distinct_keys():
    """Two files with different content must produce distinct cache keys (§4:127)."""
    from agentic_core.cache.config_file_cache import ConfigFileCache

    fake = _make_fake_cache()
    cache = ConfigFileCache(cache=fake)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f1:
        json.dump({"a": 1}, f1)
        path1 = Path(f1.name)

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f2:
        json.dump({"a": 2}, f2)
        path2 = Path(f2.name)

    try:
        cache.get_or_fetch(path1, lambda: {"a": 1})
        key1 = fake.set_json.call_args[0][0]

        fake.reset_mock()
        cache.get_or_fetch(path2, lambda: {"a": 2})
        key2 = fake.set_json.call_args[0][0]

        assert key1 != key2
    finally:
        path1.unlink()
        path2.unlink()
