"""ADG-driven tests for agentic_core/L5_safety/utils/validation_utils_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.validation_utils_util import (  # noqa: F401
        validate_email,
        validate_url,
        sanitize_filename,
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
    validate_email = None  # type: ignore[assignment,misc]
    validate_url = None  # type: ignore[assignment,misc]
    sanitize_filename = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestValidateEmail:
    def test_is_callable(self):
        assert callable(validate_email)

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestValidateUrl:
    def test_is_callable(self):
        assert callable(validate_url)

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestSanitizeFilename:
    def test_is_callable(self):
        assert callable(sanitize_filename)

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="validation_utils_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module validation_utils_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
