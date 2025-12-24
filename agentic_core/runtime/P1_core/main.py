import asyncio
import logging
from agentic_core.runtime.P1_core.runtime_bootstrapper import RuntimeBootstrapper

# Configure logging to see the Sovereign Registry in action
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

async def ignite_sovereign_runtime():
    """
    Initializes the Sovereign environment and executes a test hop.
    """
    LOGGER.info("--- IGNITING SOVEREIGN RUNTIME ---")

    # 1. Define the Sovereign Configuration (The SSOT)
    # In production, this would be loaded from agentic_core/config/blueprint_sovereign/
    config = {
        "storage_path": "./data/storage",
        "log_level": "INFO",
        "budget_limit": 50.0,
        "pii_vault_enabled": True,
        "zero_trust_mode": "strict",
        "allowed_tools": ["read_file", "search_web", "run_python"]
    }

    # 2. Instantiate the Master Constructor
    bootstrapper = RuntimeBootstrapper(config)

    try:
        # 3. Assemble the Hop for a specific role
        # Notice how L3_orchestration doesn't need to know HOW to build a hop anymore
        hop = bootstrapper.assemble_hop(role="research_specialist")

        # 4. Execute a Mission
        context = {
            "task": "Analyze current gravity leaks in the L0 maintenance layer.",
            "trace_id": "mission-001-sovereign",
            "priority": "high"
        }

        LOGGER.info("Executing Sovereign Hop...")
        result = await hop.run(context)
        
        print(f"\n[MISSION COMPLETE]\nResult: {result}")

    except Exception as e:
        LOGGER.error(f"Sovereign Runtime Failure: {str(e)}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(ignite_sovereign_runtime())
