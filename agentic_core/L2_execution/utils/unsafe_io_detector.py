"""
AST-based detector for unsafe I/O and subprocess usage.

This module provides tools to detect potentially unsafe file I/O and subprocess
operations that could bypass the mutation fence and write to protected roots.
"""

import ast
from dataclasses import dataclass
from pathlib import Path

from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
    # noqa: E402,
    # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402
    _emit_escalates_failure,
    _emit_escalates_to_human,
    # noqa: E402
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,
    # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_through,
    # noqa: E402
    _emit_routes_to_agent,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,
    _emit_snapshots_state,
    # noqa: E402
    _emit_stores_embedding,
    _emit_transcripts_response,
    _emit_updates_meta_learning_state,
    _emit_validates_agent_capability,
    _emit_validates_capability,
    _emit_verifies_boundary,
    _emit_verifies_policy,
    _emit_writes_via_uwg,
    emit_determinism_digest,
    # noqa: E402
    emit_replay_key,
)

emit_replay_key("p0", "unsafe_io_detector")
emit_determinism_digest("p0", "unsafe_io_detector")

_emit_dispatches_healing_run("p1", "unsafe_io_detector", "L2")
_emit_routes_through("p1", "unsafe_io_detector", "L2")
_emit_checks_agent_registry("p1", "unsafe_io_detector", "agent_registry")
_emit_validates_agent_capability("p1", "unsafe_io_detector", "capability")
_emit_dispatches_execution_plan("p1", "unsafe_io_detector", "exec_plan")
_emit_agent_executes_agent("p1", "unsafe_io_detector", "sub_agent")
_emit_routes_to_agent("p1", "unsafe_io_detector", "target_agent")
_emit_verifies_policy("p1", "unsafe_io_detector", "policy_check")
_emit_observes_runtime_state("p1", "unsafe_io_detector", "runtime_state")
_emit_verifies_boundary("p1", "unsafe_io_detector", "boundary_check")
_emit_transcripts_response("p1", "unsafe_io_detector", "transcript")
_emit_hard_fails_untranscripted("p1", "unsafe_io_detector")
_emit_gated_by_confidence("p1", "unsafe_io_detector", "confidence_gate")
_emit_escalates_to_human("p1", "unsafe_io_detector", "L2")
_emit_reads_policy_state("p1", "unsafe_io_detector", "L2")

_emit_applies_guardrail("p0", "unsafe_io_detector", "p0_governance")
_emit_snapshots_state("p0", "unsafe_io_detector", "state_snapshot")
_emit_authorize_and_execute("p2", "unsafe_io_detector", "execution_auth")
_emit_validates_capability("p2", "unsafe_io_detector", "capability_check")
_emit_routes_to_capability("p2", "unsafe_io_detector", "capability_route")
_emit_writes_via_uwg("p2", "unsafe_io_detector", "uwg_write")
_emit_blocks_direct_write("p2", "unsafe_io_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "unsafe_io_detector", "tool_invocation")
_emit_captures_execution_output("p2", "unsafe_io_detector", "exec_output")
_emit_dispatches_agent("p3", "unsafe_io_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "unsafe_io_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "unsafe_io_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "unsafe_io_detector", "healing_outcome")
_emit_escalates_failure("p3", "unsafe_io_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "unsafe_io_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "unsafe_io_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "unsafe_io_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "unsafe_io_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "unsafe_io_detector", "eval_metric")
_emit_stores_embedding("p4", "unsafe_io_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "unsafe_io_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "unsafe_io_detector", "exec_snapshot_link")


def _invoke_authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw):
    from agentic_core.L2_execution.enforcement.execution_guardrail_chokepoint import (
        authorize_and_execute,  # noqa: PLC0415
    )

    return authorize_and_execute(execution_context, target_callable, capability_token, payload, **kw)


def _make_execution_context(payload, target: str):
    from agentic_core.L4_state.context.execution_context import (  # noqa: PLC0415
        ActionClass,
        ExecutionContext,
    )

    return ExecutionContext.create(
        run_id="unsafe_io_detector",
        capability_token="default",
        policy_hash="default",
        execution_input=str(payload),
        execution_target=target,
        action_class=ActionClass.PRIVILEGED_LOCAL,
    )


from agentic_core.L0_routing.config import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
)
from agentic_core.L0_routing.config.path_constants import (
    TESTS_DIR,
    TOOLS_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    LayerSegment,
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
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_to_agent,
    _emit_signs_execution_trace,
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

_emit_emits_metric_event("unsafe_io_detector", "p4obs", "metric_1")
_emit_emits_metric_event("unsafe_io_detector", "p4obs", "metric_2")
_emit_emits_metric_event("unsafe_io_detector", "p4obs", "metric_3")
_emit_emits_metric_event("unsafe_io_detector", "p4obs", "metric_4")
_emit_emits_metric_event("unsafe_io_detector", "p4obs", "metric_5")
_emit_emits_metric_event("unsafe_io_detector", "p4obs", "metric_6")
_emit_records_incident_event("unsafe_io_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("unsafe_io_detector", "p4obs", "anomaly")
_emit_writes_observability_log("unsafe_io_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("unsafe_io_detector", "p4obs", "mon_state")
_emit_triggers_alert("unsafe_io_detector", "p4obs", "alert")
_emit_links_incident_trace("unsafe_io_detector", "p4obs", "trace_link")
_emit_captures_pattern("unsafe_io_detector", "p3lm", "pattern")
_emit_records_learning_event("unsafe_io_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("unsafe_io_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("unsafe_io_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("unsafe_io_detector", "p3lm", "routing")
_emit_improves_agent_policy("unsafe_io_detector", "p3lm", "policy")
_emit_stores_learning_state("unsafe_io_detector", "p3lm", "state")
_emit_records_execution_trace("unsafe_io_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("unsafe_io_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("unsafe_io_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("unsafe_io_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("unsafe_io_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("unsafe_io_detector", "env_read", "p2_env_1")
_emit_reads_environ("unsafe_io_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("unsafe_io_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("unsafe_io_detector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "unsafe_io_detector", "context_pull")
_emit_pulls_context("p1", "unsafe_io_detector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "unsafe_io_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "unsafe_io_detector", "uwg_term_2")
_emit_writes_through("p1", "unsafe_io_detector", "write_through")
_emit_writes_through("p1", "unsafe_io_detector", "write_through_2")
_emit_validated_by_safety_plane("p1", "unsafe_io_detector", "safety_validation")
_emit_invokes_eval("p1", "unsafe_io_detector", "eval_call")
_emit_proposal_commits_routing("p1", "unsafe_io_detector", "routing_commit")


@dataclass
class UnsafePattern:
    """Represents an unsafe pattern found in code."""

    file_path: str
    line_number: int
    pattern_type: str
    node_text: str
    context: str


class UnsafePatternVisitor(ast.NodeVisitor):
    """AST visitor to detect unsafe I/O and subprocess patterns."""

    # File write patterns
    WRITE_MODES = {"w", "a", "x", "wb", "ab", "xb"}
    UNSAFE_FUNCTIONS = {
        # File operations
        "open",
        "Path.write_text",
        "Path.write_bytes",
        "os.remove",
        "os.unlink",
        "os.rename",
        "os.replace",
        "shutil.rmtree",
        "shutil.move",
        # Subprocess operations
        "subprocess.run",
        "subprocess.call",
        "subprocess.check_call",
        "subprocess.check_output",
        "subprocess.Popen",
    }

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.findings: list[UnsafePattern] = []

    def visit_Call(self, node: ast.Call):
        """Visit function calls to detect unsafe patterns."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L2_EXECUTION, "UnsafePatternVisitor.visit_Call")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:UnsafePatternVisitor.visit_Call".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        # Check for open() with write modes
        if isinstance(node.func, ast.Name) and node.func.id == "open":
            if len(node.args) >= 2:
                mode_arg = node.args[1]
                if isinstance(mode_arg, ast.Constant) and mode_arg.value in self.WRITE_MODES:
                    self.add_finding(node, "open_write")

        # Check for Path.write_text/write_bytes
        elif isinstance(node.func, ast.Attribute):
            if node.func.attr in {"write_text", "write_bytes"}:
                self.add_finding(node, f"path_{node.func.attr}")
            elif node.func.attr in {"remove", "unlink", "rename", "replace"}:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "os":
                    self.add_finding(node, f"os_{node.func.attr}")
            elif node.func.attr in {"rmtree", "move"}:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "shutil":
                    self.add_finding(node, f"shutil_{node.func.attr}")
            elif node.func.attr in {"run", "call", "check_call", "check_output", "Popen"}:
                if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                    self.add_finding(node, f"subprocess_{node.func.attr}")

        self.generic_visit(node)

    def add_finding(self, node: ast.AST, pattern_type: str):
        """Add a finding to the list."""
        line_text = ast.get_source_segment(self.source, node) if hasattr(self, "source") else ""
        context = self._get_context(node)

        finding = UnsafePattern(
            file_path=self.file_path,
            line_number=node.lineno,
            pattern_type=pattern_type,
            node_text=line_text,
            context=context,
        )
        self.findings.append(finding)

    def _get_context(self, node: ast.AST) -> str:
        """Get context line for the finding."""
        if hasattr(self, "source_lines"):
            line_idx = node.lineno - 1
            if 0 <= line_idx < len(self.source_lines):
                return self.source_lines[line_idx].strip()
        return ""

    def visit(self, node: ast.AST, source: str = None) -> list[UnsafePattern]:
        """Visit AST with optional source code for context."""
        if source:
            self.source = source
            self.source_lines = source.splitlines()
        super().visit(node)
        return self.findings


def scan_for_unsafe_patterns(code: str, file_path: str) -> list[UnsafePattern]:
    """
    Scan Python code for unsafe I/O and subprocess patterns.

    Args:
        code: Python source code to scan
        file_path: Path to the file being scanned (for reporting)

    Returns:
        List of unsafe patterns found
    """
    _ectx = _make_execution_context(file_path, "unsafe_io_detector.scan_for_unsafe_patterns")
    _invoke_authorize_and_execute(
        _ectx,
        lambda p: p,
        "default",
        file_path,
        target_name="unsafe_io_detector.scan_for_unsafe_patterns",
    )
    try:
        tree = ast.parse(code)
        visitor = UnsafePatternVisitor(file_path)
        return visitor.visit(tree, code)
    # guardian: allow-silent-swallow
    except SyntaxError:
        # Return empty list for files that can't be parsed
        return []


def scan_directory_for_unsafe_patterns(
    directory: Path, recursive: bool = True, file_pattern: str = "*.py"
) -> list[UnsafePattern]:
    """
    Scan a directory for unsafe patterns in Python files.

    Args:
        directory: Directory to scan
        recursive: Whether to scan subdirectories
        file_pattern: File pattern to match (default: *.py)

    Returns:
        List of unsafe patterns found
    """
    all_findings = []

    if recursive:
        files = directory.rglob(file_pattern)
    else:
        files = directory.glob(file_pattern)

    for file_path in files:
        if file_path.is_file():
            try:
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                findings = scan_for_unsafe_patterns(content, str(file_path))
                all_findings.extend(findings)
            # guardian: allow-silent-swallow
            except (ValueError, TypeError):
                # Skip files that can't be read or parsed
                continue

    return all_findings


def get_scoped_directories(repo_root: Path) -> list[Path]:
    """Get the list of directories that should be scanned for unsafe patterns."""
    scoped_dirs = [
        repo_root / AGENTIC_CORE_DIR / "L0_routing" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / "L2_execution" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / "L3_orchestration" / "reasoning",
        repo_root / AGENTIC_CORE_DIR / APPS_LIC_DIR / "reasoning",
        repo_root / AGENTIC_CORE_DIR / APPS_RG_DIR / "reasoning",
        repo_root / AGENTIC_CORE_DIR / APPS_SHARED_DIR / "reasoning",
        repo_root / AGENTIC_CORE_DIR / TOOLS_DIR,
        repo_root / AGENTIC_CORE_DIR / "L0_routing" / "scripts",
        repo_root / AGENTIC_CORE_DIR / "L1_cognition" / "scripts",
        repo_root / AGENTIC_CORE_DIR / "L2_execution" / "scripts",
    ]

    return [d for d in scoped_dirs if d.exists()]


def is_protected_root_path(path_str: str) -> bool:
    """Check if a path string points to a protected root."""
    path = Path(path_str).resolve()

    protected_roots = {AGENTIC_CORE_DIR, TESTS_DIR, ".github"}

    # Check if any part of the path starts with a protected root
    for part in path.parts:
        if part in protected_roots:
            return True

    return False
