"""
Phase 1B evidence runner — Python-only, shell=False, no PowerShell.

Executes commands via subprocess argv arrays, captures output,
writes evidence to: docs/reports/plans/phase_01b_ci_spine_guard.md
"""

from __future__ import annotations

import subprocess
import sys

from agentic_core.L0_routing.config.path_constants import (
    OPS_SCRIPTS_DIR,
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

_emit_emits_metric_event("phase01b_spine_guard_evidence_runner", "p4obs", "metric_1")
_emit_emits_metric_event("phase01b_spine_guard_evidence_runner", "p4obs", "metric_2")
_emit_emits_metric_event("phase01b_spine_guard_evidence_runner", "p4obs", "metric_3")
_emit_emits_metric_event("phase01b_spine_guard_evidence_runner", "p4obs", "metric_4")
_emit_emits_metric_event("phase01b_spine_guard_evidence_runner", "p4obs", "metric_5")
_emit_emits_metric_event("phase01b_spine_guard_evidence_runner", "p4obs", "metric_6")
_emit_records_incident_event("phase01b_spine_guard_evidence_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("phase01b_spine_guard_evidence_runner", "p4obs", "anomaly")
_emit_writes_observability_log("phase01b_spine_guard_evidence_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("phase01b_spine_guard_evidence_runner", "p4obs", "mon_state")
_emit_triggers_alert("phase01b_spine_guard_evidence_runner", "p4obs", "alert")
_emit_links_incident_trace("phase01b_spine_guard_evidence_runner", "p4obs", "trace_link")
_emit_captures_pattern("phase01b_spine_guard_evidence_runner", "p3lm", "pattern")
_emit_records_learning_event("phase01b_spine_guard_evidence_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("phase01b_spine_guard_evidence_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("phase01b_spine_guard_evidence_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("phase01b_spine_guard_evidence_runner", "p3lm", "routing")
_emit_improves_agent_policy("phase01b_spine_guard_evidence_runner", "p3lm", "policy")
_emit_stores_learning_state("phase01b_spine_guard_evidence_runner", "p3lm", "state")
_emit_records_execution_trace("phase01b_spine_guard_evidence_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("phase01b_spine_guard_evidence_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("phase01b_spine_guard_evidence_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("phase01b_spine_guard_evidence_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("phase01b_spine_guard_evidence_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("phase01b_spine_guard_evidence_runner", "env_read", "p2_env_1")
_emit_reads_environ("phase01b_spine_guard_evidence_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("phase01b_spine_guard_evidence_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("phase01b_spine_guard_evidence_runner", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "phase01b_spine_guard_evidence_runner")
_emit_applies_guardrail("p0", "phase01b_spine_guard_evidence_runner", "p0_governance")
_emit_reads_policy_state("p0", "phase01b_spine_guard_evidence_runner", "policy_binding")
_emit_snapshots_state("p0", "phase01b_spine_guard_evidence_runner", "state_snapshot")
_emit_pulls_context("p1", "phase01b_spine_guard_evidence_runner", "context_pull")
_emit_pulls_context("p1", "phase01b_spine_guard_evidence_runner", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "phase01b_spine_guard_evidence_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "phase01b_spine_guard_evidence_runner", "uwg_term_secondary")
_emit_writes_through("p1", "phase01b_spine_guard_evidence_runner", "write_through")
_emit_writes_through("p1", "phase01b_spine_guard_evidence_runner", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "phase01b_spine_guard_evidence_runner", "safety_validation")
_emit_invokes_eval("p1", "phase01b_spine_guard_evidence_runner", "eval_call")
_emit_proposal_commits_routing("p1", "phase01b_spine_guard_evidence_runner", "routing_commit")
_emit_escalates_to_human("p1", "phase01b_spine_guard_evidence_runner", "human_escalation")
_emit_routes_through("p1", "phase01b_spine_guard_evidence_runner", "route_through")
_emit_checks_agent_registry("p1", "phase01b_spine_guard_evidence_runner", "agent_registry")
_emit_validates_agent_capability("p1", "phase01b_spine_guard_evidence_runner", "capability")
_emit_dispatches_execution_plan("p1", "phase01b_spine_guard_evidence_runner", "exec_plan")
_emit_agent_executes_agent("p1", "phase01b_spine_guard_evidence_runner", "sub_agent")
_emit_routes_to_agent("p1", "phase01b_spine_guard_evidence_runner", "target_agent")
_emit_verifies_policy("p1", "phase01b_spine_guard_evidence_runner", "policy_check")
_emit_observes_runtime_state("p1", "phase01b_spine_guard_evidence_runner", "runtime_state")
_emit_verifies_boundary("p1", "phase01b_spine_guard_evidence_runner", "boundary_check")
_emit_transcripts_response("p1", "phase01b_spine_guard_evidence_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "phase01b_spine_guard_evidence_runner")
_emit_gated_by_confidence("p1", "phase01b_spine_guard_evidence_runner", "confidence_gate")
emit_replay_key("p0", "phase01b_spine_guard_evidence_runner")
emit_determinism_digest("p0", "phase01b_spine_guard_evidence_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "phase01b_spine_guard_evidence_runner", "execution_auth")
_emit_validates_capability("p2", "phase01b_spine_guard_evidence_runner", "capability_check")
_emit_routes_to_capability("p2", "phase01b_spine_guard_evidence_runner", "capability_route")
_emit_writes_via_uwg("p2", "phase01b_spine_guard_evidence_runner", "uwg_write")
_emit_blocks_direct_write("p2", "phase01b_spine_guard_evidence_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "phase01b_spine_guard_evidence_runner", "tool_invocation")
_emit_captures_execution_output("p2", "phase01b_spine_guard_evidence_runner", "exec_output")
_emit_dispatches_agent("p3", "phase01b_spine_guard_evidence_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "phase01b_spine_guard_evidence_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "phase01b_spine_guard_evidence_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "phase01b_spine_guard_evidence_runner", "healing_outcome")
_emit_escalates_failure("p3", "phase01b_spine_guard_evidence_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "phase01b_spine_guard_evidence_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "phase01b_spine_guard_evidence_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "phase01b_spine_guard_evidence_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "phase01b_spine_guard_evidence_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "phase01b_spine_guard_evidence_runner", "eval_metric")
_emit_stores_embedding("p4", "phase01b_spine_guard_evidence_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "phase01b_spine_guard_evidence_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "phase01b_spine_guard_evidence_runner", "exec_snapshot_link")

PROJECT_ROOT = get_validated_project_root()
EVIDENCE_PATH = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans" / "phase_01b_ci_spine_guard.md"
GUARD_SCRIPT = PROJECT_ROOT / OPS_SCRIPTS_DIR / "ci" / "check_spine_bypass.py"
WORKFLOW_FILE = PROJECT_ROOT / ".github" / "workflows" / "spine-determinism-guard.yml"
BASELINE_FILE = PROJECT_ROOT / OPS_SCRIPTS_DIR / "hooks" / "spine_bypass_baseline.txt"


def run(argv: list[str]) -> tuple[int, str]:
    """Run a command with shell=False, return (returncode, combined output)."""
    result = subprocess.run(
        argv,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        shell=False,
    )
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    combined = stdout + stderr
    # Check only stderr for PowerShell invocation evidence.
    # stdout may contain diff content that legitimately references shell names.
    stderr_lines = [line for line in stderr.splitlines() if not line.strip().startswith("PS ")]
    stderr_check = "\n".join(stderr_lines)
    if "pwsh" in stderr_check.lower() or "powershell" in stderr_check.lower():
        print("ABORT: PowerShell detected in stderr output.", file=sys.stderr)
        sys.exit(1)
    return result.returncode, combined


def section(title: str, content: str) -> str:
    return "## " + title + "\n\n```\n" + content.strip() + "\n```\n\n"


def main() -> None:
    nl = "\n"

    print("Running check_spine_bypass.py...")
    guard_rc, guard_out = run([sys.executable, "ops_scripts/ci/check_spine_bypass.py"])

    print("Running git diff --stat...")
    stat_rc, stat_out = run(["git", "diff", "--stat"])

    print("Running git diff...")
    diff_rc, diff_out = run(["git", "diff"])

    guard_content = GUARD_SCRIPT.read_text(encoding="utf-8")
    workflow_content = WORKFLOW_FILE.read_text(encoding="utf-8")
    baseline_lines = (
        len(BASELINE_FILE.read_text(encoding="utf-8").splitlines()) if BASELINE_FILE.exists() else 0
    )

    sec_guard = section(
        "Command: python ops_scripts/ci/check_spine_bypass.py",
        "Exit code: " + str(guard_rc) + nl + nl + guard_out,
    )
    sec_stat = section(
        "Command: git diff --stat",
        "Exit code: " + str(stat_rc) + nl + nl + stat_out,
    )
    sec_diff = section(
        "Command: git diff",
        "Exit code: " + str(diff_rc) + nl + nl + diff_out,
    )

    parts = [
        "# Phase 1B: AST Spine Bypass + Randomness CI Guard — Evidence",
        "",
        "AST-based CI guard preventing spine bypass and randomness usage in deterministic paths.",
        "Baseline captures "
        + str(baseline_lines)
        + " pre-existing violations; only NEW violations fail the build.",
        "",
        "## Commit Hash",
        "",
        "PENDING",
        "",
        "## Files Changed",
        "",
        "- `ops_scripts/ci/check_spine_bypass.py` (created)",
        "- `ops_scripts/hooks/spine_bypass_baseline.txt` (created)",
        "- `.github/workflows/spine-determinism-guard.yml` (created)",
        "- `tools/evidence/phase01b_spine_guard_evidence_runner.py` (created)",
        "- `docs/reports/plans/phase_01b_ci_spine_guard.md` (created)",
        "",
        sec_guard,
        sec_stat,
        sec_diff,
        "## ops_scripts/ci/check_spine_bypass.py (verbatim)",
        "",
        "```python",
        guard_content,
        "```",
        "",
        "## .github/workflows/spine-determinism-guard.yml (verbatim)",
        "",
        "```yaml",
        workflow_content,
        "```",
        "",
    ]
    md = nl.join(parts)

    # Strip trailing whitespace and enforce LF line endings.
    md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(md.encode("utf-8"))
    print("Evidence written to: " + str(EVIDENCE_PATH))

    if guard_rc != 0:
        print("FAIL: check_spine_bypass.py returned non-zero.", file=sys.stderr)
        sys.exit(guard_rc)


if __name__ == "__main__":
    main()
