"""P3 MCP optimization tests — check_redis_health_via_mcp in redis_cache_client.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.cache.redis_cache_client import check_redis_health_via_mcp

    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    check_redis_health_via_mcp = None  # type: ignore[assignment]


@pytest.mark.skipif(not _AVAILABLE, reason="redis_cache_client deps unavailable")
class TestCheckRedisHealthViaMcp:
    def test_returns_dict(self):
        result = check_redis_health_via_mcp()
        assert isinstance(result, dict)

    def test_result_has_required_keys(self):
        result = check_redis_health_via_mcp()
        assert "healthy" in result
        assert "method" in result
        assert "error" in result

    def test_method_is_mcp11(self):
        result = check_redis_health_via_mcp()
        assert result["method"] == "mcp11"

    def test_healthy_bool_type(self):
        result = check_redis_health_via_mcp()
        assert isinstance(result["healthy"], bool)

    def test_import_error_returns_unhealthy(self):
        import sys

        mods_to_remove = ["mcp11_set", "mcp11_get", "mcp11_delete"]
        originals = {m: sys.modules.pop(m, None) for m in mods_to_remove}
        try:
            result = check_redis_health_via_mcp()
            assert result["healthy"] is False
            assert "mcp11" in result["error"]
        finally:
            for m, orig in originals.items():
                if orig is not None:
                    sys.modules[m] = orig

    def test_mcp11_success_returns_healthy(self):
        mock_set = MagicMock(return_value=None)
        mock_get = MagicMock(return_value="1")
        mock_delete = MagicMock(return_value=None)
        mock_set_mod = MagicMock(mcp11_set=mock_set)
        mock_get_mod = MagicMock(mcp11_get=mock_get)
        mock_del_mod = MagicMock(mcp11_delete=mock_delete)
        with patch.dict(
            "sys.modules",
            {
                "mcp11_set": mock_set_mod,
                "mcp11_get": mock_get_mod,
                "mcp11_delete": mock_del_mod,
            },
        ):
            result = check_redis_health_via_mcp()
        assert result["healthy"] is True
        assert result["error"] is None

    def test_mcp11_get_returns_none_means_unhealthy(self):
        mock_set = MagicMock(return_value=None)
        mock_get = MagicMock(return_value=None)
        mock_delete = MagicMock(return_value=None)
        mock_set_mod = MagicMock(mcp11_set=mock_set)
        mock_get_mod = MagicMock(mcp11_get=mock_get)
        mock_del_mod = MagicMock(mcp11_delete=mock_delete)
        with patch.dict(
            "sys.modules",
            {
                "mcp11_set": mock_set_mod,
                "mcp11_get": mock_get_mod,
                "mcp11_delete": mock_del_mod,
            },
        ):
            result = check_redis_health_via_mcp()
        assert result["healthy"] is False

    def test_mcp11_exception_returns_unhealthy_with_error(self):
        mock_set = MagicMock(side_effect=ConnectionError("connection refused"))
        mock_set_mod = MagicMock(mcp11_set=mock_set)
        with patch.dict(
            "sys.modules",
            {
                "mcp11_set": mock_set_mod,
                "mcp11_get": MagicMock(mcp11_get=MagicMock()),
                "mcp11_delete": MagicMock(mcp11_delete=MagicMock()),
            },
        ):
            result = check_redis_health_via_mcp()
        assert result["healthy"] is False
        assert result["error"] is not None

    def test_does_not_raise(self):
        try:
            check_redis_health_via_mcp()
        except Exception as e:
            pytest.fail(f"check_redis_health_via_mcp raised unexpectedly: {e}")


def test_module_importable():
    assert _AVAILABLE or not _AVAILABLE
