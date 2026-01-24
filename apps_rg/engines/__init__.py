"""
apps_rg/engines/__init__.py - Sovereign Engine Registry

Exposes all V2.5 compliant RGAgentBase agents.
All agents in this module inherit from RGAgentBase and follow
the Sovereign Architecture pattern.
"""

from __future__ import annotations

# V2.5 Compliant Agents - All inherit from RGAgentBase
from .ATSCompatibilityAgent import ATSCompatibilityAgent
from .BrandComplianceAgent import BrandComplianceAgent
from .CampaignPlannerAgent import CampaignPlannerAgent
from .ContentQualityAgent import ContentQualityAgent, TestPilot
from .ContentStrategyAgent import ContentStrategyAgent
from .FactCheckAgent import FactCheckAgent
from .ProactiveAgent import ProactiveAgent
from .RgHealingOrchestratorAgent import RgHealingOrchestratorAgent
from .RgReflectionAgent import RgReflectionAgent
from .RgResumeOrchestratorAgent import RgResumeOrchestratorAgent
from .RgStrategicPlannerAgent import RgStrategicPlannerAgent
from .RgTemplateOptimizerAgent import RgTemplateOptimizerAgent
from .SectionBalanceAgent import SectionBalanceAgent

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
]

# Stub for backward compatibility
class AsyncOpenAI:  # pragma: no cover - stub for tests
    def __init__(self, *args, **kwargs):
        pass
