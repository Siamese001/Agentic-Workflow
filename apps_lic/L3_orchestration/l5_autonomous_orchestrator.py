"""
🚀 PHASE 5: THIN WRAPPER - L5+ Autonomous Orchestrator for Outreach Engine

This is now a thin wrapper that delegates to the consolidated orchestrator_main.py
All orchestration logic has been moved to agentic_core/core/orchestrator_main.py

Legacy API preserved for backward compatibility.
"""

import asyncio
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Phase 5: Import from consolidated orchestrator
from agentic_core.core.orchestrator_main import (
    ConsolidatedOrchestrator,
    OrchestratorConfig,
    create_orchestrator,
)


class L5OutreachOrchestrator:
    """
    Thin wrapper for L5+ Outreach Orchestrator.
    Delegates to ConsolidatedOrchestrator.
    """
    
    def __init__(
        self,
        campaign_id: str,
        archetype: str = "RECRUITER",
        max_cycles: int = 5,
        quality_threshold: float = 0.75,
        enable_intervention: bool = True,
    ):
        """Initialize L5+ outreach orchestrator."""
        self.campaign_id = campaign_id
        self.archetype = archetype
        
        # Create config for consolidated orchestrator
        config = OrchestratorConfig(
            max_cycles=max_cycles,
            quality_threshold=quality_threshold,
            enable_intervention=enable_intervention,
        )
        
        # Delegate to consolidated orchestrator
        self.orchestrator = create_orchestrator(config=config)
        
        logger.info(f"🔗 L5OutreachOrchestrator wrapper initialized (delegates to orchestrator_main)")
    
    async def run(self, target_path: Optional[str] = None):
        """Run the orchestration mission."""
        logger.info(f"🚀 Running L5+ Outreach Orchestrator for campaign: {self.campaign_id}")
        
        results = await self.orchestrator.run_mission(
            target_path=target_path,
            workflow_id=f"outreach_{self.campaign_id}"
        )
        
        return results


def create_l5_outreach_orchestrator(
    campaign_id: str,
    archetype: str = "RECRUITER",
    max_cycles: int = 5,
    quality_threshold: float = 0.75,
    enable_intervention: bool = True,
) -> L5OutreachOrchestrator:
    """Factory function to create L5+ outreach orchestrator."""
    return L5OutreachOrchestrator(
        campaign_id=campaign_id,
        archetype=archetype,
        max_cycles=max_cycles,
        quality_threshold=quality_threshold,
        enable_intervention=enable_intervention,
    )
