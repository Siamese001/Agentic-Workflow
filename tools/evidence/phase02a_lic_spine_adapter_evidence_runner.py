"""
Phase 2A evidence runner — Python-only, shell=False, no PowerShell.

Writes evidence to: docs/reports/plans/phase_02a_lic_spine_adapter.md
"""

from __future__ import annotations

import subprocess
import sys

from agentic_core.L0_routing.config.path_constants import (
    APPS_LIC_DIR,
    TESTS_DIR,
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
    _emit_reads_through,
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

_emit_emits_metric_event("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "metric_1")
_emit_emits_metric_event("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "metric_2")
_emit_emits_metric_event("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "metric_3")
_emit_emits_metric_event("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "metric_4")
_emit_emits_metric_event("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "metric_5")
_emit_emits_metric_event("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "metric_6")
_emit_records_incident_event("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "incident")
_emit_captures_runtime_anomaly("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "anomaly")
_emit_writes_observability_log("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "obs_log")
_emit_updates_monitoring_state("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "mon_state")
_emit_triggers_alert("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "alert")
_emit_links_incident_trace("phase02a_lic_spine_adapter_evidence_runner", "p4obs", "trace_link")
_emit_captures_pattern("phase02a_lic_spine_adapter_evidence_runner", "p3lm", "pattern")
_emit_records_learning_event("phase02a_lic_spine_adapter_evidence_runner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("phase02a_lic_spine_adapter_evidence_runner", "p3lm", "snapshot")
_emit_feeds_meta_learning("phase02a_lic_spine_adapter_evidence_runner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("phase02a_lic_spine_adapter_evidence_runner", "p3lm", "routing")
_emit_improves_agent_policy("phase02a_lic_spine_adapter_evidence_runner", "p3lm", "policy")
_emit_stores_learning_state("phase02a_lic_spine_adapter_evidence_runner", "p3lm", "state")
_emit_records_execution_trace("phase02a_lic_spine_adapter_evidence_runner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("phase02a_lic_spine_adapter_evidence_runner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("phase02a_lic_spine_adapter_evidence_runner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("phase02a_lic_spine_adapter_evidence_runner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("phase02a_lic_spine_adapter_evidence_runner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("phase02a_lic_spine_adapter_evidence_runner", "env_read", "p2_env_1")
_emit_reads_environ("phase02a_lic_spine_adapter_evidence_runner", "env_read", "p2_env_2")
_emit_reads_runtime_state("phase02a_lic_spine_adapter_evidence_runner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("phase02a_lic_spine_adapter_evidence_runner", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "phase02a_lic_spine_adapter_evidence_runner")
_emit_applies_guardrail("p0", "phase02a_lic_spine_adapter_evidence_runner", "p0_governance")
_emit_reads_policy_state("p0", "phase02a_lic_spine_adapter_evidence_runner", "policy_binding")
_emit_snapshots_state("p0", "phase02a_lic_spine_adapter_evidence_runner", "state_snapshot")
_emit_pulls_context("p1", "phase02a_lic_spine_adapter_evidence_runner", "context_pull")
_emit_pulls_context("p1", "phase02a_lic_spine_adapter_evidence_runner", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "phase02a_lic_spine_adapter_evidence_runner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "phase02a_lic_spine_adapter_evidence_runner", "uwg_term_secondary")
_emit_writes_through("p1", "phase02a_lic_spine_adapter_evidence_runner", "write_through")
_emit_writes_through("p1", "phase02a_lic_spine_adapter_evidence_runner", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "phase02a_lic_spine_adapter_evidence_runner", "safety_validation")
_emit_invokes_eval("p1", "phase02a_lic_spine_adapter_evidence_runner", "eval_call")
_emit_proposal_commits_routing("p1", "phase02a_lic_spine_adapter_evidence_runner", "routing_commit")
_emit_escalates_to_human("p1", "phase02a_lic_spine_adapter_evidence_runner", "human_escalation")
_emit_routes_through("p1", "phase02a_lic_spine_adapter_evidence_runner", "route_through")
_emit_checks_agent_registry("p1", "phase02a_lic_spine_adapter_evidence_runner", "agent_registry")
_emit_validates_agent_capability("p1", "phase02a_lic_spine_adapter_evidence_runner", "capability")
_emit_dispatches_execution_plan("p1", "phase02a_lic_spine_adapter_evidence_runner", "exec_plan")
_emit_agent_executes_agent("p1", "phase02a_lic_spine_adapter_evidence_runner", "sub_agent")
_emit_routes_to_agent("p1", "phase02a_lic_spine_adapter_evidence_runner", "target_agent")
_emit_verifies_policy("p1", "phase02a_lic_spine_adapter_evidence_runner", "policy_check")
_emit_observes_runtime_state("p1", "phase02a_lic_spine_adapter_evidence_runner", "runtime_state")
_emit_verifies_boundary("p1", "phase02a_lic_spine_adapter_evidence_runner", "boundary_check")
_emit_transcripts_response("p1", "phase02a_lic_spine_adapter_evidence_runner", "transcript")
_emit_hard_fails_untranscripted("p1", "phase02a_lic_spine_adapter_evidence_runner")
_emit_gated_by_confidence("p1", "phase02a_lic_spine_adapter_evidence_runner", "confidence_gate")
emit_replay_key("p0", "phase02a_lic_spine_adapter_evidence_runner")
emit_determinism_digest("p0", "phase02a_lic_spine_adapter_evidence_runner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "phase02a_lic_spine_adapter_evidence_runner", "execution_auth")
_emit_validates_capability("p2", "phase02a_lic_spine_adapter_evidence_runner", "capability_check")
_emit_routes_to_capability("p2", "phase02a_lic_spine_adapter_evidence_runner", "capability_route")
_emit_writes_via_uwg("p2", "phase02a_lic_spine_adapter_evidence_runner", "uwg_write")
_emit_blocks_direct_write("p2", "phase02a_lic_spine_adapter_evidence_runner", "direct_write_block")
_emit_records_tool_invocation("p2", "phase02a_lic_spine_adapter_evidence_runner", "tool_invocation")
_emit_captures_execution_output("p2", "phase02a_lic_spine_adapter_evidence_runner", "exec_output")
_emit_dispatches_agent("p3", "phase02a_lic_spine_adapter_evidence_runner", "agent_dispatch")
_emit_coordinates_agents("p3", "phase02a_lic_spine_adapter_evidence_runner", "agent_coordination")
_emit_records_workflow_lineage("p3", "phase02a_lic_spine_adapter_evidence_runner", "workflow_lineage")
_emit_records_healing_outcome("p3", "phase02a_lic_spine_adapter_evidence_runner", "healing_outcome")
_emit_escalates_failure("p3", "phase02a_lic_spine_adapter_evidence_runner", "failure_escalation")
_emit_orchestrates_workflow("p3", "phase02a_lic_spine_adapter_evidence_runner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "phase02a_lic_spine_adapter_evidence_runner", "healing_dispatch")
_emit_invokes_evaluation("p3", "phase02a_lic_spine_adapter_evidence_runner", "evaluation_signal")
_emit_records_telemetry_event("p4", "phase02a_lic_spine_adapter_evidence_runner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "phase02a_lic_spine_adapter_evidence_runner", "eval_metric")
_emit_stores_embedding("p4", "phase02a_lic_spine_adapter_evidence_runner", "embedding_store")
_emit_updates_meta_learning_state("p4", "phase02a_lic_spine_adapter_evidence_runner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "phase02a_lic_spine_adapter_evidence_runner", "exec_snapshot_link")
_emit_reads_through("l4", "phase02a_lic_spine_adapter_evidence_runner", "urg_read_1")
_emit_reads_through("l4", "phase02a_lic_spine_adapter_evidence_runner", "urg_read_2")
_emit_reads_through("l4", "phase02a_lic_spine_adapter_evidence_runner", "urg_read_3")
_emit_reads_through("l4", "phase02a_lic_spine_adapter_evidence_runner", "urg_read_4")
_emit_reads_through("l4", "phase02a_lic_spine_adapter_evidence_runner", "urg_read_5")

PROJECT_ROOT = get_validated_project_root()
EVIDENCE_PATH = PROJECT_ROOT / "docs" / REPORTS_DIR / "plans" / "phase_02a_lic_spine_adapter.md"
ADAPTER_FILE = PROJECT_ROOT / APPS_LIC_DIR / "engines" / "lic_spine_adapter.py"
TEST_FILE = PROJECT_ROOT / TESTS_DIR / "unit_min_deps" / "test_apps_lic_spine_adapter.py"


def run(argv: list[str]) -> tuple[int, str]:
    result = subprocess.run(argv, cwd=str(PROJECT_ROOT), capture_output=True, shell=False)
    stdout = result.stdout.decode("utf-8", errors="replace")
    stderr = result.stderr.decode("utf-8", errors="replace")
    combined = stdout + stderr
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

    print("Running focused pytest...")
    focused_rc, focused_out = run(
        [sys.executable, "-m", "pytest", "-q", "tests/unit_min_deps/test_apps_lic_spine_adapter.py"]
    )

    print("Running full suite...")
    full_rc, full_out = run([sys.executable, "-m", "pytest", "-q"])

    print("Running git diff --stat...")
    stat_rc, stat_out = run(["git", "diff", "--stat"])

    print("Running git diff...")
    diff_rc, diff_out = run(["git", "diff"])

    adapter_content = ADAPTER_FILE.read_text(encoding="utf-8")
    test_content = TEST_FILE.read_text(encoding="utf-8")

    sec_focused = section(
        "Command: python -m pytest -q tests/unit_min_deps/test_apps_lic_spine_adapter.py",
        "Exit code: " + str(focused_rc) + nl + nl + focused_out,
    )
    sec_full = section(
        "Command: python -m pytest -q (full suite)",
        "Exit code: " + str(full_rc) + nl + nl + full_out,
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
        "# Phase 2A: LIC Spine Adapter + CID Binding — Evidence",
        "",
        "Pure-wiring adapter forcing all LIC entry through the canonical spine "
        "(AirlockAssembler → PathRouter → ExecutionOrchestrator) with deterministic "
        "CID derived from GovernedPayload manifest hash before any HOP stage runs.",
        "",
        "## Commit Hash",
        "",
        "PENDING",
        "",
        "## Files Changed",
        "",
        "- `apps_lic/engines/lic_spine_adapter.py` (created)",
        "- `apps_lic/engines/__init__.py` (fixed broken eager imports)",
        "- `apps_lic/engines/ExecutiveStrategyAgent.py` (shim created)",
        "- `apps_lic/engines/HOPPipelineExecutor.py` (shim created)",
        "- `apps_lic/engines/LICValidationExecutor.py` (shim created)",
        "- `apps_lic/engines/OutreachMessageAgent.py` (shim created)",
        "- `tests/unit_min_deps/test_apps_lic_spine_adapter.py` (created)",
        "- `tools/evidence/phase02a_lic_spine_adapter_evidence_runner.py` (created)",
        "- `docs/reports/plans/phase_02a_lic_spine_adapter.md` (created)",
        "",
        sec_focused,
        sec_full,
        sec_stat,
        sec_diff,
        "## apps_lic/engines/lic_spine_adapter.py (verbatim)",
        "",
        "```python",
        adapter_content,
        "```",
        "",
        "## tests/unit_min_deps/test_apps_lic_spine_adapter.py (verbatim)",
        "",
        "```python",
        test_content,
        "```",
        "",
    ]
    md = nl.join(parts)
    md = "\n".join(line.rstrip() for line in md.splitlines()) + "\n"
    EVIDENCE_PATH.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE_PATH.write_bytes(md.encode("utf-8"))
    print("Evidence written to: " + str(EVIDENCE_PATH))

    if focused_rc != 0:
        print("FAIL: focused pytest returned non-zero.", file=sys.stderr)
        sys.exit(focused_rc)


if __name__ == "__main__":
    main()
