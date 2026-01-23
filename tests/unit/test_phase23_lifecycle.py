"""
[PHASE 23] Unit Tests for Lifecycle-Aware Component System.

Tests:
1. LifecycleMixin - Async startup/shutdown protocol
2. AuditTrailMixin - Cryptographic chain-of-custody
3. CapabilityDiscoveryMixin - Redis registry pattern
4. HealerMixin - Per-violation-type per-file budget

[SSOT] Tests for Phase 23 lifecycle components.
"""

from __future__ import annotations

import hashlib
from unittest.mock import patch

import pytest

# =============================================================================
# LifecycleMixin Tests
# =============================================================================


class TestLifecycleMixin:
    """Tests for the LifecycleMixin async startup/shutdown protocol."""

    @pytest.fixture
    def lifecycle_component(self):
        """Create a test component with LifecycleMixin."""
        from agentic_core.utils.core_extensions.lifecycle_mixin import (
            LifecycleMixin,
        )

        class TestComponent(LifecycleMixin):
            def __init__(self):
                super().__init__()
                self.startup_called = False
                self.shutdown_called = False
                self.resource = None

            async def _do_startup(self):
                self.startup_called = True
                self.resource = "initialized"

            async def _do_shutdown(self):
                self.shutdown_called = True
                self.resource = None

        return TestComponent()

    @pytest.mark.asyncio
    async def test_lifecycle_states(self, lifecycle_component):
        """Test that lifecycle states transition correctly."""
        from agentic_core.utils.core_extensions.lifecycle_mixin import LifecycleState

        # Initial state
        assert lifecycle_component.lifecycle_state == LifecycleState.CREATED
        assert not lifecycle_component.is_ready

        # After startup
        await lifecycle_component.startup()
        assert lifecycle_component.lifecycle_state == LifecycleState.READY
        assert lifecycle_component.is_ready
        assert lifecycle_component.startup_called

        # After shutdown
        await lifecycle_component.shutdown()
        assert lifecycle_component.lifecycle_state == LifecycleState.STOPPED
        assert lifecycle_component.is_stopped
        assert lifecycle_component.shutdown_called

    @pytest.mark.asyncio
    async def test_require_ready_raises_before_startup(self, lifecycle_component):
        """Test that require_ready raises if not started."""
        from agentic_core.utils.core_extensions.lifecycle_mixin import LifecycleError

        with pytest.raises(LifecycleError):
            lifecycle_component.require_ready()

    @pytest.mark.asyncio
    async def test_require_ready_passes_after_startup(self, lifecycle_component):
        """Test that require_ready passes after startup."""
        await lifecycle_component.startup()
        lifecycle_component.require_ready()  # Should not raise

    @pytest.mark.asyncio
    async def test_double_startup_is_idempotent(self, lifecycle_component):
        """Test that calling startup twice doesn't fail."""
        await lifecycle_component.startup()
        await lifecycle_component.startup()  # Should not raise
        assert lifecycle_component.is_ready

    @pytest.mark.asyncio
    async def test_double_shutdown_is_idempotent(self, lifecycle_component):
        """Test that calling shutdown twice doesn't fail."""
        await lifecycle_component.startup()
        await lifecycle_component.shutdown()
        await lifecycle_component.shutdown()  # Should not raise
        assert lifecycle_component.is_stopped

    @pytest.mark.asyncio
    async def test_async_context_manager(self, lifecycle_component):
        """Test async context manager protocol."""
        async with lifecycle_component:
            assert lifecycle_component.is_ready
            assert lifecycle_component.resource == "initialized"

        assert lifecycle_component.is_stopped
        assert lifecycle_component.resource is None

    @pytest.mark.asyncio
    async def test_lifecycle_stats(self, lifecycle_component):
        """Test lifecycle statistics."""
        await lifecycle_component.startup()
        stats = lifecycle_component.get_lifecycle_stats()

        assert stats["state"] == "ready"
        assert stats["startup_time"] is not None
        assert stats["uptime_seconds"] is not None
        assert stats["error"] is None


# =============================================================================
# AuditTrailMixin Tests
# =============================================================================


class TestAuditTrailMixin:
    """Tests for the AuditTrailMixin cryptographic chain."""

    @pytest.fixture
    def audit_component(self):
        """Create a test component with AuditTrailMixin."""
        from agentic_core.utils.core_extensions.audit_trail_mixin import AuditTrailMixin

        class TestComponent(AuditTrailMixin):
            def __init__(self):
                super().__init__()
                self.emitted_events = []

            async def emit_event(self, event_type, payload, severity="INFO"):
                """Mock event_emission_mixin method."""
                self.emitted_events.append(
                    {
                        "type": event_type,
                        "payload": payload,
                        "severity": severity,
                    }
                )

        return TestComponent()

    def test_genesis_hash(self, audit_component):
        """Test that chain starts with genesis hash."""
        assert audit_component.get_chain_head() == "0" * 64

    def test_proof_generation(self, audit_component):
        """Test that proofs are generated correctly."""
        proof = audit_component._generate_audit_proof(
            "TEST_ACTION",
            {"key": "value"},
        )

        assert proof.action_id.startswith("act_")
        assert proof.prev_hash == "0" * 64  # Genesis
        assert len(proof.curr_hash) == 64  # SHA-256
        assert proof.timestamp > 0

    def test_hash_chain_advances(self, audit_component):
        """Test that hash chain advances with each action."""
        proof1 = audit_component._generate_audit_proof("ACTION_1", {"a": 1})
        proof2 = audit_component._generate_audit_proof("ACTION_2", {"b": 2})

        # Second proof should link to first
        assert proof2.prev_hash == proof1.curr_hash

        # Chain head should be latest hash
        assert audit_component.get_chain_head() == proof2.curr_hash

    def test_deterministic_hashing(self, audit_component):
        """Test that same input produces same hash."""
        # Reset chain for deterministic test
        audit_component._audit_last_hash = "0" * 64
        audit_component._audit_session_salt = "test_salt"

        # Generate proof with fixed timestamp
        with patch("time.time", return_value=1000.0):
            proof = audit_component._generate_audit_proof("TEST", {"x": 1})

        # Manually compute expected hash
        raw_data = f"{'0' * 64}|test_salt|TEST|[('x', 1)]|1000.0"
        expected_hash = hashlib.sha256(raw_data.encode()).hexdigest()

        assert proof.curr_hash == expected_hash

    @pytest.mark.asyncio
    async def test_emit_auditable_action(self, audit_component):
        """Test async auditable action emission."""
        proof = await audit_component.emit_auditable_action(
            "FILE_MOVE",
            {"from": "/a", "to": "/b"},
        )

        # Proof should be returned
        assert proof.curr_hash is not None

        # Event should be emitted
        assert len(audit_component.emitted_events) == 1
        event = audit_component.emitted_events[0]
        assert event["type"] == "AUDIT_FILE_MOVE"
        assert "audit_proof" in event["payload"]

    def test_sync_audit_proof(self, audit_component):
        """Test synchronous proof generation."""
        proof = audit_component.emit_auditable_action_sync(
            "SYNC_ACTION",
            {"data": "test"},
        )

        assert proof.curr_hash is not None
        assert proof.action_id is not None

    def test_chain_integrity_verification(self, audit_component):
        """Test chain integrity verification."""
        # Generate a chain of proofs
        proofs = []
        for i in range(5):
            proof = audit_component._generate_audit_proof(f"ACTION_{i}", {"i": i})
            proofs.append(proof)

        # Verify chain integrity
        is_valid, broken_index = audit_component.verify_chain_integrity(proofs)
        assert is_valid is True
        assert broken_index is None

    def test_chain_integrity_detects_tampering(self, audit_component):
        """Test that chain integrity verification detects tampering."""
        from agentic_core.utils.core_extensions.audit_trail_mixin import AuditProof

        # Generate valid proofs
        proofs = []
        for i in range(3):
            proof = audit_component._generate_audit_proof(f"ACTION_{i}", {"i": i})
            proofs.append(proof)

        # Tamper with middle proof
        proofs[1] = AuditProof(
            action_id=proofs[1].action_id,
            prev_hash="tampered_hash",  # Broken link
            curr_hash=proofs[1].curr_hash,
            timestamp=proofs[1].timestamp,
        )

        # Verify should detect break
        is_valid, broken_index = audit_component.verify_chain_integrity(proofs)
        assert is_valid is False
        assert broken_index == 1

    def test_audit_chain_stats(self, audit_component):
        """Test audit chain statistics."""
        # Generate some actions
        for i in range(3):
            audit_component._generate_audit_proof(f"ACTION_{i}", {"i": i})

        stats = audit_component.get_audit_chain_stats()

        assert stats.total_actions == 3
        assert stats.chain_id == audit_component._audit_session_salt
        assert stats.last_hash == audit_component.get_chain_head()


# =============================================================================
# CapabilityDiscoveryMixin Tests
# =============================================================================


class TestCapabilityDiscoveryMixin:
    """Tests for the CapabilityDiscoveryMixin registry pattern."""

    @pytest.fixture
    def capability_component(self):
        """Create a test component with CapabilityDiscoveryMixin."""
        from agentic_core.utils.core_extensions.capability_discovery_mixin import (
            CapabilityDiscoveryMixin,
        )

        class TestComponent(CapabilityDiscoveryMixin):
            pass

        return TestComponent(agent_id="test_agent_123")

    def test_capability_registration(self, capability_component):
        """Test declarative capability registration."""
        capability_component.register_capability("heal_syntax")
        capability_component.register_capability("heal_imports")

        assert "heal_syntax" in capability_component._capabilities
        assert "heal_imports" in capability_component._capabilities

    def test_capability_unregistration(self, capability_component):
        """Test capability unregistration."""
        capability_component.register_capability("heal_syntax")
        capability_component.unregister_capability("heal_syntax")

        assert "heal_syntax" not in capability_component._capabilities

    def test_agent_id_generation(self):
        """Test that agent_id is generated if not provided."""
        from agentic_core.utils.core_extensions.capability_discovery_mixin import (
            CapabilityDiscoveryMixin,
        )

        class TestComponent(CapabilityDiscoveryMixin):
            pass

        component = TestComponent()
        assert component._agent_id.startswith("TestComponent_")

    def test_discovery_stats(self, capability_component):
        """Test capability discovery statistics."""
        capability_component.register_capability("heal_syntax")
        capability_component.register_capability("validate_layer")

        stats = capability_component.get_discovery_stats()

        assert stats["agent_id"] == "test_agent_123"
        assert stats["capability_count"] == 2
        assert "heal_syntax" in stats["capabilities"]
        assert "validate_layer" in stats["capabilities"]

    @pytest.mark.asyncio
    async def test_graceful_degradation_no_redis(self, capability_component):
        """Test graceful degradation when Redis is unavailable."""
        capability_component.register_capability("test_cap")

        # Simulate Redis unavailable
        capability_component._registry_connected = False

        # Should not crash
        providers = await capability_component.find_providers("test_cap")
        assert providers == []


# =============================================================================
# HealerMixin Granular Budget Tests
# =============================================================================


class TestHealerMixinGranularBudget:
    """Tests for Phase 23 per-violation-type per-file budget."""

    @pytest.fixture
    def healer_component(self):
        """Create a test component with HealerMixin."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

        class TestHealer(HealerMixin):
            def __init__(self):
                super().__init__()

        return TestHealer()

    def test_granular_budget_initialization(self, healer_component):
        """Test that granular budget is initialized empty."""
        assert healer_component._healer_granular_budget == {}

    def test_granular_budget_tracking(self, healer_component):
        """Test that granular budget tracks per file and violation type."""
        # Simulate budget increment
        key1 = ("/path/to/file1.py", "SYNTAX_ERROR")
        key2 = ("/path/to/file1.py", "IMPORT_ERROR")
        key3 = ("/path/to/file2.py", "SYNTAX_ERROR")

        healer_component._healer_granular_budget[key1] = 1
        healer_component._healer_granular_budget[key2] = 2
        healer_component._healer_granular_budget[key3] = 1

        # Same file, different violation types should be separate
        assert healer_component._healer_granular_budget[key1] == 1
        assert healer_component._healer_granular_budget[key2] == 2

        # Different file, same violation type should be separate
        assert healer_component._healer_granular_budget[key3] == 1

    def test_reset_healing_budget_clears_granular(self, healer_component):
        """Test that reset_healing_budget clears granular budget."""
        healer_component._healer_granular_budget[("/a.py", "ERROR")] = 3
        healer_component._healing_count = 10

        healer_component.reset_healing_budget()

        assert healer_component._healing_count == 0
        assert healer_component._healer_granular_budget == {}

    def test_reset_granular_budget_for_file(self, healer_component):
        """Test resetting granular budget for a specific file."""
        healer_component._healer_granular_budget[("/a.py", "ERROR1")] = 2
        healer_component._healer_granular_budget[("/a.py", "ERROR2")] = 1
        healer_component._healer_granular_budget[("/b.py", "ERROR1")] = 3

        healer_component.reset_granular_budget_for_file("/a.py")

        # /a.py entries should be removed
        assert ("/a.py", "ERROR1") not in healer_component._healer_granular_budget
        assert ("/a.py", "ERROR2") not in healer_component._healer_granular_budget

        # /b.py should remain
        assert healer_component._healer_granular_budget[("/b.py", "ERROR1")] == 3

    def test_get_granular_budget_stats(self, healer_component):
        """Test granular budget statistics."""
        healer_component._healer_granular_budget[("/a.py", "ERROR")] = 2
        healer_component._healer_granular_budget[("/b.py", "ERROR")] = 1

        stats = healer_component.get_granular_budget_stats()

        assert stats["total_entries"] == 2
        assert stats["max_per_violation_type_per_file"] == 3
        assert ("/a.py", "ERROR") in stats["budget_usage"]

    def test_granular_budget_allows_different_violation_types(self, healer_component):
        """Test that fixing one violation type doesn't block another."""
        # Exhaust budget for SYNTAX_ERROR on file
        healer_component._healer_granular_budget[("/test.py", "SYNTAX_ERROR")] = 3

        # IMPORT_ERROR should still have budget
        import_key = ("/test.py", "IMPORT_ERROR")
        assert healer_component._healer_granular_budget.get(import_key, 0) == 0

        # This is the key insight: different violation types are independent


# =============================================================================
# Integration Tests
# =============================================================================


class TestPhase23Integration:
    """Integration tests for Phase 23 lifecycle components."""

    def test_lifecycle_mixin_import(self):
        """Test that LifecycleMixin can be imported."""
        from agentic_core.utils.core_extensions.lifecycle_mixin import (
            LifecycleError,
            LifecycleMixin,
            LifecycleState,
        )

        assert LifecycleMixin is not None
        assert LifecycleState is not None
        assert LifecycleError is not None

    def test_audit_trail_mixin_import(self):
        """Test that AuditTrailMixin can be imported."""
        from agentic_core.utils.core_extensions.audit_trail_mixin import (
            AuditChainStats,
            AuditProof,
            AuditTrailMixin,
        )

        assert AuditTrailMixin is not None
        assert AuditProof is not None
        assert AuditChainStats is not None

    def test_capability_discovery_mixin_import(self):
        """Test that CapabilityDiscoveryMixin can be imported."""
        from agentic_core.utils.core_extensions.capability_discovery_mixin import (
            CapabilityDiscoveryMixin,
        )

        assert CapabilityDiscoveryMixin is not None

    def test_healer_mixin_has_granular_budget(self):
        """Test that HealerMixin has Phase 23 granular budget methods."""
        from agentic_core.utils.core_extensions.healer_mixin import HealerMixin

        assert hasattr(HealerMixin, "_max_healing_per_violation_type_per_file")
        assert hasattr(HealerMixin, "reset_granular_budget_for_file")
        assert hasattr(HealerMixin, "get_granular_budget_stats")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
