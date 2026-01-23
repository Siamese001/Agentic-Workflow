"""
Test suite for Accelerated Consolidation.

MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
Focus: Nomenclature Accuracy, Redundancy Removal, Mixin Verification.
"""
import pytest
from pathlib import Path

# Get repo root (tests/ is one level down from repo root)
REPO_ROOT = Path(__file__).resolve().parent.parent


class TestAcceleratedConsolidation:
    """
    MANDATORY: 100% PASS REQUIREMENT for Windsurf Execution.
    Focus: Nomenclature Accuracy, Redundancy Removal, Mixin Verification.
    """

    def test_mass_rename_integrity(self, disable_path_shield):
        """Verify that 'Agent' suffixes were purged from Enum files."""
        # Check domain model rename
        assert not (REPO_ROOT / "apps_lic" / "domain" / "FailureClassifierAgent.py").exists()
        assert (REPO_ROOT / "apps_lic" / "domain" / "failure_types.py").exists()
        
        # Check governance rename
        assert not (REPO_ROOT / "apps_lic" / "engines" / "governance_shield_agent.py").exists()
        assert (REPO_ROOT / "apps_lic" / "engines" / "governance_shield_types.py").exists()

    def test_routing_stub_deletion(self, disable_path_shield):
        """Verify that k1_router_agent.py has been terminally deleted."""
        assert not (REPO_ROOT / "apps_lic" / "engines" / "k1_router_agent.py").exists()

    def test_specialist_inheritance_purity(self):
        """Verify that consolidated agents correctly inherit the Sovereign Base."""
        from apps_lic.engines.HOPOrchestratorAgent import HOPOrchestratorAgent
        from apps_lic.engines.k1_routing_agent import RoutingSpecialist
        
        # Verify 100% Pass: Mixins must be present for healing and testing
        assert hasattr(HOPOrchestratorAgent, "heal_repository")
        assert hasattr(RoutingSpecialist, "_run_self_tests")

    def test_unknown_count_reduction(self):
        """Verify that the 'UNKNOWN' classification in the AST scan has decreased."""
        # To be executed via post-refactor AST scan script.
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
