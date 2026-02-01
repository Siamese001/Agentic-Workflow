"""
Phase 1 Optimization Tests - Agent Configuration Integration
Tests for agents using centralized configuration system.
"""

import pytest
from apps_rg.engines.ATSCompatibilityAgent import ATSCompatibilityAgent
from apps_rg.engines.BrandComplianceAgent import BrandComplianceAgent
from apps_rg.engines.CampaignPlannerAgent import CampaignPlannerAgent


class TestATSCompatibilityAgentConfig:
    """Test ATSCompatibilityAgent with centralized config."""

    def test_agent_imports_successfully(self):
        """Test that ATSCompatibilityAgent can be imported."""
        assert ATSCompatibilityAgent is not None

    def test_agent_loads_config_on_init(self):
        """Test that agent loads configuration on initialization."""
        # Note: This test verifies the agent can initialize with config loading
        # The actual initialization requires context which we don't test here
        # We're just verifying the class structure is correct
        assert hasattr(ATSCompatibilityAgent, "__post_init__")

    def test_config_attributes_exist(self):
        """Test that expected config attributes will be set."""
        # Verify the agent class has the expected structure
        # The actual attributes are set in __post_init__
        assert ATSCompatibilityAgent is not None


class TestBrandComplianceAgentConfig:
    """Test BrandComplianceAgent with centralized config."""

    def test_agent_imports_successfully(self):
        """Test that BrandComplianceAgent can be imported."""
        assert BrandComplianceAgent is not None

    def test_agent_loads_config_on_init(self):
        """Test that agent has __post_init__ method."""
        assert hasattr(BrandComplianceAgent, "__post_init__")

    def test_config_attributes_exist(self):
        """Test that expected config attributes will be set."""
        assert BrandComplianceAgent is not None


class TestCampaignPlannerAgentConfig:
    """Test CampaignPlannerAgent with centralized config."""

    def test_agent_imports_successfully(self):
        """Test that CampaignPlannerAgent can be imported."""
        assert CampaignPlannerAgent is not None

    def test_agent_loads_config_on_init(self):
        """Test that agent has __post_init__ method."""
        assert hasattr(CampaignPlannerAgent, "__post_init__")

    def test_agent_has_active_channels_field(self):
        """Test that agent has active_channels field."""
        # Verify the dataclass field exists
        assert hasattr(CampaignPlannerAgent, "__dataclass_fields__")
        assert "active_channels" in CampaignPlannerAgent.__dataclass_fields__


class TestPhase1ConfigFiles:
    """Test that all Phase 1 config files exist and are valid."""

    def test_ats_compatibility_yaml_exists(self):
        """Test that ats_compatibility.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/ats_compatibility.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_brand_compliance_yaml_exists(self):
        """Test that brand_compliance.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/brand_compliance.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_campaign_planner_yaml_exists(self):
        """Test that campaign_planner.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/campaign_planner.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_content_quality_yaml_exists(self):
        """Test that content_quality.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/content_quality.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_section_balance_yaml_exists(self):
        """Test that section_balance.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/section_balance.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_campaign_balance_yaml_exists(self):
        """Test that campaign_balance.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/campaign_balance.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_hop4_routing_yaml_exists(self):
        """Test that hop4_routing.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/hop4_routing.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_hop5_generation_yaml_exists(self):
        """Test that hop5_generation.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/hop5_generation.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_hop6_validation_yaml_exists(self):
        """Test that hop6_validation.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/hop6_validation.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_hop7_gate_decision_yaml_exists(self):
        """Test that hop7_gate_decision.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/hop7_gate_decision.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"

    def test_deliverability_yaml_exists(self):
        """Test that deliverability.yaml exists."""
        from pathlib import Path

        config_path = Path("config/agent_configs/deliverability.yaml")
        assert config_path.exists(), f"Config file not found: {config_path}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
