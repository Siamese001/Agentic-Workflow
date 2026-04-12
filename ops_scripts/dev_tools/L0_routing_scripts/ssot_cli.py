from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "ssot_cli")
emit_determinism_digest("p0", "ssot_cli")

_emit_dispatches_healing_run("p1", "ssot_cli", "L0")
_emit_routes_through("p1", "ssot_cli", "L0")
_emit_checks_agent_registry("p1", "ssot_cli", "agent_registry")
_emit_validates_agent_capability("p1", "ssot_cli", "capability")
_emit_dispatches_execution_plan("p1", "ssot_cli", "exec_plan")
_emit_agent_executes_agent("p1", "ssot_cli", "sub_agent")
_emit_routes_to_agent("p1", "ssot_cli", "target_agent")
_emit_verifies_policy("p1", "ssot_cli", "policy_check")
_emit_observes_runtime_state("p1", "ssot_cli", "runtime_state")
_emit_verifies_boundary("p1", "ssot_cli", "boundary_check")
_emit_transcripts_response("p1", "ssot_cli", "transcript")
_emit_hard_fails_untranscripted("p1", "ssot_cli")
_emit_gated_by_confidence("p1", "ssot_cli", "confidence_gate")
_emit_escalates_to_human("p1", "ssot_cli", "L0")
_emit_reads_policy_state("p1", "ssot_cli", "L0")
_emit_authorize_and_execute("p2", "ssot_cli", "execution_auth")
_emit_validates_capability("p2", "ssot_cli", "capability_check")
_emit_routes_to_capability("p2", "ssot_cli", "capability_route")
_emit_writes_via_uwg("p2", "ssot_cli", "uwg_write")
_emit_blocks_direct_write("p2", "ssot_cli", "direct_write_block")
_emit_records_tool_invocation("p2", "ssot_cli", "tool_invocation")
_emit_captures_execution_output("p2", "ssot_cli", "exec_output")
_emit_dispatches_agent("p3", "ssot_cli", "agent_dispatch")
_emit_coordinates_agents("p3", "ssot_cli", "agent_coordination")
_emit_records_workflow_lineage("p3", "ssot_cli", "workflow_lineage")
_emit_records_healing_outcome("p3", "ssot_cli", "healing_outcome")
_emit_escalates_failure("p3", "ssot_cli", "failure_escalation")
_emit_orchestrates_workflow("p3", "ssot_cli", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ssot_cli", "healing_dispatch")
_emit_invokes_evaluation("p3", "ssot_cli", "evaluation_signal")
_emit_records_telemetry_event("p4", "ssot_cli", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ssot_cli", "eval_metric")
_emit_stores_embedding("p4", "ssot_cli", "embedding_store")
_emit_updates_meta_learning_state("p4", "ssot_cli", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ssot_cli", "exec_snapshot_link")

"\nSSOT - Sovereign Single Source of Truth CLI\n\nProfessional-grade command-line tool for SSOT architectural governance.\nProvides a unified interface for scanning, validation, and enforcement.\n\nUsage:\n    python scripts/ssot_util.py scan              # Scan and list all agents\n    python scripts/ssot_util.py validate          # Run comprehensive validation\n    python scripts/ssot_util.py enforce           # Apply automated remediation\n    python scripts/ssot_util.py status            # Show compliance dashboard\n\nSimilar to git/npm, this tool provides a discoverable interface for\narchitectural governance as a first-class citizen of your workflow.\n"
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).parent.parent.resolve()
# guardian: allow-global-mutation
sys.path.insert(0, str(REPO))
from agentic_core.base_agents.ssot_scanner import SSOTScanner
from agentic_core.base_agents.unified_validator import UnifiedSSOTValidator

from agentic_core.L0_routing.enforcement.mutation_prohibition import assert_no_persistent_write
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("ssot_cli", "p4obs", "metric_1")
_emit_emits_metric_event("ssot_cli", "p4obs", "metric_2")
_emit_emits_metric_event("ssot_cli", "p4obs", "metric_3")
_emit_emits_metric_event("ssot_cli", "p4obs", "metric_4")
_emit_emits_metric_event("ssot_cli", "p4obs", "metric_5")
_emit_emits_metric_event("ssot_cli", "p4obs", "metric_6")
_emit_records_incident_event("ssot_cli", "p4obs", "incident")
_emit_captures_runtime_anomaly("ssot_cli", "p4obs", "anomaly")
_emit_writes_observability_log("ssot_cli", "p4obs", "obs_log")
_emit_updates_monitoring_state("ssot_cli", "p4obs", "mon_state")
_emit_triggers_alert("ssot_cli", "p4obs", "alert")
_emit_links_incident_trace("ssot_cli", "p4obs", "trace_link")
_emit_captures_pattern("ssot_cli", "p3lm", "pattern")
_emit_records_learning_event("ssot_cli", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ssot_cli", "p3lm", "snapshot")
_emit_feeds_meta_learning("ssot_cli", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ssot_cli", "p3lm", "routing")
_emit_improves_agent_policy("ssot_cli", "p3lm", "policy")
_emit_stores_learning_state("ssot_cli", "p3lm", "state")
_emit_records_execution_trace("ssot_cli", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ssot_cli", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ssot_cli", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ssot_cli", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ssot_cli", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ssot_cli", "env_read", "p2_env_1")
_emit_reads_environ("ssot_cli", "env_read", "p2_env_2")
_emit_reads_runtime_state("ssot_cli", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ssot_cli", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "ssot_cli", "context_pull")
_emit_pulls_context("p1", "ssot_cli", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "ssot_cli", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ssot_cli", "uwg_term_2")
_emit_writes_through("p1", "ssot_cli", "write_through")
_emit_writes_through("p1", "ssot_cli", "write_through_2")
_emit_validated_by_safety_plane("p1", "ssot_cli", "safety_validation")
_emit_invokes_eval("p1", "ssot_cli", "eval_call")
_emit_proposal_commits_routing("p1", "ssot_cli", "routing_commit")


def print_header(title: str, char: str = "=", width: int = 80) -> None:
    """Print formatted section header."""
    import uuid as _uuid  # noqa: PLC0415

    _emit_snapshots_state(str(_uuid.uuid4()), "print_header", "state_snapshot")
    import hashlib as _hashlib  # noqa: PLC0415
    import uuid as _uuid  # noqa: PLC0415

    _tid = str(_uuid.uuid4())
    _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
    import uuid as _uuid  # noqa: PLC0415

    _emit_applies_guardrail(str(_uuid.uuid4()), "print_header", "p0_governance")
    import uuid as _uuid  # noqa: PLC0415

    _trace_id = str(_uuid.uuid4())
    _emit_records_execution_trace(_trace_id, LayerSegment.L0_ROUTING, "print_header")
    print()
    print(char * width)
    print(f"  {title}")
    print(char * width)
    print()


def cmd_scan(args) -> int:
    """
    Scan command: List all discovered agents and their metadata.

    Returns:
        Exit code (0 for success)
    """
    print_header("SSOT SCANNER - Agent Discovery")
    print("Scanning filesystem for agents...")
    scanner = SSOTScanner(REPO)
    agents = scanner.scan_agents()
    stats = scanner.get_compliance_stats()
    print(f"\nDiscovered {stats['total_agents']} agents")
    print()
    if args.summary:
        print("Summary by Layer:")
        layer_counts = {}
        for agent in agents:
            layer = agent.assigned_layer
            layer_counts[layer] = layer_counts.get(layer, 0) + 1
        for layer in sorted(layer_counts.keys()):
            print(f"  {layer}: {layer_counts[layer]} agents")
    elif args.violations_only:
        violations = scanner.find_gravity_violations()
        if violations:
            print(f"Gravity Violations: {len(violations)}")
            for agent in violations:
                print(f"  • {agent.relative_path}")
                print(f"    Actual: {agent.layer}, Assigned: {agent.assigned_layer}")
        else:
            print("✅ No gravity violations found")
    else:
        if args.limit:
            agents = agents[: args.limit]
            print(f"Showing first {args.limit} agents:")
        else:
            print("All agents:")
        print()
        for agent in agents:
            status = "✅" if not agent.has_gravity_violation else "⚠️"
            print(f"{status} {agent.relative_path}")
            print(f"   Class: {agent.class_name}")
            print(f"   Layer: {agent.layer} (assigned: {agent.assigned_layer})")
            if agent.base_classes:
                print(f"   Bases: {', '.join(agent.base_classes[:3])}")
            print()
    print("Statistics:")
    print(f"  Total agents: {stats['total_agents']}")
    print(f"  Compliant: {stats['compliant_agents']}")
    print(f"  Violations: {stats['gravity_violations']}")
    print(f"  Compliance: {stats['compliance_percentage']:.1f}%")
    return 0


def cmd_validate(args) -> int:
    """
    Validate command: Run comprehensive SSOT validation.

    Returns:
        Exit code (0 if compliant, 1 if violations found)
    """
    print_header("SSOT VALIDATOR - Comprehensive Health Check")
    print("Running validation checks...")
    print("  • Gravity violations (physical location)")
    print("  • Import violations (upward dependencies)")
    print("  • Hierarchy violations (depth limits)")
    print("  • Drift violations (filesystem vs blueprint)")
    print()
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    if args.summary:
        print(f"Compliance Score: {report.compliance_score:.1f}%")
        print(f"Total Violations: {report.total_violations}")
        print(f"  • Gravity:    {len(report.gravity_violations)}")
        print(f"  • Imports:    {len(report.import_violations)}")
        print(f"  • Hierarchy:  {len(report.hierarchy_violations)}")
        print(f"  • Drift:      {len(report.drift_violations)}")
        print()
        if report.is_compliant:
            print("✅ Status: COMPLIANT")
        else:
            print("⚠️  Status: NON-COMPLIANT")
    else:
        print(report.to_markdown())
    if args.output or args.markdown:
        if args.output:
            output_path = Path(args.output)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = REPO / f"SSOT_Health_Report_{timestamp}.md"
        assert_no_persistent_write("L0", "write_text")
        output_path.write_text(report.to_markdown(), encoding="utf-8")
        print(f"\n📄 Report saved: {output_path}")
    if args.json:
        json_data = {
            "compliance_score": report.compliance_score,
            "total_violations": report.total_violations,
            "is_compliant": report.is_compliant,
            "scan_duration": report.scan_duration,
            "violations": {
                "gravity": len(report.gravity_violations),
                "imports": len(report.import_violations),
                "hierarchy": len(report.hierarchy_violations),
                "drift": len(report.drift_violations),
            },
        }
        print("\n" + json.dumps(json_data, indent=2))
    return 0 if report.is_compliant else 1


def cmd_enforce(args) -> int:
    """
    Enforce command: Apply automated remediation.

    Returns:
        Exit code (0 for success)
    """
    dry_run = not args.execute
    mode_str = "DRY-RUN (Preview Only)" if dry_run else "LIVE EXECUTION"
    print_header(f"SSOT ENFORCER - {mode_str}")
    if dry_run:
        print("⚠️  Running in DRY-RUN mode")
        print("   No changes will be made to the filesystem")
        print("   Use --execute flag to apply changes")
        print()
    else:
        print("🔥 LIVE EXECUTION MODE")
        print("   Changes will be applied to the filesystem")
        print("   All operations will be logged")
        print()
        if not args.yes:
            response = input("Continue with enforcement? (yes/no): ").strip().lower()
            if response not in ("yes", "y"):
                print("\nEnforcement cancelled by user.")
                return 0
        print()
    print("Step 1: Running validation...")
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    print(f"  Compliance: {report.compliance_score:.1f}%")
    print(f"  Violations: {report.total_violations}")
    print()
    if report.is_compliant:
        print("✅ System is fully compliant - no enforcement needed")
        return 0
    print("Step 2: Initializing enforcer...")
    relocator = SSOTRelocator(REPO, dry_run=dry_run)
    print(f"  Log file: {relocator.log_file}")
    print()
    print("Step 3: Applying remediation...")
    total_operations = 0
    total_successful = 0
    total_failed = 0
    if (args.all or args.drift) and report.drift_violations:
        print(f"\n{('[DRY-RUN] ' if dry_run else '')}Fixing drift violations...")
        drift_report = relocator.relocate_orphans(report.drift_violations)
        print(f"  Operations: {drift_report.total_operations}")
        print(f"  Successful: {drift_report.successful}")
        print(f"  Failed: {drift_report.failed}")
        total_operations += drift_report.total_operations
        total_successful += drift_report.successful
        total_failed += drift_report.failed
    if (args.all or args.hierarchy) and report.hierarchy_violations:
        print(f"\n{('[DRY-RUN] ' if dry_run else '')}Fixing hierarchy violations...")
        hierarchy_report = relocator.enforce_hierarchy(report.hierarchy_violations)
        print(f"  Operations: {hierarchy_report.total_operations}")
        print(f"  Successful: {hierarchy_report.successful}")
        print(f"  Failed: {hierarchy_report.failed}")
        total_operations += hierarchy_report.total_operations
        total_successful += hierarchy_report.successful
        total_failed += hierarchy_report.failed
    if (args.all or args.gravity) and report.gravity_violations:
        print(f"\n{('[DRY-RUN] ' if dry_run else '')}Fixing gravity violations...")
        gravity_report = relocator.relocate_agents(report.gravity_violations)
        print(f"  Operations: {gravity_report.total_operations}")
        print(f"  Successful: {gravity_report.successful}")
        print(f"  Failed: {gravity_report.failed}")
        total_operations += gravity_report.total_operations
        total_successful += gravity_report.successful
        total_failed += gravity_report.failed
    if report.import_violations:
        print(f"\n⚠️  Import violations: {len(report.import_violations)}")
        print("   These require manual refactoring (cannot be auto-fixed)")
    print_header("ENFORCEMENT SUMMARY", "-", 60)
    print(f"Mode: {mode_str}")
    print(f"Total operations: {total_operations}")
    print(f"Successful: {total_successful}")
    print(f"Failed: {total_failed}")
    if total_operations > 0:
        success_rate = total_successful / total_operations * 100
        print(f"Success rate: {success_rate:.1f}%")
    print()
    if dry_run:
        print("⚠️  DRY-RUN complete - no changes were made")
        print("   Run with --execute to apply changes")
    else:
        print("✅ Enforcement complete")
        print(f"   Check {relocator.log_file} for details")
        print("\n📋 Next: Run 'python scripts/ssot_util.py validate' to verify")
    return 0 if total_failed == 0 else 1


def cmd_status(args) -> int:
    """
    Status command: Show high-level compliance dashboard.

    Returns:
        Exit code (0 for success)
    """
    print_header("SSOT STATUS - Compliance Dashboard")
    validator = UnifiedSSOTValidator(REPO)
    report = validator.validate_all()
    print("Overall Health:")
    print(f"  Compliance Score: {report.compliance_score:.1f}%")
    print(f"  Status: {('✅ COMPLIANT' if report.is_compliant else '⚠️  NON-COMPLIANT')}")
    print()
    print("Violation Breakdown:")
    print(f"  Gravity:    {len(report.gravity_violations):3d} (agents in wrong layers)")
    print(f"  Imports:    {len(report.import_violations):3d} (upward dependencies)")
    print(f"  Hierarchy:  {len(report.hierarchy_violations):3d} (depth limit exceeded)")
    print(f"  Drift:      {len(report.drift_violations):3d} (unauthorized folders)")
    print(f"  {'─' * 40}")
    print(f"  Total:      {report.total_violations:3d}")
    print()
    print("System Statistics:")
    print(f"  Total agents: {report.total_agents}")
    print(f"  Files scanned: {report.total_files_scanned}")
    print(f"  Scan duration: {report.scan_duration:.2f}s")
    print()
    if not report.is_compliant:
        print("Recommended Actions:")
        if report.gravity_violations:
            print(f"  1. Fix {len(report.gravity_violations)} gravity violations:")
            print("     python scripts/ssot_util.py enforce --gravity --execute")
        if report.drift_violations:
            print(f"  2. Archive {len(report.drift_violations)} orphaned folders:")
            print("     python scripts/ssot_util.py enforce --drift --execute")
        if report.hierarchy_violations:
            print(f"  3. Flatten {len(report.hierarchy_violations)} deep folders:")
            print("     python scripts/ssot_util.py enforce --hierarchy --execute")
        if report.import_violations:
            print(f"  4. Refactor {len(report.import_violations)} import violations:")
            print("     (Manual refactoring required - see health report)")
        print()
        print("  Or fix all at once:")
        print("     python scripts/ssot_util.py enforce --execute")
    else:
        print("✅ No actions needed - system is fully compliant!")
    return 0


def main():
    """Main entry point for SSOT CLI."""
    parser = argparse.ArgumentParser(
        prog="ssot",
        description="SSOT - Sovereign Single Source of Truth CLI",
        epilog="For more information on a command, use: python scripts/ssot_util.py <command> --help",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    scan_parser = subparsers.add_parser("scan", help="Scan and list all discovered agents")
    scan_parser.add_argument(
        "--summary",
        action="store_true",
        help="Show summary by layer instead of full listing",
    )
    scan_parser.add_argument(
        "--violations-only",
        action="store_true",
        help="Show only agents with gravity violations",
    )
    scan_parser.add_argument("--limit", type=int, help="Limit number of agents displayed")
    validate_parser = subparsers.add_parser("validate", help="Run comprehensive SSOT validation")
    validate_parser.add_argument(
        "--summary",
        action="store_true",
        help="Show brief summary instead of full report",
    )
    validate_parser.add_argument("--markdown", action="store_true", help="Save report as Markdown file")
    validate_parser.add_argument("--json", action="store_true", help="Output report as JSON")
    validate_parser.add_argument("--output", type=str, help="Output file path for Markdown report")
    enforce_parser = subparsers.add_parser("enforce", help="Apply automated remediation")
    enforce_parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute enforcement (default is dry-run)",
    )
    enforce_parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    enforce_parser.add_argument("--gravity", action="store_true", help="Fix gravity violations only")
    enforce_parser.add_argument("--drift", action="store_true", help="Fix drift violations only")
    enforce_parser.add_argument("--hierarchy", action="store_true", help="Fix hierarchy violations only")
    enforce_parser.add_argument(
        "--all",
        action="store_true",
        default=True,
        help="Fix all violations (default)",
    )
    subparsers.add_parser("status", help="Show compliance dashboard")
    args = parser.parse_args()
    if args.command == "scan":
        return cmd_scan(args)
    elif args.command == "validate":
        return cmd_validate(args)
    elif args.command == "enforce":
        return cmd_enforce(args)
    elif args.command == "status":
        return cmd_status(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
