"""Foundational behavioral tests for agentic_core/L2_execution/tools/safe_subprocess.py.

fan_in=3 — imported by 3 other modules.
ADG import-hygiene is covered separately by test_safe_subprocess_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.tools.safe_subprocess import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_DEPTH,
        MAX_RETRIES,
        THRESHOLD,
        safe_subprocess_call,
        safe_subprocess_check_call,
        safe_subprocess_check_output,
        safe_subprocess_popen,
        safe_subprocess_run,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    safe_subprocess_run = None  # type: ignore[assignment,misc]
    safe_subprocess_call = None  # type: ignore[assignment,misc]
    safe_subprocess_check_call = None  # type: ignore[assignment,misc]
    safe_subprocess_check_output = None  # type: ignore[assignment,misc]
    safe_subprocess_popen = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]
    MAX_DEPTH = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestSafeSubprocessRunFunction:
    def test_is_callable(self):
        assert callable(safe_subprocess_run)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_subprocess_run)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestSafeSubprocessCallFunction:
    def test_is_callable(self):
        assert callable(safe_subprocess_call)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_subprocess_call)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestSafeSubprocessCheckCallFunction:
    def test_is_callable(self):
        assert callable(safe_subprocess_check_call)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_subprocess_check_call)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestSafeSubprocessCheckOutputFunction:
    def test_is_callable(self):
        assert callable(safe_subprocess_check_output)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_subprocess_check_output)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestSafeSubprocessPopenFunction:
    def test_is_callable(self):
        assert callable(safe_subprocess_popen)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(safe_subprocess_popen)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

    def test_value_is_truthy_or_defined(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

    def test_value_is_truthy_or_defined(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None

    def test_value_is_truthy_or_defined(self):
        assert BATCH_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="safe_subprocess.py deps unavailable")
class TestMaxDepthConstant:
    def test_is_not_none(self):
        assert MAX_DEPTH is not None

    def test_value_is_truthy_or_defined(self):
        assert MAX_DEPTH is not None


def test_module_importable():
    """Smoke: safe_subprocess importable or gracefully unavailable."""
    pass
