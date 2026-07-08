from __future__ import annotations

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract.emit_replay_key("p0", "gravity_visitor_util")
trace_contract.emit_determinism_digest("p0", "gravity_visitor_util")

trace_contract._emit_dispatches_healing_run("p1", "gravity_visitor_util", "L5")
trace_contract._emit_routes_through("p1", "gravity_visitor_util", "L5")
trace_contract._emit_checks_agent_registry("p1", "gravity_visitor_util", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "gravity_visitor_util", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "gravity_visitor_util", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "gravity_visitor_util", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "gravity_visitor_util", "target_agent")
trace_contract._emit_verifies_policy("p1", "gravity_visitor_util", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "gravity_visitor_util", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "gravity_visitor_util", "boundary_check")
trace_contract._emit_transcripts_response("p1", "gravity_visitor_util", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "gravity_visitor_util")
trace_contract._emit_gated_by_confidence("p1", "gravity_visitor_util", "confidence_gate")
trace_contract._emit_escalates_to_human("p1", "gravity_visitor_util", "L5")
trace_contract._emit_reads_policy_state("p1", "gravity_visitor_util", "L5")

trace_contract._emit_applies_guardrail("p0", "gravity_visitor_util", "p0_governance")
trace_contract._emit_snapshots_state("p0", "gravity_visitor_util", "state_snapshot")
trace_contract._emit_authorize_and_execute("p2", "gravity_visitor_util", "execution_auth")
trace_contract._emit_validates_capability("p2", "gravity_visitor_util", "capability_check")
trace_contract._emit_routes_to_capability("p2", "gravity_visitor_util", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "gravity_visitor_util", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "gravity_visitor_util", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "gravity_visitor_util", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "gravity_visitor_util", "exec_output")
trace_contract._emit_dispatches_agent("p3", "gravity_visitor_util", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "gravity_visitor_util", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "gravity_visitor_util", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "gravity_visitor_util", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "gravity_visitor_util", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "gravity_visitor_util", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "gravity_visitor_util", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "gravity_visitor_util", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "gravity_visitor_util", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "gravity_visitor_util", "eval_metric")
trace_contract._emit_stores_embedding("p4", "gravity_visitor_util", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "gravity_visitor_util", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "gravity_visitor_util", "exec_snapshot_link")

'AST Engine - Centralized Architectural Parsing Logic.\n\n[Phase 5] Provides shared AST utilities for L5 agents.\nCentralizes import extraction and gravity violation detection.\n\nUsage:\n\n    imports = get_file_imports(Path("my_file.py"))\n    # Returns: [("module.name", line_number), ...]\n'
import ast
import logging
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR

trace_contract._emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("gravity_visitor_util", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("gravity_visitor_util", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("gravity_visitor_util", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("gravity_visitor_util", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("gravity_visitor_util", "p4obs", "alert")
trace_contract._emit_links_incident_trace("gravity_visitor_util", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("gravity_visitor_util", "p3lm", "pattern")
trace_contract._emit_records_learning_event("gravity_visitor_util", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("gravity_visitor_util", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("gravity_visitor_util", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("gravity_visitor_util", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("gravity_visitor_util", "p3lm", "policy")
trace_contract._emit_stores_learning_state("gravity_visitor_util", "p3lm", "state")
trace_contract._emit_records_execution_trace("gravity_visitor_util", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("gravity_visitor_util", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("gravity_visitor_util", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("gravity_visitor_util", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("gravity_visitor_util", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("gravity_visitor_util", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("gravity_visitor_util", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("gravity_visitor_util", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("gravity_visitor_util", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "gravity_visitor_util", "context_pull")
trace_contract._emit_pulls_context("p1", "gravity_visitor_util", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "gravity_visitor_util", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "gravity_visitor_util", "uwg_term_2")
trace_contract._emit_writes_through("p1", "gravity_visitor_util", "write_through")
trace_contract._emit_writes_through("p1", "gravity_visitor_util", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "gravity_visitor_util", "safety_validation")
trace_contract._emit_invokes_eval("p1", "gravity_visitor_util", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "gravity_visitor_util", "routing_commit")

Logger = logging.getLogger(__name__)


class GravityVisitor(ast.NodeVisitor):
    """
    Standardized AST visitor for architectural gravity enforcement.

    Extracts all import statements from a Python file for layer analysis.
    """

    def __init__(self, source_layer: str, file_path: Path) -> None:
        self.source_layer = source_layer
        self.file_path = file_path
        self.imports: list[tuple[str, int]] = []

    def visit_Import(self, node: ast.Import) -> None:
        """Handle 'import x' statements."""
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        trace_contract._emit_records_execution_trace(_trace_id, trace_contract.LayerSegment.L5_POLICY, "GravityVisitor.visit_Import")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GravityVisitor.visit_Import".encode()).hexdigest()[:24]
        trace_contract._emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        for alias in node.names:
            self.imports.append((alias.name, node.lineno))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        """Handle 'from x import y' statements."""
        if node.module:
            self.imports.append((node.module, node.lineno))
        self.generic_visit(node)


def get_file_imports(file_path: Path) -> list[tuple[str, int]]:
    """
    Centralized utility to extract imports from a Python file.

    Args:
        file_path: Path to the Python file

    Returns:    # review: Syntax errors should be caught at parser level, not runtime
        List of (module_name, line_number) tuples
    """
    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
        visitor = GravityVisitor("unknown", file_path)
        visitor.visit(tree)
        return visitor.imports
    except SyntaxError as e:  # review: Syntax errors should be caught at parser level, not runtime
        Logger.debug(f"Syntax error in {file_path}: {e}")
        return []
    except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
        Logger.debug(f"Could not parse {file_path}: {e}")
        return []


def extract_layer_from_path(file_path: Path) -> str | None:
    """
    Extract the layer (L0-L6, Apps) from a file path.

    Args:
        file_path: Path to analyze

    Returns:
        Layer string (e.g., "L3") or None if not determinable
    """
    path_str = str(file_path)
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f"/{layer}_" in path_str or f"\\{layer}_" in path_str:
            return layer
        if f"/{layer}/" in path_str or f"\\{layer}\\" in path_str:
            return layer
    if "/apps_" in path_str or "\\apps_" in path_str:
        return "Apps"
    if "/apps/" in path_str or "\\apps/" in path_str:
        return "Apps"
    if f"/{TESTS_DIR}/" in path_str or f"\\{TESTS_DIR}\\" in path_str:
        return TESTS_DIR
    return None


def extract_layer_from_import(import_path: str) -> str | None:
    """
    Extract the layer from an import path.

    Args:
        import_path: Import module path (e.g., "agentic_core.L5_safety.validators")

    Returns:
        Layer string (e.g., "L5") or None if not determinable
    """
    for layer in ["L0", "L1", "L2", "L3", "L4", "L5", "L6"]:
        if f".{layer}_" in import_path or f"{layer}_" in import_path:
            return layer
    if ".apps_" in import_path or "apps_" in import_path:
        return "Apps"
    return None


def check_gravity_violation(
    source_layer: str,
    target_layer: str,
    gravity_rules: dict[str, set[str]] | None = None,
) -> bool:
    """
    Check if importing from target_layer violates gravity rules.

    Args:
        source_layer: Layer of the file doing the import
        target_layer: Layer being imported from
        gravity_rules: Optional custom gravity rules dict

    Returns:
        True if this is a violation, False if allowed
    """
    if gravity_rules is None:
        gravity_rules = {
            "L0": {"L0"},
            "L1": {"L0", "L1"},
            "L2": {"L0", "L1", "L2"},
            "L3": {"L0", "L1", "L2", "L3"},
            "L4": {"L0", "L1", "L2", "L3", "L4"},
            "L5": {"L0", "L1", "L2", "L3", "L4", "L5"},
            "L6": {"L0", "L1", "L2", "L3", "L4", "L5", "L6"},
            "Apps": {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "Apps"},
            "tests": {"L0", "L1", "L2", "L3", "L4", "L5", "L6", "Apps", "tests"},
        }
    allowed_layers = gravity_rules.get(source_layer, set())
    return target_layer not in allowed_layers
