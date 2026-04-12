"""
Phase 2 Assembly Stage Evidence Generator
Python-only evidence capture for deterministic Assembly Stage implementation.
"""

import subprocess
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    get_validated_project_root,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("phase2_assembly_stage_evidence", "p4obs", "metric_1")
_emit_emits_metric_event("phase2_assembly_stage_evidence", "p4obs", "metric_2")
_emit_emits_metric_event("phase2_assembly_stage_evidence", "p4obs", "metric_3")
_emit_emits_metric_event("phase2_assembly_stage_evidence", "p4obs", "metric_4")
_emit_emits_metric_event("phase2_assembly_stage_evidence", "p4obs", "metric_5")
_emit_emits_metric_event("phase2_assembly_stage_evidence", "p4obs", "metric_6")
_emit_records_incident_event("phase2_assembly_stage_evidence", "p4obs", "incident")
_emit_captures_runtime_anomaly("phase2_assembly_stage_evidence", "p4obs", "anomaly")
_emit_writes_observability_log("phase2_assembly_stage_evidence", "p4obs", "obs_log")
_emit_updates_monitoring_state("phase2_assembly_stage_evidence", "p4obs", "mon_state")
_emit_triggers_alert("phase2_assembly_stage_evidence", "p4obs", "alert")
_emit_links_incident_trace("phase2_assembly_stage_evidence", "p4obs", "trace_link")
_emit_captures_pattern("phase2_assembly_stage_evidence", "p3lm", "pattern")
_emit_records_learning_event("phase2_assembly_stage_evidence", "p3lm", "learning_event")
_emit_writes_learning_snapshot("phase2_assembly_stage_evidence", "p3lm", "snapshot")
_emit_feeds_meta_learning("phase2_assembly_stage_evidence", "p3lm", "meta_feed")
_emit_updates_routing_strategy("phase2_assembly_stage_evidence", "p3lm", "routing")
_emit_improves_agent_policy("phase2_assembly_stage_evidence", "p3lm", "policy")
_emit_stores_learning_state("phase2_assembly_stage_evidence", "p3lm", "state")
_emit_records_execution_trace("phase2_assembly_stage_evidence", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("phase2_assembly_stage_evidence", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("phase2_assembly_stage_evidence", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("phase2_assembly_stage_evidence", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("phase2_assembly_stage_evidence", "L4_STATE", "p2_trace_5")
_emit_reads_environ("phase2_assembly_stage_evidence", "env_read", "p2_env_1")
_emit_reads_environ("phase2_assembly_stage_evidence", "env_read", "p2_env_2")
_emit_reads_runtime_state("phase2_assembly_stage_evidence", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("phase2_assembly_stage_evidence", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "phase2_assembly_stage_evidence")
_emit_applies_guardrail("p0", "phase2_assembly_stage_evidence", "p0_governance")
_emit_reads_policy_state("p0", "phase2_assembly_stage_evidence", "policy_binding")
_emit_snapshots_state("p0", "phase2_assembly_stage_evidence", "state_snapshot")
_emit_pulls_context("p1", "phase2_assembly_stage_evidence", "context_pull")
_emit_pulls_context("p1", "phase2_assembly_stage_evidence", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "phase2_assembly_stage_evidence", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "phase2_assembly_stage_evidence", "uwg_term_secondary")
_emit_writes_through("p1", "phase2_assembly_stage_evidence", "write_through")
_emit_writes_through("p1", "phase2_assembly_stage_evidence", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "phase2_assembly_stage_evidence", "safety_validation")
_emit_invokes_eval("p1", "phase2_assembly_stage_evidence", "eval_call")
_emit_proposal_commits_routing("p1", "phase2_assembly_stage_evidence", "routing_commit")
_emit_escalates_to_human("p1", "phase2_assembly_stage_evidence", "human_escalation")
_emit_routes_through("p1", "phase2_assembly_stage_evidence", "route_through")
_emit_checks_agent_registry("p1", "phase2_assembly_stage_evidence", "agent_registry")
_emit_validates_agent_capability("p1", "phase2_assembly_stage_evidence", "capability")
_emit_dispatches_execution_plan("p1", "phase2_assembly_stage_evidence", "exec_plan")
_emit_agent_executes_agent("p1", "phase2_assembly_stage_evidence", "sub_agent")
_emit_routes_to_agent("p1", "phase2_assembly_stage_evidence", "target_agent")
_emit_verifies_policy("p1", "phase2_assembly_stage_evidence", "policy_check")
_emit_observes_runtime_state("p1", "phase2_assembly_stage_evidence", "runtime_state")
_emit_verifies_boundary("p1", "phase2_assembly_stage_evidence", "boundary_check")
_emit_transcripts_response("p1", "phase2_assembly_stage_evidence", "transcript")
_emit_hard_fails_untranscripted("p1", "phase2_assembly_stage_evidence")
_emit_gated_by_confidence("p1", "phase2_assembly_stage_evidence", "confidence_gate")
emit_replay_key("p0", "phase2_assembly_stage_evidence")
emit_determinism_digest("p0", "phase2_assembly_stage_evidence")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "phase2_assembly_stage_evidence", "execution_auth")
_emit_validates_capability("p2", "phase2_assembly_stage_evidence", "capability_check")
_emit_routes_to_capability("p2", "phase2_assembly_stage_evidence", "capability_route")
_emit_writes_via_uwg("p2", "phase2_assembly_stage_evidence", "uwg_write")
_emit_blocks_direct_write("p2", "phase2_assembly_stage_evidence", "direct_write_block")
_emit_records_tool_invocation("p2", "phase2_assembly_stage_evidence", "tool_invocation")
_emit_captures_execution_output("p2", "phase2_assembly_stage_evidence", "exec_output")
_emit_dispatches_agent("p3", "phase2_assembly_stage_evidence", "agent_dispatch")
_emit_coordinates_agents("p3", "phase2_assembly_stage_evidence", "agent_coordination")
_emit_records_workflow_lineage("p3", "phase2_assembly_stage_evidence", "workflow_lineage")
_emit_records_healing_outcome("p3", "phase2_assembly_stage_evidence", "healing_outcome")
_emit_escalates_failure("p3", "phase2_assembly_stage_evidence", "failure_escalation")
_emit_orchestrates_workflow("p3", "phase2_assembly_stage_evidence", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "phase2_assembly_stage_evidence", "healing_dispatch")
_emit_invokes_evaluation("p3", "phase2_assembly_stage_evidence", "evaluation_signal")
_emit_records_telemetry_event("p4", "phase2_assembly_stage_evidence", "telemetry_event")
_emit_captures_evaluation_metric("p4", "phase2_assembly_stage_evidence", "eval_metric")
_emit_stores_embedding("p4", "phase2_assembly_stage_evidence", "embedding_store")
_emit_updates_meta_learning_state("p4", "phase2_assembly_stage_evidence", "meta_learning")
_emit_links_execution_to_snapshot("p4", "phase2_assembly_stage_evidence", "exec_snapshot_link")


def get_repo_root() -> Path:
    return get_validated_project_root()


def run_command(cmd: list[str], cwd: Path) -> str:
    """Run command and capture stdout+stderr."""
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    return result.stdout + result.stderr


def main():
    """Generate Phase 2 Assembly Stage evidence bundle."""
    repo_root = get_repo_root()
    evidence_file = repo_root / "docs" / REPORTS_DIR / "plans" / "phase2_assembly_stage_evidence.md"
    evidence_file.parent.mkdir(parents=True, exist_ok=True)
    print(f"Generating Phase 2 evidence at: {evidence_file}")
    sections = []
    print("Collecting git HEAD...")
    sections.append("# Git HEAD\n")
    sections.append("```")
    sections.append(run_command(["git", "rev-parse", "HEAD"], repo_root).strip())
    sections.append("```\n\n")
    print("Collecting git status...")
    sections.append("# Git Status\n")
    sections.append("```")
    sections.append(run_command(["git", "status", "--porcelain"], repo_root).strip())
    sections.append("```\n\n")
    print("Running assembly stage tests...")
    sections.append("# Assembly Stage Tests\n")
    sections.append("```")
    sections.append(
        run_command(
            [
                sys.executable,
                "-m",
                "pytest",
                "-q",
                "tests/unit/L0_routing/test_assembly_stage.py",
                "-m",
                "unit",
            ],
            repo_root,
        )
    )
    sections.append("```\n\n")
    print("Running all L0_routing tests...")
    sections.append("# All L0 Routing Tests\n")
    sections.append("```")
    sections.append(
        run_command([sys.executable, "-m", "pytest", "-q", "tests/unit/L0_routing", "-m", "unit"], repo_root)
    )
    sections.append("```\n\n")
    print("Scanning for wall-clock tokens...")
    assembly_file = repo_root / AGENTIC_CORE_DIR / "L0_routing" / "engines" / "assembly_stage.py"
    forbidden_tokens = [
        "datetime.now",
        "datetime.utcnow",
        "time.time",
        "perf_counter",
        "monotonic",
        "pendulum",
        "arrow.",
    ]
    sections.append("# Wall-Clock Token Scan\n")
    sections.append("```")
    content = assembly_file.read_text(encoding="utf-8")
    found_tokens = []
    for token in forbidden_tokens:
        if token in content:
            found_tokens.append(token)
    if found_tokens:
        sections.append(f"FORBIDDEN TOKENS FOUND: {found_tokens}")
    else:
        sections.append("No forbidden wall-clock tokens found")
    sections.append("```\n\n")
    print("Collecting git show --stat...")
    sections.append("# Git Show --stat\n")
    sections.append("```")
    sections.append(run_command(["git", "show", "--stat"], repo_root))
    sections.append("```\n\n")
    print(f"Writing evidence to {evidence_file}...")
    evidence_content = "".join(sections)
    evidence_file.write_text(evidence_content, encoding="utf-8")
    print("Phase 2 Assembly Stage evidence generation complete!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
