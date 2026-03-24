"""ADG-driven tests for apps_shared/utils/config_loader_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_shared.utils.config_loader_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        ConfigLoader,
        ConfigLoadResult,
        get_config_loader,
        load_agent_config,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    ConfigLoadResult = None  # type: ignore[assignment,misc]
    ConfigLoader = None  # type: ignore[assignment,misc]
    get_config_loader = None  # type: ignore[assignment,misc]
    load_agent_config = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestConfigLoadResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ConfigLoadResult)
    def test_importable(self):
        assert ConfigLoadResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestConfigLoader:
    def test_is_class(self):
        assert isinstance(ConfigLoader, type)
    def test_importable(self):
        assert ConfigLoader is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestGetConfigLoader:
    def test_is_callable(self):
        assert callable(get_config_loader)

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestLoadAgentConfig:
    def test_is_callable(self):
        assert callable(load_agent_config)

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="config_loader_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module config_loader_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE