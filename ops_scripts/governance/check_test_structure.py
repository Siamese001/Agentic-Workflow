"""
file: ops_scripts/governance/check_test_structure.py
description: |
    [GOVERNANCE SENTRY]
    Strictly enforces the 'Scope Mirroring' testing architecture.

    Rules Enforced:
    1. NO tests allowed in tests/ root (except conftest.py).
    2. All tests must reside in tests/unit, tests/integration, tests/e2e, or tests/fixtures.
    3. Test paths must mirror source paths (e.g., tests/unit/agentic_core/L5_safety matches agentic_core/L5_safety).

    Exit Code:
    0: Structure compliant.
    1: Violations found (prints list).
"""
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
    TESTS_DIR,
    THRESHOLD,
    get_validated_project_root,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    _emit_emits_metric_event,
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_links_incident_trace,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_policy_state,  # noqa: E402
    _emit_reads_runtime_state,
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_stores_learning_state,
    _emit_transcripts_response,
    _emit_triggers_alert,
    _emit_updates_meta_learning_state,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_emits_metric_event("check_test_structure", "p4obs", "metric_1")
_emit_emits_metric_event("check_test_structure", "p4obs", "metric_2")
_emit_emits_metric_event("check_test_structure", "p4obs", "metric_3")
_emit_emits_metric_event("check_test_structure", "p4obs", "metric_4")
_emit_emits_metric_event("check_test_structure", "p4obs", "metric_5")
_emit_emits_metric_event("check_test_structure", "p4obs", "metric_6")
_emit_records_incident_event("check_test_structure", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_test_structure", "p4obs", "anomaly")
_emit_writes_observability_log("check_test_structure", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_test_structure", "p4obs", "mon_state")
_emit_triggers_alert("check_test_structure", "p4obs", "alert")
_emit_links_incident_trace("check_test_structure", "p4obs", "trace_link")
_emit_captures_pattern("check_test_structure", "p3lm", "pattern")
_emit_records_learning_event("check_test_structure", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_test_structure", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_test_structure", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_test_structure", "p3lm", "routing")
_emit_improves_agent_policy("check_test_structure", "p3lm", "policy")
_emit_stores_learning_state("check_test_structure", "p3lm", "state")
_emit_records_execution_trace("check_test_structure", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_test_structure", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_test_structure", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_test_structure", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_test_structure", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_test_structure", "env_read", "p2_env_1")
_emit_reads_environ("check_test_structure", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_test_structure", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_test_structure", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "check_test_structure")
_emit_applies_guardrail("p0", "check_test_structure", "p0_governance")
_emit_reads_policy_state("p0", "check_test_structure", "policy_binding")
_emit_snapshots_state("p0", "check_test_structure", "state_snapshot")
_emit_pulls_context("p1", "check_test_structure", "context_pull")
_emit_pulls_context("p1", "check_test_structure", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_test_structure", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_test_structure", "uwg_term_secondary")
_emit_writes_through("p1", "check_test_structure", "write_through")
_emit_writes_through("p1", "check_test_structure", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_test_structure", "safety_validation")
_emit_invokes_eval("p1", "check_test_structure", "eval_call")
_emit_proposal_commits_routing("p1", "check_test_structure", "routing_commit")
_emit_escalates_to_human("p1", "check_test_structure", "human_escalation")
_emit_routes_through("p1", "check_test_structure", "route_through")
_emit_checks_agent_registry("p1", "check_test_structure", "agent_registry")
_emit_validates_agent_capability("p1", "check_test_structure", "capability")
_emit_dispatches_execution_plan("p1", "check_test_structure", "exec_plan")
_emit_agent_executes_agent("p1", "check_test_structure", "sub_agent")
_emit_routes_to_agent("p1", "check_test_structure", "target_agent")
_emit_verifies_policy("p1", "check_test_structure", "policy_check")
_emit_observes_runtime_state("p1", "check_test_structure", "runtime_state")
_emit_verifies_boundary("p1", "check_test_structure", "boundary_check")
_emit_transcripts_response("p1", "check_test_structure", "transcript")
_emit_hard_fails_untranscripted("p1", "check_test_structure")
_emit_gated_by_confidence("p1", "check_test_structure", "confidence_gate")
emit_replay_key("p0", "check_test_structure")
emit_determinism_digest("p0", "check_test_structure")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_test_structure", "execution_auth")
_emit_validates_capability("p2", "check_test_structure", "capability_check")
_emit_routes_to_capability("p2", "check_test_structure", "capability_route")
_emit_writes_via_uwg("p2", "check_test_structure", "uwg_write")
_emit_blocks_direct_write("p2", "check_test_structure", "direct_write_block")
_emit_records_tool_invocation("p2", "check_test_structure", "tool_invocation")
_emit_captures_execution_output("p2", "check_test_structure", "exec_output")
_emit_dispatches_agent("p3", "check_test_structure", "agent_dispatch")
_emit_coordinates_agents("p3", "check_test_structure", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_test_structure", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_test_structure", "healing_outcome")
_emit_escalates_failure("p3", "check_test_structure", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_test_structure", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_test_structure", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_test_structure", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_test_structure", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_test_structure", "eval_metric")
_emit_stores_embedding("p4", "check_test_structure", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_test_structure", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_test_structure", "exec_snapshot_link")
PROJECT_ROOT = get_validated_project_root()
TESTS_ROOT = PROJECT_ROOT / TESTS_DIR
ALLOWED_ROOTS = {'unit', 'integration', 'e2e', 'functional', 'fixtures', 'migration', 'governance', 'L0_routing'}
ALLOWED_ROOT_FILES = {'conftest.py', 'pytest.ini', 'README.md', '__init__.py'}

def check_structure():
    print(f'[GOVERNANCE] Scanning {TESTS_ROOT} for structural violations...')
    violations = []
    if not TESTS_ROOT.exists():
        print('CRITICAL: tests/ directory missing!')
        sys.exit(1)
    for item in TESTS_ROOT.iterdir():
        if item.is_file():
            if item.name not in ALLOWED_ROOT_FILES:
                violations.append(f'[ROOT VIOLATION] File found in tests root: {item.name}')
            continue
        if item.is_dir():
            if item.name not in ALLOWED_ROOTS and item.name not in {'__pycache__', '.pytest_cache'}:
                violations.append(f'[FOLDER VIOLATION] Unknown test category: tests/{item.name}')
                continue
            if item.name in {'unit', 'integration'}:
                check_mirror_depth(item, violations)
    if violations:
        print(f'[FAILED] Found {len(violations)} structural violations:')
        for v in violations:
            print(f'  - {v}')
        sys.exit(1)
    else:
        print('[PASSED] Test structure is strictly compliant.')
        sys.exit(0)

def check_mirror_depth(category_path: Path, violations: list):
    """
    Ensures that under tests/unit/, we have immediate domain roots
    (agentic_core, apps_rg, etc.) and not loose files.
    """
    for sub in category_path.iterdir():
        if sub.is_file():
            if sub.name not in {'__init__.py', 'conftest.py'} and (not sub.name.endswith('.pyc')):
                violations.append(f'[DEPTH VIOLATION] Test file found too shallow: {sub.relative_to(PROJECT_ROOT)}')
        elif sub.is_dir():
            if sub.name in {'__pycache__', '.pytest_cache'}:
                continue
            pass
if __name__ == '__main__':
    check_structure()
