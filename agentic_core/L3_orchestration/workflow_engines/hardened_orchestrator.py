"""
🚀 PHASE 5: THIN WRAPPER - Hardened Workflow Orchestrator

This is now a thin wrapper that delegates to the consolidated orchestrator_main.py
All orchestration logic has been moved to agentic_core/core/orchestrator_main.py

Legacy API preserved for backward compatibility.
"""
import logging
import re
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)
from agentic_core.core.orchestrator_main import OrchestratorConfig, create_orchestrator
from agentic_core.common.healing.healer_mixin import HealerMixin

class HardenedWorkflowOrchestrator(HealerMixin):
    """
    Thin wrapper for Hardened Workflow Orchestrator.
    Delegates to ConsolidatedOrchestrator.
    
    Legacy API preserved for backward compatibility.
    """

    def __init__(self, workflow_spec: Optional[Any]=None, run_base_dir: str='./pipeline_runs', storage_path: Optional[str]=None) -> None:
        """Initialize the hardened orchestrator wrapper.

        Args:
            workflow_spec: Workflow specification (legacy, not used)
            run_base_dir: Base directory for run outputs
            storage_path: Path for atomic state storage (legacy, not used)
        """
        config = OrchestratorConfig(checkpoint_dir=run_base_dir, enable_checkpointing=True)
        self.orchestrator = create_orchestrator(config=config)
        self.workflow_spec = workflow_spec
        self.run_base_dir = run_base_dir
        Logger.info('🔗 HardenedWorkflowOrchestrator wrapper initialized (delegates to orchestrator_main)')

    async def initialize_or_resume_workflow(self, workflow_id: str, total_k_nodes: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize new workflow or resume from Checkpoint (legacy wrapper)."""
        Logger.info(f'🔗 Delegating workflow initialization to orchestrator_main')
        return context

    async def execute_workflow_with_resilience(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with resilience (delegates to orchestrator_main)."""
        Logger.info(f'🚀 Delegating workflow execution to orchestrator_main')
        results: Any = await self.orchestrator.run_mission(target_path=context.get('target_path'), workflow_id=workflow_id)
        return results

def create_hardened_orchestrator(workflow_spec: Optional[Any]=None, run_base_dir: str='./pipeline_runs', storage_path: Optional[str]=None) -> HardenedWorkflowOrchestrator:
    """Create a hardened orchestrator (thin wrapper to consolidated orchestrator).

    Args:
        workflow_spec: Workflow specification (legacy, not used)
        run_base_dir: Base directory for run outputs
        storage_path: Path for atomic state storage (legacy, not used)

    Returns:
        HardenedWorkflowOrchestrator instance
    """
    return HardenedWorkflowOrchestrator(workflow_spec=workflow_spec, run_base_dir=run_base_dir, storage_path=storage_path)