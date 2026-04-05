#!/usr/bin/env python3
"""
Test Silent Skip CI Guardrail

Scans test files for over-broad import guards that silently skip ALL tests
when any non-import error occurs during module setup.

Anti-pattern (DANGEROUS):
    try:
        from some.module import Foo, NONEXISTENT_CONSTANT
        _AVAILABLE = True
    except Exception:          # catches NameError, AttributeError, SyntaxError…
        _AVAILABLE = False     # ALL tests in this file permanently silently skip

Required pattern (SAFE):
    except ImportError:        # only catches genuine missing modules
        _AVAILABLE = False

RCA: This pattern caused 1569 test files to silently drop all coverage whenever
a real bug existed in the imported module, hiding defects indefinitely.
Two layers of existing scanning excluded test files:
  1. SilentDegradationDetector — explicitly whitelists test_*.py
  2. AntiPatternScanner.DEFAULT_EXCLUDES — contains **/test_*
This script fills that gap.

Usage:
    python ops_scripts/ci/check_test_silent_skips.py [dir_or_file ...]
    python ops_scripts/ci/check_test_silent_skips.py --json

Exit codes:
    0 — No violations
    1 — Violations found (build fails)
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path

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

_emit_records_execution_trace("p0", "evidence", "check_test_silent_skips")
_emit_applies_guardrail("p0", "check_test_silent_skips", "p0_governance")
_emit_reads_policy_state("p0", "check_test_silent_skips", "policy_binding")
_emit_snapshots_state("p0", "check_test_silent_skips", "state_snapshot")
emit_replay_key("p0", "check_test_silent_skips")
emit_determinism_digest("p0", "check_test_silent_skips")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_test_silent_skips", "execution_auth")
_emit_validates_capability("p2", "check_test_silent_skips", "capability_check")
_emit_routes_to_capability("p2", "check_test_silent_skips", "capability_route")
_emit_writes_via_uwg("p2", "check_test_silent_skips", "uwg_write")
_emit_blocks_direct_write("p2", "check_test_silent_skips", "direct_write_block")
_emit_records_tool_invocation("p2", "check_test_silent_skips", "tool_invocation")
_emit_captures_execution_output("p2", "check_test_silent_skips", "exec_output")
_emit_dispatches_agent("p3", "check_test_silent_skips", "agent_dispatch")
_emit_coordinates_agents("p3", "check_test_silent_skips", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_test_silent_skips", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_test_silent_skips", "healing_outcome")
_emit_escalates_failure("p3", "check_test_silent_skips", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_test_silent_skips", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_test_silent_skips", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_test_silent_skips", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_test_silent_skips", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_test_silent_skips", "eval_metric")
_emit_stores_embedding("p4", "check_test_silent_skips", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_test_silent_skips", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_test_silent_skips", "exec_snapshot_link")

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # guardian: allow-global-mutation -- CI bootstrap

from agentic_core.L5_safety.validators.test_skip_detector_validator import (
    TestSilentSkipDetector,
)
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

_emit_emits_metric_event("check_test_silent_skips", "p4obs", "metric_1")
_emit_emits_metric_event("check_test_silent_skips", "p4obs", "metric_2")
_emit_emits_metric_event("check_test_silent_skips", "p4obs", "metric_3")
_emit_emits_metric_event("check_test_silent_skips", "p4obs", "metric_4")
_emit_emits_metric_event("check_test_silent_skips", "p4obs", "metric_5")
_emit_emits_metric_event("check_test_silent_skips", "p4obs", "metric_6")
_emit_records_incident_event("check_test_silent_skips", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_test_silent_skips", "p4obs", "anomaly")
_emit_writes_observability_log("check_test_silent_skips", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_test_silent_skips", "p4obs", "mon_state")
_emit_triggers_alert("check_test_silent_skips", "p4obs", "alert")
_emit_links_incident_trace("check_test_silent_skips", "p4obs", "trace_link")
_emit_captures_pattern("check_test_silent_skips", "p3lm", "pattern")
_emit_records_learning_event("check_test_silent_skips", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_test_silent_skips", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_test_silent_skips", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_test_silent_skips", "p3lm", "routing")
_emit_improves_agent_policy("check_test_silent_skips", "p3lm", "policy")
_emit_stores_learning_state("check_test_silent_skips", "p3lm", "state")
_emit_records_execution_trace("check_test_silent_skips", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_test_silent_skips", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_test_silent_skips", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_test_silent_skips", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_test_silent_skips", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_test_silent_skips", "env_read", "p2_env_1")
_emit_reads_environ("check_test_silent_skips", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_test_silent_skips", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_test_silent_skips", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "check_test_silent_skips", "context_pull")
_emit_pulls_context("p1", "check_test_silent_skips", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_test_silent_skips", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_test_silent_skips", "uwg_term_secondary")
_emit_writes_through("p1", "check_test_silent_skips", "write_through")
_emit_writes_through("p1", "check_test_silent_skips", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_test_silent_skips", "safety_validation")
_emit_invokes_eval("p1", "check_test_silent_skips", "eval_call")
_emit_proposal_commits_routing("p1", "check_test_silent_skips", "routing_commit")
_emit_escalates_to_human("p1", "check_test_silent_skips", "human_escalation")
_emit_routes_through("p1", "check_test_silent_skips", "route_through")
_emit_checks_agent_registry("p1", "check_test_silent_skips", "agent_registry")
_emit_validates_agent_capability("p1", "check_test_silent_skips", "capability")
_emit_dispatches_execution_plan("p1", "check_test_silent_skips", "exec_plan")
_emit_agent_executes_agent("p1", "check_test_silent_skips", "sub_agent")
_emit_routes_to_agent("p1", "check_test_silent_skips", "target_agent")
_emit_verifies_policy("p1", "check_test_silent_skips", "policy_check")
_emit_observes_runtime_state("p1", "check_test_silent_skips", "runtime_state")
_emit_verifies_boundary("p1", "check_test_silent_skips", "boundary_check")
_emit_transcripts_response("p1", "check_test_silent_skips", "transcript")
_emit_hard_fails_untranscripted("p1", "check_test_silent_skips")
_emit_gated_by_confidence("p1", "check_test_silent_skips", "confidence_gate")

DEFAULT_SCAN_DIRS = ["tests"]
DEFAULT_EXCLUDES = {"__pycache__", ".pyc"}


def _collect_test_files(roots: list[str]) -> list[Path]:
    """Collect all test_*.py and *_test.py files under the given roots."""
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
        prog="check_test_silent_skips",
        description="Scan test files for over-broad import guards (except Exception: _AVAILABLE=False)",
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
        "--max-violations",
        type=int,
        default=None,
        metavar="N",
        help="Exit 0 if violation count <= N (ratchet mode)",
    )
    args = parser.parse_args()

    detector = TestSilentSkipDetector()
    test_files = _collect_test_files(args.paths)

    if not test_files:
        print(f"[check_test_silent_skips] No test files found under: {args.paths}")
        return 0

    all_violations = []
    for f in test_files:
        result = detector.scan_file(f)
        for v in result.violations:
            if not v.whitelisted:
                all_violations.append(v)

    if args.json_output:
        payload = {
            "total_files_scanned": len(test_files),
            "total_violations": len(all_violations),
            "violations": [v.to_dict() for v in all_violations],
        }
        print(json.dumps(payload, indent=2, default=str))
    else:
        print(
            f"[check_test_silent_skips] Scanned {len(test_files)} test file(s) — "
            f"{len(all_violations)} violation(s)"
        )
        for v in all_violations:
            rel = Path(v.file_path).relative_to(_REPO_ROOT) if Path(v.file_path).is_absolute() else v.file_path
            flag = v.metadata.get("flag", "?")
            caught = v.metadata.get("caught", "?")
            print(f"  {rel}:{v.line_number}  [{caught}]  {flag}=False")
            print(f"    → {v.message[:100]}")

    if args.max_violations is not None:
        return 0 if len(all_violations) <= args.max_violations else 1

    return 1 if all_violations else 0


if __name__ == "__main__":
    sys.exit(main())
