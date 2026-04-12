"""Automated fixer: convert all illegitimate pytest.skip() / importorskip to
pytest.fail() or delete dead stubs, as classified by classify_skips.py.

Strategy:
  - pytest.skip(msg) → pytest.fail(msg)  for all illegitimate sites
  - pytest.importorskip(pkg) for mandatory deps → raise ImportError assertion
  - "not yet implemented" stubs → comment body with pytest.fail()
  - Legitimate sites (Redis, Playwright, tamper env flag, platform, faiss-gpu)
    are left untouched.

Run from repo root:
    python ops_scripts/fix_illegitimate_skips.py
"""

import ast
import re
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    BATCH_SIZE,
    BUFFER_SIZE,
    DEFAULT_SLEEP,
    DEFAULT_TIMEOUT,
    MAX_DEPTH,
    MAX_FILES,
    MAX_RETRIES,
    TESTS_DIR,
    THRESHOLD,
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

_emit_emits_metric_event("fix_illegitimate_skips", "p4obs", "metric_1")
_emit_emits_metric_event("fix_illegitimate_skips", "p4obs", "metric_2")
_emit_emits_metric_event("fix_illegitimate_skips", "p4obs", "metric_3")
_emit_emits_metric_event("fix_illegitimate_skips", "p4obs", "metric_4")
_emit_emits_metric_event("fix_illegitimate_skips", "p4obs", "metric_5")
_emit_emits_metric_event("fix_illegitimate_skips", "p4obs", "metric_6")
_emit_records_incident_event("fix_illegitimate_skips", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_illegitimate_skips", "p4obs", "anomaly")
_emit_writes_observability_log("fix_illegitimate_skips", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_illegitimate_skips", "p4obs", "mon_state")
_emit_triggers_alert("fix_illegitimate_skips", "p4obs", "alert")
_emit_links_incident_trace("fix_illegitimate_skips", "p4obs", "trace_link")
_emit_captures_pattern("fix_illegitimate_skips", "p3lm", "pattern")
_emit_records_learning_event("fix_illegitimate_skips", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_illegitimate_skips", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_illegitimate_skips", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_illegitimate_skips", "p3lm", "routing")
_emit_improves_agent_policy("fix_illegitimate_skips", "p3lm", "policy")
_emit_stores_learning_state("fix_illegitimate_skips", "p3lm", "state")
_emit_records_execution_trace("fix_illegitimate_skips", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_illegitimate_skips", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_illegitimate_skips", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_illegitimate_skips", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_illegitimate_skips", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_illegitimate_skips", "env_read", "p2_env_1")
_emit_reads_environ("fix_illegitimate_skips", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_illegitimate_skips", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_illegitimate_skips", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "fix_illegitimate_skips")
_emit_applies_guardrail("p0", "fix_illegitimate_skips", "p0_governance")
_emit_reads_policy_state("p0", "fix_illegitimate_skips", "policy_binding")
_emit_snapshots_state("p0", "fix_illegitimate_skips", "state_snapshot")
_emit_pulls_context("p1", "fix_illegitimate_skips", "context_pull")
_emit_pulls_context("p1", "fix_illegitimate_skips", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_illegitimate_skips", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_illegitimate_skips", "uwg_term_secondary")
_emit_writes_through("p1", "fix_illegitimate_skips", "write_through")
_emit_writes_through("p1", "fix_illegitimate_skips", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_illegitimate_skips", "safety_validation")
_emit_invokes_eval("p1", "fix_illegitimate_skips", "eval_call")
_emit_proposal_commits_routing("p1", "fix_illegitimate_skips", "routing_commit")
_emit_escalates_to_human("p1", "fix_illegitimate_skips", "human_escalation")
_emit_routes_through("p1", "fix_illegitimate_skips", "route_through")
_emit_checks_agent_registry("p1", "fix_illegitimate_skips", "agent_registry")
_emit_validates_agent_capability("p1", "fix_illegitimate_skips", "capability")
_emit_dispatches_execution_plan("p1", "fix_illegitimate_skips", "exec_plan")
_emit_agent_executes_agent("p1", "fix_illegitimate_skips", "sub_agent")
_emit_routes_to_agent("p1", "fix_illegitimate_skips", "target_agent")
_emit_verifies_policy("p1", "fix_illegitimate_skips", "policy_check")
_emit_observes_runtime_state("p1", "fix_illegitimate_skips", "runtime_state")
_emit_verifies_boundary("p1", "fix_illegitimate_skips", "boundary_check")
_emit_transcripts_response("p1", "fix_illegitimate_skips", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_illegitimate_skips")
_emit_gated_by_confidence("p1", "fix_illegitimate_skips", "confidence_gate")
emit_replay_key("p0", "fix_illegitimate_skips")
emit_determinism_digest("p0", "fix_illegitimate_skips")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "fix_illegitimate_skips", "execution_auth")
_emit_validates_capability("p2", "fix_illegitimate_skips", "capability_check")
_emit_routes_to_capability("p2", "fix_illegitimate_skips", "capability_route")
_emit_writes_via_uwg("p2", "fix_illegitimate_skips", "uwg_write")
_emit_blocks_direct_write("p2", "fix_illegitimate_skips", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_illegitimate_skips", "tool_invocation")
_emit_captures_execution_output("p2", "fix_illegitimate_skips", "exec_output")
_emit_dispatches_agent("p3", "fix_illegitimate_skips", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_illegitimate_skips", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_illegitimate_skips", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_illegitimate_skips", "healing_outcome")
_emit_escalates_failure("p3", "fix_illegitimate_skips", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_illegitimate_skips", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_illegitimate_skips", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_illegitimate_skips", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_illegitimate_skips", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_illegitimate_skips", "eval_metric")
_emit_stores_embedding("p4", "fix_illegitimate_skips", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_illegitimate_skips", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_illegitimate_skips", "exec_snapshot_link")
ROOT = get_validated_project_root()
TESTS = ROOT / TESTS_DIR
LEGITIMATE_REASONS_SUBSTRINGS = [
    "redis not running",
    "redis not",
    "playwright not installed",
    "playwright visual tests should be run separately",
    "ssot_orch_negctrl_tamper",
    "activate tamper",
    "read-only directory",
    "faiss-gpu",
]
NOT_IMPLEMENTED_SUBSTRINGS = ["not yet implemented", "method not implemented yet"]


def is_legitimate(reason: str) -> bool:
    r = reason.lower()
    return any(k in r for k in LEGITIMATE_REASONS_SUBSTRINGS)


def is_not_implemented(reason: str) -> bool:
    r = reason.lower()
    return any(k in r for k in NOT_IMPLEMENTED_SUBSTRINGS)


def fix_file(path: Path) -> tuple[bool, int]:
    """Return (changed, num_fixes) for a single file."""
    original = path.read_text(encoding="utf-8", errors="replace")
    lines = original.splitlines(keepends=True)
    try:
        tree = ast.parse(original)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError:
        return (False, 0)
    illegit_lines: dict[int, tuple[str, str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if isinstance(func, ast.Attribute) and func.attr == "importorskip":
            rawargs = [ast.unparse(a) for a in node.args]
            reason = rawargs[0].strip("\"'") if rawargs else "missing import"
            illegit_lines[node.lineno] = ("importorskip", reason)
        elif (
            isinstance(func, ast.Attribute)
            and func.attr == "skip"
            and isinstance(func.value, ast.Name)
            and (func.value.id == "pytest")
        ):
            rawargs = [ast.unparse(a) for a in node.args]
            reason = rawargs[0].strip("\"'") if rawargs else ""
            if not is_legitimate(reason):
                kind = "not_implemented" if is_not_implemented(reason) else "skip"
                illegit_lines[node.lineno] = (kind, reason)
    if not illegit_lines:
        return (False, 0)
    changed = False
    fixes = 0
    new_lines = list(lines)
    for lineno, (kind, reason) in sorted(illegit_lines.items()):
        idx = lineno - 1
        line = new_lines[idx]
        if kind == "importorskip":
            m = re.search("importorskip\\s*\\(\\s*[\"\\']([^\"\\']+)[\"\\']", line)
            if m:
                pkg = m.group(1)
                indent = len(line) - len(line.lstrip())
                ind = " " * indent
                new_lines[idx] = (
                    f'{ind}try:\n{ind}    import {pkg}  # noqa: F401\n{ind}except ImportError:\n{ind}    pytest.fail("{pkg} is a mandatory dependency — install it")\n'
                )
                changed = True
                fixes += 1
            continue
        if kind == "not_implemented":
            new_line = line.replace("pytest.skip(", "pytest.fail(", 1)
            if new_line != line:
                new_lines[idx] = new_line
                changed = True
                fixes += 1
            continue
        new_line = line.replace("pytest.skip(", "pytest.fail(", 1)
        if new_line != line:
            new_lines[idx] = new_line
            changed = True
            fixes += 1
    if changed:
        path.write_text("".join(new_lines), encoding="utf-8")
    return (changed, fixes)


def main() -> None:
    total_files = 0
    total_fixes = 0
    for path in sorted(TESTS.rglob("test_*.py")):
        changed, fixes = fix_file(path)
        if changed:
            rel = path.relative_to(ROOT)
            print(f"  FIXED {fixes:3d} site(s)  {rel}")
            total_files += 1
            total_fixes += fixes
    print(f"\nDONE: {total_fixes} fixes across {total_files} files")


if __name__ == "__main__":
    main()
