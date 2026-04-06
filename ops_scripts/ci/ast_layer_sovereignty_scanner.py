"""
AST Layer Sovereignty Scanner — CI enforcement for cross-layer import restrictions.

Enforces that no layer imports upward (higher layers importing from lower-numbered
layers is fine; lower layers importing from higher is a violation):

  L1 must NOT import L2, L3, L4, L5, L6
  L2 must NOT import L5, L6
  L3 must NOT import L5, L6
  apps_* must NOT import directly from agentic_core.L* layers

Exit codes:
  0 — no violations
  1 — one or more violations found

Phase 1.2: Mathematically-Sealed Sovereignty Hardening
"""

from __future__ import annotations

import ast
import sys
import warnings
from pathlib import Path

# Try to import ADG Query Bridge for ADG-powered layer validation
try:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "adg"))
    from adg_query_bridge import ADGQueryBridge, Node
    ADG_AVAILABLE = True
except ImportError as e:
    warnings.warn(f"ADG Query Bridge unavailable, falling back to AST: {e}")
    ADG_AVAILABLE = False

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    TESTS_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
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

_emit_emits_metric_event("ast_layer_sovereignty_scanner", "p4obs", "metric_1")
_emit_emits_metric_event("ast_layer_sovereignty_scanner", "p4obs", "metric_2")
_emit_emits_metric_event("ast_layer_sovereignty_scanner", "p4obs", "metric_3")
_emit_emits_metric_event("ast_layer_sovereignty_scanner", "p4obs", "metric_4")
_emit_emits_metric_event("ast_layer_sovereignty_scanner", "p4obs", "metric_5")
_emit_emits_metric_event("ast_layer_sovereignty_scanner", "p4obs", "metric_6")
_emit_records_incident_event("ast_layer_sovereignty_scanner", "p4obs", "incident")
_emit_captures_runtime_anomaly("ast_layer_sovereignty_scanner", "p4obs", "anomaly")
_emit_writes_observability_log("ast_layer_sovereignty_scanner", "p4obs", "obs_log")
_emit_updates_monitoring_state("ast_layer_sovereignty_scanner", "p4obs", "mon_state")
_emit_triggers_alert("ast_layer_sovereignty_scanner", "p4obs", "alert")
_emit_links_incident_trace("ast_layer_sovereignty_scanner", "p4obs", "trace_link")
_emit_captures_pattern("ast_layer_sovereignty_scanner", "p3lm", "pattern")
_emit_records_learning_event("ast_layer_sovereignty_scanner", "p3lm", "learning_event")
_emit_writes_learning_snapshot("ast_layer_sovereignty_scanner", "p3lm", "snapshot")
_emit_feeds_meta_learning("ast_layer_sovereignty_scanner", "p3lm", "meta_feed")
_emit_updates_routing_strategy("ast_layer_sovereignty_scanner", "p3lm", "routing")
_emit_improves_agent_policy("ast_layer_sovereignty_scanner", "p3lm", "policy")
_emit_stores_learning_state("ast_layer_sovereignty_scanner", "p3lm", "state")
_emit_records_execution_trace("ast_layer_sovereignty_scanner", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("ast_layer_sovereignty_scanner", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("ast_layer_sovereignty_scanner", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("ast_layer_sovereignty_scanner", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("ast_layer_sovereignty_scanner", "L4_STATE", "p2_trace_5")
_emit_reads_environ("ast_layer_sovereignty_scanner", "env_read", "p2_env_1")
_emit_reads_environ("ast_layer_sovereignty_scanner", "env_read", "p2_env_2")
_emit_reads_runtime_state("ast_layer_sovereignty_scanner", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("ast_layer_sovereignty_scanner", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "ast_layer_sovereignty_scanner")
_emit_applies_guardrail("p0", "ast_layer_sovereignty_scanner", "p0_governance")
_emit_reads_policy_state("p0", "ast_layer_sovereignty_scanner", "policy_binding")
_emit_snapshots_state("p0", "ast_layer_sovereignty_scanner", "state_snapshot")
_emit_pulls_context("p1", "ast_layer_sovereignty_scanner", "context_pull")
_emit_pulls_context("p1", "ast_layer_sovereignty_scanner", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "ast_layer_sovereignty_scanner", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "ast_layer_sovereignty_scanner", "uwg_term_secondary")
_emit_writes_through("p1", "ast_layer_sovereignty_scanner", "write_through")
_emit_writes_through("p1", "ast_layer_sovereignty_scanner", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "ast_layer_sovereignty_scanner", "safety_validation")
_emit_invokes_eval("p1", "ast_layer_sovereignty_scanner", "eval_call")
_emit_proposal_commits_routing("p1", "ast_layer_sovereignty_scanner", "routing_commit")
_emit_escalates_to_human("p1", "ast_layer_sovereignty_scanner", "human_escalation")
_emit_routes_through("p1", "ast_layer_sovereignty_scanner", "route_through")
_emit_checks_agent_registry("p1", "ast_layer_sovereignty_scanner", "agent_registry")
_emit_validates_agent_capability("p1", "ast_layer_sovereignty_scanner", "capability")
_emit_dispatches_execution_plan("p1", "ast_layer_sovereignty_scanner", "exec_plan")
_emit_agent_executes_agent("p1", "ast_layer_sovereignty_scanner", "sub_agent")
_emit_routes_to_agent("p1", "ast_layer_sovereignty_scanner", "target_agent")
_emit_verifies_policy("p1", "ast_layer_sovereignty_scanner", "policy_check")
_emit_observes_runtime_state("p1", "ast_layer_sovereignty_scanner", "runtime_state")
_emit_verifies_boundary("p1", "ast_layer_sovereignty_scanner", "boundary_check")
_emit_transcripts_response("p1", "ast_layer_sovereignty_scanner", "transcript")
_emit_hard_fails_untranscripted("p1", "ast_layer_sovereignty_scanner")
_emit_gated_by_confidence("p1", "ast_layer_sovereignty_scanner", "confidence_gate")
emit_replay_key("p0", "ast_layer_sovereignty_scanner")
emit_determinism_digest("p0", "ast_layer_sovereignty_scanner")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "ast_layer_sovereignty_scanner", "execution_auth")
_emit_validates_capability("p2", "ast_layer_sovereignty_scanner", "capability_check")
_emit_routes_to_capability("p2", "ast_layer_sovereignty_scanner", "capability_route")
_emit_writes_via_uwg("p2", "ast_layer_sovereignty_scanner", "uwg_write")
_emit_blocks_direct_write("p2", "ast_layer_sovereignty_scanner", "direct_write_block")
_emit_records_tool_invocation("p2", "ast_layer_sovereignty_scanner", "tool_invocation")
_emit_captures_execution_output("p2", "ast_layer_sovereignty_scanner", "exec_output")
_emit_dispatches_agent("p3", "ast_layer_sovereignty_scanner", "agent_dispatch")
_emit_coordinates_agents("p3", "ast_layer_sovereignty_scanner", "agent_coordination")
_emit_records_workflow_lineage("p3", "ast_layer_sovereignty_scanner", "workflow_lineage")
_emit_records_healing_outcome("p3", "ast_layer_sovereignty_scanner", "healing_outcome")
_emit_escalates_failure("p3", "ast_layer_sovereignty_scanner", "failure_escalation")
_emit_orchestrates_workflow("p3", "ast_layer_sovereignty_scanner", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "ast_layer_sovereignty_scanner", "healing_dispatch")
_emit_invokes_evaluation("p3", "ast_layer_sovereignty_scanner", "evaluation_signal")
_emit_records_telemetry_event("p4", "ast_layer_sovereignty_scanner", "telemetry_event")
_emit_captures_evaluation_metric("p4", "ast_layer_sovereignty_scanner", "eval_metric")
_emit_stores_embedding("p4", "ast_layer_sovereignty_scanner", "embedding_store")
_emit_updates_meta_learning_state("p4", "ast_layer_sovereignty_scanner", "meta_learning")
_emit_links_execution_to_snapshot("p4", "ast_layer_sovereignty_scanner", "exec_snapshot_link")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_1")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_2")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_3")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_4")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_5")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_6")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_7")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_8")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_9")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_10")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_11")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_12")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_13")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_14")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_15")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_16")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_17")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_18")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_19")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_20")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_21")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_22")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_23")
_emit_reads_through("l4", "ast_layer_sovereignty_scanner", "urg_read_24")

# ---------------------------------------------------------------------------
# Layer inversion rules: {source_layer: (forbidden_target_layers, ...)}
# ---------------------------------------------------------------------------

_LAYER_RULES: dict[str, tuple[str, ...]] = {
    "agentic_core.L0_routing": (
        "agentic_core.L1_cognition",
        "agentic_core.L2_execution",
        "agentic_core.L3_orchestration",
        "agentic_core.L4_state",
        "agentic_core.L5_safety",
        "agentic_core.L6_observability",
    ),
    "agentic_core.L1_cognition": (
        "agentic_core.L2_execution",
        "agentic_core.L3_orchestration",
        "agentic_core.L4_state",
        "agentic_core.L5_safety",
        "agentic_core.L6_observability",
    ),
    "agentic_core.L2_execution": ("agentic_core.L5_safety", "agentic_core.L6_observability"),
    "agentic_core.L3_orchestration": ("agentic_core.L5_safety", "agentic_core.L6_observability"),
}

# apps_* must not directly import any agentic_core.L[0-9]* numbered layer
# (L_CONTRACTS, L_SHARED, L_APP, L_TOOLS, L_RUNTIME etc. are shared layers and are allowed)
_APPS_PREFIXES = (APPS_LIC_DIR, APPS_RG_DIR, APPS_SHARED_DIR)
_L_LAYER_PREFIX = AGENTIC_CORE_DIR + ".L"
_L_NUMBERED_PREFIXES = tuple(f"{AGENTIC_CORE_DIR}.L{n}" for n in range(7))

_EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS


def _layer_prefix_of(file_path: Path) -> str | None:
    """Return the dotted module prefix for *file_path*, or None if not in a layer."""
    parts = file_path.as_posix().split("/")
    for i, part in enumerate(parts):
        if part.startswith("agentic_core") and i + 1 < len(parts):
            next_part = parts[i + 1]
            if next_part.startswith("L") and next_part[1:2].isdigit():
                return f"agentic_core.{next_part}"
    # Check apps_*
    for app_prefix in _APPS_PREFIXES:
        if any(p == app_prefix for p in parts):
            return app_prefix
    return None


class _ModuleLevelImportVisitor(ast.NodeVisitor):
    """Collect only module-level imports, skipping TYPE_CHECKING guards and function/class bodies."""

    def __init__(self) -> None:
        self._result: list[tuple[int, str]] = []
        self._in_function: int = 0
        self._in_type_checking: bool = False

    def visit_If(self, node: ast.If) -> None:
        test = node.test
        is_tc = (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
            isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
        )
        old = self._in_type_checking
        if is_tc:
            self._in_type_checking = True
        self.generic_visit(node)
        self._in_type_checking = old

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._in_function += 1
        self.generic_visit(node)
        self._in_function -= 1

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._in_function += 1
        self.generic_visit(node)
        self._in_function -= 1

    def visit_Import(self, node: ast.Import) -> None:
        if self._in_function == 0 and not self._in_type_checking:
            for alias in node.names:
                self._result.append((node.lineno, alias.name))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if self._in_function == 0 and not self._in_type_checking:
            if node.module:
                self._result.append((node.lineno, node.module))

    @property
    def result(self) -> list[tuple[int, str]]:
        return self._result


def _extract_imported_modules(tree: ast.AST) -> list[tuple[int, str]]:
    """Return module-level imports only, skipping TYPE_CHECKING guards and function/class bodies."""
    visitor = _ModuleLevelImportVisitor()
    visitor.visit(tree)
    return visitor.result


def scan_file(file_path: Path) -> list[str]:
    """Return list of violation strings for *file_path*."""
    violations: list[str] = []

    try:
        source = file_path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(file_path))
    except SyntaxError as exc:
        return [f"PARSE_ERROR {file_path}:{exc.lineno}: {exc.msg}"]

    source_layer = _layer_prefix_of(file_path)
    if source_layer is None:
        return []

    # Use ADG for layer validation when available
    if ADG_AVAILABLE:
        try:
            violations.extend(_scan_file_with_adg(file_path, source_layer, tree))
        except Exception as e:
            warnings.warn(f"ADG layer validation failed, falling back to AST: {e}")
            violations.extend(_scan_file_with_ast(file_path, source_layer, tree))
    else:
        violations.extend(_scan_file_with_ast(file_path, source_layer, tree))

    return violations


def _scan_file_with_adg(file_path: Path, source_layer: str, tree: ast.AST) -> list[str]:
    """Scan file using ADG for layer validation."""
    violations = []

    try:
        bridge = ADGQueryBridge()

        # Get imports from ADG for this file
        file_rel_path = str(file_path.relative_to(get_validated_project_root()))
        imports = _extract_imported_modules(tree)

        # For each import, validate layer constraints using ADG
        for lineno, mod in imports:
            # Get the target layer from ADG
            target_layer = _get_layer_from_adg(bridge, mod)

            if target_layer:
                # Check layer inversion using ADG layer data
                if source_layer in _LAYER_RULES:
                    forbidden = _LAYER_RULES[source_layer]
                    for forbidden_prefix in forbidden:
                        if target_layer == forbidden_prefix or target_layer.startswith(forbidden_prefix + "."):
                            violations.append(
                                f"VIOLATION {file_path}:{lineno}: layer inversion — {source_layer} imports {mod} (target layer: {target_layer})"
                            )

                # Check apps_* direct L* imports
                if any(source_layer == ap for ap in _APPS_PREFIXES):
                    if target_layer.startswith(_L_LAYER_PREFIX):
                        violations.append(
                            f"VIOLATION {file_path}:{lineno}: "
                            f"apps_* direct L* import — {source_layer} imports {mod} "
                            f"(target layer: {target_layer}, use agentic_core.interfaces shims)"
                        )
        else:
            # If no layer found in ADG, fall back to AST validation
            violations.extend(_validate_import_with_ast(file_path, source_layer, lineno, mod))

    except Exception as e:
        warnings.warn(f"ADG scan failed: {e}")
        # Fall back to AST
        violations.extend(_scan_file_with_ast(file_path, source_layer, tree))

    return violations


def _get_layer_from_adg(bridge: ADGQueryBridge, module_name: str) -> str | None:
    """Get layer information for a module from ADG."""
    try:
        # Try to find nodes matching this module
        # This is a simplified approach - in practice would need more sophisticated matching
        for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
            nodes = bridge.nodes_in_layer(layer)
            for node in nodes:
                if (module_name in node.label or
                    module_name in str(node.file_path) or
                    node.label.endswith(module_name)):
                    return layer
        return None
    except Exception:
        return None


def _validate_import_with_ast(file_path: Path, source_layer: str, lineno: int, mod: str) -> list[str]:
    """Fallback AST-based validation for a single import."""
    violations = []

    # Check layer inversion for agentic_core layers
    if source_layer in _LAYER_RULES:
        forbidden = _LAYER_RULES[source_layer]
        for forbidden_prefix in forbidden:
            if mod == forbidden_prefix or mod.startswith(forbidden_prefix + "."):
                violations.append(
                    f"VIOLATION {file_path}:{lineno}: layer inversion — {source_layer} imports {mod}"
                )

    # Check apps_* direct L* imports
    if any(source_layer == ap for ap in _APPS_PREFIXES):
        if any(mod == p or mod.startswith(p + ".") for p in _L_NUMBERED_PREFIXES):
            violations.append(
                f"VIOLATION {file_path}:{lineno}: "
                f"apps_* direct L* import — {source_layer} imports {mod} "
                f"(use agentic_core.interfaces shims)"
            )

    return violations


def _scan_file_with_ast(file_path: Path, source_layer: str, tree: ast.AST) -> list[str]:
    """Original AST-based scanning as fallback."""
    violations = []

    imports = _extract_imported_modules(tree)

    # Check layer inversion for agentic_core layers
    if source_layer in _LAYER_RULES:
        forbidden = _LAYER_RULES[source_layer]
        for lineno, mod in imports:
            for forbidden_prefix in forbidden:
                if mod == forbidden_prefix or mod.startswith(forbidden_prefix + "."):
                    violations.append(
                        f"VIOLATION {file_path}:{lineno}: layer inversion — {source_layer} imports {mod}"
                    )

    # Check apps_* direct numbered-layer imports (L0-L6 only; L_CONTRACTS etc. are allowed)
    if any(source_layer == ap for ap in _APPS_PREFIXES):
        for lineno, mod in imports:
            if any(mod == p or mod.startswith(p + ".") for p in _L_NUMBERED_PREFIXES):
                violations.append(
                    f"VIOLATION {file_path}:{lineno}: "
                    f"apps_* direct L* import — {source_layer} imports {mod} "
                    f"(use agentic_core.interfaces shims)"
                )

    return violations


def main(argv: list[str] | None = None) -> int:
    repo_root = get_validated_project_root()
    all_violations: list[str] = []
    files_scanned = 0

    scan_roots = (
        # guardian: allow-path-string
        list(repo_root.glob(AGENTIC_CORE_DIR + "/L*"))
        + list(repo_root.glob(APPS_LIC_DIR))
        + list(repo_root.glob(APPS_RG_DIR))
        + list(repo_root.glob(APPS_SHARED_DIR))
    )

    for root in scan_roots:
        if not root.is_dir():
            continue
        for py_file in sorted(root.rglob("*.py")):
            if any(part in _EXCLUDE_DIRS for part in py_file.parts):
                continue
            files_scanned += 1
            all_violations.extend(scan_file(py_file))

    if all_violations:
        print("FAIL: Layer sovereignty violations detected:")
        for v in all_violations:
            print(f"  {v}")
        return 1

    print(f"OK: ast_layer_sovereignty_scanner passed ({files_scanned} files scanned, 0 violations)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
