"""Tests for EgressProxy - outbound network call proxy and gating."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.egress_proxy import EgressProxy


class TestEgressProxy:
    def test_init_with_allowed_hosts(self):
        proxy = EgressProxy(allowed_hosts=["api.anthropic.com"])
        assert "api.anthropic.com" in proxy.allowed_hosts

    def test_allow_request_to_allowed_host(self):
        proxy = EgressProxy(allowed_hosts=["api.anthropic.com"])
        assert proxy.is_allowed("https://api.anthropic.com/v1/messages") is True

    def test_block_request_to_disallowed_host(self):
        proxy = EgressProxy(allowed_hosts=["api.anthropic.com"])
        assert proxy.is_allowed("https://evil.example.com") is False

    def test_proxy_request_success(self):
        proxy = EgressProxy(allowed_hosts=["api.test.com"])
        client = Mock()
        client.request.return_value = {"status": 200}
        proxy.set_client(client)
        result = proxy.request("GET", "https://api.test.com/x")
        assert result["status"] == 200

    def test_proxy_blocks_disallowed(self):
        proxy = EgressProxy(allowed_hosts=["api.test.com"])
        with pytest.raises(PermissionError):
            proxy.request("GET", "https://blocked.com")

    def test_add_allowed_host(self):
        proxy = EgressProxy(allowed_hosts=[])
        proxy.add_allowed_host("api.new.com")
        assert "api.new.com" in proxy.allowed_hosts

    def test_remove_allowed_host(self):
        proxy = EgressProxy(allowed_hosts=["api.x.com"])
        proxy.remove_allowed_host("api.x.com")
        assert "api.x.com" not in proxy.allowed_hosts

    def test_audit_log(self):
        proxy = EgressProxy(allowed_hosts=["api.test.com"])
        monitor = Mock()
        proxy.set_monitor(monitor)
        client = Mock()
        client.request.return_value = {"status": 200}
        proxy.set_client(client)
        proxy.request("GET", "https://api.test.com/x")
        monitor.log.assert_called()
