"""
apps_rg/engines/CampaignPlannerAgent.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from apps_rg.utils.RGAgentBase import RGAgentBase
from apps_shared.config.config_loader_config import load_agent_config

Logger = logging.getLogger(__name__)


@dataclass
class CampaignPlannerAgent(RGAgentBase):
    """
    Sovereign Campaign Planner.
    Orchestrates high-level campaign strategies and timeline alignment.
    """

    # Replacing mutable list=[] with defensive field factory
    active_channels: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Initialize and validate campaign parameters."""
        super().__post_init__()

        # Load configuration from centralized config system
        self._config = load_agent_config("campaign_planner")

        # Extract configuration values
        agent_defaults = self._config.get("agent_defaults", {})
        self.name = agent_defaults.get("name", "CampaignPlannerAgent")
        self.campaign_id = agent_defaults.get("campaign_id", "default_campaign")
        self.strategy_model = agent_defaults.get("strategy_model", "gpt-4-turbo")

        # Channel configuration
        channel_config = self._config.get("channel_configuration", {})
        if not self.active_channels:
            self.active_channels = channel_config.get("default_active_channels", ["email", "social"])

        # Strategy parameters
        self.strategy_params = self._config.get("strategy_parameters", {})

    def generate_strategy(self, context: dict[str, str]) -> dict[str, str]:
        """
        Execute campaign strategy generation.
        """
        Logger.info(f"Generating strategy for {self.campaign_id}")
        # Logic implementation placeholder
        return {
            "status": "generated",
            "campaign_id": self.campaign_id,
            "channels": ",".join(self.active_channels),
        }
