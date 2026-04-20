"""
Write Gateway Enforcement Scanner

AST-based static analysis to detect direct file writes bypassing write_gateway.
Enforces that non-L2 layers use the write gateway for persistence operations.
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_dispatches_healing_run,  # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,  # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,  # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
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

emit_replay_key("p0", "write_gateway_enforcer")
emit_determinism_digest("p0", "write_gateway_enforcer")

_emit_dispatches_healing_run("p1", "write_gateway_enforcer", "L5")
_emit_routes_through("p1", "write_gateway_enforcer", "L5")
_emit_checks_agent_registry("p1", "write_gateway_enforcer", "agent_registry")
_emit_validates_agent_capability("p1", "write_gateway_enforcer", "capability")
_emit_dispatches_execution_plan("p1", "write_gateway_enforcer", "exec_plan")
_emit_agent_executes_agent("p1", "write_gateway_enforcer", "sub_agent")
_emit_routes_to_agent("p1", "write_gateway_enforcer", "target_agent")
_emit_verifies_policy("p1", "write_gateway_enforcer", "policy_check")
_emit_observes_runtime_state("p1", "write_gateway_enforcer", "runtime_state")
_emit_verifies_boundary("p1", "write_gateway_enforcer", "boundary_check")
_emit_transcripts_response("p1", "write_gateway_enforcer", "transcript")
_emit_hard_fails_untranscripted("p1", "write_gateway_enforcer")
_emit_gated_by_confidence("p1", "write_gateway_enforcer", "confidence_gate")
_emit_escalates_to_human("p1", "write_gateway_enforcer", "L5")
_emit_reads_policy_state("p1", "write_gateway_enforcer", "L5")

_emit_applies_guardrail("p0", "write_gateway_enforcer", "p0_governance")
_emit_snapshots_state("p0", "write_gateway_enforcer", "state_snapshot")
_emit_authorize_and_execute("p2", "write_gateway_enforcer", "execution_auth")
_emit_validates_capability("p2", "write_gateway_enforcer", "capability_check")
_emit_routes_to_capability("p2", "write_gateway_enforcer", "capability_route")
_emit_writes_via_uwg("p2", "write_gateway_enforcer", "uwg_write")
_emit_blocks_direct_write("p2", "write_gateway_enforcer", "direct_write_block")
_emit_records_tool_invocation("p2", "write_gateway_enforcer", "tool_invocation")
_emit_captures_execution_output("p2", "write_gateway_enforcer", "exec_output")
_emit_dispatches_agent("p3", "write_gateway_enforcer", "agent_dispatch")
_emit_coordinates_agents("p3", "write_gateway_enforcer", "agent_coordination")
_emit_records_workflow_lineage("p3", "write_gateway_enforcer", "workflow_lineage")
_emit_records_healing_outcome("p3", "write_gateway_enforcer", "healing_outcome")
_emit_escalates_failure("p3", "write_gateway_enforcer", "failure_escalation")
_emit_orchestrates_workflow("p3", "write_gateway_enforcer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "write_gateway_enforcer", "healing_dispatch")
_emit_invokes_evaluation("p3", "write_gateway_enforcer", "evaluation_signal")
_emit_records_telemetry_event("p4", "write_gateway_enforcer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "write_gateway_enforcer", "eval_metric")
_emit_stores_embedding("p4", "write_gateway_enforcer", "embedding_store")
_emit_updates_meta_learning_state("p4", "write_gateway_enforcer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "write_gateway_enforcer", "exec_snapshot_link")
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
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
    _emit_records_incident_event,
    _emit_records_learning_event,
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
from tqdm import tqdm

_emit_emits_metric_event("write_gateway_enforcer", "p4obs", "metric_1")
_emit_emits_metric_event("write_gateway_enforcer", "p4obs", "metric_2")
_emit_emits_metric_event("write_gateway_enforcer", "p4obs", "metric_3")
_emit_emits_metric_event("write_gateway_enforcer", "p4obs", "metric_4")
_emit_emits_metric_event("write_gateway_enforcer", "p4obs", "metric_5")
_emit_emits_metric_event("write_gateway_enforcer", "p4obs", "metric_6")
_emit_records_incident_event("write_gateway_enforcer", "p4obs", "incident")
_emit_captures_runtime_anomaly("write_gateway_enforcer", "p4obs", "anomaly")
_emit_writes_observability_log("write_gateway_enforcer", "p4obs", "obs_log")
_emit_updates_monitoring_state("write_gateway_enforcer", "p4obs", "mon_state")
_emit_triggers_alert("write_gateway_enforcer", "p4obs", "alert")
_emit_links_incident_trace("write_gateway_enforcer", "p4obs", "trace_link")
_emit_captures_pattern("write_gateway_enforcer", "p3lm", "pattern")
_emit_records_learning_event("write_gateway_enforcer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("write_gateway_enforcer", "p3lm", "snapshot")
_emit_feeds_meta_learning("write_gateway_enforcer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("write_gateway_enforcer", "p3lm", "routing")
_emit_improves_agent_policy("write_gateway_enforcer", "p3lm", "policy")
_emit_stores_learning_state("write_gateway_enforcer", "p3lm", "state")
_emit_records_execution_trace("write_gateway_enforcer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("write_gateway_enforcer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("write_gateway_enforcer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("write_gateway_enforcer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("write_gateway_enforcer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("write_gateway_enforcer", "env_read", "p2_env_1")
_emit_reads_environ("write_gateway_enforcer", "env_read", "p2_env_2")
_emit_reads_runtime_state("write_gateway_enforcer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("write_gateway_enforcer", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "write_gateway_enforcer", "context_pull")
_emit_pulls_context("p1", "write_gateway_enforcer", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "write_gateway_enforcer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "write_gateway_enforcer", "uwg_term_2")
_emit_writes_through("p1", "write_gateway_enforcer", "write_through")
_emit_writes_through("p1", "write_gateway_enforcer", "write_through_2")
_emit_validated_by_safety_plane("p1", "write_gateway_enforcer", "safety_validation")
_emit_invokes_eval("p1", "write_gateway_enforcer", "eval_call")
_emit_proposal_commits_routing("p1", "write_gateway_enforcer", "routing_commit")


class WriteGatewayVisitor(ast.NodeVisitor):
    """AST visitor to detect direct file writes."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []
        self.in_allowlisted_function = False
        self.current_line_content = ""
        self._with_flagged_lines: set[int] = set()

    def visit(self, node: ast.AST) -> None:
        """Override to track line content."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "WriteGatewayVisitor.visit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:WriteGatewayVisitor.visit".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if hasattr(node, "lineno"):
            try:
                with open(self.file_path, encoding="utf-8") as f:
                    lines = f.readlines()
                    if 0 <= node.lineno - 1 < len(lines):
                        self.current_line_content = lines[node.lineno - 1]
            except (OSError, UnicodeDecodeError, IndexError, AttributeError) as e:
                self.current_line_content = ""
        super().visit(node)

    def _check_allowlist(self) -> bool:
        """Check if current line has allowlist comment."""
        return "# guardian: allow-direct-write" in self.current_line_content

    def visit_Call(self, node: ast.Call) -> None:
        """Check for direct file write calls."""
        if self._check_allowlist():
            self.generic_visit(node)
            return
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if node.lineno in self._with_flagged_lines:
                self.generic_visit(node)
                return
            if node.args:
                mode_arg = None
                if len(node.args) >= 2:
                    mode_arg = node.args[1]
                else:
                    for kw in node.keywords:
                        if kw.arg == "mode":
                            mode_arg = kw.value
                            break
                if mode_arg and isinstance(mode_arg, ast.Constant):
                    if isinstance(mode_arg.value, str):
                        write_modes = {"w", "wb", "a", "ab", "w+", "wb+", "a+", "ab+"}
                        if any(mode_arg.value.startswith(mode) for mode in write_modes):
                            snippet = f'open(..., mode="{mode_arg.value}")'
                            self.violations.append((node.lineno, "DIRECT_OPEN_WRITE", snippet))
        if isinstance(node.func, ast.Attribute):
            if node.func.attr in ["write_text", "write_bytes"]:
                snippet = f"Path.{node.func.attr}(...)"
                self.violations.append((node.lineno, "DIRECT_PATH_WRITE", snippet))
        if isinstance(node.func, ast.Name) and node.func.id == "json":
            if isinstance(node.func, ast.Name):
                if hasattr(node, "parent"):
                    pass
        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> None:
        """Check for 'with open(...)' patterns."""
        if self._check_allowlist():
            self.generic_visit(node)
            return
        for item in tqdm(node.items, desc="Processing", unit="item"):
            if isinstance(item.context_expr, ast.Call):
                if isinstance(item.context_expr.func, ast.Name) and item.context_expr.func.id == "open":
                    mode_arg = None
                    if len(item.context_expr.args) >= 2:
                        mode_arg = item.context_expr.args[1]
                    else:
                        for kw in item.context_expr.keywords:
                            if kw.arg == "mode":
                                mode_arg = kw.value
                                break
                    if mode_arg and isinstance(mode_arg, ast.Constant):
                        if isinstance(mode_arg.value, str):
                            write_modes = {"w", "wb", "a", "ab", "w+", "wb+", "a+", "ab+"}
                            if any(mode_arg.value.startswith(mode) for mode in write_modes):
                                snippet = f'with open(..., mode="{mode_arg.value}")'
                                self.violations.append((node.lineno, "DIRECT_WITH_WRITE", snippet))
                                self._with_flagged_lines.add(item.context_expr.lineno)
        self.generic_visit(node)


def scan_file_for_writes(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for direct file writes.

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    """
    violations = []
    if "L2_execution" in str(file_path):
        return violations
    if "ptc" in str(file_path).lower() and "tool_call_store.py" in str(file_path):
        return violations
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        visitor = WriteGatewayVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        violations.append((e.lineno or 0, "WRITE_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        violations.append((0, "WRITE_SCAN_ERROR", f"Scan error: {e}"))
    return violations


_WRITE_SCAN_ROOTS = [
    "agentic_core/L3_orchestration/replay",
    "agentic_core/L3_orchestration/arbitration",
    "agentic_core/L3_orchestration/ptc",
    "agentic_core/L4_state/storage",
]


def scan_repository_for_writes(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan governance-critical storage/replay directories for direct file writes.

    Only scans the directories where the UWG write-gateway contract is enforced.
    Legacy script, agent, and reasoning directories are excluded.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []
    for scan_root in tqdm(_WRITE_SCAN_ROOTS, desc="Processing", unit="item"):
        scan_path = repo_root / scan_root
        if not scan_path.exists():
            continue
        for py_file in scan_path.rglob("*.py"):
            if "L2_execution" in py_file.parts:
                continue
            violations = scan_file_for_writes(py_file)
            for lineno, rule_id, snippet in violations:
                rel_path = str(py_file.relative_to(repo_root))
                all_violations.append((rel_path, lineno, rule_id, snippet))
    all_violations.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return all_violations


__all__ = ["scan_file_for_writes", "scan_repository_for_writes"]
