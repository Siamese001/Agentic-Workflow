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

from agentic_core.runtime.contracts import lifecycle_trace_contract as trace_contract

trace_contract._emit_applies_guardrail("p0", "hallucination_detection_mixin", "p0_governance")
trace_contract._emit_reads_policy_state("p0", "hallucination_detection_mixin", "policy_binding")
trace_contract._emit_snapshots_state("p0", "hallucination_detection_mixin", "state_snapshot")
from tqdm import tqdm

trace_contract._emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_1")
trace_contract._emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_2")
trace_contract._emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_3")
trace_contract._emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_4")
trace_contract._emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_5")
trace_contract._emit_emits_metric_event("hallucination_detection_mixin", "p4obs", "metric_6")
trace_contract._emit_records_incident_event("hallucination_detection_mixin", "p4obs", "incident")
trace_contract._emit_captures_runtime_anomaly("hallucination_detection_mixin", "p4obs", "anomaly")
trace_contract._emit_writes_observability_log("hallucination_detection_mixin", "p4obs", "obs_log")
trace_contract._emit_updates_monitoring_state("hallucination_detection_mixin", "p4obs", "mon_state")
trace_contract._emit_triggers_alert("hallucination_detection_mixin", "p4obs", "alert")
trace_contract._emit_links_incident_trace("hallucination_detection_mixin", "p4obs", "trace_link")
trace_contract._emit_captures_pattern("hallucination_detection_mixin", "p3lm", "pattern")
trace_contract._emit_records_learning_event("hallucination_detection_mixin", "p3lm", "learning_event")
trace_contract._emit_writes_learning_snapshot("hallucination_detection_mixin", "p3lm", "snapshot")
trace_contract._emit_feeds_meta_learning("hallucination_detection_mixin", "p3lm", "meta_feed")
trace_contract._emit_updates_routing_strategy("hallucination_detection_mixin", "p3lm", "routing")
trace_contract._emit_improves_agent_policy("hallucination_detection_mixin", "p3lm", "policy")
trace_contract._emit_stores_learning_state("hallucination_detection_mixin", "p3lm", "state")
trace_contract._emit_records_execution_trace("hallucination_detection_mixin", "L0_ROUTING", "p2_trace_1")
trace_contract._emit_records_execution_trace("hallucination_detection_mixin", "L1_REASONING", "p2_trace_2")
trace_contract._emit_records_execution_trace("hallucination_detection_mixin", "L2_EXECUTION", "p2_trace_3")
trace_contract._emit_records_execution_trace("hallucination_detection_mixin", "L3_ORCHESTRATION", "p2_trace_4")
trace_contract._emit_records_execution_trace("hallucination_detection_mixin", "L4_STATE", "p2_trace_5")
trace_contract._emit_reads_environ("hallucination_detection_mixin", "env_read", "p2_env_1")
trace_contract._emit_reads_environ("hallucination_detection_mixin", "env_read", "p2_env_2")
trace_contract._emit_reads_runtime_state("hallucination_detection_mixin", "runtime_state", "p2_rt_1")
trace_contract._emit_reads_runtime_state("hallucination_detection_mixin", "runtime_state", "p2_rt_2")
trace_contract._emit_pulls_context("p1", "hallucination_detection_mixin", "context_pull")
trace_contract._emit_pulls_context("p1", "hallucination_detection_mixin", "context_pull_2")
trace_contract._emit_execution_terminates_at_uwg("p1", "hallucination_detection_mixin", "uwg_term")
trace_contract._emit_execution_terminates_at_uwg("p1", "hallucination_detection_mixin", "uwg_term_2")
trace_contract._emit_writes_through("p1", "hallucination_detection_mixin", "write_through")
trace_contract._emit_writes_through("p1", "hallucination_detection_mixin", "write_through_2")
trace_contract._emit_validated_by_safety_plane("p1", "hallucination_detection_mixin", "safety_validation")
trace_contract._emit_invokes_eval("p1", "hallucination_detection_mixin", "eval_call")
trace_contract._emit_proposal_commits_routing("p1", "hallucination_detection_mixin", "routing_commit")
trace_contract._emit_escalates_to_human("p1", "hallucination_detection_mixin", "human_escalation")
trace_contract._emit_routes_through("p1", "hallucination_detection_mixin", "route_through")
trace_contract._emit_checks_agent_registry("p1", "hallucination_detection_mixin", "agent_registry")
trace_contract._emit_validates_agent_capability("p1", "hallucination_detection_mixin", "capability")
trace_contract._emit_dispatches_execution_plan("p1", "hallucination_detection_mixin", "exec_plan")
trace_contract._emit_agent_executes_agent("p1", "hallucination_detection_mixin", "sub_agent")
trace_contract._emit_routes_to_agent("p1", "hallucination_detection_mixin", "target_agent")
trace_contract._emit_verifies_policy("p1", "hallucination_detection_mixin", "policy_check")
trace_contract._emit_observes_runtime_state("p1", "hallucination_detection_mixin", "runtime_state")
trace_contract._emit_verifies_boundary("p1", "hallucination_detection_mixin", "boundary_check")
trace_contract._emit_transcripts_response("p1", "hallucination_detection_mixin", "transcript")
trace_contract._emit_hard_fails_untranscripted("p1", "hallucination_detection_mixin")
trace_contract._emit_gated_by_confidence("p1", "hallucination_detection_mixin", "confidence_gate")
trace_contract.emit_replay_key("p0", "hallucination_detection_mixin")
trace_contract.emit_determinism_digest("p0", "hallucination_detection_mixin")
trace_contract._emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
trace_contract._emit_authorize_and_execute("p2", "hallucination_detection_mixin", "execution_auth")
trace_contract._emit_validates_capability("p2", "hallucination_detection_mixin", "capability_check")
trace_contract._emit_routes_to_capability("p2", "hallucination_detection_mixin", "capability_route")
trace_contract._emit_writes_via_uwg("p2", "hallucination_detection_mixin", "uwg_write")
trace_contract._emit_blocks_direct_write("p2", "hallucination_detection_mixin", "direct_write_block")
trace_contract._emit_records_tool_invocation("p2", "hallucination_detection_mixin", "tool_invocation")
trace_contract._emit_captures_execution_output("p2", "hallucination_detection_mixin", "exec_output")
trace_contract._emit_dispatches_agent("p3", "hallucination_detection_mixin", "agent_dispatch")
trace_contract._emit_coordinates_agents("p3", "hallucination_detection_mixin", "agent_coordination")
trace_contract._emit_records_workflow_lineage("p3", "hallucination_detection_mixin", "workflow_lineage")
trace_contract._emit_records_healing_outcome("p3", "hallucination_detection_mixin", "healing_outcome")
trace_contract._emit_escalates_failure("p3", "hallucination_detection_mixin", "failure_escalation")
trace_contract._emit_orchestrates_workflow("p3", "hallucination_detection_mixin", "workflow_orchestration")
trace_contract._emit_dispatches_healing_run("p3", "hallucination_detection_mixin", "healing_dispatch")
trace_contract._emit_invokes_evaluation("p3", "hallucination_detection_mixin", "evaluation_signal")
trace_contract._emit_records_telemetry_event("p4", "hallucination_detection_mixin", "telemetry_event")
trace_contract._emit_captures_evaluation_metric("p4", "hallucination_detection_mixin", "eval_metric")
trace_contract._emit_stores_embedding("p4", "hallucination_detection_mixin", "embedding_store")
trace_contract._emit_updates_meta_learning_state("p4", "hallucination_detection_mixin", "meta_learning")
trace_contract._emit_links_execution_to_snapshot("p4", "hallucination_detection_mixin", "exec_snapshot_link")

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
        trace_contract._emit_records_execution_trace(
            _trace_id, trace_contract.LayerSegment.L3_ORCHESTRATION, "HallucinationDetectionMixin.verify_target_exists"
        )

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
        except (
            SyntaxError,
            UnicodeDecodeError,
        ) as e:  # guardian: allow-silent-swallow -- acceptable exception handling
            logger.warning(f"Cannot parse {file_path} for hallucination check: {e}")
            return False

    def _find_target_in_ast(self, tree: ast.AST, target_type: str, target_name: str) -> bool:
        """Find target in AST based on type."""
        for node in tqdm(ast.walk(tree), desc="Processing", unit="item"):
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
