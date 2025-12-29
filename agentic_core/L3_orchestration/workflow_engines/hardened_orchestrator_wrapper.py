"""
Hardened Orchestrator - Thin Wrapper
Delegates to consolidated core orchestrator in agentic_core/core/orchestrator_main.py

This is a stub-and-proxy pattern implementation that eliminates race conditions
by routing all orchestration through the consolidated AtomicBlackboard-integrated core.
"""
import asyncio
import logging
import re
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.core.orchestrator_main import OrchestratorConfig, create_orchestrator
from agentic_core.L1_cognition.P2_domain.context import ValidationContext
logger: Any = logging.getLogger(__name__)

async def run_hardened_orchestrator(workflow_id: str, workflow_type: str='resume_generation', storage_path: Optional[str]=None, run_base_dir: str='./pipeline_runs') -> Any:
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
    logger.info(f'🚀 Hardened Orchestrator (Wrapper)')
    logger.info(f'   Workflow: {workflow_id}')
    logger.info(f'   Type: {workflow_type}')
    config: Any = OrchestratorConfig(max_cycles=5, enable_checkpointing=True, checkpoint_dir=storage_path or './checkpoints')
    context: Any = ValidationContext()
    orchestrator: Any = create_orchestrator(config=config, context=context)
    resume_agent: Any = create_resume_agent(context=context, workflow_id=workflow_id, workflow_type=workflow_type, enable_titanium_rag=True, enable_state_persistence=True, storage_path=storage_path, run_base_dir=run_base_dir)
    results: Any = await orchestrator.execute_workflow(workflow_id=workflow_id, agents=[resume_agent])
    return results
if __name__ == '__main__':
    import argparse
    parser: Any = argparse.ArgumentParser(description='Hardened Orchestrator')
    parser.add_argument('--workflow-id', required=True, help='Workflow ID')
    parser.add_argument('--workflow-type', default='resume_generation', help='Workflow type')
    parser.add_argument('--storage-path', help='Storage path for state')
    args: Any = parser.parse_args()
    asyncio.run(run_hardened_orchestrator(workflow_id=args.workflow_id, workflow_type=args.workflow_type, storage_path=args.storage_path))
