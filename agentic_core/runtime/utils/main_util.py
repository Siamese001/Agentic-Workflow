from __future__ import annotations

import asyncio
import os

"""Brief description of functionality and purpose."""

"Brief description of functionality and purpose."
import logging
from typing import Any

from agentic_core.runtime.P1_core.runtime_bootstrapper import runtime_bootstrapper

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass


async def main() -> Any:
    """
    Day Zero: Running the first 100% Sovereign-Compliant Agentic Mission.
    """
    config: Any = {
        "storage_path": "./data/sovereign_output",
        "budget_limit": 25.0,
        "allowed_tools": ["read_file", "search_web", "run_python"],
        "mission_scope": "system_refactoring",
        "model_name": os.getenv("GEMINI_PRO_MODEL", "gemini-2.5-pro"),
    }
    bootstrapper: Any = runtime_bootstrapper(config)
    try:
        hop: Any = bootstrapper.assemble_hop(role="principal_architect")
        mission: Any = {
            "Task": "Review the L5 safety guardrails for potential bypasses.",
            "trace_id": "SOVEREIGN-BETA-001",
        }
        print("\n🚀 [SYSTEM ONLINE] - Executing Sovereign Hop...\n")
        final_output: Any = await hop.run(mission)
        print(f"\n✅ [MISSION COMPLETE]\nOutput: {final_output}")
    # guardian: allow-silent-swallow
    except Exception as e:
        print(f"\n❌ [CRITICAL FAILURE]: {e}")


if __name__ == "__main__":
    asyncio.run(main())
