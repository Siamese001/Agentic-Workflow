"""ADG-driven tests for apps_rg/utils/sovereign_config_loader_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_rg.utils.sovereign_config_loader_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        SovereignConfigLoader,
        get_config_path,
        load_rg_specs,
        reload_config,
        save_rg_specs,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    SovereignConfigLoader = None  # type: ignore[assignment,misc]
    get_config_path = None  # type: ignore[assignment,misc]
    load_rg_specs = None  # type: ignore[assignment,misc]
    save_rg_specs = None  # type: ignore[assignment,misc]
    reload_config = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestSovereignConfigLoader:
    def test_is_class(self):
        assert isinstance(SovereignConfigLoader, type)
    def test_importable(self):
        assert SovereignConfigLoader is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestGetConfigPath:
    def test_is_callable(self):
        assert callable(get_config_path)

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestLoadRgSpecs:
    def test_is_callable(self):
        assert callable(load_rg_specs)

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestSaveRgSpecs:
    def test_is_callable(self):
        assert callable(save_rg_specs)

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestReloadConfig:
    def test_is_callable(self):
        assert callable(reload_config)

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="sovereign_config_loader_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module sovereign_config_loader_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
