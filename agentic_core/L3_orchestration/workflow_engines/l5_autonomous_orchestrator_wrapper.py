"""
L5 Autonomous Orchestrator - Thin Wrapper
Delegates to consolidated core orchestrator in agentic_core/core/orchestrator_main.py

This is a stub-and-proxy pattern implementation that eliminates race conditions
by routing all orchestration through the consolidated AtomicBlackboard-integrated core.
"""
import asyncio
import logging
import re

from agentic_core.core.orchestrator_main import (
    OrchestratorConfig,
    create_orchestrator,
)
from agentic_core.L1_cognition.P2_domain.context import ValidationContext

logger = logging.getLogger(__name__)


async def run_l5_outreach_orchestrator(
    campaign_id: str,
    archetype: str = "RECRUITER",
    max_cycles: int = 5,
    quality_threshold: float = 0.75,
    enable_intervention: bool = True
):
    """
    Run L5+ autonomous outreach orchestrator.
    
    This is a thin wrapper that delegates to the consolidated orchestrator.
    
    Args:
        campaign_id: Campaign identifier
        archetype: Campaign archetype
        max_cycles: Maximum cycles
        quality_threshold: Quality threshold
        enable_intervention: Enable human intervention
        
    Returns:
        Workflow execution results
    """
    logger.info(f"🚀 L5 Outreach Orchestrator (Wrapper)")
    logger.info(f"   Campaign: {campaign_id}")
    logger.info(f"   Archetype: {archetype}")
    
    config = OrchestratorConfig(
        max_cycles=max_cycles,
        quality_threshold=quality_threshold,
        enable_intervention=enable_intervention
    )
    
    context = ValidationContext()
    orchestrator = create_orchestrator(config=config, context=context)
    
    outreach_agent = create_outreach_agent(
        context=context,
        campaign_id=campaign_id,
        archetype=archetype,
        max_cycles=max_cycles,
        quality_threshold=quality_threshold,
        enable_intervention=enable_intervention
    )
    results = await orchestrator.execute_workflow(
        workflow_id=f"outreach_{campaign_id}",
        agents=[outreach_agent]
    )
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="L5 Outreach Orchestrator")
    parser.add_argument("--campaign-id", required=True, help="Campaign ID")
    parser.add_argument("--archetype", default="RECRUITER", help="Campaign archetype")
    parser.add_argument("--max-cycles", type=int, default=5, help="Max cycles")
    
    args = parser.parse_args()
    
    asyncio.run(run_l5_outreach_orchestrator(
        campaign_id=args.campaign_id,
        archetype=args.archetype,
        max_cycles=args.max_cycles
    ))
