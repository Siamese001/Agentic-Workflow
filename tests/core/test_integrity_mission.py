The provided Python code is already very well-structured and adheres to most PEP 8 style guidelines. There are no syntax violations. The only minor style improvement that can be made is adding a return type hint to the `run_integrity_mission` function, as it does not explicitly return a value.

Here's the healed code with the addition of `-> None` for the function's return type hint:

```python
import asyncio
import logging

# Third-party / Project-specific imports
from agentic_core.L1_cognition.P1_interfaces import OrchestratorConfig
from agentic_core.L3_orchestration.nervous_system import NervousSystem

# Setup high-visibility logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("Phase1_Mission")


async def run_integrity_mission() -> None:  # Added return type hint
    """
    Executes an integrity mission using the Agentic Core Nervous System.

    This mission performs a Phase 1 integrity check, configures the orchestrator,
    boots the nervous system, runs the mission, and reports the results,
    including success status, output, success rate, and any errors.
    """
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

    # Calculate and log success rate
    success_rate_value = result.metadata.get('success_rate', 0)
    logger.info(f"Success Rate: {success_rate_value * 100:.1f}%")

    if result.errors:
        logger.error(f"Integrity Violations Found: {result.errors}")
    else:
        logger.info("✅ Project Integrity Asserted.")


if __name__ == "__main__":
    asyncio.run(run_integrity_mission())
```