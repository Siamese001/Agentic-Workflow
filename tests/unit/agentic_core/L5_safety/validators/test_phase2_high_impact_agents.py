#!/usr/bin/env python3
"""
Phase 2: High-Impact Agent Migration Tests

Tests for:
- Sub-Phase 2.1: ArchitectureGovernorAgent Integration
- Sub-Phase 2.2: HierarchyAgent Integration
- Sub-Phase 2.3: CodeHealerAgent Integration
- Sub-Phase 2.4: LocationAgent Integration

Success Criteria:
- 70%+ cache hit ratio for repeated violations
- Healing time reduced by 40%+
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
# SUB-PHASE 2.1: ARCHITECTURE GOVERNOR AGENT INTEGRATION TESTS
# =============================================================================


class TestArchitectureGovernorAgentIntegration:
    """Test ArchitectureGovernorAgent meta-learning integration."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_method_uses_meta_learning(self, mock_integrity):
        """Verify heal() method integrates with meta-learning."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=Path.cwd())

        # Verify heal method exists and uses meta-learning delegation
        assert hasattr(agent, "heal")
        assert hasattr(agent, "_do_heal")

        # Test heal returns correct structure
        violation = {"type": "GRAVITY", "file": "test.py", "message": "Test violation"}
        result = agent.heal(violation)

        assert "status" in result
        assert isinstance(result, dict)

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_dispatches_by_violation_type(self, mock_integrity):
        """Verify heal() dispatches to correct handler based on violation type."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=Path.cwd())

        # Test GRAVITY violation
        gravity_violation = {"type": "GRAVITY", "file": "test.py"}
        result = agent._do_heal(gravity_violation)
        assert "status" in result

        # Test NAMING violation
        naming_violation = {"type": "NAMING", "file": "test.py"}
        result = agent._do_heal(naming_violation)
        assert "status" in result

        # Test unknown violation type
        unknown_violation = {"type": "UNKNOWN", "file": "test.py"}
        result = agent._do_heal(unknown_violation)
        assert result["status"] == "skipped"

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_meta_learning_mixin_available(self, mock_integrity):
        """Verify meta-learning mixin methods are available."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=Path.cwd())

        # Verify mixin methods
        assert hasattr(agent, "ml_recall_healing_pattern")
        assert hasattr(agent, "ml_store_healing_pattern")
        assert hasattr(agent, "ml_cache_get")
        assert hasattr(agent, "ml_cache_set")
        assert hasattr(agent, "ml_check_healing_depth")

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_repository_still_works(self, mock_integrity):
        """Verify heal_repository() method still works after integration."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=Path.cwd())

        # Verify heal_repository exists and is callable
        assert hasattr(agent, "heal_repository")
        assert callable(agent.heal_repository)


# =============================================================================
# SUB-PHASE 2.2: HIERARCHY AGENT INTEGRATION TESTS
# =============================================================================


class TestHierarchyAgentIntegration:
    """Test HierarchyAgent meta-learning integration."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_method_exists(self, mock_integrity):
        """Verify heal() method exists and has correct signature."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        agent = HierarchyAgent(project_root=Path.cwd())

        assert hasattr(agent, "heal")
        assert callable(agent.heal)

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_returns_correct_structure(self, mock_integrity):
        """Verify heal() returns correct structure."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        agent = HierarchyAgent(project_root=Path.cwd())

        violation = {
            "type": "STRUCTURE",
            "file": "test.py",
            "message": "Structure violation",
        }
        result = agent.heal(violation)

        assert "status" in result
        assert isinstance(result, dict)

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_meta_learning_mixin_available(self, mock_integrity):
        """Verify meta-learning mixin methods are available."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        agent = HierarchyAgent(project_root=Path.cwd())

        # Verify mixin methods from SovereignBaseAgent
        assert hasattr(agent, "ml_recall_healing_pattern")
        assert hasattr(agent, "ml_store_healing_pattern")
        assert hasattr(agent, "ml_cache_get")
        assert hasattr(agent, "ml_cache_set")

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_create_missing_structure_still_works(self, mock_integrity):
        """Verify create_missing_structure() still works."""
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent

        agent = HierarchyAgent(project_root=Path.cwd(), healing_enabled=False)

        assert hasattr(agent, "create_missing_structure")
        assert callable(agent.create_missing_structure)


# =============================================================================
# SUB-PHASE 2.3: CODE HEALER AGENT INTEGRATION TESTS
# =============================================================================


class TestCodeHealerAgentIntegration:
    """Test CodeHealerAgent meta-learning integration."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_agent_inherits_from_sovereign_base(self, mock_integrity):
        """Verify CodeHealerAgent inherits from SovereignBaseAgent."""
        from agentic_core.L5_safety.policy_engine.CodeHealerAgent import (
            CodeHealerAgent,
        )

        agent = CodeHealerAgent(project_root=Path.cwd())

        # Verify inheritance
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        assert isinstance(agent, SovereignBaseAgent)

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_meta_learning_mixin_available(self, mock_integrity):
        """Verify meta-learning mixin methods are available."""
        from agentic_core.L5_safety.policy_engine.CodeHealerAgent import (
            CodeHealerAgent,
        )

        agent = CodeHealerAgent(project_root=Path.cwd())

        # Verify mixin methods
        assert hasattr(agent, "ml_recall_healing_pattern")
        assert hasattr(agent, "ml_store_healing_pattern")
        assert hasattr(agent, "ml_cache_get")
        assert hasattr(agent, "ml_cache_set")

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_all_method_exists(self, mock_integrity):
        """Verify heal_all() method exists."""
        from agentic_core.L5_safety.policy_engine.CodeHealerAgent import (
            CodeHealerAgent,
        )

        agent = CodeHealerAgent(project_root=Path.cwd())

        assert hasattr(agent, "heal_all")
        assert callable(agent.heal_all)


# =============================================================================
# SUB-PHASE 2.4: LOCATION AGENT INTEGRATION TESTS
# =============================================================================


class TestLocationAgentIntegration:
    """Test LocationAgent meta-learning integration."""

    def test_is_path_compliant_function_exists(self):
        """Verify is_path_compliant() function exists."""
        from agentic_core.L5_safety.validators.LocationAgent import is_path_compliant

        assert callable(is_path_compliant)

    def test_is_path_compliant_returns_boolean(self):
        """Verify is_path_compliant() returns boolean."""
        from agentic_core.L5_safety.validators.LocationAgent import is_path_compliant

        result = is_path_compliant("agentic_core/L5_safety/validators/test.py")
        assert isinstance(result, bool)

    def test_heal_function_exists(self):
        """Verify heal() function exists at module level."""
        from agentic_core.L5_safety.validators.LocationAgent import heal

        assert callable(heal)

    def test_heal_returns_correct_structure(self):
        """Verify heal() returns correct structure."""
        from agentic_core.L5_safety.validators.LocationAgent import heal

        violation = {"type": "LOCATION", "file": "test.py", "message": "Test"}
        result = heal(violation)

        assert "status" in result
        assert isinstance(result, dict)


# =============================================================================
# PHASE 2 INTEGRATION TESTS
# =============================================================================


class TestPhase2Integration:
    """Integration tests for Phase 2 high-impact agents."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_all_agents_have_meta_learning(self, mock_integrity):
        """Verify all Phase 2 agents have meta-learning capabilities."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )
        from agentic_core.L5_safety.validators.HierarchyAgent import HierarchyAgent
        from agentic_core.L5_safety.policy_engine.CodeHealerAgent import (
            CodeHealerAgent,
        )

        agents = [
            ArchitectureGovernorAgent(project_root=Path.cwd()),
            HierarchyAgent(project_root=Path.cwd()),
            CodeHealerAgent(project_root=Path.cwd()),
        ]

        for agent in agents:
            assert hasattr(agent, "ml_recall_healing_pattern"), (
                f"{agent.__class__.__name__} missing ml_recall_healing_pattern"
            )
            assert hasattr(agent, "ml_store_healing_pattern"), (
                f"{agent.__class__.__name__} missing ml_store_healing_pattern"
            )
            assert hasattr(agent, "ml_cache_get"), (
                f"{agent.__class__.__name__} missing ml_cache_get"
            )
            assert hasattr(agent, "ml_cache_set"), (
                f"{agent.__class__.__name__} missing ml_cache_set"
            )

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_agents_domain_detection(self, mock_integrity):
        """Verify agents correctly detect their domain."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=Path.cwd())

        # Test domain detection
        domain = agent._get_ml_domain()
        assert domain in ["agentic_core", "apps_lic", "apps_rg"]


class TestPhase2PerformanceBaseline:
    """Performance baseline tests for Phase 2 agents."""

    @patch("agentic_core.domain.CoreIntegrityVerifier.CoreIntegrityVerifier.verify_core_integrity")
    def test_heal_performance(self, mock_integrity):
        """Test heal operation performance."""
        from agentic_core.L5_safety.validators.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        agent = ArchitectureGovernorAgent(project_root=Path.cwd())

        start_time = time.time()

        # Perform 10 heal operations
        for i in range(10):
            violation = {"type": "TEST", "file": f"test_{i}.py", "message": "Test"}
            agent.heal(violation)

        elapsed = time.time() - start_time

        # Should complete in < 2 seconds
        assert elapsed < 2.0, f"Heal operations took {elapsed:.2f}s, expected < 2s"

    def test_path_compliance_performance(self):
        """Test path compliance check performance."""
        from agentic_core.L5_safety.validators.LocationAgent import is_path_compliant

        start_time = time.time()

        # Perform 100 path compliance checks
        for i in range(100):
            is_path_compliant(f"agentic_core/L5_safety/validators/test_{i}.py")

        elapsed = time.time() - start_time

        # Should complete in < 1 second
        assert elapsed < 1.0, f"Path compliance checks took {elapsed:.2f}s, expected < 1s"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
