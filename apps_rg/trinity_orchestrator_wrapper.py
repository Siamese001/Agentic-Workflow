"""
Trinity Orchestrator - Thin Wrapper
Delegates to consolidated core orchestrator in agentic_core/core/orchestrator_main.py

This is a stub-and-proxy pattern implementation that eliminates race conditions
by routing all orchestration through the consolidated AtomicBlackboard-integrated core.
"""

import asyncio
import logging

from agentic_core.agents.specialized.resume_agent import create_resume_agent
from agentic_core.core.orchestrator_main import (
    OrchestratorConfig,
    create_orchestrator,
)
from agentic_core.domain.context import ValidationContext

logger = logging.getLogger(__name__)


async def run_trinity_orchestrator(
    user_goal: str,
    workflow_id: str = "trinity_workflow"
):
    """
    Run Trinity orchestrator (Cognitive + Action).
    
    This is a thin wrapper that delegates to the consolidated orchestrator.
    
    Args:
        user_goal: User goal for the agent
        workflow_id: Workflow identifier
        
    Returns:
        Workflow execution results
    """
    logger.info(f"🚀 Trinity Orchestrator (Wrapper)")
    logger.info(f"   Goal: {user_goal}")
    
    config = OrchestratorConfig(
        max_cycles=5,
        enable_intervention=False
    )
    
    context = ValidationContext()
    orchestrator = create_orchestrator(config=config, context=context)
    
    resume_agent = create_resume_agent(
        context=context,
        workflow_id=workflow_id,
        workflow_type="trinity_cognitive_action"
    )
    
    results = await orchestrator.execute_workflow(
        workflow_id=workflow_id,
        agents=[resume_agent]
    )
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Trinity Orchestrator")
    parser.add_argument(
        "goal",
        nargs="?",
        default="I need to write a function that prevents hallucinations by separating thinking from doing.",
        help="User goal for the agent"
    )
    
    args = parser.parse_args()
    
    asyncio.run(run_trinity_orchestrator(user_goal=args.goal))
