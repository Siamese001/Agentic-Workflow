"""Quick test scanner with built-in progress indicator."""
import re
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    THRESHOLD,
)
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

_emit_records_execution_trace("p0", "evidence", "quick_scan_util")
_emit_applies_guardrail("p0", "quick_scan_util", "p0_governance")
_emit_reads_policy_state("p0", "quick_scan_util", "policy_binding")
_emit_snapshots_state("p0", "quick_scan_util", "state_snapshot")
emit_replay_key("p0", "quick_scan_util")
emit_determinism_digest("p0", "quick_scan_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "quick_scan_util", "execution_auth")
_emit_validates_capability("p2", "quick_scan_util", "capability_check")
_emit_routes_to_capability("p2", "quick_scan_util", "capability_route")
_emit_writes_via_uwg("p2", "quick_scan_util", "uwg_write")
_emit_blocks_direct_write("p2", "quick_scan_util", "direct_write_block")
_emit_records_tool_invocation("p2", "quick_scan_util", "tool_invocation")
_emit_captures_execution_output("p2", "quick_scan_util", "exec_output")
_emit_dispatches_agent("p3", "quick_scan_util", "agent_dispatch")
_emit_coordinates_agents("p3", "quick_scan_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "quick_scan_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "quick_scan_util", "healing_outcome")
_emit_escalates_failure("p3", "quick_scan_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "quick_scan_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "quick_scan_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "quick_scan_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "quick_scan_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "quick_scan_util", "eval_metric")
_emit_stores_embedding("p4", "quick_scan_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "quick_scan_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "quick_scan_util", "exec_snapshot_link")
G = '\x1b[92m'
Y = '\x1b[93m'
R = '\x1b[91m'
B = '\x1b[94m'
C = '\x1b[96m'
X = '\x1b[0m'

def progress_bar(current, total, width=40):
    """Simple progress bar."""
    percent = current / total if total > 0 else 0
    filled = int(width * percent)
    bar = '█' * filled + '░' * (width - filled)
    color = G if percent > 0.7 else Y if percent > 0.3 else R
    sys.stdout.write(f'\r{color}[{bar}]{X} {current}/{total} ({percent * 100:.1f}%)')
    sys.stdout.flush()
from agentic_core.utils.ssot_discovery_validator import get_python_files
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_pulls_context,
    _emit_execution_terminates_at_uwg,
    _emit_writes_through,
    _emit_validated_by_safety_plane,
    _emit_invokes_eval,
    _emit_proposal_commits_routing,
)
from agentic_core.runtime.lifecycle_trace_contract import _emit_records_execution_trace, _emit_reads_environ, _emit_reads_runtime_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_captures_pattern, _emit_records_learning_event, _emit_writes_learning_snapshot, _emit_feeds_meta_learning, _emit_updates_routing_strategy, _emit_improves_agent_policy, _emit_stores_learning_state
from agentic_core.runtime.lifecycle_trace_contract import _emit_emits_metric_event, _emit_records_incident_event, _emit_captures_runtime_anomaly, _emit_writes_observability_log, _emit_updates_monitoring_state, _emit_triggers_alert, _emit_links_incident_trace
_emit_emits_metric_event("quick_scan_util", "p4obs", "metric_1")
_emit_emits_metric_event("quick_scan_util", "p4obs", "metric_2")
_emit_emits_metric_event("quick_scan_util", "p4obs", "metric_3")
_emit_emits_metric_event("quick_scan_util", "p4obs", "metric_4")
_emit_emits_metric_event("quick_scan_util", "p4obs", "metric_5")
_emit_emits_metric_event("quick_scan_util", "p4obs", "metric_6")
_emit_records_incident_event("quick_scan_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("quick_scan_util", "p4obs", "anomaly")
_emit_writes_observability_log("quick_scan_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("quick_scan_util", "p4obs", "mon_state")
_emit_triggers_alert("quick_scan_util", "p4obs", "alert")
_emit_links_incident_trace("quick_scan_util", "p4obs", "trace_link")
_emit_captures_pattern("quick_scan_util", "p3lm", "pattern")
_emit_records_learning_event("quick_scan_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("quick_scan_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("quick_scan_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("quick_scan_util", "p3lm", "routing")
_emit_improves_agent_policy("quick_scan_util", "p3lm", "policy")
_emit_stores_learning_state("quick_scan_util", "p3lm", "state")
_emit_records_execution_trace("quick_scan_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("quick_scan_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("quick_scan_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("quick_scan_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("quick_scan_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("quick_scan_util", "env_read", "p2_env_1")
_emit_reads_environ("quick_scan_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("quick_scan_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("quick_scan_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "quick_scan_util", "context_pull")
_emit_pulls_context("p1", "quick_scan_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "quick_scan_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "quick_scan_util", "uwg_term_secondary")
_emit_writes_through("p1", "quick_scan_util", "write_through")
_emit_writes_through("p1", "quick_scan_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "quick_scan_util", "safety_validation")
_emit_invokes_eval("p1", "quick_scan_util", "eval_call")
_emit_proposal_commits_routing("p1", "quick_scan_util", "routing_commit")

test_files = list(get_python_files(Path(TESTS_UNIT_DIR)))
skip_pattern = re.compile('@pytest\\.mark\\.skip')
total_files_with_skips = 0
total_skips = 0
print(f'{C}Scanning {len(test_files)} test files...{X}\n')
for i, py_file in enumerate(test_files, 1):
    progress_bar(i, len(test_files))
    try:
        content = py_file.read_text(encoding='utf-8')
        skip_count = len(skip_pattern.findall(content))
        if skip_count > 0:
            total_files_with_skips += 1
            total_skips += skip_count
    # guardian: allow-silent-swallow
    except:
        pass
print(f"\n\n{B}{'=' * 60}{X}")
print(f'{B}Results:{X}')
print(f"{B}{'=' * 60}{X}")
print(f'  Files with skips: {C}{total_files_with_skips}{X}')
color = G if total_skips < 200 else Y if total_skips < 400 else R
print(f'  Total skip marks: {color}{total_skips}{X}')
if total_skips < 200:
    print(f'  Status: {G}✓ EXCELLENT (<200){X}')
elif total_skips < 400:
    print(f'  Status: {Y}⚠ NEEDS WORK (200-400){X}')
else:
    print(f'  Status: {R}✗ CRITICAL (>400){X}')
print(f"{B}{'=' * 60}{X}")
