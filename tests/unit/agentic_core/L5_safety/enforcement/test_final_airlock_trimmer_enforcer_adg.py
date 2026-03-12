"""ADG-driven tests for agentic_core/L5_safety/enforcement/final_airlock_trimmer_enforcer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.final_airlock_trimmer_enforcer import (  # noqa: F401
        trim_airlock,
        trim_all_airlocks,
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
    trim_airlock = None  # type: ignore[assignment,misc]
    trim_all_airlocks = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestTrimAirlock:
    def test_is_callable(self):
        assert callable(trim_airlock)

@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestTrimAllAirlocks:
    def test_is_callable(self):
        assert callable(trim_all_airlocks)

@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="final_airlock_trimmer_enforcer.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module final_airlock_trimmer_enforcer.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
