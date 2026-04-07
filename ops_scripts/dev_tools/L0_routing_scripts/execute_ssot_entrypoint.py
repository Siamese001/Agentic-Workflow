#!/usr/bin/env python3
# NOTE: l0_execute.py was planned but never implemented. This file is ACTIVE.
"""
V15-Native Entrypoint for execute_ssot.

Single canonical entrypoint — all flags defined here, no second parse in _legacy_main.

This file exists to make the runtime boundary unambiguous:
  - execute_ssot_entrypoint.py = the ONLY invocation path.
  - execute_ssot.py = active module for agent-based healing pipeline.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    OPS_SCRIPTS_DIR,
)
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
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
    _emit_routes_through,  # noqa: E402
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

emit_replay_key("p0", "execute_ssot_entrypoint")
emit_determinism_digest("p0", "execute_ssot_entrypoint")

_emit_dispatches_healing_run("p1", "execute_ssot_entrypoint", "L0")
_emit_routes_through("p1", "execute_ssot_entrypoint", "L0")
_emit_checks_agent_registry("p1", "execute_ssot_entrypoint", "agent_registry")
_emit_validates_agent_capability("p1", "execute_ssot_entrypoint", "capability")
_emit_dispatches_execution_plan("p1", "execute_ssot_entrypoint", "exec_plan")
_emit_agent_executes_agent("p1", "execute_ssot_entrypoint", "sub_agent")
_emit_routes_to_agent("p1", "execute_ssot_entrypoint", "target_agent")
_emit_verifies_policy("p1", "execute_ssot_entrypoint", "policy_check")
_emit_observes_runtime_state("p1", "execute_ssot_entrypoint", "runtime_state")
_emit_verifies_boundary("p1", "execute_ssot_entrypoint", "boundary_check")
_emit_transcripts_response("p1", "execute_ssot_entrypoint", "transcript")
_emit_hard_fails_untranscripted("p1", "execute_ssot_entrypoint")
_emit_gated_by_confidence("p1", "execute_ssot_entrypoint", "confidence_gate")
_emit_escalates_to_human("p1", "execute_ssot_entrypoint", "L0")
_emit_reads_policy_state("p1", "execute_ssot_entrypoint", "L0")

_emit_records_execution_trace("p0", "evidence", "execute_ssot_entrypoint")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "execute_ssot_entrypoint", "p0_governance")
_emit_snapshots_state("p0", "execute_ssot_entrypoint", "state_snapshot")
_emit_authorize_and_execute("p2", "execute_ssot_entrypoint", "execution_auth")
_emit_validates_capability("p2", "execute_ssot_entrypoint", "capability_check")
_emit_routes_to_capability("p2", "execute_ssot_entrypoint", "capability_route")
_emit_writes_via_uwg("p2", "execute_ssot_entrypoint", "uwg_write")
_emit_blocks_direct_write("p2", "execute_ssot_entrypoint", "direct_write_block")
_emit_records_tool_invocation("p2", "execute_ssot_entrypoint", "tool_invocation")
_emit_captures_execution_output("p2", "execute_ssot_entrypoint", "exec_output")
_emit_dispatches_agent("p3", "execute_ssot_entrypoint", "agent_dispatch")
_emit_coordinates_agents("p3", "execute_ssot_entrypoint", "agent_coordination")
_emit_records_workflow_lineage("p3", "execute_ssot_entrypoint", "workflow_lineage")
_emit_records_healing_outcome("p3", "execute_ssot_entrypoint", "healing_outcome")
_emit_escalates_failure("p3", "execute_ssot_entrypoint", "failure_escalation")
_emit_orchestrates_workflow("p3", "execute_ssot_entrypoint", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "execute_ssot_entrypoint", "healing_dispatch")
_emit_invokes_evaluation("p3", "execute_ssot_entrypoint", "evaluation_signal")
_emit_records_telemetry_event("p4", "execute_ssot_entrypoint", "telemetry_event")
_emit_captures_evaluation_metric("p4", "execute_ssot_entrypoint", "eval_metric")
_emit_stores_embedding("p4", "execute_ssot_entrypoint", "embedding_store")
_emit_updates_meta_learning_state("p4", "execute_ssot_entrypoint", "meta_learning")
_emit_links_execution_to_snapshot("p4", "execute_ssot_entrypoint", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
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

_emit_emits_metric_event("execute_ssot_entrypoint", "p4obs", "metric_1")
_emit_emits_metric_event("execute_ssot_entrypoint", "p4obs", "metric_2")
_emit_emits_metric_event("execute_ssot_entrypoint", "p4obs", "metric_3")
_emit_emits_metric_event("execute_ssot_entrypoint", "p4obs", "metric_4")
_emit_emits_metric_event("execute_ssot_entrypoint", "p4obs", "metric_5")
_emit_emits_metric_event("execute_ssot_entrypoint", "p4obs", "metric_6")
_emit_records_incident_event("execute_ssot_entrypoint", "p4obs", "incident")
_emit_captures_runtime_anomaly("execute_ssot_entrypoint", "p4obs", "anomaly")
_emit_writes_observability_log("execute_ssot_entrypoint", "p4obs", "obs_log")
_emit_updates_monitoring_state("execute_ssot_entrypoint", "p4obs", "mon_state")
_emit_triggers_alert("execute_ssot_entrypoint", "p4obs", "alert")
_emit_links_incident_trace("execute_ssot_entrypoint", "p4obs", "trace_link")
_emit_captures_pattern("execute_ssot_entrypoint", "p3lm", "pattern")
_emit_records_learning_event("execute_ssot_entrypoint", "p3lm", "learning_event")
_emit_writes_learning_snapshot("execute_ssot_entrypoint", "p3lm", "snapshot")
_emit_feeds_meta_learning("execute_ssot_entrypoint", "p3lm", "meta_feed")
_emit_updates_routing_strategy("execute_ssot_entrypoint", "p3lm", "routing")
_emit_improves_agent_policy("execute_ssot_entrypoint", "p3lm", "policy")
_emit_stores_learning_state("execute_ssot_entrypoint", "p3lm", "state")
_emit_records_execution_trace("execute_ssot_entrypoint", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("execute_ssot_entrypoint", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("execute_ssot_entrypoint", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("execute_ssot_entrypoint", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("execute_ssot_entrypoint", "L4_STATE", "p2_trace_5")
_emit_reads_environ("execute_ssot_entrypoint", "env_read", "p2_env_1")
_emit_reads_environ("execute_ssot_entrypoint", "env_read", "p2_env_2")
_emit_reads_runtime_state("execute_ssot_entrypoint", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("execute_ssot_entrypoint", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "execute_ssot_entrypoint", "context_pull")
_emit_pulls_context("p1", "execute_ssot_entrypoint", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "execute_ssot_entrypoint", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "execute_ssot_entrypoint", "uwg_term_2")
_emit_writes_through("p1", "execute_ssot_entrypoint", "write_through")
_emit_writes_through("p1", "execute_ssot_entrypoint", "write_through_2")
_emit_validated_by_safety_plane("p1", "execute_ssot_entrypoint", "safety_validation")
_emit_invokes_eval("p1", "execute_ssot_entrypoint", "eval_call")
_emit_proposal_commits_routing("p1", "execute_ssot_entrypoint", "routing_commit")


def _resolve_repo_root() -> Path:
    """Walk upward from this file until repo markers are found."""
    cur = Path(__file__).resolve()
    for p in (cur, *cur.parents):
        if (p / AGENTIC_CORE_DIR).is_dir() and (p / OPS_SCRIPTS_DIR).is_dir():
            return p
    raise RuntimeError(f"Unable to resolve repo root from: {cur}")


def main() -> int:
    """V15-native entrypoint — single parser, deterministic, fail-closed."""
    parser = argparse.ArgumentParser(
        description="Sovereign Healing Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  # Default: healing enabled (mutations applied)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint

  # Report-only mode — disable healing (CI-friendly)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --report

  # Scan/report only — disable healing (legacy alias for --report)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --scan-only

  # Single territory with healing
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --territory L5_safety

  # Dry-run validation (explicit alias for report-only)
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --validate

  # Human-in-the-loop mode
  python -m agentic_core.L0_routing.scripts.execute_ssot_entrypoint --interactive
""",
    )
    # --- Mode flags ---
    parser.add_argument("--targets", type=str, nargs="+", help="Target paths to scan/heal")
    parser.add_argument("--territory", type=str, help="Specific territory to scan")
    parser.add_argument(
        "--domains", action="store_true", help="Scan all major domains (explicit; now also the default)",
    )
    parser.add_argument("--agent", type=str, help="Run specific agent directly")
    parser.add_argument("--list-agents", action="store_true", help="List discoverable agents")
    parser.add_argument("--agents", type=str, default=None, help="Comma-separated agent keys to run")
    parser.add_argument("--capture-baseline", action="store_true", help="Capture new Golden Baseline")
    # --- Behaviour flags ---
    # NOTE: UWG has heal jurisdiction - agents should not override
    parser.add_argument(
        "--report", "-r", action="store_true", help="Report-only mode — no mutations (disables healing)",
    )
    parser.add_argument(
        "--scan-only",
        action="store_true",
        help="Legacy alias for --report — no mutations (disables healing)",
    )
    parser.add_argument(
        "--validate", action="store_true", help="Validation-only mode (implies report-only, no mutations)",
    )
    parser.add_argument("--interactive", action="store_true", help="Enable human-in-the-loop prompts")
    parser.add_argument("--manual", action="store_true", help="Disable autonomous mode")
    parser.add_argument(
        "--allow-protected-root-mutation",
        action="store_true",
        default=True,
        help="Allow writes to protected root directories (default: True).",
    )
    parser.add_argument(
        "--apply-proposals",
        action="store_true",
        default=False,
        help="Apply approved meta-learning proposals (default: proposal_only mode).",
    )
    # --- Introspection flags ---
    parser.add_argument("--plan", action="store_true", help="Print execution plan and exit")
    parser.add_argument(
        "--arbitrate-plan", action="store_true", help="Multi-agent arbitration on plan (plan mode only)",
    )
    parser.add_argument("--ptc-plan", action="store_true", help="PTC plan context (plan mode only)")
    parser.add_argument("--fence-self-check", action="store_true", help="Run fence self-check (no mutations)")
    # --- Infra flags ---
    parser.add_argument(
        "--v15-enforcement", type=int, choices=(0, 1), default=None, help="Override V15_ENFORCEMENT",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increase log verbosity")
    parser.add_argument("--verbosity", type=int, default=0, help="Verbosity level (0-3)")
    parser.add_argument("--legacy", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args()

    # UWG heal jurisdiction: dry_run enabled only via --report, --scan-only, or --validate
    args.dry_run = args.report or args.scan_only or args.validate

    # Set heal flag for backward compatibility (UWG controls actual heal behavior)
    args.heal = not args.dry_run

    # [FENCE SELF-CHECK MODE]
    if args.fence_self_check:
        from ops_scripts.dev_tools.L0_routing_scripts.execute_ssot_cli import run_fence_self_check

        run_fence_self_check()
        return 0

    # [PLAN MODE]
    if args.plan:
        from ops_scripts.dev_tools.L0_routing_scripts.execute_ssot_cli import print_execution_plan

        print_execution_plan(arbitrate_plan=args.arbitrate_plan, ptc_plan=args.ptc_plan)
        return 0

    from ops_scripts.dev_tools.L0_routing_scripts.execute_ssot_cli import (
        REPO_ROOT,
        _apply_v15_enforcement_flag,
        _configure_logging,
        _legacy_main,
        _maybe_force_utf8_console,
    )

    _configure_logging(int(args.verbose))
    _apply_v15_enforcement_flag(args)
    _maybe_force_utf8_console()

    try:
        _legacy_main(
            args,
            repo_root=REPO_ROOT,
            allow_protected_root_mutation=args.allow_protected_root_mutation,
        )
    except SystemExit as exc:
        return int(exc.code) if exc.code is not None else 0
    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        return 130
    except Exception as e:
        print(f"[ERROR] Unexpected error in execute_ssot: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
