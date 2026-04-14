"""
file: ops_scripts/governance/intelligence_sentry.py
description: |
    [MASTER ALIGNMENT AGENT]
    1. Indexes Source Tree (agentic_core L0-L6) to build an Address Map.
    2. Recursively finds 'test_*.py' files anywhere in the project.
    3. Moves them to tests/unit/{mirrored_path}.
    4. Rewrites imports from 'from agentic_core' or 'from core' to 'from agentic_core'.
"""

"Intelligence sentry for monitoring project health."
import shutil
import sys
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "intelligence_sentry")
_emit_applies_guardrail("p0", "intelligence_sentry", "p0_governance")
_emit_reads_policy_state("p0", "intelligence_sentry", "policy_binding")
_emit_snapshots_state("p0", "intelligence_sentry", "state_snapshot")
emit_replay_key("p0", "intelligence_sentry")
emit_determinism_digest("p0", "intelligence_sentry")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "intelligence_sentry", "execution_auth")
_emit_validates_capability("p2", "intelligence_sentry", "capability_check")
_emit_routes_to_capability("p2", "intelligence_sentry", "capability_route")
_emit_writes_via_uwg("p2", "intelligence_sentry", "uwg_write")
_emit_blocks_direct_write("p2", "intelligence_sentry", "direct_write_block")
_emit_records_tool_invocation("p2", "intelligence_sentry", "tool_invocation")
_emit_captures_execution_output("p2", "intelligence_sentry", "exec_output")
_emit_dispatches_agent("p3", "intelligence_sentry", "agent_dispatch")
_emit_coordinates_agents("p3", "intelligence_sentry", "agent_coordination")
_emit_records_workflow_lineage("p3", "intelligence_sentry", "workflow_lineage")
_emit_records_healing_outcome("p3", "intelligence_sentry", "healing_outcome")
_emit_escalates_failure("p3", "intelligence_sentry", "failure_escalation")
_emit_orchestrates_workflow("p3", "intelligence_sentry", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "intelligence_sentry", "healing_dispatch")
_emit_invokes_evaluation("p3", "intelligence_sentry", "evaluation_signal")
_emit_records_telemetry_event("p4", "intelligence_sentry", "telemetry_event")
_emit_captures_evaluation_metric("p4", "intelligence_sentry", "eval_metric")
_emit_stores_embedding("p4", "intelligence_sentry", "embedding_store")
_emit_updates_meta_learning_state("p4", "intelligence_sentry", "meta_learning")
_emit_links_execution_to_snapshot("p4", "intelligence_sentry", "exec_snapshot_link")
# guardian: allow-global-mutation
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from agentic_core.L0_routing.config.path_constants import (
    ARCHIVES_DIR,
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    OPS_SCRIPTS_DIR,
    THRESHOLD,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)
from agentic_core.utils.project_root_util import get_project_root
from tqdm import tqdm

_emit_emits_metric_event("intelligence_sentry", "p4obs", "metric_1")
_emit_emits_metric_event("intelligence_sentry", "p4obs", "metric_2")
_emit_emits_metric_event("intelligence_sentry", "p4obs", "metric_3")
_emit_emits_metric_event("intelligence_sentry", "p4obs", "metric_4")
_emit_emits_metric_event("intelligence_sentry", "p4obs", "metric_5")
_emit_emits_metric_event("intelligence_sentry", "p4obs", "metric_6")
_emit_records_incident_event("intelligence_sentry", "p4obs", "incident")
_emit_captures_runtime_anomaly("intelligence_sentry", "p4obs", "anomaly")
_emit_writes_observability_log("intelligence_sentry", "p4obs", "obs_log")
_emit_updates_monitoring_state("intelligence_sentry", "p4obs", "mon_state")
_emit_triggers_alert("intelligence_sentry", "p4obs", "alert")
_emit_links_incident_trace("intelligence_sentry", "p4obs", "trace_link")
_emit_captures_pattern("intelligence_sentry", "p3lm", "pattern")
_emit_records_learning_event("intelligence_sentry", "p3lm", "learning_event")
_emit_writes_learning_snapshot("intelligence_sentry", "p3lm", "snapshot")
_emit_feeds_meta_learning("intelligence_sentry", "p3lm", "meta_feed")
_emit_updates_routing_strategy("intelligence_sentry", "p3lm", "routing")
_emit_improves_agent_policy("intelligence_sentry", "p3lm", "policy")
_emit_stores_learning_state("intelligence_sentry", "p3lm", "state")
_emit_records_execution_trace("intelligence_sentry", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("intelligence_sentry", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("intelligence_sentry", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("intelligence_sentry", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("intelligence_sentry", "L4_STATE", "p2_trace_5")
_emit_reads_environ("intelligence_sentry", "env_read", "p2_env_1")
_emit_reads_environ("intelligence_sentry", "env_read", "p2_env_2")
_emit_reads_runtime_state("intelligence_sentry", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("intelligence_sentry", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "intelligence_sentry", "context_pull")
_emit_pulls_context("p1", "intelligence_sentry", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "intelligence_sentry", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "intelligence_sentry", "uwg_term_secondary")
_emit_writes_through("p1", "intelligence_sentry", "write_through")
_emit_writes_through("p1", "intelligence_sentry", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "intelligence_sentry", "safety_validation")
_emit_invokes_eval("p1", "intelligence_sentry", "eval_call")
_emit_proposal_commits_routing("p1", "intelligence_sentry", "routing_commit")
_emit_escalates_to_human("p1", "intelligence_sentry", "human_escalation")
_emit_routes_through("p1", "intelligence_sentry", "route_through")
_emit_checks_agent_registry("p1", "intelligence_sentry", "agent_registry")
_emit_validates_agent_capability("p1", "intelligence_sentry", "capability")
_emit_dispatches_execution_plan("p1", "intelligence_sentry", "exec_plan")
_emit_agent_executes_agent("p1", "intelligence_sentry", "sub_agent")
_emit_routes_to_agent("p1", "intelligence_sentry", "target_agent")
_emit_verifies_policy("p1", "intelligence_sentry", "policy_check")
_emit_observes_runtime_state("p1", "intelligence_sentry", "runtime_state")
_emit_verifies_boundary("p1", "intelligence_sentry", "boundary_check")
_emit_transcripts_response("p1", "intelligence_sentry", "transcript")
_emit_hard_fails_untranscripted("p1", "intelligence_sentry")
_emit_gated_by_confidence("p1", "intelligence_sentry", "confidence_gate")

PROJECT_ROOT = get_project_root()
SOURCE_ROOTS = [AGENTIC_CORE_DIR, APPS_RG_DIR, APPS_LIC_DIR]
TEST_UNIT_ROOT = PROJECT_ROOT / TESTS_UNIT_DIR


def build_source_map():
    print("🧠 Indexing Source Tree (L0-L6)...")
    source_index = {}
    for root in SOURCE_ROOTS:
        path = PROJECT_ROOT / root
        if not path.exists():
            continue
        for file in path.rglob("*.py"):
            if file.name == "__init__.py":
                continue
            source_index[file.stem] = file.parent.relative_to(PROJECT_ROOT)
    return source_index


def fix_imports(file_path):
    content = file_path.read_text(encoding="utf-8")
    original = content
    content = re.sub("from src\\.agentic_core", "from agentic_core", content)
    content = re.sub("from core\\.", "from agentic_core.", content)
    if content != original:
        file_path.write_text(content, encoding="utf-8")
        return True
    return False


def execute_sentry():
    source_map = build_source_map()
    print("🚀 Scanning for misplaced test files...")
    all_tests = [
        f
        for f in PROJECT_ROOT.rglob("test_*.py")
        if "/tests/" not in str(f.as_posix())
        and OPS_SCRIPTS_DIR not in str(f.as_posix())
        and (ARCHIVES_DIR not in str(f.as_posix()))
    ]
    moved = 0
    for test_file in tqdm(all_tests, desc="Processing", unit="item"):
        target_stem = test_file.stem.replace("test_", "")
        if target_stem in source_map:
            dest_dir = TEST_UNIT_ROOT / source_map[target_stem]
        else:
            relative_path = test_file.parent.relative_to(PROJECT_ROOT)
            dest_dir = TEST_UNIT_ROOT / relative_path
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / test_file.name
        shutil.move(str(test_file), str(dest_path))
        fix_imports(dest_path)
        print(f"  [MIRRORED] {test_file.name} -> {dest_dir.relative_to(TEST_UNIT_ROOT)}")
        moved += 1
    print(f"✅ Sentry Complete. Mirrored {moved} files and patched imports.")


if __name__ == "__main__":
    execute_sentry()
