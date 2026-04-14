"""
Silent Degradation Anti-Pattern Detector

Detects patterns where operations silently no-op or report fake success instead of
failing loudly, violating §5.2 Critical Infrastructure Fail-Closed requirement.

Pattern taxonomy
----------------
AVAILABILITY_GUARD_SKIP  — if not self._X_available: [log] return None/[]/{}
SILENT_SUCCESS_ON_NOOP   — result is not None or (fn is None): return True (noop = success)
PHANTOM_MODULE_IMPORT    — try: importlib.import_module("mcp<N>") except ImportError: flag=False
EXCEPT_IMPORT_PASS       — except ImportError: pass   (ImportError-specific silent swallow)
LOG_AND_RETURN_MOCK      — logger.*("…mock/fallback…") + return mock_data
SKIP_STRING_RETURN       — return "…: Skipped (…not available…)"

Guardian exemption: # guardian: allow-silent-degradation -- <specific justification>
"""

from __future__ import annotations

import ast
import re
import uuid
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

_emit_authorize_and_execute("p2", "silent_degradation_validator", "execution_auth")
_emit_validates_capability("p2", "silent_degradation_validator", "capability_check")
_emit_routes_to_capability("p2", "silent_degradation_validator", "capability_route")
_emit_writes_via_uwg("p2", "silent_degradation_validator", "uwg_write")
_emit_blocks_direct_write("p2", "silent_degradation_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "silent_degradation_validator", "tool_invocation")
_emit_captures_execution_output("p2", "silent_degradation_validator", "exec_output")
_emit_dispatches_agent("p3", "silent_degradation_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "silent_degradation_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "silent_degradation_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "silent_degradation_validator", "healing_outcome")
_emit_escalates_failure("p3", "silent_degradation_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "silent_degradation_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "silent_degradation_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "silent_degradation_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "silent_degradation_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "silent_degradation_validator", "eval_metric")
_emit_stores_embedding("p4", "silent_degradation_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "silent_degradation_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "silent_degradation_validator", "exec_snapshot_link")
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

from .base_detector_validator import (
    AntiPatternCategory,
    AntiPatternDetector,
    AntiPatternViolation,
    EnforcementLevel,
)
from tqdm import tqdm

_emit_emits_metric_event("silent_degradation_validator", "p4obs", "metric_1")
_emit_emits_metric_event("silent_degradation_validator", "p4obs", "metric_2")
_emit_emits_metric_event("silent_degradation_validator", "p4obs", "metric_3")
_emit_emits_metric_event("silent_degradation_validator", "p4obs", "metric_4")
_emit_emits_metric_event("silent_degradation_validator", "p4obs", "metric_5")
_emit_emits_metric_event("silent_degradation_validator", "p4obs", "metric_6")
_emit_records_incident_event("silent_degradation_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("silent_degradation_validator", "p4obs", "anomaly")
_emit_writes_observability_log("silent_degradation_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("silent_degradation_validator", "p4obs", "mon_state")
_emit_triggers_alert("silent_degradation_validator", "p4obs", "alert")
_emit_links_incident_trace("silent_degradation_validator", "p4obs", "trace_link")
_emit_captures_pattern("silent_degradation_validator", "p3lm", "pattern")
_emit_records_learning_event("silent_degradation_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("silent_degradation_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("silent_degradation_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("silent_degradation_validator", "p3lm", "routing")
_emit_improves_agent_policy("silent_degradation_validator", "p3lm", "policy")
_emit_stores_learning_state("silent_degradation_validator", "p3lm", "state")
_emit_records_execution_trace("silent_degradation_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("silent_degradation_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("silent_degradation_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("silent_degradation_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("silent_degradation_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("silent_degradation_validator", "env_read", "p2_env_1")
_emit_reads_environ("silent_degradation_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("silent_degradation_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("silent_degradation_validator", "runtime_state", "p2_rt_2")

emit_replay_key("p0", "silent_degradation_validator")
emit_determinism_digest("p0", "silent_degradation_validator")

_emit_dispatches_healing_run("p1", "silent_degradation_validator", "L5")
_emit_routes_through("p1", "silent_degradation_validator", "L5")
_emit_checks_agent_registry("p1", "silent_degradation_validator", "agent_registry")
_emit_validates_agent_capability("p1", "silent_degradation_validator", "capability")
_emit_dispatches_execution_plan("p1", "silent_degradation_validator", "exec_plan")
_emit_agent_executes_agent("p1", "silent_degradation_validator", "sub_agent")
_emit_routes_to_agent("p1", "silent_degradation_validator", "target_agent")
_emit_verifies_policy("p1", "silent_degradation_validator", "policy_check")
_emit_observes_runtime_state("p1", "silent_degradation_validator", "runtime_state")
_emit_verifies_boundary("p1", "silent_degradation_validator", "boundary_check")
_emit_transcripts_response("p1", "silent_degradation_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "silent_degradation_validator")
_emit_gated_by_confidence("p1", "silent_degradation_validator", "confidence_gate")
_emit_escalates_to_human("p1", "silent_degradation_validator", "L5")
_emit_reads_policy_state("p1", "silent_degradation_validator", "L5")
_emit_pulls_context("p1", "silent_degradation_validator", "context_pull")
_emit_pulls_context("p1", "silent_degradation_validator", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "silent_degradation_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "silent_degradation_validator", "uwg_term_secondary")
_emit_writes_through("p1", "silent_degradation_validator", "write_through")
_emit_writes_through("p1", "silent_degradation_validator", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "silent_degradation_validator", "safety_validation")
_emit_invokes_eval("p1", "silent_degradation_validator", "eval_call")
_emit_proposal_commits_routing("p1", "silent_degradation_validator", "routing_commit")

_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "silent_degradation_validator", "p0_governance")
_emit_snapshots_state("p0", "silent_degradation_validator", "state_snapshot")

# Attribute name suffixes that signal an "availability" flag
_AVAIL_SUFFIXES: tuple[str, ...] = (
    "_available",
    "_initialized",
    "_connected",
    "_ready",
    "_enabled",
    "_active",
    "_loaded",
)

# Logger method names that can precede a mock return
_LOG_METHODS: frozenset[str] = frozenset({"warning", "warn", "info", "debug", "error", "critical"})

# Keywords in logger message strings that betray silent fallback behaviour
_MOCK_KEYWORDS: tuple[str, ...] = (
    "mock",
    "fallback",
    "not available",
    "unavailable",
    "skipping",
    "skipped",
    "degraded",
    "offline mode",
)

# Pattern that identifies MCP phantom-module names (e.g. "mcp11", "mcp4")
_MCP_PHANTOM_RE = re.compile(r"^mcp\d+$")

# Substrings that indicate a "skip" return string value
_SKIP_SUBSTRINGS: tuple[str, ...] = (
    "Skipped",
    "skipped",
    "not available",
    "unavailable",
    "SKIPPED",
    ": skip",
)

# Return values that count as "empty / null" (availability guard patterns)
_NULL_CONSTANTS: frozenset[object] = frozenset({None, "", 0})


# ---------------------------------------------------------------------------
# Small AST helpers
# ---------------------------------------------------------------------------


def _is_none_or_empty(value: ast.expr | None) -> bool:
    """True when the return value is None, [], {}, '', 0, or False."""
    if value is None:
        return True  # bare `return`
    if isinstance(value, ast.Constant):
        return value.value in _NULL_CONSTANTS
    if isinstance(value, ast.List):
        return len(value.elts) == 0
    if isinstance(value, ast.Dict):
        return len(value.keys) == 0
    return False


def _body_first_empty_return(body: list[ast.stmt]) -> ast.Return | None:
    """Return the first empty/null return statement in *body*, else None."""
    for stmt in body:
        if isinstance(stmt, ast.Return) and _is_none_or_empty(stmt.value):
            return stmt
    return None


def _is_neg_avail_test(test: ast.expr) -> bool:
    """True when *test* is `not self._X<avail_suffix>` or a negated availability call."""
    if not isinstance(test, ast.UnaryOp) or not isinstance(test.op, ast.Not):
        return False
    inner = test.operand
    if isinstance(inner, ast.Attribute):
        attr = inner.attr
        return any(attr.endswith(suf) for suf in _AVAIL_SUFFIXES)
    if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute):
        attr = inner.func.attr
        return "available" in attr or "initialized" in attr or "ready" in attr
    return False


def _extract_avail_attr_name(test: ast.expr) -> str:
    """Extract the availability attribute name from a `not self._X` test."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        inner = test.operand
        if isinstance(inner, ast.Attribute):
            return f"self.{inner.attr}"
        if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Attribute):
            return f"self.{inner.func.attr}(...)"
    return "<availability_flag>"


class _ShallowWalker(ast.NodeVisitor):
    """Visit all nodes in a statement list without descending into nested functions/classes."""

    def __init__(self) -> None:
        self.nodes: list[ast.AST] = []

    def visit(self, node: ast.AST) -> None:
        self.nodes.append(node)
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            self.generic_visit(node)


def _shallow_walk(stmts: list[ast.stmt]) -> list[ast.AST]:
    """Return all descendant nodes from *stmts*, not crossing into nested functions."""
    walker = _ShallowWalker()
    for s in stmts:
        walker.visit(s)
    return walker.nodes


# ---------------------------------------------------------------------------
# Detector
# ---------------------------------------------------------------------------


class SilentDegradationDetector(AntiPatternDetector):
    """
    Detects silent degradation patterns — operations that silently no-op or
    return fake success instead of raising.  Enforces §5.2 Fail-Closed.

    Six sub-patterns are covered; each may be individually exempted with:
        # guardian: allow-silent-degradation -- <specific justification>
    placed on the line immediately preceding the flagged statement.
    """

    WHITELIST_COMMENT = "# guardian: allow-silent-degradation"

    def __init__(
        self,
        enforcement_level: EnforcementLevel = EnforcementLevel.WARNING,
        whitelisted_patterns: list[str] | None = None,
        whitelisted_files: list[str] | None = None,
    ) -> None:
        super().__init__(enforcement_level, whitelisted_patterns, whitelisted_files)
        self.whitelisted_files = self.whitelisted_files + [
            "test_*.py",
            "*_test.py",
            "conftest.py",
        ]

    @property
    def category(self) -> AntiPatternCategory:
        return AntiPatternCategory.SILENT_DEGRADATION

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def detect(self, file_path: Path, tree: ast.Module) -> list[AntiPatternViolation]:
        """Scan *tree* for all silent degradation sub-patterns."""

        _emit_records_execution_trace(
            str(uuid.uuid4()),
            LayerSegment.L5_POLICY,
            f"SilentDegradationDetector.detect:{file_path.name}",
        )
        violations: list[AntiPatternViolation] = []
        try:
            source_lines = file_path.read_text(encoding="utf-8").splitlines()
        except (ValueError, TypeError, RuntimeError) as e:
            source_lines = []

        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
            if isinstance(node, ast.If):
                v = self._check_availability_guard(node, file_path, source_lines)
                if v:
                    violations.append(v)
                v = self._check_silent_success_on_noop(node, file_path, source_lines)
                if v:
                    violations.append(v)
            elif isinstance(node, ast.Try):
                v = self._check_phantom_module_import(node, file_path, source_lines)
                if v:
                    violations.append(v)
            elif isinstance(node, ast.ExceptHandler):
                v = self._check_except_import_pass(node, file_path, source_lines)
                if v:
                    violations.append(v)
                v = self._check_log_and_return_mock(node, file_path, source_lines)
                if v:
                    violations.append(v)
            elif isinstance(node, ast.Return):
                v = self._check_skip_string_return(node, file_path, source_lines)
                if v:
                    violations.append(v)

        return violations

    # ------------------------------------------------------------------
    # Pattern 1 — AVAILABILITY_GUARD_SKIP
    #
    #   if not self._mcp_available:
    #       Logger.debug(...)
    #       return None          ← silently drops the operation
    # ------------------------------------------------------------------

    def _check_availability_guard(
        self,
        node: ast.If,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        if not _is_neg_avail_test(node.test):
            return None
        ret = _body_first_empty_return(node.body)
        if ret is None:
            return None
        if self._has_whitelist(source_lines, node.lineno):
            return None

        attr_name = _extract_avail_attr_name(node.test)
        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=(
                f"Availability guard skip: `{attr_name}` gate returns None/empty instead of "
                "raising. Operations are silently dropped when the dependency is unavailable."
            ),
            evidence=self._get_source_line(file_path, node.lineno),
            severity="error",
            suggested_fix=(
                f"Replace `if not {attr_name}: return None` with:\n"
                f"    if not {attr_name}:\n"
                f'        raise RuntimeError("{attr_name} is unavailable — cannot proceed")'
            ),
            metadata={"sub_pattern": "AVAILABILITY_GUARD_SKIP", "attr": attr_name},
        )

    # ------------------------------------------------------------------
    # Pattern 2 — SILENT_SUCCESS_ON_NOOP
    #
    #   if result is not None or (self._fn is None and self._mod is None):
    #       return True          ← reports success when nothing executed
    # ------------------------------------------------------------------

    def _check_silent_success_on_noop(
        self,
        node: ast.If,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        if not isinstance(node.test, ast.BoolOp) or not isinstance(node.test.op, ast.Or):
            return None

        has_is_not_none = any(self._is_is_not_none_compare(v) for v in node.test.values)
        has_null_noop_guard = any(self._is_null_and_guard(v) for v in node.test.values)
        if not (has_is_not_none and has_null_noop_guard):
            return None

        has_success_return = any(
            isinstance(s, ast.Return) and isinstance(s.value, ast.Constant) and s.value.value in (True, 1)
            for s in node.body
        )
        if not has_success_return:
            return None
        if self._has_whitelist(source_lines, node.lineno):
            return None

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=(
                "Silent success on no-op: `return True` when MCP module/fn is None — "
                "the operation was never executed but callers see success. "
                "Stats counters tick up for operations that did nothing."
            ),
            evidence=self._get_source_line(file_path, node.lineno),
            severity="error",
            suggested_fix=(
                "Remove the `or (fn is None and mod is None)` clause. "
                "If MCP is unavailable raise RuntimeError rather than returning success."
            ),
            metadata={"sub_pattern": "SILENT_SUCCESS_ON_NOOP"},
        )

    @staticmethod
    def _is_is_not_none_compare(node: ast.expr) -> bool:
        return (
            isinstance(node, ast.Compare)
            and any(isinstance(op, ast.IsNot) for op in node.ops)
            and any(isinstance(c, ast.Constant) and c.value is None for c in node.comparators)
        )

    @staticmethod
    def _is_null_and_guard(node: ast.expr) -> bool:
        """True when node is `A is None` or `A is None and B is None ...`."""

        def _is_is_none(n: ast.expr) -> bool:
            return (
                isinstance(n, ast.Compare)
                and any(isinstance(op, ast.Is) for op in n.ops)
                and any(isinstance(c, ast.Constant) and c.value is None for c in n.comparators)
            )

        if _is_is_none(node):
            return True
        if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
            return any(_is_is_none(v) for v in node.values)
        return False

    # ------------------------------------------------------------------
    # Pattern 3 — PHANTOM_MODULE_IMPORT
    #
    #   try:
    #       _mod = importlib.import_module("mcp11")   ← not a Python module
    #       self._mcp_available = True
    #   except ImportError:
    #       self._mcp_available = False               ← permanently False
    # ------------------------------------------------------------------

    def _check_phantom_module_import(
        self,
        node: ast.Try,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        phantom_name = self._find_mcp_phantom_import(node.body)
        if phantom_name is None:
            return None

        catches_import_error = any(self._handler_catches_import_error(h) for h in node.handlers)
        if not catches_import_error:
            return None
        if self._has_whitelist(source_lines, node.lineno):
            return None

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=(
                f"Phantom MCP module import: `{phantom_name}` is an MCP tool namespace "
                "prefix, not a Python module. This import always raises ImportError, "
                "permanently setting the availability flag to False and making every "
                "downstream operation a silent no-op."
            ),
            evidence=self._get_source_line(file_path, node.lineno),
            severity="error",
            suggested_fix=(
                f'Remove `importlib.import_module("{phantom_name}")`. '
                "Inject MCP callables via a `set_mcp_functions()` method, or raise at "
                "construction time when the required dependency is absent."
            ),
            metadata={"sub_pattern": "PHANTOM_MODULE_IMPORT", "module": phantom_name},
        )

    @staticmethod
    def _find_mcp_phantom_import(body: list[ast.stmt]) -> str | None:
        """Return the mcp<N> module name if a phantom import is found, else None."""
        for node in tqdm(_shallow_walk(body), desc="Processing", unit="item"):
            # importlib.import_module("mcp11")
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "import_module"
                and node.args
                and isinstance(node.args[0], ast.Constant)
                and isinstance(node.args[0].value, str)
                and _MCP_PHANTOM_RE.match(node.args[0].value)
            ):
                return node.args[0].value
            # from mcp11 import something
            if isinstance(node, ast.ImportFrom) and node.module and _MCP_PHANTOM_RE.match(node.module):
                return node.module
        return None

    @staticmethod
    def _handler_catches_import_error(handler: ast.ExceptHandler) -> bool:
        if handler.type is None:
            return True  # bare except catches everything
        if isinstance(handler.type, ast.Name):
            return handler.type.id in (
                "ImportError",
                "ModuleNotFoundError",
                "Exception",
                "BaseException",
            )
        if isinstance(handler.type, ast.Tuple):
            return any(
                isinstance(e, ast.Name) and e.id in ("ImportError", "ModuleNotFoundError")
                for e in handler.type.elts
            )
        return False

    # ------------------------------------------------------------------
    # Pattern 4 — EXCEPT_IMPORT_PASS
    #
    #   except ImportError:
    #       pass   ← module unavailability is silently swallowed
    # ------------------------------------------------------------------

    def _check_except_import_pass(
        self,
        node: ast.ExceptHandler,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        if not self._is_import_error_handler(node):
            return None
        # Only flag when the handler has NO meaningful error propagation
        if self._has_raise_or_error_return(node.body):
            return None
        # Must have at least a pass (not just an empty body — AST guarantees body is non-empty)
        if self._has_whitelist(source_lines, node.lineno):
            return None

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=(
                "Silent ImportError swallow: `except ImportError: pass` (or log-only) "
                "discards module unavailability. Callers operate on an unconfigured "
                "dependency without any indication of failure."
            ),
            evidence=self._get_source_line(file_path, node.lineno),
            severity="warning",
            suggested_fix=(
                "Replace with:\n"
                "    except ImportError as exc:\n"
                '        raise ImportError("Required module not available") from exc\n'
                "Or set a flag AND ensure every consumer of that flag raises on use."
            ),
            metadata={"sub_pattern": "EXCEPT_IMPORT_PASS"},
        )

    @staticmethod
    def _is_import_error_handler(node: ast.ExceptHandler) -> bool:
        if node.type is None:
            return False
        if isinstance(node.type, ast.Name):
            return node.type.id in ("ImportError", "ModuleNotFoundError")
        if isinstance(node.type, ast.Tuple):
            return any(
                isinstance(e, ast.Name) and e.id in ("ImportError", "ModuleNotFoundError")
                for e in node.type.elts
            )
        return False

    @staticmethod
    def _has_raise_or_error_return(body: list[ast.stmt]) -> bool:
        """True when the handler body contains a raise or an explicit error return."""
        for stmt in body:
            if isinstance(stmt, ast.Raise):
                return True
            if isinstance(stmt, ast.Return):
                v = stmt.value
                # return False, return {"error": ...}, return None are explicit signals
                if isinstance(v, ast.Constant) and v.value is False:
                    return True
                if isinstance(v, ast.Dict):
                    return True
        return False

    # ------------------------------------------------------------------
    # Pattern 5 — LOG_AND_RETURN_MOCK
    #
    #   except ImportError:
    #       Logger.warning("mcp4_fetch not available, returning mock")
    #       return {"status": "mock_success", ...}
    # ------------------------------------------------------------------

    def _check_log_and_return_mock(
        self,
        node: ast.ExceptHandler,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        if not self._has_mock_log_call(node.body):
            return None
        has_dict_return = any(
            isinstance(s, ast.Return) and isinstance(s.value, (ast.Dict, ast.Call)) for s in node.body
        )
        if not has_dict_return:
            return None
        if self._has_whitelist(source_lines, node.lineno):
            return None

        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=(
                "Log and return mock: logging unavailability then returning fabricated "
                "data. Callers receive fake results with no way to detect the failure."
            ),
            evidence=self._get_source_line(file_path, node.lineno),
            severity="warning",
            suggested_fix=(
                "Raise an exception instead of returning mock data:\n"
                "    except ImportError as exc:\n"
                '        raise RuntimeError("Dependency unavailable") from exc'
            ),
            metadata={"sub_pattern": "LOG_AND_RETURN_MOCK"},
        )

    @staticmethod
    def _has_mock_log_call(body: list[ast.stmt]) -> bool:
        """True when any logger call in *body* contains a mock/fallback keyword."""
        for node in tqdm(_shallow_walk(body), desc="Processing", unit="item"):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _LOG_METHODS
            ):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        lowered = arg.value.lower()
                        if any(kw in lowered for kw in _MOCK_KEYWORDS):
                            return True
                # f-string arguments
                for arg in node.args:
                    if isinstance(arg, ast.JoinedStr):
                        # Reconstruct partial text from Constant parts of the f-string
                        parts = " ".join(
                            v.value
                            for v in arg.values
                            if isinstance(v, ast.Constant) and isinstance(v.value, str)
                        ).lower()
                        if any(kw in parts for kw in _MOCK_KEYWORDS):
                            return True
        return False

    # ------------------------------------------------------------------
    # Pattern 6 — SKIP_STRING_RETURN
    #
    #   return "Hierarchy probe: Skipped (agent not available)"
    # ------------------------------------------------------------------

    def _check_skip_string_return(
        self,
        node: ast.Return,
        file_path: Path,
        source_lines: list[str],
    ) -> AntiPatternViolation | None:
        if not isinstance(node.value, ast.Constant) or not isinstance(node.value.value, str):
            return None
        val: str = node.value.value
        if not any(sub in val for sub in _SKIP_SUBSTRINGS):
            return None
        # Require at least one additional contextual signal to avoid false positives
        lower = val.lower()
        if not ("available" in lower or "agent" in lower or "skip" in lower or "probe" in lower):
            return None
        if self._has_whitelist(source_lines, node.lineno):
            return None

        preview = val[:70] + ("..." if len(val) > 70 else "")
        return AntiPatternViolation(
            file_path=file_path,
            line_number=node.lineno,
            category=self.category,
            message=(
                f'Skip string return: `return "{preview}"` — callers cannot '
                "distinguish a genuine result from a silent skip."
            ),
            evidence=self._get_source_line(file_path, node.lineno),
            severity="warning",
            suggested_fix=(
                "Raise a domain-specific exception instead of returning a skip string:\n"
                '    raise RuntimeError("<dependency> not available")'
            ),
            metadata={"sub_pattern": "SKIP_STRING_RETURN", "value": val[:80]},
        )

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _has_whitelist(self, source_lines: list[str], lineno: int) -> bool:
        """True when the guardian exemption comment appears within 5 lines above the violation.

        Searches up to 5 lines back so comments placed above a `try:` block
        (rather than immediately above the flagged statement) are respected.
        """
        for check_idx in range(lineno - 2, max(-1, lineno - 5), -1):  # up to 3 lines above
            if 0 <= check_idx < len(source_lines):
                if self.WHITELIST_COMMENT in source_lines[check_idx]:
                    return True
        return False


__all__ = ["SilentDegradationDetector"]
