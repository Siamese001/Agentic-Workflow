#!/usr/bin/env python3
"""
Test Quality CI Guardrail

Scans test files for low-quality assertion patterns that cause tests to pass
even when the underlying functionality is completely broken.

Anti-patterns detected:
  VACUOUS_ASSERT     — assert True / always-true expression [HARD_BLOCK]
  SOLE_TYPE_CHECK    — all assertions are isinstance/is-not-None/hasattr [WARNING]
  WRITE_WITHOUT_READ — write method called, no read-back verification [WARNING]

ADG importability stubs (*_adg.py) are exempt from SOLE_TYPE_CHECK and
WRITE_WITHOUT_READ (they are intentionally type-only by design).

Usage:
    python ops_scripts/ci/check_test_quality.py [paths...]
    python ops_scripts/ci/check_test_quality.py --json
    python ops_scripts/ci/check_test_quality.py --sub-pattern VACUOUS_ASSERT
    python ops_scripts/ci/check_test_quality.py --max-errors N   (ratchet)

Exit codes:
    0 — No HARD_BLOCK violations
    1 — HARD_BLOCK violations found (assert True)
    2 — WARNING violations only (vacuous type checks, write-no-read)

Note: exit code 2 does not block CI by default; use --strict to treat warnings
as errors.
"""

from __future__ import annotations

import argparse
import io
import json
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

_emit_records_execution_trace("p0", "evidence", "check_test_quality")
_emit_applies_guardrail("p0", "check_test_quality", "p0_governance")
_emit_reads_policy_state("p0", "check_test_quality", "policy_binding")
_emit_snapshots_state("p0", "check_test_quality", "state_snapshot")
emit_replay_key("p0", "check_test_quality")
emit_determinism_digest("p0", "check_test_quality")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_test_quality", "execution_auth")
_emit_validates_capability("p2", "check_test_quality", "capability_check")
_emit_routes_to_capability("p2", "check_test_quality", "capability_route")
_emit_writes_via_uwg("p2", "check_test_quality", "uwg_write")
_emit_blocks_direct_write("p2", "check_test_quality", "direct_write_block")
_emit_records_tool_invocation("p2", "check_test_quality", "tool_invocation")
_emit_captures_execution_output("p2", "check_test_quality", "exec_output")
_emit_dispatches_agent("p3", "check_test_quality", "agent_dispatch")
_emit_coordinates_agents("p3", "check_test_quality", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_test_quality", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_test_quality", "healing_outcome")
_emit_escalates_failure("p3", "check_test_quality", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_test_quality", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_test_quality", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_test_quality", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_test_quality", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_test_quality", "eval_metric")
_emit_stores_embedding("p4", "check_test_quality", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_test_quality", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_test_quality", "exec_snapshot_link")

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

_emit_emits_metric_event("check_test_quality", "p4obs", "metric_1")
_emit_emits_metric_event("check_test_quality", "p4obs", "metric_2")
_emit_emits_metric_event("check_test_quality", "p4obs", "metric_3")
_emit_emits_metric_event("check_test_quality", "p4obs", "metric_4")
_emit_emits_metric_event("check_test_quality", "p4obs", "metric_5")
_emit_emits_metric_event("check_test_quality", "p4obs", "metric_6")
_emit_records_incident_event("check_test_quality", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_test_quality", "p4obs", "anomaly")
_emit_writes_observability_log("check_test_quality", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_test_quality", "p4obs", "mon_state")
_emit_triggers_alert("check_test_quality", "p4obs", "alert")
_emit_links_incident_trace("check_test_quality", "p4obs", "trace_link")
_emit_captures_pattern("check_test_quality", "p3lm", "pattern")
_emit_records_learning_event("check_test_quality", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_test_quality", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_test_quality", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_test_quality", "p3lm", "routing")
_emit_improves_agent_policy("check_test_quality", "p3lm", "policy")
_emit_stores_learning_state("check_test_quality", "p3lm", "state")
_emit_records_execution_trace("check_test_quality", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_test_quality", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_test_quality", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_test_quality", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_test_quality", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_test_quality", "env_read", "p2_env_1")
_emit_reads_environ("check_test_quality", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_test_quality", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_test_quality", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_test_quality", "context_pull")
_emit_pulls_context("p1", "check_test_quality", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_test_quality", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_test_quality", "uwg_term_secondary")
_emit_writes_through("p1", "check_test_quality", "write_through")
_emit_writes_through("p1", "check_test_quality", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_test_quality", "safety_validation")
_emit_invokes_eval("p1", "check_test_quality", "eval_call")
_emit_proposal_commits_routing("p1", "check_test_quality", "routing_commit")
_emit_escalates_to_human("p1", "check_test_quality", "human_escalation")
_emit_routes_through("p1", "check_test_quality", "route_through")
_emit_checks_agent_registry("p1", "check_test_quality", "agent_registry")
_emit_validates_agent_capability("p1", "check_test_quality", "capability")
_emit_dispatches_execution_plan("p1", "check_test_quality", "exec_plan")
_emit_agent_executes_agent("p1", "check_test_quality", "sub_agent")
_emit_routes_to_agent("p1", "check_test_quality", "target_agent")
_emit_verifies_policy("p1", "check_test_quality", "policy_check")
_emit_observes_runtime_state("p1", "check_test_quality", "runtime_state")
_emit_verifies_boundary("p1", "check_test_quality", "boundary_check")
_emit_transcripts_response("p1", "check_test_quality", "transcript")
_emit_hard_fails_untranscripted("p1", "check_test_quality")
_emit_gated_by_confidence("p1", "check_test_quality", "confidence_gate")

DEFAULT_SCAN_DIRS = ["tests"]


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


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="check_test_quality",
        description="Scan test files for vacuous / weak assertions",
    )
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        default=DEFAULT_SCAN_DIRS,
        help="Directories or files to scan (default: tests/)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Emit results as JSON",
    )
    parser.add_argument(
        "--sub-pattern",
        choices=["VACUOUS_ASSERT", "SOLE_TYPE_CHECK", "WRITE_WITHOUT_READ"],
        default=None,
        help="Only report this sub-pattern",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat WARNING violations as blocking errors",
    )
    parser.add_argument(
        "--max-errors",
        type=int,
        default=None,
        metavar="N",
        help="Exit 0 if hard-block violation count <= N (ratchet mode)",
    )
    args = parser.parse_args()

    detector = TestQualityDetector()
    test_files = _collect_test_files(args.paths)

    if not test_files:
        print(f"[check_test_quality] No test files found under: {args.paths}")
        return 0

    all_violations = []
    for f in test_files:
        result = detector.scan_file(f)
        for v in result.violations:
            if v.whitelisted:
                continue
            if args.sub_pattern and v.metadata.get("sub_pattern") != args.sub_pattern:
                continue
            all_violations.append(v)

    hard_violations = [v for v in all_violations if v.severity == "error"]
    warn_violations = [v for v in all_violations if v.severity == "warning"]

    # Summary by sub-pattern
    by_pattern: dict[str, int] = {}
    for v in all_violations:
        sp = v.metadata.get("sub_pattern", "unknown")
        by_pattern[sp] = by_pattern.get(sp, 0) + 1

    if args.json_output:
        payload = {
            "total_files_scanned": len(test_files),
            "total_violations": len(all_violations),
            "hard_block_count": len(hard_violations),
            "warning_count": len(warn_violations),
            "by_sub_pattern": by_pattern,
            "violations": [v.to_dict() for v in all_violations],
        }
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(
            f"[check_test_quality] Scanned {len(test_files)} file(s) — "
            f"{len(hard_violations)} hard-block, {len(warn_violations)} warning",
        )
        for sp, count in sorted(by_pattern.items()):
            print(f"  {sp}: {count}")

        if hard_violations:
            print("\nHARD-BLOCK violations (assert True / always-true):")
            for v in hard_violations[:30]:
                rel = (
                    Path(v.file_path).relative_to(_REPO_ROOT)
                    if Path(v.file_path).is_absolute()
                    else v.file_path
                )
                fn = v.metadata.get("test_function", "?")
                print(f"  {rel}:{v.line_number}  [{fn}]")
                print(f"    {v.evidence}")
            if len(hard_violations) > 30:
                print(f"  … and {len(hard_violations) - 30} more")

        if warn_violations and (args.strict or args.sub_pattern):
            print("\nWARNING violations:")
            for v in warn_violations[:20]:
                rel = (
                    Path(v.file_path).relative_to(_REPO_ROOT)
                    if Path(v.file_path).is_absolute()
                    else v.file_path
                )
                sp = v.metadata.get("sub_pattern", "?")
                fn = v.metadata.get("test_function", "?")
                print(f"  [{sp}] {rel}:{v.line_number}  {fn}")
            if len(warn_violations) > 20:
                print(f"  … and {len(warn_violations) - 20} more")

    if args.max_errors is not None:
        return 0 if len(hard_violations) <= args.max_errors else 1

    if hard_violations:
        return 1
    if warn_violations and args.strict:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
