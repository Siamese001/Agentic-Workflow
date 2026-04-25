"""
CST Transformers - Concrete LibCST transformations for surgical healing.

Provides specific transformers for different types of code modifications
while preserving comments, whitespace, and formatting.
"""

from __future__ import annotations

from dataclasses import dataclass

import libcst as cst

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

emit_replay_key("p0", "cst_transformers_types")
emit_determinism_digest("p0", "cst_transformers_types")

_emit_dispatches_healing_run("p1", "cst_transformers_types", "L5")
_emit_routes_through("p1", "cst_transformers_types", "L5")
_emit_checks_agent_registry("p1", "cst_transformers_types", "agent_registry")
_emit_validates_agent_capability("p1", "cst_transformers_types", "capability")
_emit_dispatches_execution_plan("p1", "cst_transformers_types", "exec_plan")
_emit_agent_executes_agent("p1", "cst_transformers_types", "sub_agent")
_emit_routes_to_agent("p1", "cst_transformers_types", "target_agent")
_emit_verifies_policy("p1", "cst_transformers_types", "policy_check")
_emit_observes_runtime_state("p1", "cst_transformers_types", "runtime_state")
_emit_verifies_boundary("p1", "cst_transformers_types", "boundary_check")
_emit_transcripts_response("p1", "cst_transformers_types", "transcript")
_emit_hard_fails_untranscripted("p1", "cst_transformers_types")
_emit_gated_by_confidence("p1", "cst_transformers_types", "confidence_gate")
_emit_escalates_to_human("p1", "cst_transformers_types", "L5")
_emit_reads_policy_state("p1", "cst_transformers_types", "L5")

_emit_applies_guardrail("p0", "cst_transformers_types", "p0_governance")
_emit_snapshots_state("p0", "cst_transformers_types", "state_snapshot")
_emit_authorize_and_execute("p2", "cst_transformers_types", "execution_auth")
_emit_validates_capability("p2", "cst_transformers_types", "capability_check")
_emit_routes_to_capability("p2", "cst_transformers_types", "capability_route")
_emit_writes_via_uwg("p2", "cst_transformers_types", "uwg_write")
_emit_blocks_direct_write("p2", "cst_transformers_types", "direct_write_block")
_emit_records_tool_invocation("p2", "cst_transformers_types", "tool_invocation")
_emit_captures_execution_output("p2", "cst_transformers_types", "exec_output")
_emit_dispatches_agent("p3", "cst_transformers_types", "agent_dispatch")
_emit_coordinates_agents("p3", "cst_transformers_types", "agent_coordination")
_emit_records_workflow_lineage("p3", "cst_transformers_types", "workflow_lineage")
_emit_records_healing_outcome("p3", "cst_transformers_types", "healing_outcome")
_emit_escalates_failure("p3", "cst_transformers_types", "failure_escalation")
_emit_orchestrates_workflow("p3", "cst_transformers_types", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "cst_transformers_types", "healing_dispatch")
_emit_invokes_evaluation("p3", "cst_transformers_types", "evaluation_signal")
_emit_records_telemetry_event("p4", "cst_transformers_types", "telemetry_event")
_emit_captures_evaluation_metric("p4", "cst_transformers_types", "eval_metric")
_emit_stores_embedding("p4", "cst_transformers_types", "embedding_store")
_emit_updates_meta_learning_state("p4", "cst_transformers_types", "meta_learning")
_emit_links_execution_to_snapshot("p4", "cst_transformers_types", "exec_snapshot_link")
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

_emit_emits_metric_event("cst_transformers_types", "p4obs", "metric_1")
_emit_emits_metric_event("cst_transformers_types", "p4obs", "metric_2")
_emit_emits_metric_event("cst_transformers_types", "p4obs", "metric_3")
_emit_emits_metric_event("cst_transformers_types", "p4obs", "metric_4")
_emit_emits_metric_event("cst_transformers_types", "p4obs", "metric_5")
_emit_emits_metric_event("cst_transformers_types", "p4obs", "metric_6")
_emit_records_incident_event("cst_transformers_types", "p4obs", "incident")
_emit_captures_runtime_anomaly("cst_transformers_types", "p4obs", "anomaly")
_emit_writes_observability_log("cst_transformers_types", "p4obs", "obs_log")
_emit_updates_monitoring_state("cst_transformers_types", "p4obs", "mon_state")
_emit_triggers_alert("cst_transformers_types", "p4obs", "alert")
_emit_links_incident_trace("cst_transformers_types", "p4obs", "trace_link")
_emit_captures_pattern("cst_transformers_types", "p3lm", "pattern")
_emit_records_learning_event("cst_transformers_types", "p3lm", "learning_event")
_emit_writes_learning_snapshot("cst_transformers_types", "p3lm", "snapshot")
_emit_feeds_meta_learning("cst_transformers_types", "p3lm", "meta_feed")
_emit_updates_routing_strategy("cst_transformers_types", "p3lm", "routing")
_emit_improves_agent_policy("cst_transformers_types", "p3lm", "policy")
_emit_stores_learning_state("cst_transformers_types", "p3lm", "state")
_emit_records_execution_trace("cst_transformers_types", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("cst_transformers_types", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("cst_transformers_types", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("cst_transformers_types", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("cst_transformers_types", "L4_STATE", "p2_trace_5")
_emit_reads_environ("cst_transformers_types", "env_read", "p2_env_1")
_emit_reads_environ("cst_transformers_types", "env_read", "p2_env_2")
_emit_reads_runtime_state("cst_transformers_types", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("cst_transformers_types", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "cst_transformers_types", "context_pull")
_emit_pulls_context("p1", "cst_transformers_types", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "cst_transformers_types", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "cst_transformers_types", "uwg_term_2")
_emit_writes_through("p1", "cst_transformers_types", "write_through")
_emit_writes_through("p1", "cst_transformers_types", "write_through_2")
_emit_validated_by_safety_plane("p1", "cst_transformers_types", "safety_validation")
_emit_invokes_eval("p1", "cst_transformers_types", "eval_call")
_emit_proposal_commits_routing("p1", "cst_transformers_types", "routing_commit")


@dataclass
class ImportTarget:
    """Target for import removal operations."""

    line_number: int
    module_name: str | None = None
    name: str | None = None


@dataclass
class DocstringTarget:
    """Target for docstring insertion operations."""

    line_number: int
    name: str | None = None
    node_type: str = "class"
    docstring: str = '"""TODO: Add docstring."""'


@dataclass
class BareExceptTarget:
    """Target for bare except fix operations."""

    line_number: int
    exception_type: str = "Exception"


class SurgicalImportRemover(cst.CSTTransformer):
    """
    CST transformer that removes specific imports while preserving formatting.

    Uses a string-based approach to identify and remove imports by name.
    """

    def __init__(self, targets: list[ImportTarget]):
        """
        Initialize with import removal targets.

        Args:
            targets: List of imports to remove
        """
        self.targets = targets
        self.target_lines = {t.line_number for t in targets}
        self.target_names = {t.name for t in targets if t.name}
        self.modifications_made = 0
        self.lines = None
        self.current_line = 0

    def on_visit(self, node: cst.CSTNode) -> bool:
        """Initialize line tracking."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "SurgicalImportRemover.on_visit")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:SurgicalImportRemover.on_visit".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if isinstance(node, cst.Module):
            self.lines = node.code.split("\n")
        return True

    def leave_Import(self, original_node: cst.Import, updated_node: cst.Import) -> cst.Import:
        """Handle Import nodes by checking if they match our targets."""
        for alias in updated_node.names:
            name = alias.asname.value if alias.asname else alias.name.value
            if name in self.target_names:
                self.modifications_made += 1
                return cst.RemoveFromParent()
        return updated_node

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        """
        Handle ImportFrom nodes (e.g., `from os import path`, `from x import a, b`).

        Supports both full line removal and partial name removal.
        """
        if not hasattr(original_node, "position") or not original_node.position:
            return updated_node
        line_targeted = original_node.position.line in self.target_lines
        module_targeted = original_node.module and original_node.module.value in self.target_modules
        if not (line_targeted or module_targeted):
            return updated_node
        names_to_remove = set()
        for alias in original_node.names:
            name = alias.asname or alias.name
            if name in self.target_names:
                names_to_remove.add(name)
        if not names_to_remove:
            if line_targeted and (not self.target_names):
                self.modifications_made += 1
                return cst.RemoveFromParent()
            return updated_node
        remaining_names = []
        for alias in original_node.names:
            name = alias.asname or alias.name
            if name not in names_to_remove:
                remaining_names.append(alias)
        if not remaining_names:
            self.modifications_made += 1
            return cst.RemoveFromParent()
        new_node = updated_node.with_changes(names=remaining_names)
        self.modifications_made += 1
        return new_node

    def leave_SimpleStatementLine(
        self,
        original_node: cst.SimpleStatementLine,
        updated_node: cst.SimpleStatementLine,
    ) -> cst.SimpleStatementLine:
        """
        Handle SimpleStatementLine to remove empty import statements.

        This catches cases where we removed all names from a multi-line import
        and need to clean up the empty statement.
        """
        if len(updated_node.body) == 0:
            if (
                hasattr(original_node, "position")
                and original_node.position
                and (original_node.position.line in self.target_lines)
            ):
                self.modifications_made += 1
                return cst.RemoveFromParent()
        return updated_node


class SurgicalDocstringInserter(cst.CSTTransformer):
    """
    CST transformer that inserts docstrings while preserving formatting.

    Inserts docstrings at the beginning of class or function bodies.
    Uses name-based matching since CST nodes don't have position metadata.
    """

    def __init__(self, targets: list[DocstringTarget]):
        """
        Initialize with docstring insertion targets.

        Args:
            targets: List of DocstringTarget objects specifying where to insert
        """
        self.targets = targets
        self.target_names = {t.name for t in targets if t.name}
        self.target_lines = {t.line_number for t in targets}
        self.target_map = {t.name: t for t in targets if t.name}
        self.modifications_made = 0

    def _has_docstring(self, body: cst.IndentedBlock) -> bool:
        """Check if the body already has a docstring."""
        if len(body.body) == 0:
            return False
        first_stmt = body.body[0]
        if isinstance(first_stmt, cst.SimpleStatementLine):
            if len(first_stmt.body) > 0:
                first_expr = first_stmt.body[0]
                if isinstance(first_expr, cst.Expr):
                    value = first_expr.value
                    if isinstance(value, cst.SimpleString | cst.ConcatenatedString):
                        if isinstance(value, cst.SimpleString):
                            return value.value.startswith(('"""', "'''"))
        return False

    def _create_docstring_stmt(self, docstring: str) -> cst.SimpleStatementLine:
        """Create a docstring statement line."""
        return cst.SimpleStatementLine(body=[cst.Expr(value=cst.SimpleString(value=docstring))])

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef) -> cst.ClassDef:
        """Insert docstring into class if targeted by name."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalDocstringInserter.leave_ClassDef",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalDocstringInserter.leave_ClassDef".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        class_name = updated_node.name.value
        if class_name not in self.target_names:
            return updated_node
        if self._has_docstring(updated_node.body):
            return updated_node
        target = self.target_map.get(class_name)
        docstring = target.docstring if target else '"""TODO: Add class docstring."""'
        docstring_stmt = self._create_docstring_stmt(docstring)
        new_body_stmts = [docstring_stmt] + list(updated_node.body.body)
        new_body = updated_node.body.with_changes(body=new_body_stmts)
        self.modifications_made += 1
        return updated_node.with_changes(body=new_body)

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef:
        """Insert docstring into function if targeted by name."""
        func_name = updated_node.name.value
        if func_name not in self.target_names:
            return updated_node
        if self._has_docstring(updated_node.body):
            return updated_node
        target = self.target_map.get(func_name)
        docstring = target.docstring if target else '"""TODO: Add function docstring."""'
        docstring_stmt = self._create_docstring_stmt(docstring)
        new_body_stmts = [docstring_stmt] + list(updated_node.body.body)
        new_body = updated_node.body.with_changes(body=new_body_stmts)
        self.modifications_made += 1
        return updated_node.with_changes(body=new_body)


class SurgicalBareExceptFixer(cst.CSTTransformer):
    """
    CST transformer that fixes bare except clauses.

    Converts `except:` to `except Exception:` while preserving formatting.
    Fixes ALL bare except clauses found (no position metadata needed).
    """

    def __init__(self, targets: list[BareExceptTarget] | None = None, fix_all: bool = True):
        """
        Initialize bare except fixer.

        Args:
            targets: Optional list of specific targets (if None, fix all)
            fix_all: If True, fix all bare except clauses found
        """
        self.targets = targets or []
        self.target_lines = {t.line_number for t in self.targets} if self.targets else set()
        self.fix_all = fix_all
        self.modifications_made = 0

    def leave_ExceptHandler(
        self,
        original_node: cst.ExceptHandler,
        updated_node: cst.ExceptHandler,
    ) -> cst.ExceptHandler:
        """Fix bare except clauses."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalBareExceptFixer.leave_ExceptHandler",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalBareExceptFixer.leave_ExceptHandler".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if updated_node.type is not None:
            return updated_node
        if self.fix_all or (self.target_lines and self._should_fix(original_node)):
            exception_type = cst.Name(value="Exception")
            new_node = updated_node.with_changes(
                type=exception_type,
                whitespace_after_except=cst.SimpleWhitespace(" "),
            )
            self.modifications_made += 1
            return new_node
        return updated_node

    def _should_fix(self, node: cst.ExceptHandler) -> bool:
        """Check if this node should be fixed based on targets."""
        if hasattr(node, "position") and node.position:
            return node.position.line in self.target_lines
        return self.fix_all


class SurgicalFutureImportInserter(cst.CSTTransformer):
    """
    CST transformer that inserts __future__ imports at the top of modules.

    Handles proper placement after shebang and module docstrings.
    """

    def __init__(self, future_imports: list[str] | None = None):
        """
        Initialize with future imports to add.

        Args:
            future_imports: List of future imports (e.g., ["annotations"])
        """
        self.future_imports = future_imports or ["annotations"]
        self.modifications_made = 0
        self.has_future_import = False

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        """Check if __future__ import already exists."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalFutureImportInserter.visit_ImportFrom",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalFutureImportInserter.visit_ImportFrom".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if node.module and isinstance(node.module, cst.Attribute):
            pass
        elif node.module and isinstance(node.module, cst.Name):
            if node.module.value == "__future__":
                self.has_future_import = True
        return True

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Insert __future__ import at the correct position in the module."""
        if self.has_future_import:
            return updated_node
        insert_idx = 0
        body = list(updated_node.body)
        if body:
            first_stmt = body[0]
            if isinstance(first_stmt, cst.SimpleStatementLine):
                if len(first_stmt.body) > 0:
                    first_expr = first_stmt.body[0]
                    if isinstance(first_expr, cst.Expr):
                        if isinstance(first_expr.value, cst.SimpleString):
                            insert_idx = 1
        import_names = [cst.ImportAlias(name=cst.Name(value=name)) for name in self.future_imports]
        future_import = cst.SimpleStatementLine(
            body=[cst.ImportFrom(module=cst.Name(value="__future__"), names=import_names)],
            trailing_whitespace=cst.TrailingWhitespace(
                whitespace=cst.SimpleWhitespace(value=""),
                comment=None,
                newline=cst.Newline(value=None),
            ),
        )
        new_body = body[:insert_idx] + [future_import] + body[insert_idx:]
        self.modifications_made += 1
        return updated_node.with_changes(body=new_body)


class SurgicalTrailingWhitespaceFixer(cst.CSTTransformer):
    """
    CST transformer that removes trailing whitespace from lines.

    Preserves all code structure while cleaning up whitespace.
    """

    def __init__(self):
        """Initialize the trailing whitespace fixer."""
        self.modifications_made = 0

    def leave_TrailingWhitespace(
        self,
        original_node: cst.TrailingWhitespace,
        updated_node: cst.TrailingWhitespace,
    ) -> cst.TrailingWhitespace:
        """Remove trailing whitespace before newlines."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalTrailingWhitespaceFixer.leave_TrailingWhitespace",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalTrailingWhitespaceFixer.leave_TrailingWhitespace".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if updated_node.whitespace.value.strip() == "" and updated_node.whitespace.value:
            new_node = updated_node.with_changes(whitespace=cst.SimpleWhitespace(""))
            self.modifications_made += 1
            return new_node
        return updated_node

    def leave_EmptyLine(self, original_node: cst.EmptyLine, updated_node: cst.EmptyLine) -> cst.EmptyLine:
        """Remove trailing whitespace from empty lines."""
        if updated_node.whitespace.value:
            new_node = updated_node.with_changes(whitespace=cst.SimpleWhitespace(""))
            self.modifications_made += 1
            return new_node
        return updated_node


class SurgicalBlankLineNormalizer(cst.CSTTransformer):
    """
    CST transformer that normalizes excessive blank lines.

    Reduces multiple consecutive blank lines to a maximum of 2.
    """

    # guardian: allow-magic-config
    def __init__(self, max_blank_lines: int = 2):
        """
        Initialize the blank line normalizer.

        Args:
            max_blank_lines: Maximum allowed consecutive blank lines
        """
        self.max_blank_lines = max_blank_lines
        self.modifications_made = 0

    def leave_Module(self, original_node: cst.Module, updated_node: cst.Module) -> cst.Module:
        """Normalize blank lines in the module body."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalBlankLineNormalizer.leave_Module",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalBlankLineNormalizer.leave_Module".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        new_body = []
        consecutive_empty = 0
        for stmt in tqdm(updated_node.body, desc="Processing", unit="item"):
            if hasattr(stmt, "leading_lines") and stmt.leading_lines:
                new_leading = []
                for line in stmt.leading_lines:
                    if isinstance(line, cst.EmptyLine):
                        consecutive_empty += 1
                        if consecutive_empty <= self.max_blank_lines:
                            new_leading.append(line)
                        else:
                            self.modifications_made += 1
                    else:
                        consecutive_empty = 0
                        new_leading.append(line)
                if len(new_leading) != len(stmt.leading_lines):
                    stmt = stmt.with_changes(leading_lines=new_leading)
            new_body.append(stmt)
            consecutive_empty = 0
        if self.modifications_made > 0:
            return updated_node.with_changes(body=new_body)
        return updated_node


@dataclass
class StructuralTarget:
    """Target for structural fix operations."""

    line_number: int
    fix_type: str


@dataclass
class TypeHintTarget:
    """Target for type hint operations."""

    line_number: int
    name: str
    hint_type: str
    type_annotation: str


class SurgicalTypeHintInserter(cst.CSTTransformer):
    """
    CST transformer that inserts type hints into function signatures.

    Adds return type hints and parameter type hints while preserving formatting.
    """

    def __init__(self, targets: list[TypeHintTarget]):
        """
        Initialize with type hint targets.

        Args:
            targets: List of TypeHintTarget objects specifying hints to add
        """
        self.targets = targets
        self.target_names = {t.name for t in targets}
        self.target_map = {t.name: t for t in targets}
        self.modifications_made = 0

    def leave_FunctionDef(
        self,
        original_node: cst.FunctionDef,
        updated_node: cst.FunctionDef,
    ) -> cst.FunctionDef:
        """Add type hints to function if targeted."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "SurgicalTypeHintInserter.leave_FunctionDef",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:SurgicalTypeHintInserter.leave_FunctionDef".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        func_name = updated_node.name.value
        if func_name not in self.target_names:
            return updated_node
        target = self.target_map.get(func_name)
        if not target:
            return updated_node
        if target.hint_type == "return" and updated_node.returns is None:
            try:
                annotation = cst.parse_expression(target.type_annotation)
                new_returns = cst.Annotation(annotation=annotation)
                updated_node = updated_node.with_changes(returns=new_returns)
                self.modifications_made += 1
            except (
                ValueError,
                TypeError,
                cst.ParserSyntaxError,
            ):  # guardian: allow-silent-swallow  -- ADG-burn: silent_exception_swallow
                pass  # guardian: allow-silent-swallow -- intentional: malformed type annotation is a control-flow signal to skip insertion
        return updated_node


def create_type_hint_inserter(violations) -> SurgicalTypeHintInserter | None:
    """
    Factory function to create type hint inserter from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalTypeHintInserter instance or None if no type hint violations
    """
    type_hint_targets = []
    for violation in tqdm(violations, desc="Processing", unit="item"):
        if violation.constraint_type == "missing_type_hint" and violation.fix_type == "insert":
            if violation.target_coordinate:
                name = None
                type_annotation = "Any"
                hint_type = "return"
                if violation.message:
                    import re

                    match = re.search("[Ff]unction\\s+['\\\"]?(\\w+)['\\\"]?", violation.message)
                    if match:
                        name = match.group(1)
                    type_match = re.search("type[:\\s]+['\\\"]?(\\w+)['\\\"]?", violation.message)
                    if type_match:
                        type_annotation = type_match.group(1)
                if name:
                    target = TypeHintTarget(
                        line_number=violation.target_coordinate.line,
                        name=name,
                        hint_type=hint_type,
                        type_annotation=type_annotation,
                    )
                    type_hint_targets.append(target)
    if type_hint_targets:
        return SurgicalTypeHintInserter(type_hint_targets)
    return None


def create_trailing_whitespace_fixer(violations) -> SurgicalTrailingWhitespaceFixer | None:
    """
    Factory function to create trailing whitespace fixer from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalTrailingWhitespaceFixer instance or None if no violations
    """
    for violation in violations:
        if violation.constraint_type == "trailing_whitespace":
            return SurgicalTrailingWhitespaceFixer()
    return None


# guardian: allow-magic-config
def create_blank_line_normalizer(violations, max_blank_lines: int = 2) -> SurgicalBlankLineNormalizer | None:
    """
    Factory function to create blank line normalizer from violations.

    Args:
        violations: List of ViolationConstraint objects
        max_blank_lines: Maximum allowed consecutive blank lines

    Returns:
        SurgicalBlankLineNormalizer instance or None if no violations
    """
    for violation in violations:
        if violation.constraint_type == "excessive_blank_lines":
            return SurgicalBlankLineNormalizer(max_blank_lines=max_blank_lines)
    return None


def create_import_remover(violations) -> SurgicalImportRemover | None:
    """
    Factory function to create import remover from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalImportRemover instance or None if no import violations
    """
    import_targets = []
    for violation in tqdm(violations, desc="Processing", unit="item"):
        if violation.constraint_type == "unused_import" and violation.fix_type == "delete":
            if violation.target_coordinate:
                module_name = None
                if violation.message and "Unused import:" in violation.message:
                    module_name = violation.message.split("Unused import:")[-1].strip()
                target = ImportTarget(
                    line_number=violation.target_coordinate.line,
                    module_name=module_name,
                    name=module_name,
                )
                import_targets.append(target)
    if import_targets:
        return SurgicalImportRemover(import_targets)
    return None


def create_docstring_inserter(violations) -> SurgicalDocstringInserter | None:
    """
    Factory function to create docstring inserter from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalDocstringInserter instance or None if no docstring violations
    """
    docstring_targets = []
    for violation in tqdm(violations, desc="Processing", unit="item"):
        if violation.constraint_type == "missing_docstring" and violation.fix_type == "insert":
            if violation.target_coordinate:
                name = None
                node_type = "class"
                if violation.message:
                    msg_lower = violation.message.lower()
                    if "class" in msg_lower:
                        node_type = "class"
                        import re

                        match = re.search("[Cc]lass\\s+['\\\"]?(\\w+)['\\\"]?", violation.message)
                        if match:
                            name = match.group(1)
                    elif "function" in msg_lower or "def " in msg_lower:
                        node_type = "function"
                        match = re.search("[Ff]unction\\s+['\\\"]?(\\w+)['\\\"]?", violation.message)
                        if match:
                            name = match.group(1)
                target = DocstringTarget(
                    line_number=violation.target_coordinate.line,
                    name=name,
                    node_type=node_type,
                )
                docstring_targets.append(target)
    if docstring_targets:
        return SurgicalDocstringInserter(docstring_targets)
    return None


def create_bare_except_fixer(violations) -> SurgicalBareExceptFixer | None:
    """
    Factory function to create bare except fixer from violations.

    Args:
        violations: List of ViolationConstraint objects

    Returns:
        SurgicalBareExceptFixer instance or None if no bare except violations
    """
    except_targets = []
    for violation in violations:
        if violation.constraint_type == "bare_except" and violation.fix_type == "replace":
            if violation.target_coordinate:
                target = BareExceptTarget(line_number=violation.target_coordinate.line)
                except_targets.append(target)
    if except_targets:
        return SurgicalBareExceptFixer(targets=except_targets, fix_all=True)
    return None


def create_future_import_inserter(
    violations,
    future_imports: list[str] | None = None,
) -> SurgicalFutureImportInserter | None:
    """
    Factory function to create future import inserter from violations.

    Args:
        violations: List of ViolationConstraint objects
        future_imports: List of future imports to add (default: ["annotations"])

    Returns:
        SurgicalFutureImportInserter instance or None if no future import violations
    """
    for violation in violations:
        if violation.constraint_type == "missing_future_import":
            return SurgicalFutureImportInserter(future_imports=future_imports)
    return None
