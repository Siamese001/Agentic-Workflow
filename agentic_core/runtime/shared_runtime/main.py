import asyncio
import logging

from agentic_core.runtime.P1_core.runtime_bootstrapper import RuntimeBootstrapper

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

async def main():
    """
    Day Zero: Running the first 100% Sovereign-Compliant Agentic Mission.
    """
    # 1. The Global SSOT
    config = {
        "storage_path": "./data/sovereign_output",
        "budget_limit": 25.0,
        "allowed_tools": ["read_file", "search_web", "run_python"],
        "mission_scope": "system_refactoring",
        "model_name": "gemini-2.0-flash"
    }

    # 2. Ignite the Bootstrapper
    bootstrapper = RuntimeBootstrapper(config)

    try:
        # 3. Assemble a specific Agent
        hop = bootstrapper.assemble_hop(role="principal_architect")

        # 4. Fire the mission
        mission = {
            "task": "Review the L5 safety guardrails for potential bypasses.",
            "trace_id": "SOVEREIGN-BETA-001"
        }

        print("\n🚀 [SYSTEM ONLINE] - Executing Sovereign Hop...\n")
        final_output = await hop.run(mission)
        
        print(f"\n✅ [MISSION COMPLETE]\nOutput: {final_output}")

    except Exception as e:
        print(f"\n❌ [CRITICAL FAILURE]: {e}")

if __name__ == "__main__":
    asyncio.run(main())
