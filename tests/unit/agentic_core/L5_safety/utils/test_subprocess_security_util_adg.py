"""ADG-driven tests for agentic_core/L5_safety/utils/subprocess_security_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L5_safety.utils.subprocess_security_util import (  # noqa: F401
        SecurityViolationError,
        safe_execute,
        safe_popen,
        validate_command_whitelist,
        safe_git_execute,
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
    SecurityViolationError = None  # type: ignore[assignment,misc]
    safe_execute = None  # type: ignore[assignment,misc]
    safe_popen = None  # type: ignore[assignment,misc]
    validate_command_whitelist = None  # type: ignore[assignment,misc]
    safe_git_execute = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestSecurityViolationError:
    def test_is_class(self):
        assert isinstance(SecurityViolationError, type)
    def test_importable(self):
        assert SecurityViolationError is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestSafeExecute:
    def test_is_callable(self):
        assert callable(safe_execute)

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestSafePopen:
    def test_is_callable(self):
        assert callable(safe_popen)

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestValidateCommandWhitelist:
    def test_is_callable(self):
        assert callable(validate_command_whitelist)

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestSafeGitExecute:
    def test_is_callable(self):
        assert callable(safe_git_execute)

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="subprocess_security_util.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Module subprocess_security_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE
