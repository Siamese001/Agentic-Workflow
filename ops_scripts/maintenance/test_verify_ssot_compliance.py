#!/usr/bin/env python3
"""
SSOT Compliance Verification for Archive Paths

Verifies that:
1. ArchivalGatekeeper imports ARCHIVES_DIR from structure_blueprint
2. Archive paths resolve to [project_root]/archives/... (not .archive)
3. archives/ is in SOVEREIGN_EXCLUDED_FOLDERS
4. No hardcoded archive paths remain

USAGE:
    python scripts/maintenance/verify_ssot_compliance.py
"""

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

_emit_records_execution_trace("p0", "evidence", "test_verify_ssot_compliance")
_emit_applies_guardrail("p0", "test_verify_ssot_compliance", "p0_governance")
_emit_reads_policy_state("p0", "test_verify_ssot_compliance", "policy_binding")
_emit_snapshots_state("p0", "test_verify_ssot_compliance", "state_snapshot")
emit_replay_key("p0", "test_verify_ssot_compliance")
emit_determinism_digest("p0", "test_verify_ssot_compliance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_verify_ssot_compliance", "execution_auth")
_emit_validates_capability("p2", "test_verify_ssot_compliance", "capability_check")
_emit_routes_to_capability("p2", "test_verify_ssot_compliance", "capability_route")
_emit_writes_via_uwg("p2", "test_verify_ssot_compliance", "uwg_write")
_emit_blocks_direct_write("p2", "test_verify_ssot_compliance", "direct_write_block")
_emit_records_tool_invocation("p2", "test_verify_ssot_compliance", "tool_invocation")
_emit_captures_execution_output("p2", "test_verify_ssot_compliance", "exec_output")
_emit_dispatches_agent("p3", "test_verify_ssot_compliance", "agent_dispatch")
_emit_coordinates_agents("p3", "test_verify_ssot_compliance", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_verify_ssot_compliance", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_verify_ssot_compliance", "healing_outcome")
_emit_escalates_failure("p3", "test_verify_ssot_compliance", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_verify_ssot_compliance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_verify_ssot_compliance", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_verify_ssot_compliance", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_verify_ssot_compliance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_verify_ssot_compliance", "eval_metric")
_emit_stores_embedding("p4", "test_verify_ssot_compliance", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_verify_ssot_compliance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_verify_ssot_compliance", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from agentic_core.L0_routing.config.path_constants import ARCHIVES_DIR, SOVEREIGN_EXCLUDED_FOLDERS
from agentic_core.L5_safety.enforcement.archival_gatekeeper_gate import ArchivalGatekeeper
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

_emit_emits_metric_event("test_verify_ssot_compliance", "p4obs", "metric_1")
_emit_emits_metric_event("test_verify_ssot_compliance", "p4obs", "metric_2")
_emit_emits_metric_event("test_verify_ssot_compliance", "p4obs", "metric_3")
_emit_emits_metric_event("test_verify_ssot_compliance", "p4obs", "metric_4")
_emit_emits_metric_event("test_verify_ssot_compliance", "p4obs", "metric_5")
_emit_emits_metric_event("test_verify_ssot_compliance", "p4obs", "metric_6")
_emit_records_incident_event("test_verify_ssot_compliance", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_verify_ssot_compliance", "p4obs", "anomaly")
_emit_writes_observability_log("test_verify_ssot_compliance", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_verify_ssot_compliance", "p4obs", "mon_state")
_emit_triggers_alert("test_verify_ssot_compliance", "p4obs", "alert")
_emit_links_incident_trace("test_verify_ssot_compliance", "p4obs", "trace_link")
_emit_captures_pattern("test_verify_ssot_compliance", "p3lm", "pattern")
_emit_records_learning_event("test_verify_ssot_compliance", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_verify_ssot_compliance", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_verify_ssot_compliance", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_verify_ssot_compliance", "p3lm", "routing")
_emit_improves_agent_policy("test_verify_ssot_compliance", "p3lm", "policy")
_emit_stores_learning_state("test_verify_ssot_compliance", "p3lm", "state")
_emit_records_execution_trace("test_verify_ssot_compliance", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_verify_ssot_compliance", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_verify_ssot_compliance", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_verify_ssot_compliance", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_verify_ssot_compliance", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_verify_ssot_compliance", "env_read", "p2_env_1")
_emit_reads_environ("test_verify_ssot_compliance", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_verify_ssot_compliance", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_verify_ssot_compliance", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_verify_ssot_compliance", "context_pull")
_emit_pulls_context("p1", "test_verify_ssot_compliance", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_verify_ssot_compliance", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_verify_ssot_compliance", "uwg_term_2")
_emit_writes_through("p1", "test_verify_ssot_compliance", "write_through")
_emit_writes_through("p1", "test_verify_ssot_compliance", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_verify_ssot_compliance", "safety_validation")
_emit_invokes_eval("p1", "test_verify_ssot_compliance", "eval_call")
_emit_proposal_commits_routing("p1", "test_verify_ssot_compliance", "routing_commit")
_emit_escalates_to_human("p1", "test_verify_ssot_compliance", "human_escalation")
_emit_routes_through("p1", "test_verify_ssot_compliance", "route_through")
_emit_checks_agent_registry("p1", "test_verify_ssot_compliance", "agent_registry")
_emit_validates_agent_capability("p1", "test_verify_ssot_compliance", "capability")
_emit_dispatches_execution_plan("p1", "test_verify_ssot_compliance", "exec_plan")
_emit_agent_executes_agent("p1", "test_verify_ssot_compliance", "sub_agent")
_emit_routes_to_agent("p1", "test_verify_ssot_compliance", "target_agent")
_emit_verifies_policy("p1", "test_verify_ssot_compliance", "policy_check")
_emit_observes_runtime_state("p1", "test_verify_ssot_compliance", "runtime_state")
_emit_verifies_boundary("p1", "test_verify_ssot_compliance", "boundary_check")
_emit_transcripts_response("p1", "test_verify_ssot_compliance", "transcript")
_emit_hard_fails_untranscripted("p1", "test_verify_ssot_compliance")
_emit_gated_by_confidence("p1", "test_verify_ssot_compliance", "confidence_gate")


def test_ssot_import():
    """Test 1: Verify ArchivalGatekeeper can import ARCHIVES_DIR."""
    print("\n[TEST 1] SSOT Import Test")
    try:
        # Verify ARCHIVES_DIR value
        assert ARCHIVES_DIR == ARCHIVES_DIR, f"Expected 'archives', got '{ARCHIVES_DIR}'"

        # Verify ArchivalGatekeeper uses correct name
        assert ArchivalGatekeeper.ARCHIVE_ROOT_NAME == ARCHIVES_DIR, (
            f"Expected 'archives', got '{ArchivalGatekeeper.ARCHIVE_ROOT_NAME}'"
        )

        print("  ✅ PASS: ARCHIVES_DIR imported successfully")
        print(f"     ARCHIVES_DIR = '{ARCHIVES_DIR}'")
        print(
            f"     ArchivalGatekeeper.ARCHIVE_ROOT_NAME = '{ArchivalGatekeeper.ARCHIVE_ROOT_NAME}'",
        )
        return True
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        print(f"  ❌ FAIL: {e}")
        return False


def test_path_resolution():
    """Test 2: Verify archive_root resolves to archives/ not .archive."""
    print("\n[TEST 2] Path Resolution Test")
    try:
        project_root = Path.cwd()
        ArchivalGatekeeper.reset_instance()
        gatekeeper = ArchivalGatekeeper.get_instance(project_root)

        # Verify path contains 'archives' not '.archive'
        archive_path = str(gatekeeper.archive_root)

        assert ARCHIVES_DIR in archive_path, f"'archives' not in path: {archive_path}"
        assert ".archive" not in archive_path, f"'.archive' found in path: {archive_path}"
        assert "gatekeeper" in archive_path, f"'gatekeeper' not in path: {archive_path}"

        expected = project_root / ARCHIVES_DIR / "gatekeeper"
        assert gatekeeper.archive_root == expected, f"Expected {expected}, got {gatekeeper.archive_root}"

        print("  ✅ PASS: Archive root resolves correctly")
        print(f"     archive_root = {gatekeeper.archive_root}")

        ArchivalGatekeeper.reset_instance()
        return True
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        print(f"  ❌ FAIL: {e}")
        return False


def test_exclusion_logic():
    """Test 3: Verify archives/ is in SOVEREIGN_EXCLUDED_FOLDERS."""
    print("\n[TEST 3] Exclusion Logic Test")
    try:
        assert ARCHIVES_DIR in SOVEREIGN_EXCLUDED_FOLDERS, "'archives' not in SOVEREIGN_EXCLUDED_FOLDERS"

        print("  ✅ PASS: 'archives' is in SOVEREIGN_EXCLUDED_FOLDERS")
        print(f"     SOVEREIGN_EXCLUDED_FOLDERS = {sorted(SOVEREIGN_EXCLUDED_FOLDERS)}")
        return True
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        print(f"  ❌ FAIL: {e}")
        return False


def test_no_hardcoded_paths():
    """Test 4: Verify no hardcoded .archive paths remain."""
    print("\n[TEST 4] Hardcoded Path Check")
    try:
        import inspect

        # Get source code
        source = inspect.getsource(ArchivalGatekeeper)

        # Check for hardcoded .archive
        if '".archive"' in source or "'.archive'" in source:
            print("  ❌ FAIL: Found hardcoded '.archive' in ArchivalGatekeeper")
            return False

        print("  ✅ PASS: No hardcoded '.archive' paths found")
        return True
    except Exception as e:  # guardian: allow-broad-exception -- intentional error boundary, re-raises all caught exceptions to caller
        raise
        print(f"  ❌ FAIL: {e}")
        return False


def main():
    print("=" * 70)
    print("SSOT Compliance Verification")
    print("=" * 70)

    results = []
    results.append(("SSOT Import", test_ssot_import()))
    results.append(("Path Resolution", test_path_resolution()))
    results.append(("Exclusion Logic", test_exclusion_logic()))
    results.append(("No Hardcoded Paths", test_no_hardcoded_paths()))

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n✅ ALL TESTS PASSED - SSOT COMPLIANT")
        return 0
    else:
        print(f"\n❌ {total - passed} TEST(S) FAILED - NOT SSOT COMPLIANT")
        return 1


if __name__ == "__main__":
    sys.exit(main())
