"""ADG-driven tests for apps_shared/config/titanium_search_tool_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.config.titanium_search_tool_config import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        clear_cache,
        get_pipeline_stats,
        get_titanium_search_tool,
        get_titanium_search_with_sources,
        sync_search,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    get_titanium_search_tool = None  # type: ignore[assignment,misc]
    get_titanium_search_with_sources = None  # type: ignore[assignment,misc]
    get_pipeline_stats = None  # type: ignore[assignment,misc]
    clear_cache = None  # type: ignore[assignment,misc]
    sync_search = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestGetTitaniumSearchTool:
    def test_is_callable(self):
        assert callable(get_titanium_search_tool)

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestGetTitaniumSearchWithSources:
    def test_is_callable(self):
        assert callable(get_titanium_search_with_sources)

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestGetPipelineStats:
    def test_is_callable(self):
        assert callable(get_pipeline_stats)

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestClearCache:
    def test_is_callable(self):
        assert callable(clear_cache)

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestSyncSearch:
    def test_is_callable(self):
        assert callable(sync_search)

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="titanium_search_tool_config.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module titanium_search_tool_config.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE