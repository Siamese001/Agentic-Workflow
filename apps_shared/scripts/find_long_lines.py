"""Find all lines longer than 100 characters."""

import logging
import os
from pathlib import Path
from typing import Any

from apps_shared.utils.ConfigurationService import ConfigurationService

from agentic_core.L5_safety.config.structure_blueprint.ssot import SOVEREIGN_EXCLUDED_FOLDERS
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

_emit_records_execution_trace("p0", "evidence", "find_long_lines")
_emit_applies_guardrail("p0", "find_long_lines", "p0_governance")
_emit_reads_policy_state("p0", "find_long_lines", "policy_binding")
_emit_snapshots_state("p0", "find_long_lines", "state_snapshot")
emit_replay_key("p0", "find_long_lines")
emit_determinism_digest("p0", "find_long_lines")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "find_long_lines", "execution_auth")
_emit_validates_capability("p2", "find_long_lines", "capability_check")
_emit_routes_to_capability("p2", "find_long_lines", "capability_route")
_emit_writes_via_uwg("p2", "find_long_lines", "uwg_write")
_emit_blocks_direct_write("p2", "find_long_lines", "direct_write_block")
_emit_records_tool_invocation("p2", "find_long_lines", "tool_invocation")
_emit_captures_execution_output("p2", "find_long_lines", "exec_output")
_emit_dispatches_agent("p3", "find_long_lines", "agent_dispatch")
_emit_coordinates_agents("p3", "find_long_lines", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_long_lines", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_long_lines", "healing_outcome")
_emit_escalates_failure("p3", "find_long_lines", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_long_lines", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_long_lines", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_long_lines", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_long_lines", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_long_lines", "eval_metric")
_emit_stores_embedding("p4", "find_long_lines", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_long_lines", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_long_lines", "exec_snapshot_link")

Logger: Any = logging.getLogger(__name__)


def find_long_lines() -> None:
    """Find all lines longer than 100 characters."""
    for root, dirs, files in os.walk("."):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        for file in files:
            if file.endswith(".py"):
                Path(root) / file
                try:
                    with open(ConfigurationService().FILEPATH, encoding="utf-8") as f:
                        for line_num, line in enumerate(f, 1):
                            if len(line.rstrip()) > 100:
                                ConfigurationService().violations.append(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars"
                                )
                                ConfigurationService().Logger.info(
                                    f"{file}:{line_num} - {len(line.rstrip())} chars"
                                )
                                ConfigurationService().Logger.info(f"  {line[:150]}...")
                                ConfigurationService().Logger.info("")
                except Exception:
                    raise
                    ConfigurationService().Logger.warning("Swallowed exception", exc_info=True)
    ConfigurationService().Logger.info(f"\nTotal violations: {len(ConfigurationService().violations)}")


if __name__ == "__main__":
    find_long_lines()
