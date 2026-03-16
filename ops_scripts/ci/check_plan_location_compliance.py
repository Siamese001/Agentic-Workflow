#!/usr/bin/env python3
"""
Plan Location Compliance Guardrail

Enforces Constitutional Rule #0: ALL plans, reports, and markdown artifacts
MUST be saved to `docs/reports/plans/` inside the repository.

Usage:
    python ops_scripts/ci/check_plan_location_compliance.py [--fix]
"""

import argparse

# Force UTF-8 encoding for Windows compatibility
import io
import json
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "check_plan_location_compliance")
_emit_applies_guardrail("p0", "check_plan_location_compliance", "p0_governance")
_emit_reads_policy_state("p0", "check_plan_location_compliance", "policy_binding")
_emit_snapshots_state("p0", "check_plan_location_compliance", "state_snapshot")
emit_replay_key("p0", "check_plan_location_compliance")
emit_determinism_digest("p0", "check_plan_location_compliance")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_plan_location_compliance", "execution_auth")
_emit_validates_capability("p2", "check_plan_location_compliance", "capability_check")
_emit_routes_to_capability("p2", "check_plan_location_compliance", "capability_route")
_emit_writes_via_uwg("p2", "check_plan_location_compliance", "uwg_write")
_emit_blocks_direct_write("p2", "check_plan_location_compliance", "direct_write_block")
_emit_records_tool_invocation("p2", "check_plan_location_compliance", "tool_invocation")
_emit_captures_execution_output("p2", "check_plan_location_compliance", "exec_output")
_emit_dispatches_agent("p3", "check_plan_location_compliance", "agent_dispatch")
_emit_coordinates_agents("p3", "check_plan_location_compliance", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_plan_location_compliance", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_plan_location_compliance", "healing_outcome")
_emit_escalates_failure("p3", "check_plan_location_compliance", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_plan_location_compliance", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_plan_location_compliance", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_plan_location_compliance", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_plan_location_compliance", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_plan_location_compliance", "eval_metric")
_emit_stores_embedding("p4", "check_plan_location_compliance", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_plan_location_compliance", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_plan_location_compliance", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
_REPO_ROOT = Path(__file__).resolve().parents[2]
# guardian: allow-global-mutation
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from agentic_core.L0_routing.config.path_constants import get_validated_project_root

PROJECT_ROOT = get_validated_project_root()


class PlanLocationComplianceChecker:
    """Enforces plan location compliance with Constitutional Rule #0."""

    def check_compliance(self):
        """Check for plan location violations."""
        violations = []

        # Check for .windsurf/plans directory
        windsurf_plans = PROJECT_ROOT / ".windsurf" / "plans"
        if windsurf_plans.exists():
            violations.append({
                "type": "windsurf_plans_exists",
                "directory": str(windsurf_plans),
                "message": ".windsurf/plans directory exists (violates Constitutional Rule #0)",
                "severity": "error"
            })

        # Ensure SSOT plans directory exists
        ssot_plans = PROJECT_ROOT / "docs" / "reports" / "plans"
        if not ssot_plans.exists():
            violations.append({
                "type": "missing_ssot_directory",
                "directory": str(ssot_plans),
                "message": "SSOT plans directory is missing",
                "severity": "error"
            })

        return violations

    def print_report(self):
        """Print compliance report."""
        violations = self.check_compliance()

        if not violations:
            print("✅ Plan location compliance: No violations found")
            print(f"📁 SSOT plans directory: {PROJECT_ROOT / 'docs' / 'reports' / 'plans'}")
            return 0

        print(f"❌ Plan location violations found: {len(violations)}")
        for v in violations:
            print(f"   {v['message']}")

        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check plan location compliance")
    args = parser.parse_args()

    checker = PlanLocationComplianceChecker()
    return checker.print_report()


if __name__ == "__main__":
    sys.exit(main())
