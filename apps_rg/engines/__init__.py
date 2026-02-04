"""
apps_rg/engines/__init__.py - Sovereign Engine Registry

Exposes all V2.5 compliant RGAgentBase agents.
All agents in this module inherit from RGAgentBase and follow
the Sovereign Architecture pattern.
"""

from __future__ import annotations

from apps_shared.common_utils.Provider import Provider

# [Diff Start: Export AgentExecutor]
from .agent_executor import (
    AgentConfig,
    AgentExecutor,
    AgentMessage,
    AgentResponse,
    create_agent_executor,
)

# V2.5 Compliant Agents - All inherit from RGAgentBase
from .ats_compatibility_agent import ATSCompatibilityAgent
from .brand_compliance_agent import BrandComplianceAgent
from .CampaignPlannerAgent import CampaignPlannerAgent
from .ContentQualityAgent import ContentQualityAgent, TestPilot
from .ContentStrategyAgent import ContentStrategyAgent
from .FactCheckAgent import FactCheckAgent
from .HardenedanthropicexecutorStrategy import HardenedAnthropicExecutor
from .HardenedopenaiexecutorStrategy import HardenedOpenAIExecutor
from .ProactiveAgent import ProactiveAgent
from .RgHealingOrchestratorAgent import RgHealingOrchestratorAgent
from .RgReflectionAgent import RgReflectionAgent
from .RgResumeOrchestratorAgent import RgResumeOrchestratorAgent
from .RgStrategicPlannerAgent import RgStrategicPlannerAgent
from .RgTemplateOptimizerAgent import RgTemplateOptimizerAgent

# Core Engine Components
# Router, schema, and strategist_biowriter modules not yet implemented
# from .Router import HardenedRouter as Router
# from .schema import ProviderType, RouteConfig, RouterConfig, RouteResult, RoutingTier
from .SectionBalanceAgent import SectionBalanceAgent

# from .strategist_biowriter import strategist_bio_writer

# [Diff End]

__all__ = [
    # Content Quality & Validation
    "ATSCompatibilityAgent",
    "BrandComplianceAgent",
    "ContentQualityAgent",
    "FactCheckAgent",
    "SectionBalanceAgent",
    "TestPilot",
    # Strategy & Planning
    "CampaignPlannerAgent",
    "ContentStrategyAgent",
    "RgStrategicPlannerAgent",
    "RgTemplateOptimizerAgent",
    # Orchestration & Healing
    "RgHealingOrchestratorAgent",
    "RgReflectionAgent",
    "RgResumeOrchestratorAgent",
    "ProactiveAgent",
    # Core Engine Components
    "Router",
    "HardenedRouter",
    "HardenedAnthropicExecutor",
    "HardenedOpenAIExecutor",
    "StrategistBioWriter",
    "RouterConfig",
    "RouteResult",
    "ProviderType",
    "RouteConfig",
    "RoutingTier",
    "AgentExecutor",
    "AgentConfig",
    "AgentMessage",
    "AgentResponse",
    "create_agent_executor",
    "Provider",
]


# Stub for backward compatibility
class AsyncOpenAI:  # pragma: no cover - stub for tests
    def __init__(self, *args, **kwargs):
        pass
