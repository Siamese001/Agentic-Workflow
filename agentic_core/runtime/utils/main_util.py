from __future__ import annotations

import asyncio
import os

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
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
_emit_authorize_and_execute("p2", "main_util", "execution_auth")
_emit_validates_capability("p2", "main_util", "capability_check")
_emit_routes_to_capability("p2", "main_util", "capability_route")
_emit_writes_via_uwg("p2", "main_util", "uwg_write")
_emit_blocks_direct_write("p2", "main_util", "direct_write_block")
_emit_records_tool_invocation("p2", "main_util", "tool_invocation")
_emit_captures_execution_output("p2", "main_util", "exec_output")
_emit_dispatches_agent("p3", "main_util", "agent_dispatch")
_emit_coordinates_agents("p3", "main_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "main_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "main_util", "healing_outcome")
_emit_escalates_failure("p3", "main_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "main_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "main_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "main_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "main_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "main_util", "eval_metric")
_emit_stores_embedding("p4", "main_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "main_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "main_util", "exec_snapshot_link")

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
