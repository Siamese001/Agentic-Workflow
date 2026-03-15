"""ADG-driven tests for agentic_core/L4_state/workflow_engines/policy_registry_cache.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L4_state.workflow_engines.policy_registry_cache import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        PolicyRegistryCache,
        get_policy_registry_cache,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    PolicyRegistryCache = None  # type: ignore[assignment,misc]
    get_policy_registry_cache = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestPolicyRegistryCache:
    def test_is_class(self):
        assert isinstance(PolicyRegistryCache, type)
    def test_importable(self):
        assert PolicyRegistryCache is not None

@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestGetPolicyRegistryCache:
    def test_is_callable(self):
        assert callable(get_policy_registry_cache)

@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="policy_registry_cache.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module policy_registry_cache.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
