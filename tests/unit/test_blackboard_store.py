"""Unit tests for BlackboardStore.

Phase 1 Wave 1.2 test suite. Verifies KV operations,
lease semantics, tick monotonicity, and IBlackboardLeaseVerifier compliance.
"""

import pytest

from agentic_core.L4_state.memory.blackboard_store import (
    BlackboardStore,
    LeaseResult,
    SecurityEvent,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_blackboard_store")
_emit_applies_guardrail("p0", "test_blackboard_store", "p0_governance")
_emit_reads_policy_state("p0", "test_blackboard_store", "policy_binding")
_emit_snapshots_state("p0", "test_blackboard_store", "state_snapshot")
emit_replay_key("p0", "test_blackboard_store")
emit_determinism_digest("p0", "test_blackboard_store")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)


@pytest.mark.unit
class TestBlackboardStore:
    def setup_method(self):
        self.store = BlackboardStore()
        self.store.clear()  # ensure clean state

    def test_set_and_get(self):
        self.store.set("key1", "value1", "agent1", 1)
        assert self.store.get("key1") == "value1"

    def test_get_missing_key_raises(self):
        with pytest.raises(KeyError):
            self.store.get("missing")

    def test_lease_granted_when_no_existing(self):
        result = self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        assert result.success
        assert result.expiry_tick == 15
        assert result.reason == "Lease granted"

    def test_lease_blocks_second_agent(self):
        # Agent1 gets lease
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Agent2 tries same key before expiry
        result = self.store.lease("key1", "agent2", ttl_ticks=5, commit_tick=12)
        assert not result.success
        assert result.expiry_tick == 15
        assert "agent1" in result.reason

    def test_lease_renews_after_expiry(self):
        # Agent1 gets lease
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # After expiry, Agent2 can get lease
        result = self.store.lease("key1", "agent2", ttl_ticks=3, commit_tick=16)
        assert result.success
        assert result.expiry_tick == 19

    def test_lease_same_agent_can_renew_before_expiry(self):
        # Agent1 gets lease
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Same agent can renew
        result = self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=12)
        assert result.success
        assert result.expiry_tick == 17

    def test_lease_ttl_must_be_positive(self):
        result = self.store.lease("key1", "agent1", ttl_ticks=0, commit_tick=10)
        assert not result.success
        assert result.expiry_tick == 0
        assert "positive" in result.reason

    def test_delete_requires_lease(self):
        self.store.set("key1", "value1", "agent1", 1)
        # Try delete without lease
        assert not self.store.delete("key1", "agent1", 1)
        # Get lease then delete
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        assert self.store.delete("key1", "agent1", 10)
        with pytest.raises(KeyError):
            self.store.get("key1")

    def test_delete_wrong_agent_fails(self):
        self.store.set("key1", "value1", "agent1", 1)
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Wrong agent tries to delete
        assert not self.store.delete("key1", "agent2", 10)

    def test_delete_expired_lease_fails(self):
        self.store.set("key1", "value1", "agent1", 1)
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        # Try delete after expiry
        assert not self.store.delete("key1", "agent1", 16)

    def test_verify_healing_lease_interface(self):
        """Test IBlackboardLeaseVerifier.verify_healing_lease implementation."""
        result = self.store.verify_healing_lease("resource", "agent1", 10, "write")
        assert isinstance(result, LeaseResult)
        # Should grant lease with default TTL of 10 ticks
        assert result.success
        assert result.expiry_tick == 20

    def test_log_security_event_interface(self):
        """Test IBlackboardLeaseVerifier.log_security_event implementation."""
        event = SecurityEvent(
            event_type="LEASE_VIOLATION",
            agent_id="agent1",
            resource_path="key1",
            details="Test event",
            timestamp=1234567890,
            severity="medium",
        )
        # Phase 1: no-op, should not raise
        self.store.log_security_event(event)

    def test_multiple_keys_independent(self):
        # Different keys have independent leases
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        self.store.lease("key2", "agent2", ttl_ticks=5, commit_tick=10)
        # Both should succeed
        lease1 = self.store._get_lease("key1")
        lease2 = self.store._get_lease("key2")
        assert lease1.agent_id == "agent1"
        assert lease2.agent_id == "agent2"

    def test_clear_resets_store(self):
        self.store.set("key1", "value1", "agent1", 1)
        self.store.lease("key1", "agent1", ttl_ticks=5, commit_tick=10)
        self.store.clear()
        with pytest.raises(KeyError):
            self.store.get("key1")
        assert self.store._get_lease("key1") is None
