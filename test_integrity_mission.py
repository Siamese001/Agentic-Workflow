import asyncio
import logging

from agentic_core.interfaces import OrchestratorConfig
from agentic_core.L3_orchestration.nervous_system import NervousSystem

# Setup high-visibility logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Phase1_Mission")

async def run_integrity_mission():
    # 1. Configure the Mission
    config = OrchestratorConfig(
        mission_id="integrity-scan-alpha",
        max_phases=1,  # Only run Phase 1 for this test
        enable_tri_brain=True,
        timeout_seconds=60
    )
    
    # 2. Boot the Nervous System
    logger.info("Initializing Agentic Core Nervous System...")
    ns = NervousSystem(config=config)
    
    # 3. Execute the Mission
    # This will trigger L1 Discovery (Historian/Governor) -> L2 Execution (Toolsmith)
    logger.info("Starting Phase 1: Integrity Check...")
    result = await ns.run_mission()
    
    # 4. Report Results
    logger.info(f"Mission Success: {result.success}")
    logger.info(f"Mission Output: {result.output}")
    logger.info(f"Success Rate: {result.metadata.get('success_rate', 0)*100:.1f}%")
    
    if result.errors:
        logger.error(f"Integrity Violations Found: {result.errors}")
    else:
        logger.info("✅ Project Integrity Asserted.")

if __name__ == "__main__":
    asyncio.run(run_integrity_mission())
