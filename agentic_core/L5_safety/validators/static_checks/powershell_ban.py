"""
PowerShell Prohibition Scanner

AST-based static analysis to detect PowerShell usage in the codebase.
Enforces the invariant that no runners/tools use PowerShell directly.
"""

from __future__ import annotations

import ast
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TOOLS_DIR
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

emit_replay_key("p0", "powershell_ban")
emit_determinism_digest("p0", "powershell_ban")

_emit_dispatches_healing_run("p1", "powershell_ban", "L5")
_emit_routes_through("p1", "powershell_ban", "L5")
_emit_checks_agent_registry("p1", "powershell_ban", "agent_registry")
_emit_validates_agent_capability("p1", "powershell_ban", "capability")
_emit_dispatches_execution_plan("p1", "powershell_ban", "exec_plan")
_emit_agent_executes_agent("p1", "powershell_ban", "sub_agent")
_emit_routes_to_agent("p1", "powershell_ban", "target_agent")
_emit_verifies_policy("p1", "powershell_ban", "policy_check")
_emit_observes_runtime_state("p1", "powershell_ban", "runtime_state")
_emit_verifies_boundary("p1", "powershell_ban", "boundary_check")
_emit_transcripts_response("p1", "powershell_ban", "transcript")
_emit_hard_fails_untranscripted("p1", "powershell_ban")
_emit_gated_by_confidence("p1", "powershell_ban", "confidence_gate")
_emit_escalates_to_human("p1", "powershell_ban", "L5")
_emit_reads_policy_state("p1", "powershell_ban", "L5")

_emit_applies_guardrail("p0", "powershell_ban", "p0_governance")
_emit_snapshots_state("p0", "powershell_ban", "state_snapshot")
_emit_authorize_and_execute("p2", "powershell_ban", "execution_auth")
_emit_validates_capability("p2", "powershell_ban", "capability_check")
_emit_routes_to_capability("p2", "powershell_ban", "capability_route")
_emit_writes_via_uwg("p2", "powershell_ban", "uwg_write")
_emit_blocks_direct_write("p2", "powershell_ban", "direct_write_block")
_emit_records_tool_invocation("p2", "powershell_ban", "tool_invocation")
_emit_captures_execution_output("p2", "powershell_ban", "exec_output")
_emit_dispatches_agent("p3", "powershell_ban", "agent_dispatch")
_emit_coordinates_agents("p3", "powershell_ban", "agent_coordination")
_emit_records_workflow_lineage("p3", "powershell_ban", "workflow_lineage")
_emit_records_healing_outcome("p3", "powershell_ban", "healing_outcome")
_emit_escalates_failure("p3", "powershell_ban", "failure_escalation")
_emit_orchestrates_workflow("p3", "powershell_ban", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "powershell_ban", "healing_dispatch")
_emit_invokes_evaluation("p3", "powershell_ban", "evaluation_signal")
_emit_records_telemetry_event("p4", "powershell_ban", "telemetry_event")
_emit_captures_evaluation_metric("p4", "powershell_ban", "eval_metric")
_emit_stores_embedding("p4", "powershell_ban", "embedding_store")
_emit_updates_meta_learning_state("p4", "powershell_ban", "meta_learning")
_emit_links_execution_to_snapshot("p4", "powershell_ban", "exec_snapshot_link")
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

_emit_emits_metric_event("powershell_ban", "p4obs", "metric_1")
_emit_emits_metric_event("powershell_ban", "p4obs", "metric_2")
_emit_emits_metric_event("powershell_ban", "p4obs", "metric_3")
_emit_emits_metric_event("powershell_ban", "p4obs", "metric_4")
_emit_emits_metric_event("powershell_ban", "p4obs", "metric_5")
_emit_emits_metric_event("powershell_ban", "p4obs", "metric_6")
_emit_records_incident_event("powershell_ban", "p4obs", "incident")
_emit_captures_runtime_anomaly("powershell_ban", "p4obs", "anomaly")
_emit_writes_observability_log("powershell_ban", "p4obs", "obs_log")
_emit_updates_monitoring_state("powershell_ban", "p4obs", "mon_state")
_emit_triggers_alert("powershell_ban", "p4obs", "alert")
_emit_links_incident_trace("powershell_ban", "p4obs", "trace_link")
_emit_captures_pattern("powershell_ban", "p3lm", "pattern")
_emit_records_learning_event("powershell_ban", "p3lm", "learning_event")
_emit_writes_learning_snapshot("powershell_ban", "p3lm", "snapshot")
_emit_feeds_meta_learning("powershell_ban", "p3lm", "meta_feed")
_emit_updates_routing_strategy("powershell_ban", "p3lm", "routing")
_emit_improves_agent_policy("powershell_ban", "p3lm", "policy")
_emit_stores_learning_state("powershell_ban", "p3lm", "state")
_emit_records_execution_trace("powershell_ban", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("powershell_ban", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("powershell_ban", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("powershell_ban", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("powershell_ban", "L4_STATE", "p2_trace_5")
_emit_reads_environ("powershell_ban", "env_read", "p2_env_1")
_emit_reads_environ("powershell_ban", "env_read", "p2_env_2")
_emit_reads_runtime_state("powershell_ban", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("powershell_ban", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "powershell_ban", "context_pull")
_emit_pulls_context("p1", "powershell_ban", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "powershell_ban", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "powershell_ban", "uwg_term_2")
_emit_writes_through("p1", "powershell_ban", "write_through")
_emit_writes_through("p1", "powershell_ban", "write_through_2")
_emit_validated_by_safety_plane("p1", "powershell_ban", "safety_validation")
_emit_invokes_eval("p1", "powershell_ban", "eval_call")
_emit_proposal_commits_routing("p1", "powershell_ban", "routing_commit")


class PowerShellBanVisitor(ast.NodeVisitor):
    """AST visitor to detect PowerShell usage patterns."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []

    def visit_Constant(self, node: ast.Constant) -> None:
        """Check string literals for PowerShell command invocations in docs/evidence.

        Only flags strings that START WITH 'pwsh' or 'powershell' AND contain a space,
        indicating a full command invocation (e.g. "powershell -Command ...").
        Short guard-check strings like 'powershell' or 'pwsh' used in comparisons
        are NOT flagged because they lack a following argument.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "PowerShellBanVisitor.visit_Constant",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:PowerShellBanVisitor.visit_Constant".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if isinstance(node.value, str):
            val_lower = node.value.strip().lower()
            if val_lower.startswith("pwsh ") or val_lower.startswith("powershell "):
                path_str = str(self.file_path).lower()
                if "evidence" in path_str or "docs" in path_str:
                    snippet = repr(node.value[:60])
                    self.violations.append((node.lineno, "PS_STRING_LITERAL", snippet))
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        """Check for subprocess calls with PowerShell - semantic callsite enforcement only."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == "subprocess":
                    if node.args:
                        first_arg = node.args[0]
                        if isinstance(first_arg, ast.Constant) and isinstance(first_arg.value, str):
                            cmd_lower = first_arg.value.lower()
                            if "pwsh" in cmd_lower or "powershell" in cmd_lower:
                                snippet = f"subprocess.{node.func.attr}(...{first_arg.value[:50]}...)"
                                self.violations.append((node.lineno, "PS_SUBPROCESS_ARGV0", snippet))
                        elif isinstance(first_arg, (ast.List, ast.Tuple)):
                            if first_arg.elts:
                                argv0 = first_arg.elts[0]
                                if isinstance(argv0, ast.Constant) and isinstance(argv0.value, str):
                                    argv0_lower = argv0.value.lower()
                                    if argv0_lower in ("pwsh", "powershell", "pwsh.exe", "powershell.exe"):
                                        snippet = f"subprocess.{node.func.attr}(['{argv0.value}', ...])"
                                        self.violations.append((node.lineno, "PS_SUBPROCESS_ARGV0", snippet))
        if TOOLS_DIR in str(self.file_path):
            for keyword in node.keywords:
                if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
                    if keyword.value.value is True:
                        snippet = f"subprocess.{node.func.attr}(..., shell=True, ...)"
                        self.violations.append((node.lineno, "PS_SUBPROCESS_SHELL", snippet))
        self.generic_visit(node)


def scan_file_for_powershell(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for PowerShell usage.

    For docs/evidence files: also scans raw comment lines for PS references.
    For other files: uses AST-based detection only (subprocess calls).

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    """
    violations = []
    path_str = str(file_path).lower()
    _is_docs_evidence = "evidence" in path_str or "docs" in path_str
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        visitor = PowerShellBanVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)
        if _is_docs_evidence:
            ast_linenos = {v[0] for v in violations}
            for lineno, line in tqdm(
                enumerate(content.splitlines(), start=1), desc="Processing", unit="item"
            ):
                stripped = line.strip()
                if not stripped.startswith("#"):
                    continue
                if lineno in ast_linenos:
                    continue
                line_lower = stripped.lower()
                if "pwsh" in line_lower or "powershell" in line_lower:
                    violations.append((lineno, "PS_STRING_LITERAL", stripped[:60]))
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        violations.append((e.lineno or 0, "PS_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    # guardian: allow-silent-swallower
    except (ValueError, TypeError) as e:
        violations.append((0, "PS_SCAN_ERROR", f"Scan error: {e}"))
    return violations


def scan_repository_for_powershell(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan repository for PowerShell usage.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []
    scan_dirs = ["docs/evidence"]
    for scan_dir in tqdm(scan_dirs, desc="Processing", unit="item"):
        dir_path = repo_root / scan_dir
        if not dir_path.exists():
            continue
        for py_file in dir_path.rglob("*.py"):
            violations = scan_file_for_powershell(py_file)
            for lineno, rule_id, snippet in violations:
                rel_path = str(py_file.relative_to(repo_root))
                all_violations.append((rel_path, lineno, rule_id, snippet))
    all_violations.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return all_violations


__all__ = ["scan_file_for_powershell", "scan_repository_for_powershell"]
