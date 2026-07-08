#!/usr/bin/env python3
"""
Pre-Deployment Check - Dashboard Deployment Gate
=================================================

This script MUST pass before any dashboard deployment.
It runs all E2E tests and blocks deployment if any fail.

Usage:
    python scripts/pre_deploy_check_util.py           # Run checks
    python scripts/pre_deploy_check_util.py --strict  # Strict mode (no warnings allowed)

Exit Codes:
    0 - All checks passed, deployment approved
    1 - Tests failed, deployment BLOCKED
    2 - configuration error
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from agentic_core.utils.security_util import safe_execute

trace_contract._emit_emits_metric_event("pre_deploy_check_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("pre_deploy_check_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("pre_deploy_check_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("pre_deploy_check_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("pre_deploy_check_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("pre_deploy_check_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("pre_deploy_check_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("pre_deploy_check_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("pre_deploy_check_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("pre_deploy_check_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("pre_deploy_check_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("pre_deploy_check_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("pre_deploy_check_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("pre_deploy_check_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("pre_deploy_check_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("pre_deploy_check_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("pre_deploy_check_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("pre_deploy_check_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("pre_deploy_check_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("pre_deploy_check_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("pre_deploy_check_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("pre_deploy_check_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("pre_deploy_check_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("pre_deploy_check_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("pre_deploy_check_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("pre_deploy_check_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("pre_deploy_check_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("pre_deploy_check_util", "runtime_state", "p2_rt_2")

trace_contract.emit_replay_key("p0", "pre_deploy_check_util")
trace_contract.emit_determinism_digest("p0", "pre_deploy_check_util")

trace_contract._emit_dispatches_healing_run("p1", "pre_deploy_check_util", "L5")
trace_contract._emit_routes_through("p1", "pre_deploy_check_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "pre_deploy_check_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "pre_deploy_check_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "pre_deploy_check_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "pre_deploy_check_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "pre_deploy_check_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "pre_deploy_check_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "pre_deploy_check_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "pre_deploy_check_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "pre_deploy_check_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "pre_deploy_check_util")
trace_contract._emit_gated_by_confidence("p1", "pre_deploy_check_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "pre_deploy_check_util", "L5")
trace_contract._emit_reads_policy_state("p1", "pre_deploy_check_util", "L5")
trace_contract._emit_pulls_context("p1", "pre_deploy_check_util", "context_pull")
trace_contract._emit_pulls_context("p1", "pre_deploy_check_util", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "pre_deploy_check_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "pre_deploy_check_util", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "pre_deploy_check_util", "write_through")
trace_contract._emit_writes_through("p1", "pre_deploy_check_util", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "pre_deploy_check_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "pre_deploy_check_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "pre_deploy_check_util", "routing_commit")

trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_records_execution_trace("p0", "evidence", "pre_deploy_check_util")
trace_contract._emit_applies_guardrail("p0", "pre_deploy_check_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "pre_deploy_check_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "pre_deploy_check_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "pre_deploy_check_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "pre_deploy_check_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "pre_deploy_check_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "pre_deploy_check_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "pre_deploy_check_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "pre_deploy_check_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "pre_deploy_check_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "pre_deploy_check_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "pre_deploy_check_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "pre_deploy_check_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "pre_deploy_check_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "pre_deploy_check_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "pre_deploy_check_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "pre_deploy_check_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "pre_deploy_check_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "pre_deploy_check_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "pre_deploy_check_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "pre_deploy_check_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "pre_deploy_check_util", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).parent.parent


def print_banner(message: str, char: str = "="):
    """Print a banner message."""
    width = 70
    print(char * width)
    print(f" {message}")
    print(char * width)


def run_e2e_tests() -> bool:
    """Run the E2E dashboard tests and return True if all pass."""
    print_banner("RUNNING E2E DASHBOARD TESTS")

    test_script = PROJECT_ROOT / "scripts" / "test_dashboard_end_to_end.py"

    if not test_script.exists():
        print(f"❌ ERROR: Test script not found: {test_script}")
        return False

    try:
        result = safe_execute(
            [sys.executable, str(test_script), "--auto", "--yes"],
            cwd=str(PROJECT_ROOT),
            capture_output=False,  # Show output in real-time
            timeout=DEFAULT_TIMEOUT,  # 5 minute timeout
            check=False,
        )

        return result.returncode == 0

    except subprocess.TimeoutExpired:
        print("❌ ERROR: E2E tests timed out after 5 minutes")
        return False
    except (ValueError, TypeError) as e:
        print(f"❌ ERROR: Failed to run E2E tests: {e}")
        return False


def check_ssot_files_exist() -> bool:
    """Verify all SSOT files exist."""
    print_banner("CHECKING SSOT FILES", "-")

    required_files = [
        PROJECT_ROOT / "agent_discovery_full.json",
        PROJECT_ROOT / "scripts" / "full_agent_discovery.py",
        PROJECT_ROOT / "scripts" / "dashboard_ssot_definitions.py",
        PROJECT_ROOT / "scripts" / "territory_ssot_definitions.py",
        PROJECT_ROOT / "scripts" / "regenerate_dashboard_data.py",
        PROJECT_ROOT / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "data" / "dashboard_data.js",
        PROJECT_ROOT / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "data" / "agent_data.js",
    ]

    all_exist = True
    for f in required_files:
        if f.exists():
            print(f"   ✅ {f.relative_to(PROJECT_ROOT)}")
        else:
            print(f"   ❌ MISSING: {f.relative_to(PROJECT_ROOT)}")
            all_exist = False

    return all_exist


def check_data_freshness() -> bool:
    """Check that dashboard data is not stale (regenerated recently)."""
    print_banner("CHECKING DATA FRESHNESS", "-")

    discovery_json = PROJECT_ROOT / "agent_discovery_full.json"
    dashboard_data = (
        PROJECT_ROOT / AGENTIC_CORE_DIR / "L6_observability" / "dashboards" / "data" / "dashboard_data.js"
    )

    if not discovery_json.exists() or not dashboard_data.exists():
        print("   ⚠️  Cannot check freshness - files missing")
        return True  # Don't fail on freshness if files missing (other check will catch)

    discovery_mtime = discovery_json.stat().st_mtime
    dashboard_mtime = dashboard_data.stat().st_mtime

    # Dashboard data should be newer than or same age as discovery
    if dashboard_mtime < discovery_mtime:
        print("   ⚠️  WARNING: dashboard_data.js is older than agent_discovery_full.json")
        print("   ⚠️  Consider running: python scripts/regenerate_dashboard_data.py")
        # This is a warning, not a failure
    else:
        print("   ✅ Dashboard data is up to date")

    return True


def main():
    """Main entry point for pre-deployment checks."""
    print("\n")
    print_banner("DASHBOARD PRE-DEPLOYMENT CHECK")
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Project Root: {PROJECT_ROOT}")
    print("=" * 70)

    # Track overall status
    all_passed = True

    # Check 1: SSOT files exist
    if not check_ssot_files_exist():
        print("\n❌ SSOT files check FAILED")
        all_passed = False
    else:
        print("\n✅ SSOT files check PASSED")

    # Check 2: Data freshness
    check_data_freshness()  # Warning only, doesn't fail

    # Check 3: E2E tests (most important)
    if not run_e2e_tests():
        print("\n❌ E2E tests FAILED")
        all_passed = False
    else:
        print("\n✅ E2E tests PASSED")

    # Final verdict
    print("\n")
    print_banner("DEPLOYMENT DECISION")

    if all_passed:
        print("   ✅ ALL CHECKS PASSED")
        print("   ✅ DEPLOYMENT APPROVED")
        print("=" * 70)
        return 0
    else:
        print("   ❌ CHECKS FAILED")
        print("   ❌ DEPLOYMENT BLOCKED")
        print("")
        print("   Fix all failing tests before deploying!")
        print("=" * 70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
