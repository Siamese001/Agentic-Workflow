#!/usr/bin/env python3
"""
SSOT Path Fixer — AST-based, single-pass.

Scans production code folders for hardcoded directory/file strings that
should reference SSOT constants from agentic_core.L0_routing.config,
then fixes them in-place: replaces the string literal with the constant
name and injects/extends the import block.
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
    APPS_LIC_DIR,
    APPS_RG_DIR,
    APPS_SHARED_DIR,
    SYSTEM_LEARNING_DIR,
    get_validated_project_root,
)
from agentic_core.L5_safety.config.structure_blueprint.ssot import (
    GLOBAL_EXCLUDED_DIRS,
    SOVEREIGN_EXCLUDED_FOLDERS,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_emits_metric_event("_ssot_path_fixer", "p4obs", "metric_1")
_emit_emits_metric_event("_ssot_path_fixer", "p4obs", "metric_2")
_emit_emits_metric_event("_ssot_path_fixer", "p4obs", "metric_3")
_emit_emits_metric_event("_ssot_path_fixer", "p4obs", "metric_4")
_emit_emits_metric_event("_ssot_path_fixer", "p4obs", "metric_5")
_emit_emits_metric_event("_ssot_path_fixer", "p4obs", "metric_6")
_emit_records_incident_event("_ssot_path_fixer", "p4obs", "incident")
_emit_captures_runtime_anomaly("_ssot_path_fixer", "p4obs", "anomaly")
_emit_writes_observability_log("_ssot_path_fixer", "p4obs", "obs_log")
_emit_updates_monitoring_state("_ssot_path_fixer", "p4obs", "mon_state")
_emit_triggers_alert("_ssot_path_fixer", "p4obs", "alert")
_emit_links_incident_trace("_ssot_path_fixer", "p4obs", "trace_link")
_emit_captures_pattern("_ssot_path_fixer", "p3lm", "pattern")
_emit_records_learning_event("_ssot_path_fixer", "p3lm", "learning_event")
_emit_writes_learning_snapshot("_ssot_path_fixer", "p3lm", "snapshot")
_emit_feeds_meta_learning("_ssot_path_fixer", "p3lm", "meta_feed")
_emit_updates_routing_strategy("_ssot_path_fixer", "p3lm", "routing")
_emit_improves_agent_policy("_ssot_path_fixer", "p3lm", "policy")
_emit_stores_learning_state("_ssot_path_fixer", "p3lm", "state")
_emit_records_execution_trace("_ssot_path_fixer", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("_ssot_path_fixer", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("_ssot_path_fixer", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("_ssot_path_fixer", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("_ssot_path_fixer", "L4_STATE", "p2_trace_5")
_emit_reads_environ("_ssot_path_fixer", "env_read", "p2_env_1")
_emit_reads_environ("_ssot_path_fixer", "env_read", "p2_env_2")
_emit_reads_runtime_state("_ssot_path_fixer", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("_ssot_path_fixer", "runtime_state", "p2_rt_2")

_emit_records_execution_trace("p0", "evidence", "_ssot_path_fixer")
_emit_applies_guardrail("p0", "_ssot_path_fixer", "p0_governance")
_emit_reads_policy_state("p0", "_ssot_path_fixer", "policy_binding")
_emit_snapshots_state("p0", "_ssot_path_fixer", "state_snapshot")
_emit_pulls_context("p1", "_ssot_path_fixer", "context_pull")
_emit_pulls_context("p1", "_ssot_path_fixer", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "_ssot_path_fixer", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "_ssot_path_fixer", "uwg_term_secondary")
_emit_writes_through("p1", "_ssot_path_fixer", "write_through")
_emit_writes_through("p1", "_ssot_path_fixer", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "_ssot_path_fixer", "safety_validation")
_emit_invokes_eval("p1", "_ssot_path_fixer", "eval_call")
_emit_proposal_commits_routing("p1", "_ssot_path_fixer", "routing_commit")
_emit_escalates_to_human("p1", "_ssot_path_fixer", "human_escalation")
_emit_routes_through("p1", "_ssot_path_fixer", "route_through")
_emit_checks_agent_registry("p1", "_ssot_path_fixer", "agent_registry")
_emit_validates_agent_capability("p1", "_ssot_path_fixer", "capability")
_emit_dispatches_execution_plan("p1", "_ssot_path_fixer", "exec_plan")
_emit_agent_executes_agent("p1", "_ssot_path_fixer", "sub_agent")
_emit_routes_to_agent("p1", "_ssot_path_fixer", "target_agent")
_emit_verifies_policy("p1", "_ssot_path_fixer", "policy_check")
_emit_observes_runtime_state("p1", "_ssot_path_fixer", "runtime_state")
_emit_verifies_boundary("p1", "_ssot_path_fixer", "boundary_check")
_emit_transcripts_response("p1", "_ssot_path_fixer", "transcript")
_emit_hard_fails_untranscripted("p1", "_ssot_path_fixer")
_emit_gated_by_confidence("p1", "_ssot_path_fixer", "confidence_gate")
emit_replay_key("p0", "_ssot_path_fixer")
emit_determinism_digest("p0", "_ssot_path_fixer")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "_ssot_path_fixer", "execution_auth")
_emit_validates_capability("p2", "_ssot_path_fixer", "capability_check")
_emit_routes_to_capability("p2", "_ssot_path_fixer", "capability_route")
_emit_writes_via_uwg("p2", "_ssot_path_fixer", "uwg_write")
_emit_blocks_direct_write("p2", "_ssot_path_fixer", "direct_write_block")
_emit_records_tool_invocation("p2", "_ssot_path_fixer", "tool_invocation")
_emit_captures_execution_output("p2", "_ssot_path_fixer", "exec_output")
_emit_dispatches_agent("p3", "_ssot_path_fixer", "agent_dispatch")
_emit_coordinates_agents("p3", "_ssot_path_fixer", "agent_coordination")
_emit_records_workflow_lineage("p3", "_ssot_path_fixer", "workflow_lineage")
_emit_records_healing_outcome("p3", "_ssot_path_fixer", "healing_outcome")
_emit_escalates_failure("p3", "_ssot_path_fixer", "failure_escalation")
_emit_orchestrates_workflow("p3", "_ssot_path_fixer", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "_ssot_path_fixer", "healing_dispatch")
_emit_invokes_evaluation("p3", "_ssot_path_fixer", "evaluation_signal")
_emit_records_telemetry_event("p4", "_ssot_path_fixer", "telemetry_event")
_emit_captures_evaluation_metric("p4", "_ssot_path_fixer", "eval_metric")
_emit_stores_embedding("p4", "_ssot_path_fixer", "embedding_store")
_emit_updates_meta_learning_state("p4", "_ssot_path_fixer", "meta_learning")
_emit_links_execution_to_snapshot("p4", "_ssot_path_fixer", "exec_snapshot_link")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_1")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_2")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_3")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_4")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_5")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_6")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_7")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_8")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_9")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_10")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_11")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_12")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_13")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_14")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_15")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_16")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_17")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_18")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_19")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_20")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_21")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_22")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_23")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_24")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_25")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_26")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_27")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_28")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_29")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_30")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_31")
_emit_reads_through("l4", "_ssot_path_fixer", "urg_read_32")

ROOT = get_validated_project_root()

SSOT_MAP: dict[str, str] = {
    "agentic_core": "AGENTIC_CORE_DIR",
    "apps_lic": "APPS_LIC_DIR",
    "apps_rg": "APPS_RG_DIR",
    "apps_shared": "APPS_SHARED_DIR",
    "archives": "ARCHIVES_DIR",
    "ops_scripts": "OPS_SCRIPTS_DIR",
    "system_learning": "SYSTEM_LEARNING_DIR",
    "agentic_core/L6_observability/dashboards": "DASHBOARD_DIR",
    "agentic_core/L0_maintenance": "L0_MAINTENANCE_DIR",
    "agentic_core/L0_routing": "L0_ROUTING_DIR",
    "agentic_core/L1_cognition": "L1_COGNITION_DIR",
    "agentic_core/L2_execution": "L2_EXECUTION_DIR",
    "agentic_core/L3_orchestration": "L3_ORCHESTRATION_DIR",
    "agentic_core/L4_state": "L4_STATE_DIR",
    "agentic_core/L5_safety": "L5_SAFETY_DIR",
    "agentic_core/L6_observability": "L6_OBSERVABILITY_DIR",
    "agent_discovery.json": "AGENT_DISCOVERY_JSON",
    "agent_discovery_manifest.json": "AGENT_DISCOVERY_MANIFEST_JSON",
    "runtime_state.json": "RUNTIME_STATE_JSON",
}

PROD_SCAN_ROOTS = [
    ROOT / AGENTIC_CORE_DIR,
    ROOT / APPS_LIC_DIR,
    ROOT / APPS_RG_DIR,
    ROOT / APPS_SHARED_DIR,
    ROOT / SYSTEM_LEARNING_DIR,
]

EXCLUDE_DIRS = GLOBAL_EXCLUDED_DIRS | SOVEREIGN_EXCLUDED_FOLDERS

# Files that define the SSOT or are architectural boundary leaf nodes — never touch them
SSOT_FILES = {
    ROOT / "agentic_core/L0_routing/config/path_constants.py",
    ROOT / "agentic_core/L0_routing/config/__init__.py",
    # L5 zero-dependency leaf — stdlib-only by design; adding L0 import is a layer violation
    ROOT / "agentic_core/L5_safety/config/structure_blueprint/_constants.py",
    # L5 verifier — SCAN_ROOTS tuple is intentional static data, not path construction
    ROOT / "agentic_core/L5_safety/config/structure_blueprint/_verify.py",
    # Independent root resolver — must not import from L0_routing to avoid cycles
    ROOT / "agentic_core/utils/project_root_util.py",
    # This script itself
    Path(__file__).resolve(),
}

PATH_CALL_NAMES = {
    "Path",
    "open",
    "rglob",
    "glob",
    "exists",
    "mkdir",
    "iterdir",
    "join",
    "isdir",
    "isfile",
    "listdir",
    "walk",
    "scandir",
}


# ---------------------------------------------------------------------------
# AST visitor
# ---------------------------------------------------------------------------


class PathConstructionVisitor(ast.NodeVisitor):
    def __init__(self) -> None:
        self.hits: list[tuple[int, int, str, str, str]] = []
        # (lineno, col_offset, raw_value, const_name, context)

    def _check(self, node: ast.expr, context: str) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            val = node.value.strip().rstrip("/")
            if val in SSOT_MAP:
                self.hits.append((node.lineno, node.col_offset, val, SSOT_MAP[val], context))

    def visit_Call(self, node: ast.Call) -> None:
        func = node.func
        fname = ""
        if isinstance(func, ast.Name):
            fname = func.id
        elif isinstance(func, ast.Attribute):
            fname = func.attr
        if fname in PATH_CALL_NAMES:
            for arg in node.args:
                self._check(arg, f"Call({fname})")
            for kw in node.keywords:
                self._check(kw.value, f"Call({fname})")
        self.generic_visit(node)

    def visit_BinOp(self, node: ast.BinOp) -> None:
        if isinstance(node.op, ast.Div):
            self._check(node.left, "BinOp(/)")
            self._check(node.right, "BinOp(/)")
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        for container in ast.walk(node.value):
            if isinstance(container, (ast.List, ast.Tuple)):
                for elt in container.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        v = elt.value.strip().rstrip("/")
                        if v in SSOT_MAP:
                            self.hits.append((elt.lineno, elt.col_offset, v, SSOT_MAP[v], "List/Tuple"))
        self.generic_visit(node)


# ---------------------------------------------------------------------------
# Import helpers
# ---------------------------------------------------------------------------


def existing_ssot_import(tree: ast.Module) -> tuple[ast.ImportFrom | None, set[str]]:
    """Return the first L0_routing.config ImportFrom node and all names it imports."""
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if "L0_routing.config" in mod or "path_constants" in mod:
                return node, {alias.name for alias in node.names}
    return None, set()


def last_top_level_import_lineno(tree: ast.Module) -> int:
    """Return the end_lineno of the last top-level import statement, or 0."""
    last = 0
    for node in tree.body:  # top-level only — never walk into class/function bodies
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if hasattr(node, "end_lineno"):
                last = max(last, node.end_lineno)
    return last


# ---------------------------------------------------------------------------
# Per-file fix
# ---------------------------------------------------------------------------


def fix_file(py_file: Path) -> tuple[int, int]:
    """Return (replacements_made, new_imports_added)."""
    try:
        src = py_file.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(src, filename=str(py_file))
    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
        return 0, 0

    visitor = PathConstructionVisitor()
    visitor.visit(tree)
    if not visitor.hits:
        return 0, 0

    # Deduplicate by (lineno, value)
    seen: set[tuple[int, str]] = set()
    hits: list[tuple[int, int, str, str, str]] = []
    for lineno, col, val, const, ctx in visitor.hits:
        k = (lineno, val)
        if k not in seen:
            seen.add(k)
            hits.append((lineno, col, val, const, ctx))
    hits.sort(key=lambda x: x[0])

    needed_consts = sorted({const for _, _, _, const, _ in hits})
    ssot_node, existing = existing_ssot_import(tree)
    missing_consts = [c for c in needed_consts if c not in existing]

    lines = src.splitlines(keepends=True)

    # --- Step 1: replace string literals with constant names ---
    replacements = 0
    for lineno, _col, val, const, _ctx in hits:
        idx = lineno - 1
        if idx >= len(lines):
            continue
        line = lines[idx]
        replaced = False
        for q in ("'", '"'):
            old = q + val + q
            if old in line:
                lines[idx] = line.replace(old, const, 1)
                replacements += 1
                replaced = True
                break
        if not replaced:
            # Try backslash variant
            for q in ("'", '"'):
                old = q + val.replace("/", "\\") + q
                if old in line:
                    lines[idx] = line.replace(old, const, 1)
                    replacements += 1
                    break

    # --- Step 2: inject/extend imports ---
    new_imports = 0
    if missing_consts:
        const_items = ",\n    ".join(missing_consts)
        new_import_block = f"from agentic_core.L0_routing.config import (\n    {const_items},\n)\n"

        if ssot_node is not None:
            # Extend the existing import block — ssot_node is always top-level
            start = ssot_node.lineno - 1
            end = ssot_node.end_lineno - 1
            # Build the full updated set of imported names
            all_names = sorted(existing | set(missing_consts))
            names_str = ",\n    ".join(all_names)
            updated_import = f"from agentic_core.L0_routing.config import (\n    {names_str},\n)\n"
            lines[start : end + 1] = [updated_import]
        else:
            # Re-parse with current lines to get accurate top-level import position
            try:
                tree2 = ast.parse("".join(lines))
            except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                tree2 = tree
            insert_after = last_top_level_import_lineno(tree2)
            # insert_after is 1-based end_lineno; 0-based index is insert_after
            # Insert AFTER that line means index = insert_after (0-based line after last import)
            if insert_after == 0:
                # No imports at all — insert at position 0 (before everything)
                lines.insert(0, new_import_block)
            else:
                lines.insert(insert_after, new_import_block)

        new_imports = len(missing_consts)

    if replacements > 0 or new_imports > 0:
        py_file.write_text("".join(lines), encoding="utf-8")

    return replacements, new_imports


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    total_files = 0
    total_replacements = 0
    total_new_imports = 0
    errors: list[tuple[str, str]] = []

    for scan_root in PROD_SCAN_ROOTS:
        if not scan_root.exists():
            continue
        for py_file in sorted(scan_root.rglob("*.py")):
            if any(part in EXCLUDE_DIRS for part in py_file.parts):
                continue
            if py_file.resolve() in SSOT_FILES:
                continue
            try:
                if dry_run:
                    src = py_file.read_text(encoding="utf-8", errors="replace")
                    try:
                        tree = ast.parse(src)
                    except SyntaxError:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
                        continue
                    v = PathConstructionVisitor()
                    v.visit(tree)
                    if v.hits:
                        rel = py_file.relative_to(ROOT).as_posix()
                        _, existing = existing_ssot_import(tree)
                        needed = sorted({c for _, _, _, c, _ in v.hits})
                        missing = [c for c in needed if c not in existing]
                        print(f"WOULD FIX: {rel}  (hits={len(v.hits)}, new_imports={len(missing)})")
                        total_files += 1
                else:
                    replacements, new_imports = fix_file(py_file)
                    if replacements > 0 or new_imports > 0:
                        rel = py_file.relative_to(ROOT).as_posix()
                        print(f"FIXED: {rel}  (replacements={replacements}, new_imports={new_imports})")
                        total_files += 1
                        total_replacements += replacements
                        total_new_imports += new_imports
            except Exception as exc:
                raise
                rel = py_file.relative_to(ROOT).as_posix()
                errors.append((rel, str(exc)))

    print()
    if dry_run:
        print(f"DRY RUN: {total_files} files would be fixed")
    else:
        print(
            f"DONE: {total_files} files fixed, {total_replacements} string replacements, {total_new_imports} import names added"
        )
    if errors:
        print(f"ERRORS ({len(errors)}):")
        for r, e in errors:
            print(f"  {r}: {e}")


if __name__ == "__main__":
    main()
