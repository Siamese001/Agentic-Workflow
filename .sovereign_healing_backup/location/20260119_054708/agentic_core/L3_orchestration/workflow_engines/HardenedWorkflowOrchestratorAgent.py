from __future__ import annotations
from dataclasses import dataclass
"""
🚀 PHASE 5: THIN WRAPPER - Hardened Workflow Orchestrator

This is now a thin wrapper that delegates to the consolidated orchestrator_main.py
All orchestration logic has been moved to agentic_core/core/orchestrator_main.py

Legacy API preserved for backward compatibility.
"""

# DUPLICATE ACCEPTED: App-specific customization valid
# (different contexts: L3 hardened wrapper vs apps_lic/apps_rg implementations)
# - Intentional variant for domain-specific behavior
# - Consolidated 2026-01-06

import logging
import re
from typing import Any, Dict, List, Optional, Protocol
from agentic_core.utils.core_extensions.timeout_decorator import timeout
Logger: Any = logging.getLogger(__name__)
from agentic_core.core.orchestrator_main import OrchestratorConfig, create_orchestrator
from agentic_core.utils.core_extensions.healer_mixin import HealerMixin
from agentic_core.utils.core_extensions.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.L3_orchestration.workflow_engines.l3_subatomic_testing_mixin import L3SubatomicTestingMixin
from agentic_core.L5_safety.guardrails.mcp_hardened_mixin import MCPHardenedMixin
from agentic_core.utils.core_extensions.subatomic_testing_mixin import SubatomicTestingMixin
from agentic_core.utils.core_extensions.decorators import standard_heal

@dataclass
class HardenedWorkflowOrchestratorAgent(MCPHardenedMixin, HealerMixin, L3SubatomicTestingMixin):
    """
    Thin wrapper for Hardened Workflow Orchestrator.
    Delegates to ConsolidatedOrchestratorAgent.
    
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
        Logger.info('🔗 HardenedWorkflowOrchestratorAgent wrapper initialized (delegates to orchestrator_main)')

    async def initialize_or_resume_workflow(self, workflow_id: str, total_k_nodes: int, context: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize new workflow or resume from Checkpoint (legacy wrapper)."""
        Logger.info(f'🔗 Delegating workflow initialization to orchestrator_main')
        return context

    async def execute_workflow_with_resilience(self, workflow_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute workflow with resilience (delegates to orchestrator_main)."""
        Logger.info(f'🚀 Delegating workflow execution to orchestrator_main')
        results: Any = await self.orchestrator.run_mission(target_path=context.get('target_path'), workflow_id=workflow_id)
        return results

    @timeout(300)
    @standard_heal
    def heal_repository(self, dry_run: bool = True, execute: bool = False, depth: int = 0, max_depth: int = 3, _call_path: Optional[set] = None) -> Dict[str, int]:
        """L3 orchestration agent - operational only."""
        super().heal_repository(dry_run, execute, depth, max_depth, _call_path)
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            print(f"[{agent_name}] L3 orchestration - operational only")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)


def get_hardened_workflow_orchestrator() -> HardenedWorkflowOrchestratorAgent:
    """Factory function to get hardened workflow orchestrator instance."""
    # CRITICAL FIRST: Shared HealerMixin chain (diagnostics, rollback, MCP hardening)
    super().heal_repository()

    return HardenedWorkflowOrchestratorAgent()

def create_hardened_orchestrator(workflow_spec: Optional[Any]=None, run_base_dir: str='./pipeline_runs', storage_path: Optional[str]=None) -> HardenedWorkflowOrchestratorAgent:
    """Create a hardened orchestrator (thin wrapper to consolidated orchestrator).

    Args:
        workflow_spec: Workflow specification (legacy, not used)
        run_base_dir: Base directory for run outputs
        storage_path: Path for atomic state storage (legacy, not used)

    Returns:
        HardenedWorkflowOrchestratorAgent instance
    """
    return HardenedWorkflowOrchestratorAgent(workflow_spec=workflow_spec, run_base_dir=run_base_dir, storage_path=storage_path)
