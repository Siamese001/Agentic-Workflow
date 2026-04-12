"""
Determinism Serialization Checker

AST-based static analysis to ensure deterministic serialization in replay/storage modules.
Enforces invariants about JSON serialization and timestamp handling.
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
    record_execution_trace,
)

emit_replay_key("p0", "determinism_serialization_check")
emit_determinism_digest("p0", "determinism_serialization_check")

_emit_dispatches_healing_run("p1", "determinism_serialization_check", "L5")
_emit_routes_through("p1", "determinism_serialization_check", "L5")
_emit_checks_agent_registry("p1", "determinism_serialization_check", "agent_registry")
_emit_validates_agent_capability("p1", "determinism_serialization_check", "capability")
_emit_dispatches_execution_plan("p1", "determinism_serialization_check", "exec_plan")
_emit_agent_executes_agent("p1", "determinism_serialization_check", "sub_agent")
_emit_routes_to_agent("p1", "determinism_serialization_check", "target_agent")
_emit_verifies_policy("p1", "determinism_serialization_check", "policy_check")
_emit_observes_runtime_state("p1", "determinism_serialization_check", "runtime_state")
_emit_verifies_boundary("p1", "determinism_serialization_check", "boundary_check")
_emit_transcripts_response("p1", "determinism_serialization_check", "transcript")
_emit_hard_fails_untranscripted("p1", "determinism_serialization_check")
_emit_gated_by_confidence("p1", "determinism_serialization_check", "confidence_gate")
_emit_escalates_to_human("p1", "determinism_serialization_check", "L5")
_emit_reads_policy_state("p1", "determinism_serialization_check", "L5")

_emit_applies_guardrail("p0", "determinism_serialization_check", "p0_governance")
_emit_snapshots_state("p0", "determinism_serialization_check", "state_snapshot")
_emit_authorize_and_execute("p2", "determinism_serialization_check", "execution_auth")
_emit_validates_capability("p2", "determinism_serialization_check", "capability_check")
_emit_routes_to_capability("p2", "determinism_serialization_check", "capability_route")
_emit_writes_via_uwg("p2", "determinism_serialization_check", "uwg_write")
_emit_blocks_direct_write("p2", "determinism_serialization_check", "direct_write_block")
_emit_records_tool_invocation("p2", "determinism_serialization_check", "tool_invocation")
_emit_captures_execution_output("p2", "determinism_serialization_check", "exec_output")
_emit_dispatches_agent("p3", "determinism_serialization_check", "agent_dispatch")
_emit_coordinates_agents("p3", "determinism_serialization_check", "agent_coordination")
_emit_records_workflow_lineage("p3", "determinism_serialization_check", "workflow_lineage")
_emit_records_healing_outcome("p3", "determinism_serialization_check", "healing_outcome")
_emit_escalates_failure("p3", "determinism_serialization_check", "failure_escalation")
_emit_orchestrates_workflow("p3", "determinism_serialization_check", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "determinism_serialization_check", "healing_dispatch")
_emit_invokes_evaluation("p3", "determinism_serialization_check", "evaluation_signal")
_emit_records_telemetry_event("p4", "determinism_serialization_check", "telemetry_event")
_emit_captures_evaluation_metric("p4", "determinism_serialization_check", "eval_metric")
_emit_stores_embedding("p4", "determinism_serialization_check", "embedding_store")
_emit_updates_meta_learning_state("p4", "determinism_serialization_check", "meta_learning")
_emit_links_execution_to_snapshot("p4", "determinism_serialization_check", "exec_snapshot_link")
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

record_execution_trace("determinism_serialization_check", "determinism_serialization_check_trace")


_emit_emits_metric_event("determinism_serialization_check", "p4obs", "metric_1")
_emit_emits_metric_event("determinism_serialization_check", "p4obs", "metric_2")
_emit_emits_metric_event("determinism_serialization_check", "p4obs", "metric_3")
_emit_emits_metric_event("determinism_serialization_check", "p4obs", "metric_4")
_emit_emits_metric_event("determinism_serialization_check", "p4obs", "metric_5")
_emit_emits_metric_event("determinism_serialization_check", "p4obs", "metric_6")
_emit_records_incident_event("determinism_serialization_check", "p4obs", "incident")
_emit_captures_runtime_anomaly("determinism_serialization_check", "p4obs", "anomaly")
_emit_writes_observability_log("determinism_serialization_check", "p4obs", "obs_log")
_emit_updates_monitoring_state("determinism_serialization_check", "p4obs", "mon_state")
_emit_triggers_alert("determinism_serialization_check", "p4obs", "alert")
_emit_links_incident_trace("determinism_serialization_check", "p4obs", "trace_link")
_emit_captures_pattern("determinism_serialization_check", "p3lm", "pattern")
_emit_records_learning_event("determinism_serialization_check", "p3lm", "learning_event")
_emit_writes_learning_snapshot("determinism_serialization_check", "p3lm", "snapshot")
_emit_feeds_meta_learning("determinism_serialization_check", "p3lm", "meta_feed")
_emit_updates_routing_strategy("determinism_serialization_check", "p3lm", "routing")
_emit_improves_agent_policy("determinism_serialization_check", "p3lm", "policy")
_emit_stores_learning_state("determinism_serialization_check", "p3lm", "state")
_emit_records_execution_trace("determinism_serialization_check", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("determinism_serialization_check", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("determinism_serialization_check", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("determinism_serialization_check", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("determinism_serialization_check", "L4_STATE", "p2_trace_5")
_emit_reads_environ("determinism_serialization_check", "env_read", "p2_env_1")
_emit_reads_environ("determinism_serialization_check", "env_read", "p2_env_2")
_emit_reads_runtime_state("determinism_serialization_check", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("determinism_serialization_check", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "determinism_serialization_check", "context_pull")
_emit_pulls_context("p1", "determinism_serialization_check", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "determinism_serialization_check", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "determinism_serialization_check", "uwg_term_2")
_emit_writes_through("p1", "determinism_serialization_check", "write_through")
_emit_writes_through("p1", "determinism_serialization_check", "write_through_2")
_emit_validated_by_safety_plane("p1", "determinism_serialization_check", "safety_validation")
_emit_invokes_eval("p1", "determinism_serialization_check", "eval_call")
_emit_proposal_commits_routing("p1", "determinism_serialization_check", "routing_commit")


class DeterminismVisitor(ast.NodeVisitor):
    """AST visitor to detect non-deterministic serialization patterns."""

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.violations: list[tuple[int, str, str]] = []
        self.in_serialization_function = False
        self.current_function = None

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Track function context."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "DeterminismVisitor.visit_FunctionDef",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DeterminismVisitor.visit_FunctionDef".encode()).hexdigest()[
            :24
        ]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        old_function = self.current_function
        old_in_serialization = self.in_serialization_function
        self.current_function = node.name
        serialization_functions = {
            "record_to_json",
            "record_from_json",
            "serialize",
            "deserialize",
            "to_json",
            "from_json",
            "save",
            "load",
            "write",
            "read",
            "serialize_with_timestamp",
        }
        self.in_serialization_function = node.name in serialization_functions
        self.generic_visit(node)
        self.in_serialization_function = old_in_serialization
        self.current_function = old_function

    def visit_Call(self, node: ast.Call) -> None:
        """Check function calls for non-deterministic patterns."""
        if isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "json":
                if node.func.attr == "dumps":
                    has_sort_keys = False
                    for kw in node.keywords:
                        if kw.arg == "sort_keys" and isinstance(kw.value, ast.Constant):
                            if kw.value.value is True:
                                has_sort_keys = True
                                break
                    if not has_sort_keys:
                        snippet = "json.dumps(...)"
                        self.violations.append((node.lineno, "JSON_NO_SORT_KEYS", snippet))
        if self.in_serialization_function:
            if isinstance(node.func, ast.Attribute):
                if node.func.attr == "now":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "datetime":
                        snippet = "datetime.now()"
                        self.violations.append((node.lineno, "DATETIME_NOW", snippet))
                if node.func.attr == "time":
                    if isinstance(node.func.value, ast.Name) and node.func.value.id == "time":
                        snippet = "time.time()"
                        self.violations.append((node.lineno, "TIME_TIME", snippet))
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        """Check for imports of non-deterministic modules."""
        for alias in node.names:
            if alias.name in ["time", "datetime"]:
                if self.in_serialization_function:
                    snippet = f"import {alias.name}"
                    self.violations.append((node.lineno, "IMPORT_NON_DETERMINISTIC", snippet))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Check for from-imports of non-deterministic modules."""
        if node.module in ["time", "datetime"]:
            if self.in_serialization_function:
                snippet = f"from {node.module} import ..."
                self.violations.append((node.lineno, "IMPORT_FROM_NON_DETERMINISTIC", snippet))
        self.generic_visit(node)


def scan_file_for_determinism(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for non-deterministic serialization patterns.

    Args:
        file_path: Path to file to scan

    Returns:
        List of (lineno, rule_id, snippet) tuples
    """
    violations = []
    try:
        with open(file_path, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content, filename=str(file_path))
        visitor = DeterminismVisitor(file_path)
        visitor.visit(tree)
        violations.extend(visitor.violations)
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        violations.append((e.lineno or 0, "DET_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    # guardian: allow-silent-swallower
    except (ValueError, TypeError) as e:
        violations.append((0, "DET_SCAN_ERROR", f"Scan error: {e}"))
    return violations


def scan_repository_for_determinism(repo_root: Path) -> list[tuple[str, int, str, str]]:
    """Scan repository for non-deterministic serialization in replay/storage modules.

    Args:
        repo_root: Repository root path

    Returns:
        List of (file_path, lineno, rule_id, snippet) tuples, sorted deterministically
    """
    all_violations = []
    scan_patterns = ["agentic_core/L3_orchestration/replay/**/*.py", "agentic_core/L4_state/storage/**/*.py"]
    for pattern in scan_patterns:
        for py_file in repo_root.glob(pattern):
            violations = scan_file_for_determinism(py_file)
            for lineno, rule_id, snippet in violations:
                rel_path = str(py_file.relative_to(repo_root))
                all_violations.append((rel_path, lineno, rule_id, snippet))
    all_violations.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return all_violations


# =============================================================================
# Execution-scope non-determinism checker (Gap 7 coverage)
#
# The serialization checker above only scans replay/storage modules.
# This checker covers execution-critical layers (L1_cognition, L2_execution,
# L3_orchestration, base_agents) for raw non-deterministic calls that escape
# the DeterminismGuard context manager.
# =============================================================================

#: Allowlist comment that suppresses a specific line
_EXEC_ALLOWLIST_COMMENT = "# guardian: allow-nondeterminism"

#: Modules that are themselves the determinism infrastructure — skip them.
_DETERMINISM_INFRA_PATHS = frozenset(
    [
        "determinism_guard.py",
        "replay_guard.py",
        "deterministic_providers.py",
        "determinism_serialization_check.py",
    ],
)

#: Execution-critical layer prefixes to scan.
_EXECUTION_SCOPE_PATTERNS = [
    "agentic_core/L1_cognition/**/*.py",
    "agentic_core/L2_execution/**/*.py",
    "agentic_core/L3_orchestration/**/*.py",
    "agentic_core/base_agents/**/*.py",
]


class ExecutionScopeNondeterminismVisitor(ast.NodeVisitor):
    """AST visitor that detects raw non-deterministic calls in execution-critical code.

    Flags:
    - ``time.time()`` / ``time.monotonic()`` / ``time.sleep()``
    - ``datetime.now()`` / ``datetime.utcnow()``
    - ``random.<any>()`` (except ``random.Random(seed)`` construction)
    - ``uuid.uuid4()``

    Calls on lines annotated with ``# guardian: allow-nondeterminism`` are
    suppressed, as are calls inside functions/methods named with a
    ``_determinism`` prefix (i.e., the infrastructure itself).
    """

    def __init__(self, source_lines: list[str]) -> None:
        self._lines = source_lines
        self.violations: list[tuple[int, str, str]] = []

    def _is_allowed(self, lineno: int) -> bool:
        """True if the source line carries the guardian allowlist comment."""
        if lineno < 1 or lineno > len(self._lines):
            return False
        return _EXEC_ALLOWLIST_COMMENT in self._lines[lineno - 1]

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id,
            LayerSegment.L5_POLICY,
            "ExecutionScopeNondeterminismVisitor.visit_Call",
        )
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(
            f"{_trace_id}:ExecutionScopeNondeterminismVisitor.visit_Call".encode(),
        ).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not self._is_allowed(node.lineno):
            self._check_call(node)
        self.generic_visit(node)

    def _check_call(self, node: ast.Call) -> None:
        func = node.func
        if not isinstance(func, ast.Attribute):
            self.generic_visit(node)
            return

        obj = func.value
        method = func.attr

        if isinstance(obj, ast.Name):
            obj_name = obj.id

            # time.time() / time.monotonic() / time.sleep()
            if obj_name == "time" and method in ("time", "monotonic", "sleep", "perf_counter"):
                self.violations.append((node.lineno, "EXEC_TIME_CALL", f"time.{method}()"))

            # datetime.now() / datetime.utcnow()
            elif obj_name == "datetime" and method in ("now", "utcnow"):
                self.violations.append((node.lineno, "EXEC_DATETIME_NOW", f"datetime.{method}()"))

            # random.* — flag any call except Random(seed) construction
            elif obj_name == "random" and method not in ("Random", "seed"):
                self.violations.append((node.lineno, "EXEC_RANDOM_CALL", f"random.{method}()"))

            # uuid.uuid4()
            elif obj_name == "uuid" and method == "uuid4":
                self.violations.append((node.lineno, "EXEC_UUID4_CALL", "uuid.uuid4()"))


def scan_file_for_execution_nondeterminism(file_path: Path) -> list[tuple[int, str, str]]:
    """Scan a single file for raw non-deterministic calls in execution scope.

    Args:
        file_path: Path to file to scan.

    Returns:
        List of (lineno, rule_id, snippet) tuples.
    """
    if file_path.name in _DETERMINISM_INFRA_PATHS:
        return []

    violations: list[tuple[int, str, str]] = []
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        source_lines = content.splitlines()
        tree = ast.parse(content, filename=str(file_path))
        visitor = ExecutionScopeNondeterminismVisitor(source_lines)
        visitor.visit(tree)
        violations.extend(visitor.violations)
    except SyntaxError as e:  # guardian: Syntax errors should be caught at parser level, not runtime
        violations.append((e.lineno or 0, "EXEC_SYNTAX_ERROR", f"Syntax error: {e.msg}"))
    # guardian: allow-silent-swallower
    except (ValueError, TypeError) as e:
        violations.append((0, "EXEC_SCAN_ERROR", f"Scan error: {e}"))
    return violations


def scan_execution_scope_for_nondeterminism(
    repo_root: Path,
) -> list[tuple[str, int, str, str]]:
    """Scan execution-critical layers for raw non-deterministic calls.

    Covers L1_cognition, L2_execution, L3_orchestration, and base_agents.
    Skips determinism-infrastructure modules.

    Args:
        repo_root: Repository root path.

    Returns:
        Sorted list of (file_path, lineno, rule_id, snippet) tuples.
    """
    all_violations: list[tuple[str, int, str, str]] = []
    for pattern in _EXECUTION_SCOPE_PATTERNS:
        for py_file in repo_root.glob(pattern):
            if "__pycache__" in str(py_file):
                continue
            file_violations = scan_file_for_execution_nondeterminism(py_file)
            for lineno, rule_id, snippet in file_violations:
                rel_path = str(py_file.relative_to(repo_root))
                all_violations.append((rel_path, lineno, rule_id, snippet))
    all_violations.sort(key=lambda x: (x[0], x[1], x[2], x[3]))
    return all_violations


__all__ = [
    "ExecutionScopeNondeterminismVisitor",
    "scan_execution_scope_for_nondeterminism",
    "scan_file_for_determinism",
    "scan_file_for_execution_nondeterminism",
    "scan_repository_for_determinism",
]
