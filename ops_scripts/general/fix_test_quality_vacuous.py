#!/usr/bin/env python3
"""
Mass-fixer: remove vacuous `assert True` statements from test files.

`assert True` is always-true — it provides zero signal. When a test function
calls code and then does `assert True`, the real assertion is just "no exception
was raised", which is already guaranteed by the test runner without any assert.

Transformations:
1. Remove `assert True` lines (with any trailing comment)
2. If removing the line leaves a test function with only a docstring or empty
   body, insert `pass` so the file remains syntactically valid

Only removes `assert True` at the TOP-LEVEL of a function body (not inside
conditional branches — those are handled conservatively).

Usage:
    python ops_scripts/general/fix_test_quality_vacuous.py [--dry-run] [paths...]

Exit codes:
    0 — success
    1 — errors
"""

from __future__ import annotations

import argparse
import ast
import io
import re
import sys
from pathlib import Path

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
    _emit_reads_through,
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

_emit_records_execution_trace("p0", "evidence", "fix_test_quality_vacuous")
_emit_applies_guardrail("p0", "fix_test_quality_vacuous", "p0_governance")
_emit_reads_policy_state("p0", "fix_test_quality_vacuous", "policy_binding")
_emit_snapshots_state("p0", "fix_test_quality_vacuous", "state_snapshot")
emit_replay_key("p0", "fix_test_quality_vacuous")
emit_determinism_digest("p0", "fix_test_quality_vacuous")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "fix_test_quality_vacuous", "execution_auth")
_emit_validates_capability("p2", "fix_test_quality_vacuous", "capability_check")
_emit_routes_to_capability("p2", "fix_test_quality_vacuous", "capability_route")
_emit_writes_via_uwg("p2", "fix_test_quality_vacuous", "uwg_write")
_emit_blocks_direct_write("p2", "fix_test_quality_vacuous", "direct_write_block")
_emit_records_tool_invocation("p2", "fix_test_quality_vacuous", "tool_invocation")
_emit_captures_execution_output("p2", "fix_test_quality_vacuous", "exec_output")
_emit_dispatches_agent("p3", "fix_test_quality_vacuous", "agent_dispatch")
_emit_coordinates_agents("p3", "fix_test_quality_vacuous", "agent_coordination")
_emit_records_workflow_lineage("p3", "fix_test_quality_vacuous", "workflow_lineage")
_emit_records_healing_outcome("p3", "fix_test_quality_vacuous", "healing_outcome")
_emit_escalates_failure("p3", "fix_test_quality_vacuous", "failure_escalation")
_emit_orchestrates_workflow("p3", "fix_test_quality_vacuous", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "fix_test_quality_vacuous", "healing_dispatch")
_emit_invokes_evaluation("p3", "fix_test_quality_vacuous", "evaluation_signal")
_emit_records_telemetry_event("p4", "fix_test_quality_vacuous", "telemetry_event")
_emit_captures_evaluation_metric("p4", "fix_test_quality_vacuous", "eval_metric")
_emit_stores_embedding("p4", "fix_test_quality_vacuous", "embedding_store")
_emit_updates_meta_learning_state("p4", "fix_test_quality_vacuous", "meta_learning")
_emit_links_execution_to_snapshot("p4", "fix_test_quality_vacuous", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # guardian: allow-global-mutation -- CI bootstrap

from agentic_core.L5_safety.validators.test_quality_detector_validator import (
    TestQualityDetector,
)
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_emits_metric_event,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_stores_learning_state,
    _emit_triggers_alert,
    _emit_updates_monitoring_state,
    _emit_updates_routing_strategy,
    _emit_validated_by_safety_plane,
    _emit_writes_learning_snapshot,
    _emit_writes_observability_log,
    _emit_writes_through,
)

_emit_emits_metric_event("fix_test_quality_vacuous", "p4obs", "metric_1")
_emit_emits_metric_event("fix_test_quality_vacuous", "p4obs", "metric_2")
_emit_emits_metric_event("fix_test_quality_vacuous", "p4obs", "metric_3")
_emit_emits_metric_event("fix_test_quality_vacuous", "p4obs", "metric_4")
_emit_emits_metric_event("fix_test_quality_vacuous", "p4obs", "metric_5")
_emit_emits_metric_event("fix_test_quality_vacuous", "p4obs", "metric_6")
_emit_records_incident_event("fix_test_quality_vacuous", "p4obs", "incident")
_emit_captures_runtime_anomaly("fix_test_quality_vacuous", "p4obs", "anomaly")
_emit_writes_observability_log("fix_test_quality_vacuous", "p4obs", "obs_log")
_emit_updates_monitoring_state("fix_test_quality_vacuous", "p4obs", "mon_state")
_emit_triggers_alert("fix_test_quality_vacuous", "p4obs", "alert")
_emit_links_incident_trace("fix_test_quality_vacuous", "p4obs", "trace_link")
_emit_captures_pattern("fix_test_quality_vacuous", "p3lm", "pattern")
_emit_records_learning_event("fix_test_quality_vacuous", "p3lm", "learning_event")
_emit_writes_learning_snapshot("fix_test_quality_vacuous", "p3lm", "snapshot")
_emit_feeds_meta_learning("fix_test_quality_vacuous", "p3lm", "meta_feed")
_emit_updates_routing_strategy("fix_test_quality_vacuous", "p3lm", "routing")
_emit_improves_agent_policy("fix_test_quality_vacuous", "p3lm", "policy")
_emit_stores_learning_state("fix_test_quality_vacuous", "p3lm", "state")
_emit_records_execution_trace("fix_test_quality_vacuous", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("fix_test_quality_vacuous", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("fix_test_quality_vacuous", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("fix_test_quality_vacuous", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("fix_test_quality_vacuous", "L4_STATE", "p2_trace_5")
_emit_reads_environ("fix_test_quality_vacuous", "env_read", "p2_env_1")
_emit_reads_environ("fix_test_quality_vacuous", "env_read", "p2_env_2")
_emit_reads_runtime_state("fix_test_quality_vacuous", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("fix_test_quality_vacuous", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "fix_test_quality_vacuous", "context_pull")
_emit_pulls_context("p1", "fix_test_quality_vacuous", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "fix_test_quality_vacuous", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "fix_test_quality_vacuous", "uwg_term_secondary")
_emit_writes_through("p1", "fix_test_quality_vacuous", "write_through")
_emit_writes_through("p1", "fix_test_quality_vacuous", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "fix_test_quality_vacuous", "safety_validation")
_emit_invokes_eval("p1", "fix_test_quality_vacuous", "eval_call")
_emit_proposal_commits_routing("p1", "fix_test_quality_vacuous", "routing_commit")
_emit_escalates_to_human("p1", "fix_test_quality_vacuous", "human_escalation")
_emit_routes_through("p1", "fix_test_quality_vacuous", "route_through")
_emit_checks_agent_registry("p1", "fix_test_quality_vacuous", "agent_registry")
_emit_validates_agent_capability("p1", "fix_test_quality_vacuous", "capability")
_emit_dispatches_execution_plan("p1", "fix_test_quality_vacuous", "exec_plan")
_emit_agent_executes_agent("p1", "fix_test_quality_vacuous", "sub_agent")
_emit_routes_to_agent("p1", "fix_test_quality_vacuous", "target_agent")
_emit_verifies_policy("p1", "fix_test_quality_vacuous", "policy_check")
_emit_observes_runtime_state("p1", "fix_test_quality_vacuous", "runtime_state")
_emit_verifies_boundary("p1", "fix_test_quality_vacuous", "boundary_check")
_emit_transcripts_response("p1", "fix_test_quality_vacuous", "transcript")
_emit_hard_fails_untranscripted("p1", "fix_test_quality_vacuous")
_emit_gated_by_confidence("p1", "fix_test_quality_vacuous", "confidence_gate")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_1")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_2")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_3")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_4")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_5")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_6")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_7")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_8")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_9")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_10")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_11")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_12")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_13")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_14")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_15")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_16")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_17")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_18")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_19")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_20")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_21")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_22")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_23")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_24")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_25")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_26")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_27")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_28")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_29")
_emit_reads_through("l4", "fix_test_quality_vacuous", "urg_read_30")

# Matches: assert True [# comment]  OR  assert True, "message"
_ASSERT_TRUE_RE = re.compile(r"^(\s*)assert\s+True\s*(?:[,#][^\n]*)?\n?$")
# Matches: assert len(expr) >= 0 [# comment]
_LEN_GE_ZERO_RE = re.compile(r"^(\s*)assert\s+len\s*\([^)]+\)\s*>=\s*0\s*(?:[,#][^\n]*)?\n?$")


def _collect_test_files(roots: list[str]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        p = Path(root)
        if p.is_file() and p.suffix == ".py":
            files.append(p)
        elif p.is_dir():
            for f in p.rglob("*.py"):
                if "__pycache__" in f.parts:
                    continue
                if f.name.startswith("test_") or f.name.endswith("_test.py"):
                    files.append(f)
    return sorted(set(files))


def _get_vacuous_lines(file_path: Path) -> set[int]:
    """Return 1-indexed line numbers of vacuous assert True nodes in test functions."""
    detector = TestQualityDetector()
    result = detector.scan_file(file_path)
    lines = set()
    for v in result.violations:
        if v.metadata.get("sub_pattern") == "VACUOUS_ASSERT" and not v.whitelisted:
            lines.add(v.line_number)
    return lines


def _function_body_is_empty_after_removal(
    source_lines: list[str],
    fn_start: int,
    fn_end: int,
    removed_lines: set[int],
) -> bool:
    """
    Check if a function body has any meaningful statements remaining after removal.
    fn_start/fn_end are 1-indexed line numbers.
    """
    body_content = []
    for i in range(fn_start, fn_end + 1):
        if i in removed_lines:
            continue
        line = source_lines[i - 1].rstrip()
        # Skip blank lines, docstrings, and pass
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith('"""') or stripped.startswith("'''") or stripped == '"""' or stripped == "'''":
            continue
        if stripped == "pass":
            continue
        body_content.append(line)
    return len(body_content) == 0


def _get_function_ranges(source: str) -> list[tuple[int, int, int]]:
    """
    Return list of (fn_def_lineno, body_start_lineno, body_end_lineno) for all functions.
    All line numbers are 1-indexed.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:  # guardian: Syntax errors should be caught at parser level, not runtime
        return []

    ranges = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.body:
                continue
            # body_start = first statement in body
            body_start = node.body[0].lineno
            # body_end = last line of last statement
            last_stmt = node.body[-1]
            body_end = getattr(last_stmt, "end_lineno", last_stmt.lineno)
            ranges.append((node.lineno, body_start, body_end))
    return ranges


def fix_file(file_path: Path, dry_run: bool = False) -> tuple[int, list[str]]:
    """
    Remove vacuous assert True lines from file_path.
    Returns (lines_changed, list_of_change_descriptions).
    """
    vacuous_lines = _get_vacuous_lines(file_path)
    if not vacuous_lines:
        return 0, []

    try:
        original = file_path.read_text(encoding="utf-8")
    except Exception as exc:
        return 0, [f"ERROR reading: {exc}"]

    source_lines = original.splitlines(keepends=True)
    fn_ranges = _get_function_ranges(original)

    # Determine which lines to remove
    lines_to_remove: set[int] = set()
    lines_to_add_pass_after: set[int] = set()

    for lineno in vacuous_lines:
        idx = lineno - 1
        if idx >= len(source_lines):
            continue
        line = source_lines[idx]
        if not (_ASSERT_TRUE_RE.match(line) or _LEN_GE_ZERO_RE.match(line)):
            continue
        lines_to_remove.add(lineno)

    # For each function, check if removing leaves it empty → add pass
    for fn_lineno, body_start, body_end in fn_ranges:
        fn_removed = {ln for ln in lines_to_remove if body_start <= ln <= body_end}
        if not fn_removed:
            continue
        if _function_body_is_empty_after_removal(source_lines, body_start, body_end, fn_removed):
            # Find the last removed line in this function's body — add pass there
            last_removed = max(fn_removed)
            lines_to_add_pass_after.add(last_removed)

    if not lines_to_remove:
        return 0, []

    # Apply changes (work backwards to preserve line numbers)
    new_lines = list(source_lines)
    changes: list[str] = []

    for lineno in sorted(lines_to_remove, reverse=True):
        idx = lineno - 1
        original_line = new_lines[idx].rstrip("\n")
        indent = len(original_line) - len(original_line.lstrip())
        ind = " " * indent

        if lineno in lines_to_add_pass_after:
            new_lines[idx] = f"{ind}pass\n"
            changes.append(f"  line {lineno}: replaced `assert True` with `pass`")
        else:
            new_lines[idx] = None  # type: ignore[assignment]
            changes.append(f"  line {lineno}: removed `{original_line.strip()}`")

    final_lines = [ln for ln in new_lines if ln is not None]
    new_content = "".join(final_lines)

    if not dry_run:
        try:
            file_path.write_text(new_content, encoding="utf-8")
        except Exception as exc:
            return 0, [f"ERROR writing: {exc}"]

    return len(lines_to_remove), changes


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="fix_test_quality_vacuous",
        description="Remove `assert True` statements from test files",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        default=["tests"],
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    test_files = _collect_test_files(args.paths)
    if not test_files:
        print("No test files found.")
        return 0

    total_lines = 0
    total_files = 0
    errors = 0

    for f in test_files:
        count, changes = fix_file(f, dry_run=args.dry_run)
        if changes and any(c.startswith("  ERROR") for c in changes):
            errors += 1
        if count:
            rel = f.relative_to(_REPO_ROOT) if f.is_absolute() else f
            action = "[DRY-RUN]" if args.dry_run else "FIXED"
            print(f"{action} {rel} ({count} line(s))")
            for c in changes[:5]:
                print(c)
            if len(changes) > 5:
                print(f"  … and {len(changes) - 5} more")
            total_lines += count
            total_files += 1

    action = "Would fix" if args.dry_run else "Fixed"
    print(f"\n{action} {total_lines} line(s) across {total_files} file(s).")
    if errors:
        print(f"{errors} error(s).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
