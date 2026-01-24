from pathlib import Path
from dataclasses import is_dataclass
import sys

# Ensure path visibility
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestRGSovereignSocket:
    """
    MANDATORY: 100% PASS REQUIREMENT.
    Verifies that apps_rg is correctly socketed into the Hardened Core.
    """

    def test_rg_base_inheritance(self):
        """Verify RGAgentBase inherits from SovereignBaseAgent."""
        from apps_rg.shared.core.agent_base import RGAgentBase
        from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent

        # MRO Verification: RGAgentBase -> SovereignBaseAgent -> object
        assert issubclass(RGAgentBase, SovereignBaseAgent), "RGAgentBase disconnected from Core!"

    def test_security_propagation(self):
        """Verify that Core security validation runs for RG agents."""
        from apps_rg.shared.core.agent_base import RGAgentBase

        # Test 1: Valid Boot (Should pass security check)
        agent = RGAgentBase()
        assert agent._initialized is True
        assert agent.get_rg_context()["version"] == "2.5.0"

        # Test 2: HealerMixin Availability
        assert hasattr(agent, "heal_repository"), "Self-Healing capability missing!"

    def test_campaign_planner_hardening(self):
        """Verify CampaignPlannerAgent follows V2.5 standards."""
        from apps_rg.engines.CampaignPlannerAgent import CampaignPlannerAgent

        # Dataclass Check
        assert is_dataclass(CampaignPlannerAgent), "CampaignPlanner must be a dataclass"

        # Defensive Defaults Check
        agent = CampaignPlannerAgent()
        assert agent.active_channels == ["email", "social"], "Default factory failed"

        # Mutable State Isolation Check
        agent2 = CampaignPlannerAgent()
        agent2.active_channels.append("sms")
        assert "sms" not in agent.active_channels, "Mutable state leakage detected!"

    def test_content_strategy_inheritance(self):
        """Verify ContentStrategyAgent connects to the bridge."""
        from apps_rg.engines.ContentStrategyAgent import ContentStrategyAgent
        from apps_rg.shared.core.agent_base import RGAgentBase

        assert issubclass(ContentStrategyAgent, RGAgentBase)
        agent = ContentStrategyAgent()
        result = agent.analyze_topic("AI Agents")
        assert result["relevance"] > 0

    def test_utility_isolation(self):
        """Verify stateless tools are importable and functional."""
        from apps_rg.shared.tools.text_utils import sanitize_campaign_text

        raw = "Hello!!! World**"
        clean = sanitize_campaign_text(raw)
        assert clean == "Hello World"
