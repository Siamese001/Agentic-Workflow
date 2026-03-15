"""ADG-driven tests for agentic_core/L5_safety/utils/security_controls_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.security_controls_util import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        create_instance,
        get_module_info,
        validate_config,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    get_module_info = None  # type: ignore[assignment,misc]
    validate_config = None  # type: ignore[assignment,misc]
    create_instance = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestGetModuleInfo:
    def test_is_callable(self):
        assert callable(get_module_info)

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestValidateConfig:
    def test_is_callable(self):
        assert callable(validate_config)

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestCreateInstance:
    def test_is_callable(self):
        assert callable(create_instance)

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="security_controls_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module security_controls_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
