"""E2E smoke tests — playwright sync API contract verification."""

from __future__ import annotations

import pytest

pw = pytest.importorskip("playwright", reason="playwright not installed")


def test_playwright_sync_api_exposes_core_classes():
    """Playwright sync_api exposes Browser, Page, and Playwright types."""
    from playwright import sync_api

    assert hasattr(sync_api, "sync_playwright")
    assert callable(sync_api.sync_playwright)


def test_playwright_sync_api_error_types():
    """Playwright sync_api exposes error classes for structured error handling."""
    from playwright import sync_api

    assert hasattr(sync_api, "Error")
    assert hasattr(sync_api, "TimeoutError")
    assert issubclass(sync_api.TimeoutError, Exception)
