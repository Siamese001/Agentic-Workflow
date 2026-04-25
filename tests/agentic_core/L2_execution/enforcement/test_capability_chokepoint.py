"""Tests for CapabilityChokepoint - capability gating and enforcement."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.capability_chokepoint import CapabilityChokepoint


class TestCapabilityChokepoint:
    def test_init_with_capabilities(self):
        cp = CapabilityChokepoint(capabilities=["read", "write"])
        assert "read" in cp.capabilities

    def test_init_with_empty_capabilities(self):
        with pytest.raises(ValueError):
            CapabilityChokepoint(capabilities=[])

    def test_check_allowed_capability(self):
        cp = CapabilityChokepoint(capabilities=["read"])
        assert cp.check("read") is True

    def test_check_denied_capability(self):
        cp = CapabilityChokepoint(capabilities=["read"])
        assert cp.check("write") is False

    def test_enforce_allowed(self):
        cp = CapabilityChokepoint(capabilities=["read"])
        cp.enforce("read")  # should not raise

    def test_enforce_denied(self):
        cp = CapabilityChokepoint(capabilities=["read"])
        with pytest.raises(PermissionError):
            cp.enforce("write")

    def test_grant_capability(self):
        cp = CapabilityChokepoint(capabilities=["read"])
        cp.grant("write")
        assert "write" in cp.capabilities

    def test_revoke_capability(self):
        cp = CapabilityChokepoint(capabilities=["read", "write"])
        cp.revoke("write")
        assert "write" not in cp.capabilities

    def test_get_status(self):
        cp = CapabilityChokepoint(capabilities=["read"])
        status = cp.get_status()
        assert "capabilities" in status

    def test_audit_log(self):
        cp = CapabilityChokepoint(capabilities=["read"])
        monitor = Mock()
        cp.set_monitor(monitor)
        cp.enforce("read")
        monitor.log.assert_called()
