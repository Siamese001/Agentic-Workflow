import asyncio
import logging

from agentic_core.L3_orchestration.pilot_orchestrator import PilotOrchestrator
from agentic_core.L2_execution.pilot_executor import PilotExecutor

async def main():
    logging.basicConfig(level=logging.INFO)

    orchestrator = PilotOrchestrator()
    executor = PilotExecutor()

    result = await orchestrator.run_pilot("Generate a minimal plan", executor)
    print("Pilot result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
