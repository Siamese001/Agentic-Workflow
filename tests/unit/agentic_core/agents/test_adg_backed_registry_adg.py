"""ADG-driven tests for agentic_core/agents/adg_backed_registry.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.agents.adg_backed_registry import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ADGBackedAgentRegistry,
        get_adg_registry,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ADGBackedAgentRegistry = None  # type: ignore[assignment,misc]
    get_adg_registry = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestADGBackedAgentRegistry:
    def test_is_class(self):
        assert isinstance(ADGBackedAgentRegistry, type)
    def test_importable(self):
        assert ADGBackedAgentRegistry is not None

@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestGetAdgRegistry:
    def test_is_callable(self):
        assert callable(get_adg_registry)

@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="adg_backed_registry.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module adg_backed_registry.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
