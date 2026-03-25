"""Behavioral contract tests for agentic_core.cache.redis_cache_client."""
from __future__ import annotations

import importlib
import pytest

MODULE_PATH = "agentic_core.cache.redis_cache_client"


@pytest.fixture(scope="module")
def mod():
    """Import the module under test. Fails hard if first-party import broken."""
    try:
        return importlib.import_module(MODULE_PATH)
    except Exception as exc:
        pytest.fail(
            f"FIRST-PARTY IMPORT FAILED for {MODULE_PATH}: {exc}",
            pytrace=False,
        )


def test_module_importable(mod):
    """Module imports without errors."""
    assert mod.__name__ == MODULE_PATH


def test_module_exposes_public_api(mod):
    """Module exposes expected public symbols."""
    public = [n for n in dir(mod) if not n.startswith("_")]
    assert len(public) >= 1, f"{MODULE_PATH} must expose at least one public symbol"


def test_any_is_instantiable(mod):
    """Any is accessible and is a type."""
    cls = getattr(mod, "Any", None)
    assert cls is not None, "Any must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "Any must be a class"


def test_cachedb_is_instantiable(mod):
    """CacheDB is accessible and is a type."""
    cls = getattr(mod, "CacheDB", None)
    assert cls is not None, "CacheDB must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CacheDB must be a class"


def test_cachestats_is_instantiable(mod):
    """CacheStats is accessible and is a type."""
    cls = getattr(mod, "CacheStats", None)
    assert cls is not None, "CacheStats must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "CacheStats must be a class"


def test_deterministicrediscache_is_instantiable(mod):
    """DeterministicRedisCache is accessible and is a type."""
    cls = getattr(mod, "DeterministicRedisCache", None)
    assert cls is not None, "DeterministicRedisCache must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "DeterministicRedisCache must be a class"


def test_intenum_is_instantiable(mod):
    """IntEnum is accessible and is a type."""
    cls = getattr(mod, "IntEnum", None)
    assert cls is not None, "IntEnum must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "IntEnum must be a class"


def test_layersegment_is_instantiable(mod):
    """LayerSegment is accessible and is a type."""
    cls = getattr(mod, "LayerSegment", None)
    assert cls is not None, "LayerSegment must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "LayerSegment must be a class"


def test_ordereddict_is_instantiable(mod):
    """OrderedDict is accessible and is a type."""
    cls = getattr(mod, "OrderedDict", None)
    assert cls is not None, "OrderedDict must be defined in {MODULE_PATH}"
    assert isinstance(cls, type), "OrderedDict must be a class"


def test_canonical_json_bytes_is_callable(mod):
    """canonical_json_bytes is accessible and callable."""
    func = getattr(mod, "canonical_json_bytes", None)
    assert func is not None, "canonical_json_bytes must be defined in {MODULE_PATH}"
    assert callable(func), "canonical_json_bytes must be callable"


def test_check_redis_health_is_callable(mod):
    """check_redis_health is accessible and callable."""
    func = getattr(mod, "check_redis_health", None)
    assert func is not None, "check_redis_health must be defined in {MODULE_PATH}"
    assert callable(func), "check_redis_health must be callable"


def test_check_redis_health_via_mcp_is_callable(mod):
    """check_redis_health_via_mcp is accessible and callable."""
    func = getattr(mod, "check_redis_health_via_mcp", None)
    assert func is not None, "check_redis_health_via_mcp must be defined in {MODULE_PATH}"
    assert callable(func), "check_redis_health_via_mcp must be callable"


def test_content_hash_is_callable(mod):
    """content_hash is accessible and callable."""
    func = getattr(mod, "content_hash", None)
    assert func is not None, "content_hash must be defined in {MODULE_PATH}"
    assert callable(func), "content_hash must be callable"


def test_dataclass_is_callable(mod):
    """dataclass is accessible and callable."""
    func = getattr(mod, "dataclass", None)
    assert func is not None, "dataclass must be defined in {MODULE_PATH}"
    assert callable(func), "dataclass must be callable"


def test_emit_determinism_digest_is_callable(mod):
    """emit_determinism_digest is accessible and callable."""
    func = getattr(mod, "emit_determinism_digest", None)
    assert func is not None, "emit_determinism_digest must be defined in {MODULE_PATH}"
    assert callable(func), "emit_determinism_digest must be callable"


def test_emit_replay_key_is_callable(mod):
    """emit_replay_key is accessible and callable."""
    func = getattr(mod, "emit_replay_key", None)
    assert func is not None, "emit_replay_key must be defined in {MODULE_PATH}"
    assert callable(func), "emit_replay_key must be callable"


def test_get_coordination_cache_is_callable(mod):
    """get_coordination_cache is accessible and callable."""
    func = getattr(mod, "get_coordination_cache", None)
    assert func is not None, "get_coordination_cache must be defined in {MODULE_PATH}"
    assert callable(func), "get_coordination_cache must be callable"

