from __future__ import annotations
"""
🚀 PHASE 5: THIN WRAPPER - SwarmScheduler for Canon Validator

This is now a thin wrapper that delegates to the consolidated orchestrator_main.py
All orchestration logic has been moved to agentic_core/core/orchestrator_main.py

Legacy API preserved for backward compatibility.
"""
import asyncio
import logging
from typing import Any, Dict, List, Optional, Protocol
Logger: Any = logging.getLogger(__name__)
from agentic_core.core.orchestrator_main import OrchestratorConfig, create_orchestrator

class SwarmScheduler:
    """
    Thin wrapper for Canon Validator SwarmScheduler.
    Delegates to ConsolidatedOrchestratorAgent.
    """

    def __init__(self):
        """Initialize SwarmScheduler wrapper."""
        self.ctx = ValidationContext()
        config = OrchestratorConfig(max_cycles=10, enable_healing=True, enable_intervention=True)
        self.orchestrator = create_orchestrator(config=config, context=self.ctx)
        Logger.info('🔗 SwarmScheduler wrapper initialized (delegates to orchestrator_main)')

    async def run_mission(self, target_scope: Optional[str]=None) -> Any:
        """Run the validation mission (delegates to orchestrator_main)."""
        Logger.info(f'🚀 Running Canon Validator mission')
        results: Any = await self.orchestrator.run_mission(target_path=target_scope, workflow_id='CanonValidatorAgent')
        return results
IntelligentOrchestratorAgent: Any = SwarmScheduler

async def main() -> Any:
    """Main entry point for the Canon Validator."""
    scheduler: Any = SwarmScheduler()
    await scheduler.run_mission()
if __name__ == '__main__':
    asyncio.run(main())
