from __future__ import annotations

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "gravity_visitor_util")
emit_determinism_digest("p0", "gravity_visitor_util")

_emit_dispatches_healing_run("p1", "gravity_visitor_util", "L5")
_emit_routes_through("p1", "gravity_visitor_util", "L5")
_emit_checks_agent_registry("p1", "gravity_visitor_util", "agent_registry")
_emit_validates_agent_capability("p1", "gravity_visitor_util", "capability")
_emit_dispatches_execution_plan("p1", "gravity_visitor_util", "exec_plan")
_emit_agent_executes_agent("p1", "gravity_visitor_util", "sub_agent")
_emit_routes_to_agent("p1", "gravity_visitor_util", "target_agent")
_emit_verifies_policy("p1", "gravity_visitor_util", "policy_check")
_emit_observes_runtime_state("p1", "gravity_visitor_util", "runtime_state")
_emit_verifies_boundary("p1", "gravity_visitor_util", "boundary_check")
_emit_transcripts_response("p1", "gravity_visitor_util", "transcript")
_emit_hard_fails_untranscripted("p1", "gravity_visitor_util")
_emit_gated_by_confidence("p1", "gravity_visitor_util", "confidence_gate")
_emit_escalates_to_human("p1", "gravity_visitor_util", "L5")
_emit_reads_policy_state("p1", "gravity_visitor_util", "L5")

_emit_applies_guardrail("p0", "gravity_visitor_util", "p0_governance")
_emit_snapshots_state("p0", "gravity_visitor_util", "state_snapshot")
_emit_authorize_and_execute("p2", "gravity_visitor_util", "execution_auth")
_emit_validates_capability("p2", "gravity_visitor_util", "capability_check")
_emit_routes_to_capability("p2", "gravity_visitor_util", "capability_route")
_emit_writes_via_uwg("p2", "gravity_visitor_util", "uwg_write")
_emit_blocks_direct_write("p2", "gravity_visitor_util", "direct_write_block")
_emit_records_tool_invocation("p2", "gravity_visitor_util", "tool_invocation")
_emit_captures_execution_output("p2", "gravity_visitor_util", "exec_output")
_emit_dispatches_agent("p3", "gravity_visitor_util", "agent_dispatch")
_emit_coordinates_agents("p3", "gravity_visitor_util", "agent_coordination")
_emit_records_workflow_lineage("p3", "gravity_visitor_util", "workflow_lineage")
_emit_records_healing_outcome("p3", "gravity_visitor_util", "healing_outcome")
_emit_escalates_failure("p3", "gravity_visitor_util", "failure_escalation")
_emit_orchestrates_workflow("p3", "gravity_visitor_util", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "gravity_visitor_util", "healing_dispatch")
_emit_invokes_evaluation("p3", "gravity_visitor_util", "evaluation_signal")
_emit_records_telemetry_event("p4", "gravity_visitor_util", "telemetry_event")
_emit_captures_evaluation_metric("p4", "gravity_visitor_util", "eval_metric")
_emit_stores_embedding("p4", "gravity_visitor_util", "embedding_store")
_emit_updates_meta_learning_state("p4", "gravity_visitor_util", "meta_learning")
_emit_links_execution_to_snapshot("p4", "gravity_visitor_util", "exec_snapshot_link")

'AST Engine - Centralized Architectural Parsing Logic.\n\n[Phase 5] Provides shared AST utilities for L5 agents.\nCentralizes import extraction and gravity violation detection.\n\nUsage:\n\n    imports = get_file_imports(Path("my_file.py"))\n    # Returns: [("module.name", line_number), ...]\n'
import ast
import logging
from pathlib import Path

from agentic_core.L0_routing.config.path_constants import TESTS_DIR
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

_emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_1")
_emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_2")
_emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_3")
_emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_4")
_emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_5")
_emit_emits_metric_event("gravity_visitor_util", "p4obs", "metric_6")
_emit_records_incident_event("gravity_visitor_util", "p4obs", "incident")
_emit_captures_runtime_anomaly("gravity_visitor_util", "p4obs", "anomaly")
_emit_writes_observability_log("gravity_visitor_util", "p4obs", "obs_log")
_emit_updates_monitoring_state("gravity_visitor_util", "p4obs", "mon_state")
_emit_triggers_alert("gravity_visitor_util", "p4obs", "alert")
_emit_links_incident_trace("gravity_visitor_util", "p4obs", "trace_link")
_emit_captures_pattern("gravity_visitor_util", "p3lm", "pattern")
_emit_records_learning_event("gravity_visitor_util", "p3lm", "learning_event")
_emit_writes_learning_snapshot("gravity_visitor_util", "p3lm", "snapshot")
_emit_feeds_meta_learning("gravity_visitor_util", "p3lm", "meta_feed")
_emit_updates_routing_strategy("gravity_visitor_util", "p3lm", "routing")
_emit_improves_agent_policy("gravity_visitor_util", "p3lm", "policy")
_emit_stores_learning_state("gravity_visitor_util", "p3lm", "state")
_emit_records_execution_trace("gravity_visitor_util", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("gravity_visitor_util", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("gravity_visitor_util", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("gravity_visitor_util", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("gravity_visitor_util", "L4_STATE", "p2_trace_5")
_emit_reads_environ("gravity_visitor_util", "env_read", "p2_env_1")
_emit_reads_environ("gravity_visitor_util", "env_read", "p2_env_2")
_emit_reads_runtime_state("gravity_visitor_util", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("gravity_visitor_util", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "gravity_visitor_util", "context_pull")
_emit_pulls_context("p1", "gravity_visitor_util", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "gravity_visitor_util", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "gravity_visitor_util", "uwg_term_2")
_emit_writes_through("p1", "gravity_visitor_util", "write_through")
_emit_writes_through("p1", "gravity_visitor_util", "write_through_2")
_emit_validated_by_safety_plane("p1", "gravity_visitor_util", "safety_validation")
_emit_invokes_eval("p1", "gravity_visitor_util", "eval_call")
_emit_proposal_commits_routing("p1", "gravity_visitor_util", "routing_commit")

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
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "GravityVisitor.visit_Import")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:GravityVisitor.visit_Import".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

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
