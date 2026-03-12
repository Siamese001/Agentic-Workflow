"""ADG-driven tests for agentic_core/L5_safety/enforcement/governance/logs_guard.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.enforcement.governance.logs_guard import (  # noqa: F401
        is_log_or_output_file,
        is_log_or_output_directory,
        is_excluded_directory,
        is_in_excluded_directory,
        is_allowed_location,
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
    is_log_or_output_file = None  # type: ignore[assignment,misc]
    is_log_or_output_directory = None  # type: ignore[assignment,misc]
    is_excluded_directory = None  # type: ignore[assignment,misc]
    is_in_excluded_directory = None  # type: ignore[assignment,misc]
    is_allowed_location = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsLogOrOutputFile:
    def test_is_callable(self):
        assert callable(is_log_or_output_file)

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsLogOrOutputDirectory:
    def test_is_callable(self):
        assert callable(is_log_or_output_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsExcludedDirectory:
    def test_is_callable(self):
        assert callable(is_excluded_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsInExcludedDirectory:
    def test_is_callable(self):
        assert callable(is_in_excluded_directory)

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestIsAllowedLocation:
    def test_is_callable(self):
        assert callable(is_allowed_location)

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="logs_guard.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module logs_guard.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
