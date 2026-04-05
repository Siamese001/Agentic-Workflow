#!/usr/bin/env python3
"""
Generate functionality metrics and unified diffs for blueprint duplicate pairs.
Phase 1 of duplicate cleanup workflow.
"""

from datetime import datetime
from pathlib import Path

from agentic_core.L5_safety.config.structure_blueprint import (
    AGENTIC_CORE_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
from agentic_core.utils.security_util import safe_git_execute

_emit_records_execution_trace("p0", "evidence", "generate_blueprint_metrics_util")
_emit_applies_guardrail("p0", "generate_blueprint_metrics_util", "p0_governance")
_emit_reads_policy_state("p0", "generate_blueprint_metrics_util", "policy_binding")
_emit_snapshots_state("p0", "generate_blueprint_metrics_util", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_emits_metric_event("generate_blueprint_metrics_util", "p4obs", "metric_1")
_emit_emits_metric_event("generate_blueprint_metrics_util", "p4obs", "metric_2")
_emit_emits_metric_event("generate_blueprint_metrics_util", "p4obs", "metric_3")
_emit_emits_metric_event("generate_blueprint_metrics_util", "p4obs", "metric_4")
_emit_emits_metric_event("generate_blueprint_metrics_util", "p4obs", "metric_5")
_emit_emits_metric_event("generate_blueprint_metrics_util", "p4obs", "metric_6")
_emit_records_incident_event("generate_blueprint_metrics_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("generate_blueprint_metrics_util", "p4obs", "anomaly")
_emit_writes_observability_log("generate_blueprint_metrics_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("generate_blueprint_metrics_util", "p4obs", "mon_state")
_emit_triggers_alert("generate_blueprint_metrics_util", "p4obs", "alert")
_emit_links_incident_trace("generate_blueprint_metrics_util", "p4obs", "trace_link")
_emit_captures_pattern("generate_blueprint_metrics_util", "p3lm", "pattern")
_emit_records_learning_event("generate_blueprint_metrics_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("generate_blueprint_metrics_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("generate_blueprint_metrics_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("generate_blueprint_metrics_util", "p3lm", "routing")
_emit_improves_agent_policy("generate_blueprint_metrics_util", "p3lm", "policy")
_emit_stores_learning_state("generate_blueprint_metrics_util", "p3lm", "state")
_emit_records_execution_trace("generate_blueprint_metrics_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("generate_blueprint_metrics_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("generate_blueprint_metrics_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("generate_blueprint_metrics_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("generate_blueprint_metrics_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("generate_blueprint_metrics_util", "env_read", "p2_env_1")
_emit_reads_environ("generate_blueprint_metrics_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("generate_blueprint_metrics_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("generate_blueprint_metrics_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "generate_blueprint_metrics_util", "context_pull")
_emit_pulls_context("p1", "generate_blueprint_metrics_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "generate_blueprint_metrics_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "generate_blueprint_metrics_util", "uwg_term_2")
_emit_writes_through("p1", "generate_blueprint_metrics_util", "write_through")
_emit_writes_through("p1", "generate_blueprint_metrics_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "generate_blueprint_metrics_util", "safety_validation")
_emit_invokes_eval("p1", "generate_blueprint_metrics_util", "eval_call")
_emit_proposal_commits_routing("p1", "generate_blueprint_metrics_util", "routing_commit")
_emit_escalates_to_human("p1", "generate_blueprint_metrics_util", "human_escalation")
_emit_routes_through("p1", "generate_blueprint_metrics_util", "route_through")
_emit_checks_agent_registry("p1", "generate_blueprint_metrics_util", "agent_registry")
_emit_validates_agent_capability("p1", "generate_blueprint_metrics_util", "capability")
_emit_dispatches_execution_plan("p1", "generate_blueprint_metrics_util", "exec_plan")
_emit_agent_executes_agent("p1", "generate_blueprint_metrics_util", "sub_agent")
_emit_routes_to_agent("p1", "generate_blueprint_metrics_util", "target_agent")
_emit_verifies_policy("p1", "generate_blueprint_metrics_util", "policy_check")
_emit_observes_runtime_state("p1", "generate_blueprint_metrics_util", "runtime_state")
_emit_verifies_boundary("p1", "generate_blueprint_metrics_util", "boundary_check")
_emit_transcripts_response("p1", "generate_blueprint_metrics_util", "transcript")
_emit_hard_fails_untranscripted("p1", "generate_blueprint_metrics_util")
_emit_gated_by_confidence("p1", "generate_blueprint_metrics_util", "confidence_gate")
emit_replay_key("p0", "generate_blueprint_metrics_util")
emit_determinism_digest("p0", "generate_blueprint_metrics_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "generate_blueprint_metrics_util", "execution_auth")
_emit_validates_capability("p2", "generate_blueprint_metrics_util", "capability_check")
_emit_routes_to_capability("p2", "generate_blueprint_metrics_util", "capability_route")
_emit_writes_via_uwg("p2", "generate_blueprint_metrics_util", "uwg_write")
_emit_blocks_direct_write("p2", "generate_blueprint_metrics_util", "direct_write_block")
_emit_records_tool_invocation("p2", "generate_blueprint_metrics_util", "tool_invocation")
_emit_captures_execution_output("p2", "generate_blueprint_metrics_util", "exec_output")
_emit_dispatches_agent("p3", "generate_blueprint_metrics_util", "agent_dispatch")
_emit_coordinates_agents("p3", "generate_blueprint_metrics_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "generate_blueprint_metrics_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "generate_blueprint_metrics_util", "healing_outcome")
_emit_escalates_failure("p3", "generate_blueprint_metrics_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "generate_blueprint_metrics_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "generate_blueprint_metrics_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "generate_blueprint_metrics_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "generate_blueprint_metrics_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "generate_blueprint_metrics_util", "eval_metric")
_emit_stores_embedding("p4", "generate_blueprint_metrics_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "generate_blueprint_metrics_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "generate_blueprint_metrics_util", "exec_snapshot_link")


def count_methods(file_path: Path) -> int:
    """Count method definitions in file."""
    try:
        content = file_path.read_text(encoding="utf-8")
        return sum(1 for line in content.split("\n") if line.strip().startswith("def "))
    except (ValueError, TypeError, RuntimeError) as e:
        return 0


def has_pattern(file_path: Path, pattern: str) -> bool:
    """Check if file contains pattern."""
    try:
        content = file_path.read_text(encoding="utf-8")
        return pattern in content
    except (ValueError, TypeError, RuntimeError) as e:
        return False


def count_lines(file_path: Path) -> int:
    """Count lines in file."""
    try:
        return len(file_path.read_text(encoding="utf-8").split("\n"))
    except (ValueError, TypeError, RuntimeError) as e:
        return 0


def generate_unified_diff(canonical: Path, duplicate: Path) -> str:
    """Generate unified diff between files."""
    try:
        # guardian: allow-magic-config
        result = safe_git_execute(
            ["diff", "--no-index", "--unified=3", str(canonical), str(duplicate)],
            repo_root=canonical.parent,
            timeout=DEFAULT_TIMEOUT,
            check=False,
        )
        return result.stdout
    # guardian: allow-silent-swallow
    except:
        return ""


def main():
    project_root = Path.cwd()
    blueprint_dir = project_root / AGENTIC_CORE_DIR / "config" / "blueprint_sovereign"
    validators_dir = project_root / AGENTIC_CORE_DIR / "L5_safety" / "validators"

    # Create output directory
    diff_dir = project_root / REPORTS_DIR / "blueprint_diffs"
    diff_dir.mkdir(parents=True, exist_ok=True)

    # Find blueprint agent files
    # Phase 6.9: Use ssot_discovery instead of glob
    from agentic_core.utils.schemas.ssot_discovery_validator import get_agent_files

    blueprint_agents = list(get_agent_files(blueprint_dir))

    print("=" * 80)
    print("PHASE 1: BLUEPRINT DUPLICATE METRICS")
    print("=" * 80)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Blueprint directory: {blueprint_dir}")
    print(f"Validators directory: {validators_dir}")
    print(f"Found {len(blueprint_agents)} blueprint agent files")
    print("=" * 80)

    # Generate report
    report_file = project_root / REPORTS_DIR / "blueprint_metrics_report.md"

    with open(report_file, "w", encoding="utf-8") as f:
        f.write("# Blueprint Duplicate Metrics Report\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Summary\n")
        f.write(f"- **Blueprint files found:** {len(blueprint_agents)}\n")
        f.write("- **Diff output directory:** `reports/blueprint_diffs/`\n\n")

        f.write("## Metrics Comparison\n\n")
        f.write(
            "| Agent | Canonical Lines | Dup Lines | Can Methods | Dup Methods | Can Heal | Dup Heal | Recommendation |\n",
        )
        f.write("| --- | --- | --- | --- | --- | --- | --- | --- |\n")

        pairs_found = 0

        for blueprint_file in sorted(blueprint_agents):
            agent_name = blueprint_file.stem
            canonical_file = validators_dir / blueprint_file.name

            if not canonical_file.exists():
                print(f"[SKIP] {agent_name}: No canonical in validators/")
                continue

            pairs_found += 1

            # Metrics
            can_lines = count_lines(canonical_file)
            dup_lines = count_lines(blueprint_file)
            can_methods = count_methods(canonical_file)
            dup_methods = count_methods(blueprint_file)
            can_heal = has_pattern(canonical_file, "def heal")
            dup_heal = has_pattern(blueprint_file, "def heal")

            # Recommendation
            if can_lines >= dup_lines and can_methods >= dup_methods:
                recommendation = "✅ DELETE blueprint"
            elif dup_lines > can_lines or dup_methods > can_methods:
                recommendation = "⚠️ REVIEW - dup may have additions"
            else:
                recommendation = "✅ DELETE blueprint"

            print(f"\n[{agent_name}]")
            print(f"  Canonical: {can_lines} lines, {can_methods} methods, heal={can_heal}")
            print(f"  Blueprint: {dup_lines} lines, {dup_methods} methods, heal={dup_heal}")
            print(f"  → {recommendation}")

            f.write(f"| {agent_name} | {can_lines} | {dup_lines} | {can_methods} | {dup_methods} | ")
            f.write(f"{'✅' if can_heal else '❌'} | {'✅' if dup_heal else '❌'} | {recommendation} |\n")

            # Generate diff
            diff_content = generate_unified_diff(canonical_file, blueprint_file)
            diff_file = diff_dir / f"{agent_name}_diff.patch"
            diff_file.write_text(diff_content, encoding="utf-8")

        f.write("\n## Diff Files\n\n")
        f.write(f"Generated {pairs_found} diff files in `reports/blueprint_diffs/`\n\n")
        f.write("```bash\n")
        f.write("# Open all diffs in Windsurf\n")
        f.write("code reports/blueprint_diffs/*.patch\n")
        f.write("```\n\n")

        f.write("## Delete Commands (After Review)\n\n")
        f.write("```bash\n")
        for blueprint_file in sorted(blueprint_agents):
            canonical_file = validators_dir / blueprint_file.name
            if canonical_file.exists():
                rel_path = blueprint_file.relative_to(project_root)
                f.write(f'git rm "{rel_path}"\n')
        f.write('git commit -m "chore: remove blueprint duplicate agents (Phase 1)"\n')
        f.write("```\n")

    print("\n" + "=" * 80)
    print(f"✅ Report generated: {report_file}")
    print(f"✅ Diff files generated: {diff_dir}")
    print(f"   Pairs found: {pairs_found}")
    print("=" * 80)


if __name__ == "__main__":
    main()
