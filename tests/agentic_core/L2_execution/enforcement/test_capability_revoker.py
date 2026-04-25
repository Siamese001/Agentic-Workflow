"""Tests for CapabilityRevoker - capability revocation logic."""
import pytest
from unittest.mock import Mock
from agentic_core.L2_execution.enforcement.capability_revoker import CapabilityRevoker


class TestCapabilityRevoker:
    def test_init(self):
        revoker = CapabilityRevoker()
        assert revoker is not None

    def test_revoke_capability(self):
        revoker = CapabilityRevoker()
        revoker.revoke(agent_id="agent1", capability="write")
        assert revoker.is_revoked("agent1", "write") is True

    def test_capability_not_revoked(self):
        revoker = CapabilityRevoker()
        assert revoker.is_revoked("agent1", "read") is False

    def test_revoke_all(self):
        revoker = CapabilityRevoker()
        revoker.revoke_all("agent1")
        assert revoker.is_fully_revoked("agent1") is True

    def test_restore_capability(self):
        revoker = CapabilityRevoker()
        revoker.revoke("agent1", "write")
        revoker.restore("agent1", "write")
        assert revoker.is_revoked("agent1", "write") is False

    def test_revoke_with_reason(self):
        revoker = CapabilityRevoker()
        revoker.revoke("agent1", "write", reason="policy_violation")
        record = revoker.get_revocation_record("agent1", "write")
        assert record["reason"] == "policy_violation"

    def test_list_revoked_capabilities(self):
        revoker = CapabilityRevoker()
        revoker.revoke("agent1", "write")
        revoker.revoke("agent1", "delete")
        revoked = revoker.list_revoked("agent1")
        assert len(revoked) == 2

    def test_revoke_emits_event(self):
        revoker = CapabilityRevoker()
        listener = Mock()
        revoker.add_listener(listener)
        revoker.revoke("agent1", "write")
        listener.on_revoke.assert_called_once()

    def test_revoke_idempotent(self):
        revoker = CapabilityRevoker()
        revoker.revoke("agent1", "write")
        revoker.revoke("agent1", "write")  # idempotent
        assert revoker.is_revoked("agent1", "write") is True
