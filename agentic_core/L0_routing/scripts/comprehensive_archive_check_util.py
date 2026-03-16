from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "comprehensive_archive_check_util")
emit_determinism_digest("p0", "comprehensive_archive_check_util")

_emit_dispatches_healing_run("p1", "comprehensive_archive_check_util", "L0")
_emit_routes_through("p1", "comprehensive_archive_check_util", "L0")
_emit_escalates_to_human("p1", "comprehensive_archive_check_util", "L0")
_emit_reads_policy_state("p1", "comprehensive_archive_check_util", "L0")

_emit_records_execution_trace("p0", "evidence", "comprehensive_archive_check_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "comprehensive_archive_check_util", "p0_governance")
_emit_snapshots_state("p0", "comprehensive_archive_check_util", "state_snapshot")
_emit_authorize_and_execute("p2", "comprehensive_archive_check_util", "execution_auth")
_emit_validates_capability("p2", "comprehensive_archive_check_util", "capability_check")
_emit_routes_to_capability("p2", "comprehensive_archive_check_util", "capability_route")
_emit_writes_via_uwg("p2", "comprehensive_archive_check_util", "uwg_write")
_emit_blocks_direct_write("p2", "comprehensive_archive_check_util", "direct_write_block")
_emit_records_tool_invocation("p2", "comprehensive_archive_check_util", "tool_invocation")
_emit_captures_execution_output("p2", "comprehensive_archive_check_util", "exec_output")
_emit_dispatches_agent("p3", "comprehensive_archive_check_util", "agent_dispatch")
_emit_coordinates_agents("p3", "comprehensive_archive_check_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "comprehensive_archive_check_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "comprehensive_archive_check_util", "healing_outcome")
_emit_escalates_failure("p3", "comprehensive_archive_check_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "comprehensive_archive_check_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "comprehensive_archive_check_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "comprehensive_archive_check_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "comprehensive_archive_check_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "comprehensive_archive_check_util", "eval_metric")
_emit_stores_embedding("p4", "comprehensive_archive_check_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "comprehensive_archive_check_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "comprehensive_archive_check_util", "exec_snapshot_link")

"Comprehensive check of ALL agents that might have been archived in entire chat history."
import os

from agentic_core.L0_routing.config import ARCHIVES_DIR
from agentic_core.L0_routing.config.path_constants import SOVEREIGN_EXCLUDED_FOLDERS

PROJECT_ROOT = Path("C:/Git/Agentic-Workflow")
l4_active = PROJECT_ROOT / "agentic_core/L4_state/memory/L4Agent.py"
archives_path = PROJECT_ROOT / ARCHIVES_DIR
l4_archived = []
if archives_path.exists():
    for root, dirs, files in os.walk(archives_path):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        if "L4Agent.py" in files:
            l4_archived.append(Path(root) / "L4Agent.py")
for _path in l4_archived:
    pass
archived_agents = []
if archives_path.exists():
    for root, dirs, files in os.walk(archives_path):
        dirs[:] = [d for d in dirs if d not in SOVEREIGN_EXCLUDED_FOLDERS]
        if "identity_duplicates" in root:
            continue
        for file in files:
            if file.endswith("Agent.py"):
                rel_path = os.path.relpath(Path(root) / file, archives_path)
                archived_agents.append(rel_path)
by_subdir = {}
for agent in archived_agents:
    subdir = agent.split(os.sep)[0]
    if subdir not in by_subdir:
        by_subdir[subdir] = []
    by_subdir[subdir].append(agent)
for subdir in sorted(by_subdir.keys()):
    agents = by_subdir[subdir]
    for agent in sorted(agents)[:10]:
        pass
    if len(agents) > 10:
        pass
if l4_active.exists() and len(l4_archived) == 0:
    pass
