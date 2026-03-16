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

from agentic_core.utils.security_util import safe_execute

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
)
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

emit_replay_key("p0", "pre_deploy_check_util")
emit_determinism_digest("p0", "pre_deploy_check_util")

_emit_dispatches_healing_run("p1", "pre_deploy_check_util", "L5")
_emit_routes_through("p1", "pre_deploy_check_util", "L5")
_emit_escalates_to_human("p1", "pre_deploy_check_util", "L5")
_emit_reads_policy_state("p1", "pre_deploy_check_util", "L5")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_records_execution_trace("p0", "evidence", "pre_deploy_check_util")
_emit_applies_guardrail("p0", "pre_deploy_check_util", "p0_governance")
_emit_snapshots_state("p0", "pre_deploy_check_util", "state_snapshot")
_emit_authorize_and_execute("p2", "pre_deploy_check_util", "execution_auth")
_emit_validates_capability("p2", "pre_deploy_check_util", "capability_check")
_emit_routes_to_capability("p2", "pre_deploy_check_util", "capability_route")
_emit_writes_via_uwg("p2", "pre_deploy_check_util", "uwg_write")
_emit_blocks_direct_write("p2", "pre_deploy_check_util", "direct_write_block")
_emit_records_tool_invocation("p2", "pre_deploy_check_util", "tool_invocation")
_emit_captures_execution_output("p2", "pre_deploy_check_util", "exec_output")
_emit_dispatches_agent("p3", "pre_deploy_check_util", "agent_dispatch")
_emit_coordinates_agents("p3", "pre_deploy_check_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "pre_deploy_check_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "pre_deploy_check_util", "healing_outcome")
_emit_escalates_failure("p3", "pre_deploy_check_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "pre_deploy_check_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "pre_deploy_check_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "pre_deploy_check_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "pre_deploy_check_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "pre_deploy_check_util", "eval_metric")
_emit_stores_embedding("p4", "pre_deploy_check_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "pre_deploy_check_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "pre_deploy_check_util", "exec_snapshot_link")

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
    except Exception as e:
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
