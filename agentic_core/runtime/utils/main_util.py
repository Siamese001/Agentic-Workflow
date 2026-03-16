from __future__ import annotations

import asyncio
import os

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "main_util")
_emit_applies_guardrail("p0", "main_util", "p0_governance")
_emit_reads_policy_state("p0", "main_util", "policy_binding")
_emit_snapshots_state("p0", "main_util", "state_snapshot")
emit_replay_key("p0", "main_util")
emit_determinism_digest("p0", "main_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)

"Brief description of functionality and purpose."
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
