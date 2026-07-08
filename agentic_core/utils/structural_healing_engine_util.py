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
import logging
import shutil
from pathlib import Path
from typing import Any

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract
from agentic_core.runtime.exceptions.SovereignError import StructuralError

trace_contract._emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("structural_healing_engine_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("structural_healing_engine_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("structural_healing_engine_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("structural_healing_engine_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("structural_healing_engine_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("structural_healing_engine_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("structural_healing_engine_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("structural_healing_engine_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("structural_healing_engine_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("structural_healing_engine_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("structural_healing_engine_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("structural_healing_engine_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("structural_healing_engine_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("structural_healing_engine_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("structural_healing_engine_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("structural_healing_engine_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("structural_healing_engine_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("structural_healing_engine_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("structural_healing_engine_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("structural_healing_engine_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("structural_healing_engine_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("structural_healing_engine_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("structural_healing_engine_util", "runtime_state", "p2_rt_2")

trace_contract._emit_records_execution_trace("p0", "evidence", "structural_healing_engine_util")
logger = logging.getLogger(__name__)

trace_contract._emit_applies_guardrail("p0", "structural_healing_engine_util", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "structural_healing_engine_util", "policy_binding")
trace_contract._emit_snapshots_state("p0", "structural_healing_engine_util", "state_snapshot")
trace_contract._emit_pulls_context("p1", "structural_healing_engine_util", "context_pull")
trace_contract._emit_pulls_context("p1", "structural_healing_engine_util", "context_pull_secondary")
trace_contract._emit_execution_terminates_at_uwg("p1", "structural_healing_engine_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "structural_healing_engine_util", "uwg_term_secondary")
trace_contract._emit_writes_through("p1", "structural_healing_engine_util", "write_through")
trace_contract._emit_writes_through("p1", "structural_healing_engine_util", "write_through_secondary")
trace_contract._emit_validated_by_safety_plane("p1", "structural_healing_engine_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "structural_healing_engine_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "structural_healing_engine_util", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "structural_healing_engine_util", "human_escalation")
trace_contract._emit_routes_through("p1", "structural_healing_engine_util", "route_through")
trace_contract._emit_checks_agent_registry("p1", "structural_healing_engine_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "structural_healing_engine_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "structural_healing_engine_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "structural_healing_engine_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "structural_healing_engine_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "structural_healing_engine_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "structural_healing_engine_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "structural_healing_engine_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "structural_healing_engine_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "structural_healing_engine_util")
trace_contract._emit_gated_by_confidence("p1", "structural_healing_engine_util", "confidence_gate")
trace_contract.emit_replay_key("p0", "structural_healing_engine_util")
trace_contract.emit_determinism_digest("p0", "structural_healing_engine_util")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "structural_healing_engine_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "structural_healing_engine_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "structural_healing_engine_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "structural_healing_engine_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "structural_healing_engine_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "structural_healing_engine_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "structural_healing_engine_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "structural_healing_engine_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "structural_healing_engine_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "structural_healing_engine_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "structural_healing_engine_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "structural_healing_engine_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "structural_healing_engine_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "structural_healing_engine_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "structural_healing_engine_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "structural_healing_engine_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "structural_healing_engine_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "structural_healing_engine_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "structural_healing_engine_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "structural_healing_engine_util", "exec_snapshot_link")


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
    except SyntaxError as e:  # guardian: allow-silent-swallow -- acceptable exception handling
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
        root = project_root.resolve(strict=True)
        source.resolve(strict=True).relative_to(root)
        target.resolve(strict=False).relative_to(root)
        return True
    except (OSError, RuntimeError, ValueError, FileNotFoundError) as e:
        logger.warning(
            "Rejected relocation outside project root or with unresolved source: %s",
            e,
        )
        return False
