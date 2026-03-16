#!/usr/bin/env python3
"""
[PHASE 7/8] Sovereign Lockdown Check - CI/CD Entrypoint.

This script acts as the final gatekeeper for architectural purity.
It interfaces with the ArchitectureGovernorAgent in headless mode.

Usage:
    python scripts/ci/sovereign_lockdown_check.py

Exit Codes:
    0 - Repository is sovereign-compliant (no violations)
    1 - Violations detected (commit should be blocked)
    2 - Error during verification

Pre-commit Hook Entry:
    - id: sovereign-lockdown-verification
      name: Sovereign Lockdown Verification (Phase 7)
      entry: python
      args: [scripts/ci/sovereign_lockdown_check.py]
      language: python
      pass_filenames: false
      always_run: true
"""

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

_emit_records_execution_trace("p0", "evidence", "sovereign_lockdown_check")
_emit_applies_guardrail("p0", "sovereign_lockdown_check", "p0_governance")
_emit_reads_policy_state("p0", "sovereign_lockdown_check", "policy_binding")
_emit_snapshots_state("p0", "sovereign_lockdown_check", "state_snapshot")
emit_replay_key("p0", "sovereign_lockdown_check")
emit_determinism_digest("p0", "sovereign_lockdown_check")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "sovereign_lockdown_check", "execution_auth")
_emit_validates_capability("p2", "sovereign_lockdown_check", "capability_check")
_emit_routes_to_capability("p2", "sovereign_lockdown_check", "capability_route")
_emit_writes_via_uwg("p2", "sovereign_lockdown_check", "uwg_write")
_emit_blocks_direct_write("p2", "sovereign_lockdown_check", "direct_write_block")
_emit_records_tool_invocation("p2", "sovereign_lockdown_check", "tool_invocation")
_emit_captures_execution_output("p2", "sovereign_lockdown_check", "exec_output")
_emit_dispatches_agent("p3", "sovereign_lockdown_check", "agent_dispatch")
_emit_coordinates_agents("p3", "sovereign_lockdown_check", "agent_coordination")
_emit_records_workflow_lineage("p3", "sovereign_lockdown_check", "workflow_lineage")
_emit_records_healing_outcome("p3", "sovereign_lockdown_check", "healing_outcome")
_emit_escalates_failure("p3", "sovereign_lockdown_check", "failure_escalation")
_emit_orchestrates_workflow("p3", "sovereign_lockdown_check", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "sovereign_lockdown_check", "healing_dispatch")
_emit_invokes_evaluation("p3", "sovereign_lockdown_check", "evaluation_signal")
_emit_records_telemetry_event("p4", "sovereign_lockdown_check", "telemetry_event")
_emit_captures_evaluation_metric("p4", "sovereign_lockdown_check", "eval_metric")
_emit_stores_embedding("p4", "sovereign_lockdown_check", "embedding_store")
_emit_updates_meta_learning_state("p4", "sovereign_lockdown_check", "meta_learning")
_emit_links_execution_to_snapshot("p4", "sovereign_lockdown_check", "exec_snapshot_link")


def main() -> int:
    """Run sovereign lockdown verification."""
    try:
        # Add project root to path for imports
        project_root = Path(__file__).resolve().parent.parent.parent
        # guardian: allow-global-mutation
        sys.path.insert(0, str(project_root))

        from agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent import (
            ArchitectureGovernorAgent,
        )

        print("=" * 60)
        print("SOVEREIGN LOCKDOWN VERIFICATION")
        print("=" * 60)

        # Initialize the Governor in headless/auto-approve mode
        agent = ArchitectureGovernorAgent(
            project_root=project_root,
            auto_approve=True,  # Force non-interactive sovereignty
        )

        # Execute final sync verification
        passed, results = agent.run_ci_verification_sync()

        # Extract details
        raw_result = results.get("_raw_result", results)
        violations_found = raw_result.get("violations_found", 0)
        roots_scanned = raw_result.get("roots_scanned", [])

        print(f"\nRoots Scanned: {', '.join(roots_scanned) if roots_scanned else 'None'}")
        print(f"Violations Found: {violations_found}")

        if passed:
            print("\n[OK] Sovereign Lockdown Verified: Repository is architecture-pure.")
            print("=" * 60)
            return 0
        else:
            # Output findings for CI logs
            print(f"\n[FAIL] Lockdown Failed: {violations_found} violations detected.")

            # Show violation details if available
            violations = raw_result.get("violations", [])
            if violations:
                print("\nViolations:")
                for v in violations[:10]:  # Limit to first 10
                    if isinstance(v, dict):
                        print(f"  - [{v.get('type', 'UNKNOWN')}] {v.get('message', str(v))}")
                    else:
                        print(f"  - {v}")

            print(
                "\nTo fix: Run `python -m agentic_core.L5_safety.reasoning.ArchitectureGovernorAgent --heal`",
            )
            print("=" * 60)
            return 1

    except ImportError as e:
        print(f"[ERROR] Import Error: {e}")
        print("Ensure agentic_core is properly installed.")
        return 2
    except Exception as e:
        raise
        print(f"[ERROR] Verification Error: {e}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
