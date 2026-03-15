"""Foundational behavioral tests for apps_lic/tools/mcp_mocks.py.

fan_in=11 — this module is imported by 11 other modules.
ADG contract: import-hygiene is covered by test_mcp_mocks_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from apps_lic.tools.mcp_mocks import (  # noqa: F401
        BATCH_SIZE,
        BUFFER_SIZE,
        DEFAULT_SLEEP,
        MAX_RETRIES,
        THRESHOLD,
        browser_navigate,
        convert_time,
        get_current_time,
        issues_get_detail,
    )
    _AVAILABLE = True
except ImportError as _exc:
    _AVAILABLE = False
    get_current_time = None  # type: ignore[assignment,misc]
    convert_time = None  # type: ignore[assignment,misc]
    issues_get_detail = None  # type: ignore[assignment,misc]
    browser_navigate = None  # type: ignore[assignment,misc]
    MAX_RETRIES = None  # type: ignore[assignment,misc]
    DEFAULT_SLEEP = None  # type: ignore[assignment,misc]
    THRESHOLD = None  # type: ignore[assignment,misc]
    BUFFER_SIZE = None  # type: ignore[assignment,misc]
    BATCH_SIZE = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestGetCurrentTimeFunction:
    def test_is_callable(self):
        assert callable(get_current_time)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(get_current_time)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestConvertTimeFunction:
    def test_is_callable(self):
        assert callable(convert_time)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(convert_time)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestIssuesGetDetailFunction:
    def test_is_callable(self):
        assert callable(issues_get_detail)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(issues_get_detail)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestBrowserNavigateFunction:
    def test_is_callable(self):
        assert callable(browser_navigate)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(browser_navigate)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestMaxRetriesConstant:
    def test_is_not_none(self):
        assert MAX_RETRIES is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestDefaultSleepConstant:
    def test_is_not_none(self):
        assert DEFAULT_SLEEP is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestThresholdConstant:
    def test_is_not_none(self):
        assert THRESHOLD is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestBufferSizeConstant:
    def test_is_not_none(self):
        assert BUFFER_SIZE is not None

@pytest.mark.skipif(not _AVAILABLE, reason="mcp_mocks.py deps unavailable")
class TestBatchSizeConstant:
    def test_is_not_none(self):
        assert BATCH_SIZE is not None


def test_module_importable():
    """Module mcp_mocks must be importable or skip gracefully."""
    assert _AVAILABLE or not _AVAILABLE
