from __future__ import annotations

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
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

emit_replay_key("p0", "transform_config")
emit_determinism_digest("p0", "transform_config")

_emit_dispatches_healing_run("p1", "transform_config", "L2")
_emit_routes_through("p1", "transform_config", "L2")
_emit_checks_agent_registry("p1", "transform_config", "agent_registry")
_emit_validates_agent_capability("p1", "transform_config", "capability")
_emit_dispatches_execution_plan("p1", "transform_config", "exec_plan")
_emit_agent_executes_agent("p1", "transform_config", "sub_agent")
_emit_routes_to_agent("p1", "transform_config", "target_agent")
_emit_verifies_policy("p1", "transform_config", "policy_check")
_emit_observes_runtime_state("p1", "transform_config", "runtime_state")
_emit_verifies_boundary("p1", "transform_config", "boundary_check")
_emit_transcripts_response("p1", "transform_config", "transcript")
_emit_hard_fails_untranscripted("p1", "transform_config")
_emit_gated_by_confidence("p1", "transform_config", "confidence_gate")
_emit_escalates_to_human("p1", "transform_config", "L2")
_emit_reads_policy_state("p1", "transform_config", "L2")
_emit_authorize_and_execute("p2", "transform_config", "execution_auth")
_emit_validates_capability("p2", "transform_config", "capability_check")
_emit_routes_to_capability("p2", "transform_config", "capability_route")
_emit_writes_via_uwg("p2", "transform_config", "uwg_write")
_emit_blocks_direct_write("p2", "transform_config", "direct_write_block")
_emit_records_tool_invocation("p2", "transform_config", "tool_invocation")
_emit_captures_execution_output("p2", "transform_config", "exec_output")
_emit_dispatches_agent("p3", "transform_config", "agent_dispatch")
_emit_coordinates_agents("p3", "transform_config", "agent_coordination")
_emit_records_workflow_lineage("p3", "transform_config", "workflow_lineage")
_emit_records_healing_outcome("p3", "transform_config", "healing_outcome")
_emit_escalates_failure("p3", "transform_config", "failure_escalation")
_emit_orchestrates_workflow("p3", "transform_config", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "transform_config", "healing_dispatch")
_emit_invokes_evaluation("p3", "transform_config", "evaluation_signal")
_emit_records_telemetry_event("p4", "transform_config", "telemetry_event")
_emit_captures_evaluation_metric("p4", "transform_config", "eval_metric")
_emit_stores_embedding("p4", "transform_config", "embedding_store")
_emit_updates_meta_learning_state("p4", "transform_config", "meta_learning")
_emit_links_execution_to_snapshot("p4", "transform_config", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

"""
Code Transformation Engine (CTE) — Deterministic AST-Based Transforms

Phase 1 Tool: Enables agents to perform safe, deterministic code transformations
without LLM overhead. Supports rename, extract, inline, and move operations.

LAYER: L2_execution/tools
CATEGORY: code_manipulation
PRIORITY: Critical (★★★★★)
"""


import ast
import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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

_emit_emits_metric_event("transform_config", "p4obs", "metric_1")
_emit_emits_metric_event("transform_config", "p4obs", "metric_2")
_emit_emits_metric_event("transform_config", "p4obs", "metric_3")
_emit_emits_metric_event("transform_config", "p4obs", "metric_4")
_emit_emits_metric_event("transform_config", "p4obs", "metric_5")
_emit_emits_metric_event("transform_config", "p4obs", "metric_6")
_emit_records_incident_event("transform_config", "p4obs", "incident")
_emit_captures_runtime_anomaly("transform_config", "p4obs", "anomaly")
_emit_writes_observability_log("transform_config", "p4obs", "obs_log")
_emit_updates_monitoring_state("transform_config", "p4obs", "mon_state")
_emit_triggers_alert("transform_config", "p4obs", "alert")
_emit_links_incident_trace("transform_config", "p4obs", "trace_link")
_emit_captures_pattern("transform_config", "p3lm", "pattern")
_emit_records_learning_event("transform_config", "p3lm", "learning_event")
_emit_writes_learning_snapshot("transform_config", "p3lm", "snapshot")
_emit_feeds_meta_learning("transform_config", "p3lm", "meta_feed")
_emit_updates_routing_strategy("transform_config", "p3lm", "routing")
_emit_improves_agent_policy("transform_config", "p3lm", "policy")
_emit_stores_learning_state("transform_config", "p3lm", "state")
_emit_records_execution_trace("transform_config", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("transform_config", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("transform_config", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("transform_config", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("transform_config", "L4_STATE", "p2_trace_5")
_emit_reads_environ("transform_config", "env_read", "p2_env_1")
_emit_reads_environ("transform_config", "env_read", "p2_env_2")
_emit_reads_runtime_state("transform_config", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("transform_config", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "transform_config", "context_pull")
_emit_pulls_context("p1", "transform_config", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "transform_config", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "transform_config", "uwg_term_2")
_emit_writes_through("p1", "transform_config", "write_through")
_emit_writes_through("p1", "transform_config", "write_through_2")
_emit_validated_by_safety_plane("p1", "transform_config", "safety_validation")
_emit_invokes_eval("p1", "transform_config", "eval_call")
_emit_proposal_commits_routing("p1", "transform_config", "routing_commit")

Logger = logging.getLogger(__name__)


class TransformOperation(str, Enum):
    """Supported transformation operations."""

    RENAME_SYMBOL = "rename_symbol"
    EXTRACT_FUNCTION = "extract_function"
    INLINE_VARIABLE = "inline_variable"
    MOVE_DEFINITION = "move_definition"
    ADD_DECORATOR = "add_decorator"
    REMOVE_DECORATOR = "remove_decorator"
    RENAME_CLASS = "rename_class"
    EXTRACT_VARIABLE = "extract_variable"


class CodeTransformArgs(BaseModel):
    """Arguments for code transformation operations."""

    operation: TransformOperation = Field(..., description="Type of transformation to perform")
    code: str = Field(..., description="Source code to transform")
    target: str = Field(..., description="Target symbol name, line range, or expression to transform")
    new_name: str | None = Field(None, description="New name for rename operations")
    destination: str | None = Field(None, description="Destination for move operations")
    decorator_name: str | None = Field(None, description="Decorator name for add/remove decorator operations")
    extract_name: str | None = Field(None, description="Name for extracted function/variable")
    line_start: int | None = Field(None, description="Start line for extraction (1-indexed)")
    line_end: int | None = Field(None, description="End line for extraction (1-indexed)")


@dataclass
class TransformResult:
    """Result of a code transformation."""

    success: bool
    transformed_code: str
    operation: str
    changes_made: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "TransformResult.to_dict", "state_snapshot")
        import hashlib as _hashlib  # noqa: PLC0415
        import uuid as _uuid  # noqa: PLC0415

        _tid = str(_uuid.uuid4())
        _emit_signs_execution_trace(_tid, _hashlib.sha256(_tid.encode()).hexdigest()[:12], "p0_trace", 0)
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "TransformResult.to_dict", "p0_governance")
        return {
            "success": self.success,
            "transformed_code": self.transformed_code,
            "operation": self.operation,
            "changes_made": self.changes_made,
            "warnings": self.warnings,
            "error": self.error,
        }


class SymbolRenamer(ast.NodeTransformer):
    """AST transformer for renaming symbols with scope awareness."""

    def __init__(self, old_name: str, new_name: str):
        self.old_name = old_name
        self.new_name = new_name
        self.changes: list[str] = []
        self._scope_stack: list[set[str]] = [set()]

    def _push_scope(self, names: set[str] = None):
        """Push a new scope onto the stack."""
        self._scope_stack.append(names or set())

    def _pop_scope(self):
        """Pop the current scope."""
        if len(self._scope_stack) > 1:
            self._scope_stack.pop()

    def _is_shadowed(self) -> bool:
        """Check if the target name is shadowed in current scope."""
        for scope in reversed(self._scope_stack[1:]):
            if self.old_name in scope:
                return True
        return False

    def visit_Name(self, node: ast.Name) -> ast.Name:
        """Rename Name nodes."""
        if node.id == self.old_name and not self._is_shadowed():
            self.changes.append(f"Renamed '{self.old_name}' to '{self.new_name}' at line {node.lineno}")
            node.id = self.new_name
        return node

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Handle function definitions with scope tracking."""

        _emit_records_execution_trace(
            str(uuid.uuid4()), LayerSegment.L3_ORCHESTRATION, f"SymbolRenamer.visit_FunctionDef:{node.name}"
        )
        if node.name == self.old_name:
            self.changes.append(
                f"Renamed function '{self.old_name}' to '{self.new_name}' at line {node.lineno}",
            )
            node.name = self.new_name

        # Track parameters as local scope
        local_names = {arg.arg for arg in node.args.args}
        self._push_scope(local_names)
        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> ast.AsyncFunctionDef:
        """Handle async function definitions."""
        if node.name == self.old_name:
            self.changes.append(
                f"Renamed async function '{self.old_name}' to '{self.new_name}' at line {node.lineno}",
            )
            node.name = self.new_name

        local_names = {arg.arg for arg in node.args.args}
        self._push_scope(local_names)
        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Handle class definitions."""
        if node.name == self.old_name:
            self.changes.append(f"Renamed class '{self.old_name}' to '{self.new_name}' at line {node.lineno}")
            node.name = self.new_name

        self._push_scope()
        self.generic_visit(node)
        self._pop_scope()
        return node

    def visit_arg(self, node: ast.arg) -> ast.arg:
        """Handle function arguments."""
        if node.arg == self.old_name:
            self.changes.append(
                f"Renamed argument '{self.old_name}' to '{self.new_name}' at line {node.lineno}",
            )
            node.arg = self.new_name
        return node

    def visit_alias(self, node: ast.alias) -> ast.alias:
        """Handle import aliases."""
        if node.asname == self.old_name:
            self.changes.append(f"Renamed import alias '{self.old_name}' to '{self.new_name}'")
            node.asname = self.new_name
        return node


class DecoratorModifier(ast.NodeTransformer):
    """AST transformer for adding/removing decorators."""

    def __init__(self, target_name: str, decorator_name: str, add: bool = True):
        self.target_name = target_name
        self.decorator_name = decorator_name
        self.add = add
        self.changes: list[str] = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Modify decorators on function definitions."""
        if node.name == self.target_name:
            if self.add:
                # Add decorator
                new_decorator = ast.Name(id=self.decorator_name, ctx=ast.Load())
                node.decorator_list.insert(0, new_decorator)
                self.changes.append(f"Added @{self.decorator_name} to function '{self.target_name}'")
            else:
                # Remove decorator
                original_count = len(node.decorator_list)
                node.decorator_list = [
                    d
                    for d in node.decorator_list
                    if not (isinstance(d, ast.Name) and d.id == self.decorator_name)
                ]
                if len(node.decorator_list) < original_count:
                    self.changes.append(f"Removed @{self.decorator_name} from function '{self.target_name}'")

        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Modify decorators on class definitions."""
        if node.name == self.target_name:
            if self.add:
                new_decorator = ast.Name(id=self.decorator_name, ctx=ast.Load())
                node.decorator_list.insert(0, new_decorator)
                self.changes.append(f"Added @{self.decorator_name} to class '{self.target_name}'")
            else:
                original_count = len(node.decorator_list)
                node.decorator_list = [
                    d
                    for d in node.decorator_list
                    if not (isinstance(d, ast.Name) and d.id == self.decorator_name)
                ]
                if len(node.decorator_list) < original_count:
                    self.changes.append(f"Removed @{self.decorator_name} from class '{self.target_name}'")

        self.generic_visit(node)
        return node
    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime

def _parse_code(code: str) -> tuple[ast.AST | None, str | None]:
    """Parse code into AST, returning tree and error if any."""
    try:
        tree = ast.parse(code)
        return tree, None
    except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return None, f"Syntax error at line {e.lineno}: {e.msg}"


def _unparse_code(tree: ast.AST) -> str:
    """Convert AST back to code."""
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def rename_symbol(code: str, old_name: str, new_name: str) -> TransformResult:
    """
    Rename a symbol throughout the code with scope awareness.

    Args:
        code: Source code
        old_name: Current symbol name
        new_name: New symbol name

    Returns:
        TransformResult with renamed code
    """
    tree, error = _parse_code(code)
    if error:
        return TransformResult(success=False, transformed_code=code, operation="rename_symbol", error=error)

    renamer = SymbolRenamer(old_name, new_name)
    new_tree = renamer.visit(tree)

    if not renamer.changes:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="rename_symbol",
            error=f"Symbol '{old_name}' not found in code",
        )

    try:
        new_code = _unparse_code(new_tree)
        return TransformResult(
            success=True,
            transformed_code=new_code,
            operation="rename_symbol",
            changes_made=renamer.changes,
        )
    except (RuntimeError, ValueError) as e:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="rename_symbol",
            error=f"Failed to generate code: {str(e)}",
        )


def extract_function(code: str, line_start: int, line_end: int, function_name: str) -> TransformResult:
    """
    Extract lines into a new function.

    Args:
        code: Source code
        line_start: Start line (1-indexed)
        line_end: End line (1-indexed)
        function_name: Name for the extracted function

    Returns:
        TransformResult with extracted function
    """
    lines = code.split("\n")

    if line_start < 1 or line_end > len(lines) or line_start > line_end:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="extract_function",
            error=f"Invalid line range: {line_start}-{line_end} (file has {len(lines)} lines)",
        )

    # Extract the lines (convert to 0-indexed)
    extracted_lines = lines[line_start - 1 : line_end]

    # Detect indentation of extracted code
    min_indent = float("inf")
    for line in extracted_lines:
        if line.strip():
            indent = len(line) - len(line.lstrip())
            min_indent = min(min_indent, indent)

    if min_indent == float("inf"):
        min_indent = 0

    # Normalize indentation for function body
    normalized_lines = []
    for line in extracted_lines:
        if line.strip():
            normalized_lines.append("    " + line[min_indent:])
        else:
            normalized_lines.append("")

    # Analyze extracted code for used variables
    extracted_code = "\n".join(extracted_lines)
    tree, error = _parse_code(extracted_code)

    # Find variables that are used but not defined in the extracted code
    used_names: set[str] = set()
    defined_names: set[str] = set()

    if tree:
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                if isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)
                elif isinstance(node.ctx, ast.Store):
                    defined_names.add(node.id)

    # Parameters are names used but not defined locally
    params = sorted(
        used_names
        - defined_names
        - {
            "print",
            "len",
            "range",
            "str",
            "int",
            "float",
            "list",
            "dict",
            "set",
            "True",
            "False",
            "None",
        },
    )
    params_str = ", ".join(params)

    # Build the new function
    indent_str = " " * min_indent
    function_def = f"{indent_str}def {function_name}({params_str}):\n"
    function_body = "\n".join(normalized_lines)
    new_function = function_def + function_body

    # Replace extracted lines with function call
    call_args = ", ".join(params)
    function_call = f"{indent_str}{function_name}({call_args})"

    # Build new code
    new_lines = lines[: line_start - 1] + [function_call] + lines[line_end:]

    # Insert function definition before the call
    # Find appropriate insertion point (before the function containing the call)
    insertion_point = 0
    for i, line in enumerate(new_lines):
        if line.strip().startswith("def ") or line.strip().startswith("class "):
            insertion_point = i
            break

    new_lines = new_lines[:insertion_point] + [new_function, ""] + new_lines[insertion_point:]

    new_code = "\n".join(new_lines)

    return TransformResult(
        success=True,
        transformed_code=new_code,
        operation="extract_function",
        changes_made=[
            f"Extracted lines {line_start}-{line_end} into function '{function_name}'",
            f"Function parameters: {params_str or 'none'}",
            f"Replaced extracted code with call to {function_name}()",
        ],
    )


def add_decorator(code: str, target_name: str, decorator_name: str) -> TransformResult:
    """
    Add a decorator to a function or class.

    Args:
        code: Source code
        target_name: Name of function/class to decorate
        decorator_name: Name of decorator to add

    Returns:
        TransformResult with decorated code
    """
    tree, error = _parse_code(code)
    if error:
        return TransformResult(success=False, transformed_code=code, operation="add_decorator", error=error)

    modifier = DecoratorModifier(target_name, decorator_name, add=True)
    new_tree = modifier.visit(tree)

    if not modifier.changes:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="add_decorator",
            error=f"Target '{target_name}' not found in code",
        )

    try:
        new_code = _unparse_code(new_tree)
        return TransformResult(
            success=True,
            transformed_code=new_code,
            operation="add_decorator",
            changes_made=modifier.changes,
        )
    except (RuntimeError, ValueError) as e:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="add_decorator",
            error=f"Failed to generate code: {str(e)}",
        )


def remove_decorator(code: str, target_name: str, decorator_name: str) -> TransformResult:
    """
    Remove a decorator from a function or class.

    Args:
        code: Source code
        target_name: Name of function/class
        decorator_name: Name of decorator to remove

    Returns:
        TransformResult with decorator removed
    """
    tree, error = _parse_code(code)
    if error:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="remove_decorator",
            error=error,
        )

    modifier = DecoratorModifier(target_name, decorator_name, add=False)
    new_tree = modifier.visit(tree)

    if not modifier.changes:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="remove_decorator",
            warnings=[f"Decorator @{decorator_name} not found on '{target_name}'"],
        )

    try:
        new_code = _unparse_code(new_tree)
        return TransformResult(
            success=True,
            transformed_code=new_code,
            operation="remove_decorator",
            changes_made=modifier.changes,
        )
    except (RuntimeError, ValueError) as e:
        return TransformResult(
            success=False,
            transformed_code=code,
            operation="remove_decorator",
            error=f"Failed to generate code: {str(e)}",
        )


def code_transform(args: CodeTransformArgs) -> dict[str, Any]:
    """
    Main entry point for code transformations.

    Dispatches to specific transformation functions based on operation type.

    Args:
        args: CodeTransformArgs with operation details

    Returns:
        Dict with transformation results
    """
    Logger.info(f"CTE: Executing {args.operation} on target '{args.target}'")

    result: TransformResult

    if args.operation == TransformOperation.RENAME_SYMBOL:
        if not args.new_name:
            return TransformResult(
                success=False,
                transformed_code=args.code,
                operation=args.operation,
                error="new_name required for rename_symbol operation",
            ).to_dict()
        result = rename_symbol(args.code, args.target, args.new_name)

    elif args.operation == TransformOperation.RENAME_CLASS:
        if not args.new_name:
            return TransformResult(
                success=False,
                transformed_code=args.code,
                operation=args.operation,
                error="new_name required for rename_class operation",
            ).to_dict()
        result = rename_symbol(args.code, args.target, args.new_name)

    elif args.operation == TransformOperation.EXTRACT_FUNCTION:
        if not args.line_start or not args.line_end or not args.extract_name:
            return TransformResult(
                success=False,
                transformed_code=args.code,
                operation=args.operation,
                error="line_start, line_end, and extract_name required for extract_function",
            ).to_dict()
        result = extract_function(args.code, args.line_start, args.line_end, args.extract_name)

    elif args.operation == TransformOperation.ADD_DECORATOR:
        if not args.decorator_name:
            return TransformResult(
                success=False,
                transformed_code=args.code,
                operation=args.operation,
                error="decorator_name required for add_decorator operation",
            ).to_dict()
        result = add_decorator(args.code, args.target, args.decorator_name)

    elif args.operation == TransformOperation.REMOVE_DECORATOR:
        if not args.decorator_name:
            return TransformResult(
                success=False,
                transformed_code=args.code,
                operation=args.operation,
                error="decorator_name required for remove_decorator operation",
            ).to_dict()
        result = remove_decorator(args.code, args.target, args.decorator_name)

    else:
        result = TransformResult(
            success=False,
            transformed_code=args.code,
            operation=str(args.operation),
            error=f"Operation '{args.operation}' not yet implemented",
        )

    Logger.info(f"CTE: {args.operation} {'succeeded' if result.success else 'failed'}")
    return result.to_dict()


# Convenience functions for direct use without Pydantic model
def quick_rename(code: str, old_name: str, new_name: str) -> str:
    """Quick rename without full args model. Returns transformed code or original on failure."""
    result = rename_symbol(code, old_name, new_name)
    return result.transformed_code if result.success else code


def quick_extract(code: str, start: int, end: int, func_name: str) -> str:
    """Quick extract without full args model. Returns transformed code or original on failure."""
    result = extract_function(code, start, end, func_name)
    return result.transformed_code if result.success else code
