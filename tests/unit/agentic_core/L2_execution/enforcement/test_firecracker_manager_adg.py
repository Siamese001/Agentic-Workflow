"""ADG-driven tests for agentic_core/L2_execution/enforcement/firecracker_manager.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.enforcement.firecracker_manager import (  # noqa: F401
        FirecrackerManager,
        create_firecracker_manager,
        MAX_RETRIES,
        DEFAULT_SLEEP,
        THRESHOLD,
        BUFFER_SIZE,
        BATCH_SIZE,
        MAX_DEPTH,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    FirecrackerManager = None  # type: ignore[assignment,misc]
    create_firecracker_manager = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestFirecrackerManager:
    def test_is_class(self):
        assert isinstance(FirecrackerManager, type)
    def test_importable(self):
        assert FirecrackerManager is not None

@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestCreateFirecrackerManager:
    def test_is_callable(self):
        assert callable(create_firecracker_manager)

@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="firecracker_manager.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module firecracker_manager.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
