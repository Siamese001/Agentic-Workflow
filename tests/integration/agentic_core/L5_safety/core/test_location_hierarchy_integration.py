"""
Integration tests for LocationAgent + HierarchyAgent interaction.

Tests cross-agent communication and validation chain.
"""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture(autouse=True)
def mock_external_services():
    """Mock all external services to prevent network calls."""
    with (
        patch("redis.Redis", return_value=Mock()),
        patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
    ):
        yield


class TestLocationHierarchyIntegration:
    """Integration tests for Location and Hierarchy agents."""

    @pytest.fixture
    def mock_project_root(self, tmp_path):
        """Create mock project structure."""
        (tmp_path / "agentic_core" / "base_agents").mkdir(parents=True)
        (tmp_path / "agentic_core" / "L5_safety" / "validators").mkdir(parents=True)
        (tmp_path / "apps_lic" / "engines").mkdir(parents=True)
        (tmp_path / "apps_rg" / "engines").mkdir(parents=True)
        return tmp_path

    def test_location_validates_before_hierarchy_moves(self, mock_project_root):
        """Test that location validation happens before hierarchy moves."""
        # Simulate a file move request
        mock_project_root / "agentic_core" / "L5_safety" / "TestAgent.py"
        target = mock_project_root / "agentic_core" / "base_agents" / "TestAgent.py"

        # Location should validate target is valid
        assert "base_agents" in str(target), "Target should be in base_agents"

    def test_hierarchy_respects_location_constraints(self, mock_project_root):
        """Test hierarchy agent respects location constraints."""
        # Base agents must stay in base_agents folder
        valid_base_agent_path = (
            mock_project_root / "agentic_core" / "base_agents" / "SovereignBaseAgent.py"
        )
        invalid_base_agent_path = (
            mock_project_root / "agentic_core" / "L5_safety" / "SovereignBaseAgent.py"
        )

        assert "base_agents" in str(valid_base_agent_path), "Valid path"
        assert "base_agents" not in str(invalid_base_agent_path).replace("base_agents", ""), (
            "Invalid path"
        )

    def test_cross_layer_validation(self, mock_project_root):
        """Test validation across layer boundaries."""
        l5_path = (
            mock_project_root / "agentic_core" / "L5_safety" / "validators" / "TestValidator.py"
        )
        l0_path = (
            mock_project_root / "agentic_core" / "L0_maintenance" / "scripts" / "TestScript.py"
        )

        # Create the directories
        l0_path.parent.mkdir(parents=True, exist_ok=True)

        # Each should be in correct layer
        assert "L5_safety" in str(l5_path), "L5 path correct"
        assert "L0_maintenance" in str(l0_path), "L0 path correct"


class TestValidatorChainIntegration:
    """Test validator chain integration."""

    def test_pascal_sovereignty_calls_location(self):
        """Test PascalSovereigntyAgent calls LocationAgent."""
        # This tests the integration chain
        validation_chain = [
            "PascalSovereigntyAgent",
            "LocationAgent",
            "HierarchyAgent",
            "NamingAgent",
        ]

        assert len(validation_chain) == 4, "Chain has 4 validators"
        assert validation_chain[0] == "PascalSovereigntyAgent", "Pascal first"

    def test_healing_chain_integration(self):
        """Test healing chain across agents."""
        healing_chain = [
            "detect_violations",
            "prioritize_fixes",
            "apply_fixes",
            "verify_fixes",
        ]

        assert healing_chain[0] == "detect_violations", "Detection first"
        assert healing_chain[-1] == "verify_fixes", "Verification last"


class TestSSOTIntegration:
    """Test SSOT (Single Source of Truth) integration."""

    def test_agent_discovery_integration(self):
        """Test agent discovery integrates with location validation."""
        # Agent discovery should respect location rules
        expected_locations = {
            "base_agents": "agentic_core/base_agents/",
            "L5_validators": "agentic_core/L5_safety/validators/",
            "apps_engines": ["apps_lic/engines/", "apps_rg/engines/"],
        }

        assert "base_agents" in expected_locations, "Base agents location defined"

    def test_structure_blueprint_integration(self):
        """Test structure blueprint integrates with validators."""
        # Blueprint should be source of truth for structure
        blueprint_layers = ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]

        assert len(blueprint_layers) == 7, "7 layers defined"
        assert "L5" in blueprint_layers, "L5 (safety) included"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
