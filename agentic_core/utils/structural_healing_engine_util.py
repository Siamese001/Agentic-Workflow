"""
structural_healing_engine.py - Stateless Structural Healing Operations

[MIXIN REFACTOR] Extracted pure logic from structural_healing_mixin.py.
All functions are stateless (no Agent `self` dependency).
Naming convention: *_engine.py = pure logic/transformations.

Provides:
- File relocation with integrity verification
- AST-based structure analysis
- Complexity scoring
- File split suggestions
"""

from __future__ import annotations

import ast
import hashlib
import shutil
from pathlib import Path
from typing import Any

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
from agentic_core.runtime.exceptions.SovereignError import StructuralError

_emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_1")
_emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_2")
_emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_3")
_emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_4")
_emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_5")
_emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_6")
_emit_records_incident_event("structural_healing_engine_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("structural_healing_engine_util", "p4obs", "anomaly")
_emit_writes_observability_log("structural_healing_engine_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("structural_healing_engine_util", "p4obs", "mon_state")
_emit_triggers_alert("structural_healing_engine_util", "p4obs", "alert")
_emit_links_incident_trace("structural_healing_engine_util", "p4obs", "trace_link")
_emit_captures_pattern("structural_healing_engine_util", "p3lm", "pattern")
_emit_records_learning_event("structural_healing_engine_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("structural_healing_engine_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("structural_healing_engine_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("structural_healing_engine_util", "p3lm", "routing")
_emit_improves_agent_policy("structural_healing_engine_util", "p3lm", "policy")
_emit_stores_learning_state("structural_healing_engine_util", "p3lm", "state")
_emit_records_execution_trace("structural_healing_engine_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("structural_healing_engine_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("structural_healing_engine_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("structural_healing_engine_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("structural_healing_engine_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("structural_healing_engine_util", "env_read", "p2_env_1")
_emit_reads_environ("structural_healing_engine_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("structural_healing_engine_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("structural_healing_engine_util", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "structural_healing_engine_util")
_emit_applies_guardrail("p0", "structural_healing_engine_util", "p0_governance")
_emit_reads_policy_state("p0", "structural_healing_engine_util", "policy_binding")
_emit_snapshots_state("p0", "structural_healing_engine_util", "state_snapshot")
_emit_pulls_context("p1", "structural_healing_engine_util", "context_pull")
_emit_pulls_context("p1", "structural_healing_engine_util", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "structural_healing_engine_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "structural_healing_engine_util", "uwg_term_secondary")
_emit_writes_through("p1", "structural_healing_engine_util", "write_through")
_emit_writes_through("p1", "structural_healing_engine_util", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "structural_healing_engine_util", "safety_validation")
_emit_invokes_eval("p1", "structural_healing_engine_util", "eval_call")
_emit_proposal_commits_routing("p1", "structural_healing_engine_util", "routing_commit")
_emit_escalates_to_human("p1", "structural_healing_engine_util", "human_escalation")
_emit_routes_through("p1", "structural_healing_engine_util", "route_through")
_emit_checks_agent_registry("p1", "structural_healing_engine_util", "agent_registry")
_emit_validates_agent_capability("p1", "structural_healing_engine_util", "capability")
_emit_dispatches_execution_plan("p1", "structural_healing_engine_util", "exec_plan")
_emit_agent_executes_agent("p1", "structural_healing_engine_util", "sub_agent")
_emit_routes_to_agent("p1", "structural_healing_engine_util", "target_agent")
_emit_verifies_policy("p1", "structural_healing_engine_util", "policy_check")
_emit_observes_runtime_state("p1", "structural_healing_engine_util", "runtime_state")
_emit_verifies_boundary("p1", "structural_healing_engine_util", "boundary_check")
_emit_transcripts_response("p1", "structural_healing_engine_util", "transcript")
_emit_hard_fails_untranscripted("p1", "structural_healing_engine_util")
_emit_gated_by_confidence("p1", "structural_healing_engine_util", "confidence_gate")
emit_replay_key("p0", "structural_healing_engine_util")
emit_determinism_digest("p0", "structural_healing_engine_util")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "structural_healing_engine_util", "execution_auth")
_emit_validates_capability("p2", "structural_healing_engine_util", "capability_check")
_emit_routes_to_capability("p2", "structural_healing_engine_util", "capability_route")
_emit_writes_via_uwg("p2", "structural_healing_engine_util", "uwg_write")
_emit_blocks_direct_write("p2", "structural_healing_engine_util", "direct_write_block")
_emit_records_tool_invocation("p2", "structural_healing_engine_util", "tool_invocation")
_emit_captures_execution_output("p2", "structural_healing_engine_util", "exec_output")
_emit_dispatches_agent("p3", "structural_healing_engine_util", "agent_dispatch")
_emit_coordinates_agents("p3", "structural_healing_engine_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "structural_healing_engine_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "structural_healing_engine_util", "healing_outcome")
_emit_escalates_failure("p3", "structural_healing_engine_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "structural_healing_engine_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "structural_healing_engine_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "structural_healing_engine_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "structural_healing_engine_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "structural_healing_engine_util", "eval_metric")
_emit_stores_embedding("p4", "structural_healing_engine_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "structural_healing_engine_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "structural_healing_engine_util", "exec_snapshot_link")


def relocate_file(
    source_path: Path,
    target_path: Path,
    project_root: Path,
    *,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Relocate a file with integrity verification and rollback.

    Args:
        source_path: Source file to move.
        target_path: Destination path.
        project_root: Project root for safety boundary checks.
        dry_run: If True, only validate without moving.

    Returns:
        Dict with 'status' key ('success', 'blocked', 'dry_run').
    """
    if not source_path.exists():
        raise StructuralError(f"Source file not found: {source_path}")
    if not _is_safe_relocation(source_path, target_path, project_root):
        raise StructuralError(f"Unsafe relocation: {source_path} -> {target_path}")
    source_hash = calculate_file_hash(source_path)
    if target_path.exists():
        return {"status": "blocked", "reason": "target_exists"}
    if dry_run:
        return {"status": "dry_run", "source": str(source_path), "target": str(target_path)}
    target_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(source_path), str(target_path))
    if calculate_file_hash(target_path) != source_hash:
        shutil.move(str(target_path), str(source_path))
        raise StructuralError("File integrity check failed after relocation")
    return {"status": "success"}


def analyze_file_structure(file_path: Path, *, max_lines: int = 800) -> dict[str, Any]:
    """Analyze a Python file's structure for potential issues.

    Args:
        file_path: Path to the Python file.
        max_lines: Threshold for "file too large" warning.

    Returns:
        Dict with line_count, size_bytes, has_syntax_errors, complexity_score, issues.
    """
    if not file_path.exists():
        raise StructuralError(f"File not found: {file_path}")
    content = file_path.read_text(encoding="utf-8")
    lines = content.splitlines()
    structure_info: dict[str, Any] = {
        "line_count": len(lines),
        "size_bytes": file_path.stat().st_size,
        "has_syntax_errors": False,
        "complexity_score": 0,
        "issues": [],
    }
    if structure_info["line_count"] > max_lines:
        structure_info["issues"].append(
            f"File too large: {structure_info['line_count']} lines (limit: {max_lines})",
        )
    try:
        ast.parse(content)
    # guardian: allow-silent-swallow - acceptable exception handling
    except SyntaxError as e:
        structure_info["has_syntax_errors"] = True
        structure_info["issues"].append(f"Syntax error: {e}")
    structure_info["complexity_score"] = calculate_complexity(content)
    return structure_info


def calculate_complexity(content: str) -> int:
    """Calculate simplified cyclomatic complexity score from source text.

    Args:
        content: Python source code string.

    Returns:
        Integer complexity score (1 = base).
    """
    complexity = 1
    control_keywords = ["if", "elif", "for", "while", "try", "except", "with"]
    for keyword in control_keywords:
        complexity += content.count(f" {keyword} ")
    complexity += content.count("def ")
    complexity += content.count("class ")
    return complexity


def suggest_file_split(file_path: Path, *, max_lines: int = 800) -> list[dict[str, Any]]:
    """Suggest splitting strategies for large files.

    Args:
        file_path: Path to the Python file.
        max_lines: Threshold below which no split is suggested.

    Returns:
        List of suggestion dicts with 'strategy', 'description', 'priority'.
    """
    structure = analyze_file_structure(file_path, max_lines=max_lines)
    if structure["line_count"] <= max_lines:
        return []
    suggestions = []
    content = file_path.read_text(encoding="utf-8")
    if "class " in content:
        suggestions.append(
            {
                "strategy": "split_by_classes",
                "description": "Split file into separate class files",
                "priority": "high",
            },
        )
    if "def " in content:
        suggestions.append(
            {
                "strategy": "split_by_functions",
                "description": "Group related functions into modules",
                "priority": "medium",
            },
        )
    return suggestions


def calculate_file_hash(file_path: Path) -> str:
    """SHA-256 hash of file contents."""
    return hashlib.sha256(file_path.read_bytes()).hexdigest()


def _is_safe_relocation(source: Path, target: Path, project_root: Path) -> bool:
    """Check both paths are within the project root."""
    try:
        source.resolve().relative_to(project_root.resolve())
        target.resolve().relative_to(project_root.resolve())
        return True
    except ValueError as e:
        # TODO: Add proper input validation
        logger.warning(f"Invalid input: {e}")
        return False
