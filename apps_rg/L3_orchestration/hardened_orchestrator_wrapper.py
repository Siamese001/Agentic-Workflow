"""
Hardened Orchestrator - Thin Wrapper
Delegates to consolidated core orchestrator in agentic_core/core/orchestrator_main.py

This is a stub-and-proxy pattern implementation that eliminates race conditions
by routing all orchestration through the consolidated AtomicBlackboard-integrated core.
"""

import asyncio
import logging
from typing import Optional

from agentic_core.agents.specialized.resume_agent import create_resume_agent
from agentic_core.core.orchestrator_main import (
    OrchestratorConfig,
    create_orchestrator,
)
from agentic_core.domain.context import ValidationContext

logger = logging.getLogger(__name__)


async def run_hardened_orchestrator(
    workflow_id: str,
    workflow_type: str = "resume_generation",
    storage_path: Optional[str] = None,
    run_base_dir: str = "./pipeline_runs"
):
    """
    Run hardened workflow orchestrator with atomic state management.
    
    This is a thin wrapper that delegates to the consolidated orchestrator.
    
    Args:
        workflow_id: Workflow identifier
        workflow_type: Type of workflow
        storage_path: Path for atomic state storage
        run_base_dir: Base directory for run outputs
        
    Returns:
        Workflow execution results
    """
    logger.info(f"🚀 Hardened Orchestrator (Wrapper)")
    logger.info(f"   Workflow: {workflow_id}")
    logger.info(f"   Type: {workflow_type}")
    
    config = OrchestratorConfig(
        max_cycles=5,
        enable_checkpointing=True,
        checkpoint_dir=storage_path or "./checkpoints"
    )
    
    context = ValidationContext()
    orchestrator = create_orchestrator(config=config, context=context)
    
    resume_agent = create_resume_agent(
        context=context,
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        enable_titanium_rag=True,
        enable_state_persistence=True,
        storage_path=storage_path,
        run_base_dir=run_base_dir
    )
    
    results = await orchestrator.execute_workflow(
        workflow_id=workflow_id,
        agents=[resume_agent]
    )
    
    return results


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Hardened Orchestrator")
    parser.add_argument("--workflow-id", required=True, help="Workflow ID")
    parser.add_argument("--workflow-type", default="resume_generation", help="Workflow type")
    parser.add_argument("--storage-path", help="Storage path for state")
    
    args = parser.parse_args()
    
    asyncio.run(run_hardened_orchestrator(
        workflow_id=args.workflow_id,
        workflow_type=args.workflow_type,
        storage_path=args.storage_path
    ))
