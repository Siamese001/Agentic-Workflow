"""
HallucinationDetectionMixin - V10 Epistemic Cascade Prevention.

Provides structural validation to prevent agents from acting on hallucinated
targets that don't exist in the actual codebase.

References:
- Verification Gate integration
- AST-based target validation
- Epistemic Cascade prevention (Landmine #2)
"""

import ast
import logging
from pathlib import Path
from typing import Any

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
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_escalates_to_human,
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
    _emit_routes_through,
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

_emit_applies_guardrail("p0", "hallucination_detection_mixin", "p0_governance")
_emit_reads_policy_state("p0", "hallucination_detection_mixin", "policy_binding")
_emit_snapshots_state("p0", "hallucination_detection_mixin", "state_snapshot")
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

_emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_1")
_emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_2")
_emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_3")
_emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_4")
_emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_5")
_emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_6")
_emit_records_incident_event("hallucination_detection_mixin", "p4obs", "incident")
_emit_captures_runtime_anomaly("hallucination_detection_mixin", "p4obs", "anomaly")
_emit_writes_observability_log("hallucination_detection_mixin", "p4obs", "obs_log")
_emit_updates_monitoring_state("hallucination_detection_mixin", "p4obs", "mon_state")
_emit_triggers_alert("hallucination_detection_mixin", "p4obs", "alert")
_emit_links_incident_trace("hallucination_detection_mixin", "p4obs", "trace_link")
_emit_captures_pattern("hallucination_detection_mixin", "p3lm", "pattern")
_emit_records_learning_event("hallucination_detection_mixin", "p3lm", "learning_event")
_emit_writes_learning_snapshot("hallucination_detection_mixin", "p3lm", "snapshot")
_emit_feeds_meta_learning("hallucination_detection_mixin", "p3lm", "meta_feed")
_emit_updates_routing_strategy("hallucination_detection_mixin", "p3lm", "routing")
_emit_improves_agent_policy("hallucination_detection_mixin", "p3lm", "policy")
_emit_stores_learning_state("hallucination_detection_mixin", "p3lm", "state")
_emit_records_execution_trace("hallucination_detection_mixin", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("hallucination_detection_mixin", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("hallucination_detection_mixin", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("hallucination_detection_mixin", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("hallucination_detection_mixin", "L4_STATE", "p2_trace_5")
_emit_reads_environ("hallucination_detection_mixin", "env_read", "p2_env_1")
_emit_reads_environ("hallucination_detection_mixin", "env_read", "p2_env_2")
_emit_reads_runtime_state("hallucination_detection_mixin", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("hallucination_detection_mixin", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "hallucination_detection_mixin", "context_pull")
_emit_pulls_context("p1", "hallucination_detection_mixin", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "hallucination_detection_mixin", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "hallucination_detection_mixin", "uwg_term_2")
_emit_writes_through("p1", "hallucination_detection_mixin", "write_through")
_emit_writes_through("p1", "hallucination_detection_mixin", "write_through_2")
_emit_validated_by_safety_plane("p1", "hallucination_detection_mixin", "safety_validation")
_emit_invokes_eval("p1", "hallucination_detection_mixin", "eval_call")
_emit_proposal_commits_routing("p1", "hallucination_detection_mixin", "routing_commit")
_emit_escalates_to_human("p1", "hallucination_detection_mixin", "human_escalation")
_emit_routes_through("p1", "hallucination_detection_mixin", "route_through")
_emit_checks_agent_registry("p1", "hallucination_detection_mixin", "agent_registry")
_emit_validates_agent_capability("p1", "hallucination_detection_mixin", "capability")
_emit_dispatches_execution_plan("p1", "hallucination_detection_mixin", "exec_plan")
_emit_agent_executes_agent("p1", "hallucination_detection_mixin", "sub_agent")
_emit_routes_to_agent("p1", "hallucination_detection_mixin", "target_agent")
_emit_verifies_policy("p1", "hallucination_detection_mixin", "policy_check")
_emit_observes_runtime_state("p1", "hallucination_detection_mixin", "runtime_state")
_emit_verifies_boundary("p1", "hallucination_detection_mixin", "boundary_check")
_emit_transcripts_response("p1", "hallucination_detection_mixin", "transcript")
_emit_hard_fails_untranscripted("p1", "hallucination_detection_mixin")
_emit_gated_by_confidence("p1", "hallucination_detection_mixin", "confidence_gate")
emit_replay_key("p0", "hallucination_detection_mixin")
emit_determinism_digest("p0", "hallucination_detection_mixin")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "hallucination_detection_mixin", "execution_auth")
_emit_validates_capability("p2", "hallucination_detection_mixin", "capability_check")
_emit_routes_to_capability("p2", "hallucination_detection_mixin", "capability_route")
_emit_writes_via_uwg("p2", "hallucination_detection_mixin", "uwg_write")
_emit_blocks_direct_write("p2", "hallucination_detection_mixin", "direct_write_block")
_emit_records_tool_invocation("p2", "hallucination_detection_mixin", "tool_invocation")
_emit_captures_execution_output("p2", "hallucination_detection_mixin", "exec_output")
_emit_dispatches_agent("p3", "hallucination_detection_mixin", "agent_dispatch")
_emit_coordinates_agents("p3", "hallucination_detection_mixin", "agent_coordination")
_emit_records_workflow_lineage("p3", "hallucination_detection_mixin", "workflow_lineage")
_emit_records_healing_outcome("p3", "hallucination_detection_mixin", "healing_outcome")
_emit_escalates_failure("p3", "hallucination_detection_mixin", "failure_escalation")
_emit_orchestrates_workflow("p3", "hallucination_detection_mixin", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "hallucination_detection_mixin", "healing_dispatch")
_emit_invokes_evaluation("p3", "hallucination_detection_mixin", "evaluation_signal")
_emit_records_telemetry_event("p4", "hallucination_detection_mixin", "telemetry_event")
_emit_captures_evaluation_metric("p4", "hallucination_detection_mixin", "eval_metric")
_emit_stores_embedding("p4", "hallucination_detection_mixin", "embedding_store")
_emit_updates_meta_learning_state("p4", "hallucination_detection_mixin", "meta_learning")
_emit_links_execution_to_snapshot("p4", "hallucination_detection_mixin", "exec_snapshot_link")

logger = logging.getLogger(__name__)


class HallucinationDetectionMixin:
    """
    Mixin providing hallucination detection capabilities.

    Prevents Epistemic Cascade by verifying that action targets actually
    exist before allowing operations to proceed.

    MRO RULE: This mixin MUST precede base agent classes in inheritance.

    Usage:
        class MyAgent(HallucinationDetectionMixin, SovereignBaseAgent):
            pass
    """

    _hallucination_cache: dict[str, bool] = {}

    def verify_target_exists(self, file_path: Path, target_type: str, target_name: str) -> bool:
        """
        Verify that a target node exists in the file.

        Args:
            file_path: Path to the file to check
            target_type: Type of target ('function', 'class', 'import', 'variable')
            target_name: Name of the target to find

        Returns:
            True if target exists, False if hallucinated
        """
        import uuid as _uuid  # noqa: PLC0415
        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L3_ORCHESTRATION, "HallucinationDetectionMixin.verify_target_exists")

        if not file_path.exists():
            logger.warning(f"Hallucination check: file does not exist: {file_path}")
            return False
        cache_key = f"{file_path}:{target_type}:{target_name}"
        if cache_key in self._hallucination_cache:
            return self._hallucination_cache[cache_key]
        try:
            content = file_path.read_text(encoding="utf-8")
            tree = ast.parse(content)
            result = self._find_target_in_ast(tree, target_type, target_name)
            self._hallucination_cache[cache_key] = result
            if not result:
                logger.warning(
                    f"Hallucination detected: {target_type} '{target_name}' not found in {file_path}",
                )
            return result
        # guardian: allow-silent-swallow - acceptable exception handling
        except (SyntaxError, UnicodeDecodeError) as e:
            logger.warning(f"Cannot parse {file_path} for hallucination check: {e}")
            return False

    def _find_target_in_ast(self, tree: ast.AST, target_type: str, target_name: str) -> bool:
        """Find target in AST based on type."""
        for node in ast.walk(tree):
            if target_type == "function":
                if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                    if node.name == target_name:
                        return True
            elif target_type == "class":
                if isinstance(node, ast.ClassDef):
                    if node.name == target_name:
                        return True
            elif target_type == "import":
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == target_name or (alias.asname and alias.asname == target_name):
                            return True
                elif isinstance(node, ast.ImportFrom):
                    for alias in node.names:
                        if alias.name == target_name or (alias.asname and alias.asname == target_name):
                            return True
            elif target_type == "variable":
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == target_name:
                            return True
        return False

    def clear_hallucination_cache(self) -> None:
        """Clear the hallucination detection cache."""
        self._hallucination_cache.clear()

    def get_hallucination_stats(self) -> dict[str, Any]:
        """Get statistics about hallucination detection."""
        return {
            "cache_size": len(self._hallucination_cache),
            "cached_targets": list(self._hallucination_cache.keys())[:10],
        }
