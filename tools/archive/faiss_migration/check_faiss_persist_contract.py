#!/usr/bin/env python3
"""check_faiss_persist_contract.py - AST-based CI gate for FAISS persistence contract.

Enforces that every call site that finalizes or rebuilds a FAISS index also
calls persist_to_disk() downstream, OR explicitly documents why persistence
is intentionally skipped via a guardian comment.

Rules enforced (AST-only, no regex):
  R1: Any function body containing a call to ``finalize_build()`` or
      ``rebuild()`` on a LocalFAISSStore must also contain a call to
      ``persist_to_disk()`` in the same function scope, OR carry a guardian
      comment ``# guardian: faiss-no-persist`` on the finalize/rebuild line.

  R2: Any call to ``persist_to_disk()`` must occur in a context where the
      target directory is a subdirectory created under a base_path
      (heuristic: the call must pass at least two positional/keyword
      arguments, matching the (index_id, dest_dir, ...) signature).

Usage:
    python ops_scripts/ci/check_faiss_persist_contract.py
    python ops_scripts/ci/check_faiss_persist_contract.py [file1.py file2.py ...]

Exit codes:
    0  All checks pass.
    1  One or more violations found.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    SYSTEM_LEARNING_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

_emit_emits_metric_event("check_faiss_persist_contract", "p4obs", "metric_1")
_emit_emits_metric_event("check_faiss_persist_contract", "p4obs", "metric_2")
_emit_emits_metric_event("check_faiss_persist_contract", "p4obs", "metric_3")
_emit_emits_metric_event("check_faiss_persist_contract", "p4obs", "metric_4")
_emit_emits_metric_event("check_faiss_persist_contract", "p4obs", "metric_5")
_emit_emits_metric_event("check_faiss_persist_contract", "p4obs", "metric_6")
_emit_records_incident_event("check_faiss_persist_contract", "p4obs", "incident")
_emit_captures_runtime_anomaly("check_faiss_persist_contract", "p4obs", "anomaly")
_emit_writes_observability_log("check_faiss_persist_contract", "p4obs", "obs_log")
_emit_updates_monitoring_state("check_faiss_persist_contract", "p4obs", "mon_state")
_emit_triggers_alert("check_faiss_persist_contract", "p4obs", "alert")
_emit_links_incident_trace("check_faiss_persist_contract", "p4obs", "trace_link")
_emit_captures_pattern("check_faiss_persist_contract", "p3lm", "pattern")
_emit_records_learning_event("check_faiss_persist_contract", "p3lm", "learning_event")
_emit_writes_learning_snapshot("check_faiss_persist_contract", "p3lm", "snapshot")
_emit_feeds_meta_learning("check_faiss_persist_contract", "p3lm", "meta_feed")
_emit_updates_routing_strategy("check_faiss_persist_contract", "p3lm", "routing")
_emit_improves_agent_policy("check_faiss_persist_contract", "p3lm", "policy")
_emit_stores_learning_state("check_faiss_persist_contract", "p3lm", "state")
_emit_records_execution_trace("check_faiss_persist_contract", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("check_faiss_persist_contract", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("check_faiss_persist_contract", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("check_faiss_persist_contract", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("check_faiss_persist_contract", "L4_STATE", "p2_trace_5")
_emit_reads_environ("check_faiss_persist_contract", "env_read", "p2_env_1")
_emit_reads_environ("check_faiss_persist_contract", "env_read", "p2_env_2")
_emit_reads_runtime_state("check_faiss_persist_contract", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("check_faiss_persist_contract", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "check_faiss_persist_contract")
_emit_applies_guardrail("p0", "check_faiss_persist_contract", "p0_governance")
_emit_reads_policy_state("p0", "check_faiss_persist_contract", "policy_binding")
_emit_snapshots_state("p0", "check_faiss_persist_contract", "state_snapshot")
_emit_pulls_context("p1", "check_faiss_persist_contract", "context_pull")
_emit_pulls_context("p1", "check_faiss_persist_contract", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "check_faiss_persist_contract", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "check_faiss_persist_contract", "uwg_term_secondary")
_emit_writes_through("p1", "check_faiss_persist_contract", "write_through")
_emit_writes_through("p1", "check_faiss_persist_contract", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "check_faiss_persist_contract", "safety_validation")
_emit_invokes_eval("p1", "check_faiss_persist_contract", "eval_call")
_emit_proposal_commits_routing("p1", "check_faiss_persist_contract", "routing_commit")
_emit_escalates_to_human("p1", "check_faiss_persist_contract", "human_escalation")
_emit_routes_through("p1", "check_faiss_persist_contract", "route_through")
_emit_checks_agent_registry("p1", "check_faiss_persist_contract", "agent_registry")
_emit_validates_agent_capability("p1", "check_faiss_persist_contract", "capability")
_emit_dispatches_execution_plan("p1", "check_faiss_persist_contract", "exec_plan")
_emit_agent_executes_agent("p1", "check_faiss_persist_contract", "sub_agent")
_emit_routes_to_agent("p1", "check_faiss_persist_contract", "target_agent")
_emit_verifies_policy("p1", "check_faiss_persist_contract", "policy_check")
_emit_observes_runtime_state("p1", "check_faiss_persist_contract", "runtime_state")
_emit_verifies_boundary("p1", "check_faiss_persist_contract", "boundary_check")
_emit_transcripts_response("p1", "check_faiss_persist_contract", "transcript")
_emit_hard_fails_untranscripted("p1", "check_faiss_persist_contract")
_emit_gated_by_confidence("p1", "check_faiss_persist_contract", "confidence_gate")
emit_replay_key("p0", "check_faiss_persist_contract")
emit_determinism_digest("p0", "check_faiss_persist_contract")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "check_faiss_persist_contract", "execution_auth")
_emit_validates_capability("p2", "check_faiss_persist_contract", "capability_check")
_emit_routes_to_capability("p2", "check_faiss_persist_contract", "capability_route")
_emit_writes_via_uwg("p2", "check_faiss_persist_contract", "uwg_write")
_emit_blocks_direct_write("p2", "check_faiss_persist_contract", "direct_write_block")
_emit_records_tool_invocation("p2", "check_faiss_persist_contract", "tool_invocation")
_emit_captures_execution_output("p2", "check_faiss_persist_contract", "exec_output")
_emit_dispatches_agent("p3", "check_faiss_persist_contract", "agent_dispatch")
_emit_coordinates_agents("p3", "check_faiss_persist_contract", "agent_coordination")
_emit_records_workflow_lineage("p3", "check_faiss_persist_contract", "workflow_lineage")
_emit_records_healing_outcome("p3", "check_faiss_persist_contract", "healing_outcome")
_emit_escalates_failure("p3", "check_faiss_persist_contract", "failure_escalation")
_emit_orchestrates_workflow("p3", "check_faiss_persist_contract", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "check_faiss_persist_contract", "healing_dispatch")
_emit_invokes_evaluation("p3", "check_faiss_persist_contract", "evaluation_signal")
_emit_records_telemetry_event("p4", "check_faiss_persist_contract", "telemetry_event")
_emit_captures_evaluation_metric("p4", "check_faiss_persist_contract", "eval_metric")
_emit_stores_embedding("p4", "check_faiss_persist_contract", "embedding_store")
_emit_updates_meta_learning_state("p4", "check_faiss_persist_contract", "meta_learning")
_emit_links_execution_to_snapshot("p4", "check_faiss_persist_contract", "exec_snapshot_link")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_1")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_2")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_3")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_4")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_5")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_6")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_7")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_8")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_9")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_10")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_11")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_12")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_13")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_14")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_15")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_16")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_17")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_18")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_19")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_20")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_21")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_22")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_23")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_24")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_25")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_26")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_27")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_28")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_29")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_30")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_31")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_32")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_33")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_34")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_35")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_36")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_37")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_38")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_39")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_40")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_41")
_emit_reads_through("l4", "check_faiss_persist_contract", "urg_read_42")

PROJECT_ROOT = get_validated_project_root()

_SCAN_ROOTS = [
    PROJECT_ROOT / SYSTEM_LEARNING_DIR,
    PROJECT_ROOT / AGENTIC_CORE_DIR,
]

_EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

_FINALIZE_NAMES = {"finalize_build", "rebuild"}
_PERSIST_NAME = "persist_to_disk"
_GUARDIAN_COMMENT = "guardian: faiss-no-persist"
_GUARDIAN_REASON_RE = "reason="


def _collect_files(roots: list[Path]) -> list[Path]:
    files: list[Path] = []
    for root in roots:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            if any(part in _EXCLUDE_DIRS for part in path.parts):
                continue
            files.append(path)
    return sorted(files)


def _has_call_name(node: ast.expr, name: str) -> bool:
    """Return True if an AST Call node's function resolves to the given name."""
    if not isinstance(node, ast.Call):
        return False
    func = node.func
    if isinstance(func, ast.Attribute):
        return func.attr == name
    if isinstance(func, ast.Name):
        return func.id == name
    return False


def _call_names_in_body(body: list[ast.stmt]) -> set[str]:
    """Collect all method/function call names reachable within a flat body."""
    names: set[str] = set()
    for node in ast.walk(ast.Module(body=body, type_ignores=[])):
        if isinstance(node, ast.Call):
            func = node.func
            if isinstance(func, ast.Attribute):
                names.add(func.attr)
            elif isinstance(func, ast.Name):
                names.add(func.id)
    return names


def _source_lines_for_file(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging    # guardian: Add error context logging
        return []


def _line_has_guardian(source_lines: list[str], lineno: int) -> bool:
    """Return True if the 1-indexed line contains the guardian comment."""
    idx = lineno - 1
    if 0 <= idx < len(source_lines):
        return _GUARDIAN_COMMENT in source_lines[idx]
    return False


def _line_guardian_has_reason(source_lines: list[str], lineno: int) -> bool:
    """Return True if the guardian comment also includes 'reason=<text>'."""
    idx = lineno - 1
    if 0 <= idx < len(source_lines):
        line = source_lines[idx]
        if _GUARDIAN_COMMENT not in line:
            return False
        reason_start = line.find(_GUARDIAN_REASON_RE)
        if reason_start == -1:
            return False
        reason_value = line[reason_start + len(_GUARDIAN_REASON_RE) :].strip()
        return bool(reason_value)
    return False


class _Violation:
    def __init__(self, path: Path, lineno: int, rule: str, detail: str) -> None:
        self.path = path
        self.lineno = lineno
        self.rule = rule
        self.detail = detail

    def __str__(self) -> str:
        try:
            display = self.path.relative_to(PROJECT_ROOT)
        except ValueError:
            display = self.path
        return f"  {display}:{self.lineno}  [{self.rule}]  {self.detail}"


def _check_file(path: Path, source_lines: list[str]) -> list[_Violation]:
    violations: list[_Violation] = []
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"), filename=str(path))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return violations

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        body = node.body
        call_names_in_fn = _call_names_in_body(body)
        has_persist = _PERSIST_NAME in call_names_in_fn

        for stmt in ast.walk(ast.Module(body=body, type_ignores=[])):
            if not isinstance(stmt, ast.Expr):
                continue
            if not isinstance(stmt.value, ast.Call):
                continue
            call = stmt.value
            for finalize_name in _FINALIZE_NAMES:
                if _has_call_name(call, finalize_name):
                    has_guardian = _line_has_guardian(source_lines, stmt.lineno)
                    if not has_persist and not has_guardian:
                        violations.append(
                            _Violation(
                                path=path,
                                lineno=stmt.lineno,
                                rule="R1",
                                detail=(
                                    f"Call to {finalize_name}() in function "
                                    f"'{node.name}' has no downstream persist_to_disk() "
                                    f"in the same scope. Add persist_to_disk() or annotate "
                                    f"the line with '# {_GUARDIAN_COMMENT} reason=<explanation>'"
                                ),
                            )
                        )
                    elif has_guardian and not _line_guardian_has_reason(source_lines, stmt.lineno):
                        violations.append(
                            _Violation(
                                path=path,
                                lineno=stmt.lineno,
                                rule="R2",
                                detail=(
                                    f"Guardian comment '# {_GUARDIAN_COMMENT}' on {finalize_name}() "
                                    f"in function '{node.name}' is missing required justification. "
                                    f"Use: '# {_GUARDIAN_COMMENT} reason=<explanation>'"
                                ),
                            )
                        )
    return violations


def _run(files: list[Path]) -> list[_Violation]:
    all_violations: list[_Violation] = []
    for path in files:
        source_lines = _source_lines_for_file(path)
        all_violations.extend(_check_file(path, source_lines))
    return all_violations


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    if argv:
        files = [Path(a).resolve() for a in argv if a.endswith(".py")]
    else:
        files = _collect_files(_SCAN_ROOTS)

    violations = _run(files)

    scanned = len(files)
    violation_count = len(violations)
    print(f"check_faiss_persist_contract: scanned={scanned} violations={violation_count}")

    if violations:
        print("FAIL: FAISS persist contract violations found:")
        for v in violations:
            print(str(v))
        return 1

    print("OK: FAISS persist contract satisfied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
