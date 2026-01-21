
# SEMANTIC SIGNAL AUTO-INSERTED (NamingAgent Enhancement)
# File appears to be a sovereign component but missing canon high-signal keywords.
# Suggested keywords to add in docstring/code: engine, guardrail, healer, memory, prompt, state
# This boosts alignment detection — review and integrate appropriately

from __future__ import annotations
"""
L5 Autonomous Orchestrator - Thin Wrapper
Delegates to consolidated core orchestrator in agentic_core/core/orchestrator_main.py

This is a stub-and-proxy pattern implementation that eliminates race conditions
by routing all orchestration through the consolidated AtomicBlackboard-integrated core.
"""
import asyncio
import logging
import re
from agentic_core.core.orchestrator_main import OrchestratorConfig, create_orchestrator
from agentic_core.L1_cognition.P2_domain.context import ValidationContext

# [SSOT IMPORT] Structure blueprint is the single source of truth
from typing import Any
from agentic_core.L5_safety.validators.structure_blueprint import (
    SOVEREIGN_REGISTRY,
    CORE_SUBFOLDER_MAP,
)

Logger: Any = logging.getLogger(__name__)

async def run_l5_outreach_orchestrator(campaign_id: str, Archetype: str='RECRUITER', max_cycles: int=5, quality_threshold: float=0.75, enable_intervention: bool=True) -> Any:
    """
    Run L5+ autonomous outreach orchestrator.

    This is a thin wrapper that delegates to the consolidated orchestrator.

    Args:
        campaign_id: Campaign identifier
        Archetype: Campaign Archetype
        max_cycles: Maximum cycles
        quality_threshold: Quality threshold
        enable_intervention: Enable human intervention

    Returns:
        Workflow execution results
    """
    Logger.info(f'🚀 L5 Outreach Orchestrator (Wrapper)')
    Logger.info(f'   Campaign: {campaign_id}')
    Logger.info(f'   Archetype: {Archetype}')
    config: Any = OrchestratorConfig(max_cycles=max_cycles, quality_threshold=quality_threshold, enable_intervention=enable_intervention)
    context: Any = ValidationContext()
    orchestrator: Any = create_orchestrator(config=config, context=context)
    outreach_agent: Any = create_outreach_agent(context=context, campaign_id=campaign_id, Archetype=Archetype, max_cycles=max_cycles, quality_threshold=quality_threshold, enable_intervention=enable_intervention)
    results: Any = await orchestrator.execute_workflow(workflow_id=f'outreach_{campaign_id}', agents=[outreach_agent])
    return results
if __name__ == '__main__':
    import argparse
    parser: Any = argparse.ArgumentParser(description='L5 Outreach Orchestrator')
    parser.add_argument('--campaign-id', required=True, help='Campaign ID')
    parser.add_argument('--Archetype', default='RECRUITER', help='Campaign Archetype')
    parser.add_argument('--max-cycles', type=int, default=5, help='Max cycles')
    args: Any = parser.parse_args()
    asyncio.run(run_l5_outreach_orchestrator(campaign_id=args.campaign_id, Archetype=args.Archetype, max_cycles=args.max_cycles))
