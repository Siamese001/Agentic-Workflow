"""Tests for NetworkEgressGuard - egress traffic policy enforcement."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.network_egress_guard import NetworkEgressGuard


class TestNetworkEgressGuard:
    def test_init_with_policy(self):
        g = NetworkEgressGuard(policy={"allowed_hosts": ["api.test.com"]})
        assert g.policy is not None

    def test_validate_allowed_egress(self):
        g = NetworkEgressGuard(policy={"allowed_hosts": ["api.test.com"]})
        result = g.validate({"host": "api.test.com", "port": 443})
        assert result.valid is True

    def test_validate_blocked_egress(self):
        g = NetworkEgressGuard(policy={"allowed_hosts": ["api.test.com"]})
        result = g.validate({"host": "evil.com", "port": 443})
        assert result.valid is False

    def test_enforce_allowed(self):
        g = NetworkEgressGuard(policy={"allowed_hosts": ["api.test.com"]})
        g.enforce({"host": "api.test.com", "port": 443})

    def test_enforce_blocked(self):
        g = NetworkEgressGuard(policy={"allowed_hosts": ["api.test.com"]})
        with pytest.raises(PermissionError):
            g.enforce({"host": "evil.com", "port": 443})

    def test_port_restriction(self):
        g = NetworkEgressGuard(policy={
            "allowed_hosts": ["api.test.com"],
            "allowed_ports": [443]
        })
        result = g.validate({"host": "api.test.com", "port": 80})
        assert result.valid is False

    def test_update_policy(self):
        g = NetworkEgressGuard(policy={"allowed_hosts": []})
        g.update_policy({"allowed_hosts": ["api.x.com"]})
        assert "api.x.com" in g.policy["allowed_hosts"]

    def test_get_violations(self):
        g = NetworkEgressGuard(policy={"allowed_hosts": ["api.test.com"]})
        try:
            g.enforce({"host": "evil.com", "port": 443})
        except PermissionError:
            pass
        violations = g.get_violations()
        assert len(violations) >= 1
