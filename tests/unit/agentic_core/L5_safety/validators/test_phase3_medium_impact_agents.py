#!/usr/bin/env python3
"""
Phase 3: Medium-Impact Agent Rollout Tests

Tests for:
- Sub-Phase 3.1: HygieneGuardianAgent Integration
- Sub-Phase 3.2: StructureValidatorAgent Integration (via other agents)
- Sub-Phase 3.3: GravityLeakRepairAgent Integration
- Sub-Phase 3.4: ArchivalGatekeeper Integration

Success Criteria:
- 50%+ cache hit ratio for repeated operations
- All agents integrate with meta-learning without breaking existing functionality
"""

import sys
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Mock problematic imports before any imports
sys.modules["agentic_core.L5_safety.validators.PascalSovereigntyAgent"] = MagicMock()


# =============================================================================
# SUB-PHASE 3.1: HYGIENE GUARDIAN AGENT INTEGRATION TESTS
# =============================================================================


class TestHygieneGuardianAgentIntegration:
    """Test HygieneGuardianAgent meta-learning integration."""

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_agent_exists(self, mock_integrity):
        """Verify HygieneGuardianAgent can be imported."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
            HygieneGuardianAgent,
        )

        agent = HygieneGuardianAgent(project_root=Path.cwd())
        assert agent is not None

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_heal_method_exists(self, mock_integrity):
        """Verify heal() method exists."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
            HygieneGuardianAgent,
        )

        agent = HygieneGuardianAgent(project_root=Path.cwd())
        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_heal_returns_correct_structure(self, mock_integrity):
        """Verify heal() returns correct structure."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
            HygieneGuardianAgent,
        )

        agent = HygieneGuardianAgent(project_root=Path.cwd())
        violation = {"type": "HYGIENE", "file": "test.py", "message": "Test"}
        result = agent.heal(violation)

        assert "status" in result
        assert isinstance(result, dict)

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_inherits_from_sovereign_base(self, mock_integrity):
        """Verify agent inherits from SovereignBaseAgent."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
            HygieneGuardianAgent,
        )
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = HygieneGuardianAgent(project_root=Path.cwd())
        assert isinstance(agent, SovereignBaseAgent)


# =============================================================================
# SUB-PHASE 3.3: GRAVITY LEAK REPAIR AGENT INTEGRATION TESTS
# =============================================================================


class TestGravityLeakRepairAgentIntegration:
    """Test GravityLeakRepairAgent meta-learning integration."""

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_agent_exists(self, mock_integrity):
        """Verify GravityLeakRepairAgent can be imported."""
        from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import (
            GravityLeakRepairAgent,
        )

        agent = GravityLeakRepairAgent(project_root=Path.cwd())
        assert agent is not None

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_inherits_from_sovereign_base(self, mock_integrity):
        """Verify agent inherits from SovereignBaseAgent."""
        from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import (
            GravityLeakRepairAgent,
        )
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        agent = GravityLeakRepairAgent(project_root=Path.cwd())
        assert isinstance(agent, SovereignBaseAgent)

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_meta_learning_mixin_available(self, mock_integrity):
        """Verify meta-learning mixin methods are available."""
        from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import (
            GravityLeakRepairAgent,
        )

        agent = GravityLeakRepairAgent(project_root=Path.cwd())

        assert hasattr(agent, "ml_recall_healing_pattern")
        assert hasattr(agent, "ml_store_healing_pattern")
        assert hasattr(agent, "ml_cache_get")
        assert hasattr(agent, "ml_cache_set")


# =============================================================================
# SUB-PHASE 3.4: ARCHIVAL GATEKEEPER INTEGRATION TESTS
# =============================================================================


class TestArchivalGatekeeperIntegration:
    """Test ArchivalGatekeeper meta-learning integration."""

    def test_gatekeeper_exists(self):
        """Verify ArchivalGatekeeper can be imported."""
        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

        gatekeeper = ArchivalGatekeeper.get_instance(Path.cwd())
        assert gatekeeper is not None

    def test_gatekeeper_singleton_pattern(self):
        """Verify ArchivalGatekeeper uses singleton pattern."""
        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

        gk1 = ArchivalGatekeeper.get_instance(Path.cwd())
        gk2 = ArchivalGatekeeper.get_instance(Path.cwd())

        assert gk1 is gk2

    def test_safe_archive_method_exists(self):
        """Verify safe_archive method exists."""
        from agentic_core.L5_safety.core.ArchivalGatekeeper import ArchivalGatekeeper

        gatekeeper = ArchivalGatekeeper.get_instance(Path.cwd())
        assert hasattr(gatekeeper, "safe_archive")
        assert callable(gatekeeper.safe_archive)


# =============================================================================
# PHASE 3 INTEGRATION TESTS
# =============================================================================


class TestPhase3Integration:
    """Integration tests for Phase 3 medium-impact agents."""

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_all_agents_have_meta_learning(self, mock_integrity):
        """Verify all Phase 3 agents have meta-learning capabilities."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
            HygieneGuardianAgent,
        )
        from agentic_core.L5_safety.gravity.GravityLeakRepairAgent import (
            GravityLeakRepairAgent,
        )

        agents = [
            HygieneGuardianAgent(project_root=Path.cwd()),
            GravityLeakRepairAgent(project_root=Path.cwd()),
        ]

        for agent in agents:
            assert hasattr(
                agent, "ml_recall_healing_pattern"
            ), f"{agent.__class__.__name__} missing ml_recall_healing_pattern"
            assert hasattr(
                agent, "ml_store_healing_pattern"
            ), f"{agent.__class__.__name__} missing ml_store_healing_pattern"

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_agents_domain_detection(self, mock_integrity):
        """Verify agents correctly detect their domain."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
            HygieneGuardianAgent,
        )

        agent = HygieneGuardianAgent(project_root=Path.cwd())
        domain = agent._get_ml_domain()
        assert domain in ["agentic_core", "apps_lic", "apps_rg"]


class TestPhase3PerformanceBaseline:
    """Performance baseline tests for Phase 3 agents."""

    @patch(
        "agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity"
    )
    def test_hygiene_agent_performance(self, mock_integrity):
        """Test HygieneGuardianAgent performance."""
        from agentic_core.L5_safety.validators.HygieneGuardianAgent import (
            HygieneGuardianAgent,
        )

        agent = HygieneGuardianAgent(project_root=Path.cwd())

        start_time = time.time()

        # Perform 10 heal operations
        for i in range(10):
            violation = {"type": "HYGIENE", "file": f"test_{i}.py", "message": "Test"}
            agent.heal(violation)

        elapsed = time.time() - start_time

        # Should complete in < 2 seconds
        assert elapsed < 2.0, f"Heal operations took {elapsed:.2f}s, expected < 2s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
