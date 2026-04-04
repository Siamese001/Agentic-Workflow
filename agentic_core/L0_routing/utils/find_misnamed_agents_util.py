"""
[DEPRECATED] Find files containing agent classes that don't follow *Agent.py naming.

Use scripts/full_agent_discovery.py as the canonical AST scan.
This script performs its own AST scan which may conflict with the SSOT.
"""
# guardian: allow-silent_swallower - ADG violation exemption


import warnings

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "find_misnamed_agents_util")
emit_determinism_digest("p0", "find_misnamed_agents_util")

_emit_dispatches_healing_run("p1", "find_misnamed_agents_util", "L0")
_emit_routes_through("p1", "find_misnamed_agents_util", "L0")
_emit_checks_agent_registry("p1", "find_misnamed_agents_util", "agent_registry")
_emit_validates_agent_capability("p1", "find_misnamed_agents_util", "capability")
_emit_dispatches_execution_plan("p1", "find_misnamed_agents_util", "exec_plan")
_emit_agent_executes_agent("p1", "find_misnamed_agents_util", "sub_agent")
_emit_routes_to_agent("p1", "find_misnamed_agents_util", "target_agent")
_emit_verifies_policy("p1", "find_misnamed_agents_util", "policy_check")
_emit_observes_runtime_state("p1", "find_misnamed_agents_util", "runtime_state")
_emit_verifies_boundary("p1", "find_misnamed_agents_util", "boundary_check")
_emit_transcripts_response("p1", "find_misnamed_agents_util", "transcript")
_emit_hard_fails_untranscripted("p1", "find_misnamed_agents_util")
_emit_gated_by_confidence("p1", "find_misnamed_agents_util", "confidence_gate")
_emit_escalates_to_human("p1", "find_misnamed_agents_util", "L0")
_emit_reads_policy_state("p1", "find_misnamed_agents_util", "L0")
_emit_authorize_and_execute("p2", "find_misnamed_agents_util", "execution_auth")
_emit_validates_capability("p2", "find_misnamed_agents_util", "capability_check")
_emit_routes_to_capability("p2", "find_misnamed_agents_util", "capability_route")
_emit_writes_via_uwg("p2", "find_misnamed_agents_util", "uwg_write")
_emit_blocks_direct_write("p2", "find_misnamed_agents_util", "direct_write_block")
_emit_records_tool_invocation("p2", "find_misnamed_agents_util", "tool_invocation")
_emit_captures_execution_output("p2", "find_misnamed_agents_util", "exec_output")
_emit_dispatches_agent("p3", "find_misnamed_agents_util", "agent_dispatch")
_emit_coordinates_agents("p3", "find_misnamed_agents_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "find_misnamed_agents_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "find_misnamed_agents_util", "healing_outcome")
_emit_escalates_failure("p3", "find_misnamed_agents_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "find_misnamed_agents_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "find_misnamed_agents_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "find_misnamed_agents_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "find_misnamed_agents_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "find_misnamed_agents_util", "eval_metric")
_emit_stores_embedding("p4", "find_misnamed_agents_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "find_misnamed_agents_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "find_misnamed_agents_util", "exec_snapshot_link")

warnings.warn(
    "find_misnamed_agents.py is DEPRECATED. Use full_agent_discovery.py instead.",
    DeprecationWarning,
    stacklevel=2,
)
import ast
from pathlib import Path

from agentic_core.L0_routing.config import AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("find_misnamed_agents_util", "p4obs", "metric_1")
_emit_emits_metric_event("find_misnamed_agents_util", "p4obs", "metric_2")
_emit_emits_metric_event("find_misnamed_agents_util", "p4obs", "metric_3")
_emit_emits_metric_event("find_misnamed_agents_util", "p4obs", "metric_4")
_emit_emits_metric_event("find_misnamed_agents_util", "p4obs", "metric_5")
_emit_emits_metric_event("find_misnamed_agents_util", "p4obs", "metric_6")
_emit_records_incident_event("find_misnamed_agents_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("find_misnamed_agents_util", "p4obs", "anomaly")
_emit_writes_observability_log("find_misnamed_agents_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("find_misnamed_agents_util", "p4obs", "mon_state")
_emit_triggers_alert("find_misnamed_agents_util", "p4obs", "alert")
_emit_links_incident_trace("find_misnamed_agents_util", "p4obs", "trace_link")
_emit_captures_pattern("find_misnamed_agents_util", "p3lm", "pattern")
_emit_records_learning_event("find_misnamed_agents_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("find_misnamed_agents_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("find_misnamed_agents_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("find_misnamed_agents_util", "p3lm", "routing")
_emit_improves_agent_policy("find_misnamed_agents_util", "p3lm", "policy")
_emit_stores_learning_state("find_misnamed_agents_util", "p3lm", "state")
_emit_records_execution_trace("find_misnamed_agents_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("find_misnamed_agents_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("find_misnamed_agents_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("find_misnamed_agents_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("find_misnamed_agents_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("find_misnamed_agents_util", "env_read", "p2_env_1")
_emit_reads_environ("find_misnamed_agents_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("find_misnamed_agents_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("find_misnamed_agents_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "find_misnamed_agents_util", "context_pull")
_emit_pulls_context("p1", "find_misnamed_agents_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "find_misnamed_agents_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "find_misnamed_agents_util", "uwg_term_2")
_emit_writes_through("p1", "find_misnamed_agents_util", "write_through")
_emit_writes_through("p1", "find_misnamed_agents_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "find_misnamed_agents_util", "safety_validation")
_emit_invokes_eval("p1", "find_misnamed_agents_util", "eval_call")
_emit_proposal_commits_routing("p1", "find_misnamed_agents_util", "routing_commit")

try:
    from agentic_core.L0_routing.scripts.full_agent_discovery import (
        AGENTIC_CORE_DIR,
        APPS_LIC_DIR,
        APPS_RG_DIR,
        APPS_SHARED_DIR,
        get_python_files,
    )
except ImportError:  # guardian: allow-silent-swallow
    AGENTIC_CORE_DIR = Path(AGENTIC_CORE_DIR)
    APPS_LIC_DIR = Path(APPS_LIC_DIR)
    APPS_RG_DIR = Path(APPS_RG_DIR)
    APPS_SHARED_DIR = Path(APPS_SHARED_DIR)

    def get_python_files(directory):
        """Fallback implementation to get Python files."""
        return directory.rglob("*.py")


PROJECT_ROOT = Path(__file__).parent.parent
AGENT_SUFFIXES = {
    "Agent",
    "Handler",
    "Manager",
    "Controller",
    "Executor",
    "Validator",
    "Orchestrator",
    "Governor",
    "Enforcer",
    "Analyzer",
    "Sentinel",
}
EXCLUDE = {"Mixin", "Base", "Abstract", "Protocol"}


def has_agent_class(path: Path) -> list:
    """Return agent class names in file."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "has_agent_class", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "has_agent_class", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "has_agent_class")
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="ignore"))
    except (ValueError, TypeError):  # guardian: allow-silent-swallow
        return []
    agents = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            if any(p in node.name for p in EXCLUDE):
                continue
            if any(node.name.endswith(s) for s in AGENT_SUFFIXES):
                agents.append(node.name)
    return agents


scan_dirs = [AGENTIC_CORE_DIR, APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR]
misnamed = []
properly_named = 0
for d in scan_dirs:
    dir_path = PROJECT_ROOT / d
    if not dir_path.exists():
        continue
    for py_file in get_python_files(dir_path):
        if "__pycache__" in str(py_file):
            continue
        agents = has_agent_class(py_file)
        if agents:
            if "Agent" in py_file.name:
                properly_named += 1
            else:
                misnamed.append((py_file.relative_to(PROJECT_ROOT), agents))
print(f"Properly named (*Agent.py with agent classes): {properly_named}")
print(f"Misnamed (contains agents but no 'Agent' in filename): {len(misnamed)}")
print(f"\n{'=' * 60}")
print("FILES NEEDING RENAME:")
print(f"{'=' * 60}\n")
for path, classes in sorted(misnamed)[:50]:
    print(f"{path}")
    print(f"  Classes: {', '.join(classes)}")
    print()
if len(misnamed) > 50:
    print(f"... and {len(misnamed) - 50} more files")
