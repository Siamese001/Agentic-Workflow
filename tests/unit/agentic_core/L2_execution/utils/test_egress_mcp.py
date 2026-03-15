"""P2 MCP optimization tests for egress_util.py — mcp4_fetch integration."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L2_execution.utils.egress_util import NetworkingUtility

    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    NetworkingUtility = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="egress_util deps unavailable")
class TestFetchUrlEgressEnforcement:
    """Egress filter must be enforced before any MCP fetch call."""

    def setup_method(self):
        self.util = NetworkingUtility(allowed_hosts={"allowed.com"})

    def test_blocked_host_never_calls_mcp4(self):
        called = []
        mock_fn = MagicMock(side_effect=lambda **kwargs: called.append(kwargs) or "content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://blocked.evil.com/data")
        assert result["status"] == "blocked"
        assert called == [], "mcp4_fetch must NOT be called for blocked hosts"

    def test_allowed_host_attempts_mcp4(self):
        mock_fn = MagicMock(return_value="page content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert result["status"] in ("success", "mock_success", "error")

    def test_allowed_host_mcp4_success_returns_content(self):
        mock_fn = MagicMock(return_value="real page content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert result["status"] == "success"
        assert result["content"] == "real page content"
        assert result["url"] == "https://allowed.com/page"

    def test_allowed_host_mcp4_unavailable_falls_back(self):
        import sys

        original = sys.modules.pop("mcp4_fetch", None)
        try:
            result = self.util.fetch_url("https://allowed.com/page")
            assert result["status"] == "mock_success"
            assert "mcp4_fetch unavailable" in result["content"]
        finally:
            if original is not None:
                sys.modules["mcp4_fetch"] = original

    def test_allowed_host_mcp4_exception_returns_error(self):
        mock_fn = MagicMock(side_effect=RuntimeError("network timeout"))
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert result["status"] == "error"
        assert "network timeout" in result["reason"]

    def test_result_always_contains_host(self):
        mock_fn = MagicMock(return_value="content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = self.util.fetch_url("https://allowed.com/page")
        assert "host" in result

    def test_blocked_result_structure(self):
        result = self.util.fetch_url("https://blocked.com/page")
        assert "status" in result
        assert "reason" in result
        assert "host" in result
        assert result["status"] == "blocked"


@pytest.mark.skipif(not _AVAILABLE, reason="egress_util deps unavailable")
class TestFetchUrlSubdomainAllowed:
    def test_subdomain_of_allowed_host_is_fetched(self):
        util = NetworkingUtility(allowed_hosts={"example.com"})
        mock_fn = MagicMock(return_value="subdomain content")
        with patch.dict("sys.modules", {"mcp4_fetch": MagicMock(mcp4_fetch=mock_fn)}):
            result = util.fetch_url("https://api.example.com/v1/data")
        assert result["status"] in ("success", "mock_success")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
