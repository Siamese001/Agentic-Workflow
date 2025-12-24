"""
🚀 PHASE 5: THIN WRAPPER - SwarmScheduler for Canon Validator

This is now a thin wrapper that delegates to the consolidated orchestrator_main.py
All orchestration logic has been moved to agentic_core/core/orchestrator_main.py

Legacy API preserved for backward compatibility.
"""

import asyncio
import logging
from typing import Optional
from typing import Any, Optional, Protocol, Dict, List

logger = logging.getLogger(__name__)

# Phase 5: Import from consolidated orchestrator
from agentic_core.core.orchestrator_main import (
    OrchestratorConfig,
    create_orchestrator,
)
from agentic_core.L1_cognition.P2_domain.context import ValidationContext


class SwarmScheduler:
    """
    Thin wrapper for Canon Validator SwarmScheduler.
    Delegates to ConsolidatedOrchestrator.
    """

    def __init__(self):
        """Initialize SwarmScheduler wrapper."""
        self.ctx = ValidationContext()
        
        # Create config for consolidated orchestrator
        config = OrchestratorConfig(
            max_cycles=10,
            enable_healing=True,
            enable_intervention=True,
        )
        
        # Delegate to consolidated orchestrator
        self.orchestrator = create_orchestrator(config=config, context=self.ctx)
        
        logger.info("🔗 SwarmScheduler wrapper initialized (delegates to orchestrator_main)")

    async def run_mission(self, target_scope: Optional[str] = None):
        """Run the validation mission (delegates to orchestrator_main)."""
        logger.info(f"🚀 Running Canon Validator mission")
        
        results = await self.orchestrator.run_mission(
            target_path=target_scope,
            workflow_id="canon_validator"
        )
        
        return results



# Legacy alias for backward compatibility
IntelligentOrchestrator = SwarmScheduler


async def main():
    """Main entry point for the Canon Validator."""
    scheduler = SwarmScheduler()
    await scheduler.run_mission()


if __name__ == "__main__":
    asyncio.run(main())