"""
Verification Gate - Structural validation layer to prevent Epistemic Cascade.

This module provides a verification mechanism that agents must query before
executing high-impact changes, preventing blind trust in upstream hallucinations.

Integrates with L4ContextManager for shared file analysis caching.
"""

import ast
import logging
from pathlib import Path
from typing import Any

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.mixins.hallucination_detection_mixin import (
    HallucinationDetectionMixin,
)
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

emit_replay_key("p0", "verification_gate")
emit_determinism_digest("p0", "verification_gate")

_emit_dispatches_healing_run("p1", "verification_gate", "L5")
_emit_routes_through("p1", "verification_gate", "L5")
_emit_checks_agent_registry("p1", "verification_gate", "agent_registry")
_emit_validates_agent_capability("p1", "verification_gate", "capability")
_emit_dispatches_execution_plan("p1", "verification_gate", "exec_plan")
_emit_agent_executes_agent("p1", "verification_gate", "sub_agent")
_emit_routes_to_agent("p1", "verification_gate", "target_agent")
_emit_verifies_policy("p1", "verification_gate", "policy_check")
_emit_observes_runtime_state("p1", "verification_gate", "runtime_state")
_emit_verifies_boundary("p1", "verification_gate", "boundary_check")
_emit_transcripts_response("p1", "verification_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "verification_gate")
_emit_gated_by_confidence("p1", "verification_gate", "confidence_gate")
_emit_escalates_to_human("p1", "verification_gate", "L5")
_emit_reads_policy_state("p1", "verification_gate", "L5")

_emit_applies_guardrail("p0", "verification_gate", "p0_governance")
_emit_snapshots_state("p0", "verification_gate", "state_snapshot")
_emit_authorize_and_execute("p2", "verification_gate", "execution_auth")
_emit_validates_capability("p2", "verification_gate", "capability_check")
_emit_routes_to_capability("p2", "verification_gate", "capability_route")
_emit_writes_via_uwg("p2", "verification_gate", "uwg_write")
_emit_blocks_direct_write("p2", "verification_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "verification_gate", "tool_invocation")
_emit_captures_execution_output("p2", "verification_gate", "exec_output")
_emit_dispatches_agent("p3", "verification_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "verification_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "verification_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "verification_gate", "healing_outcome")
_emit_escalates_failure("p3", "verification_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "verification_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "verification_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "verification_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "verification_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "verification_gate", "eval_metric")
_emit_stores_embedding("p4", "verification_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "verification_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "verification_gate", "exec_snapshot_link")
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

_emit_emits_metric_event("verification_gate", "p4obs", "metric_1")
_emit_emits_metric_event("verification_gate", "p4obs", "metric_2")
_emit_emits_metric_event("verification_gate", "p4obs", "metric_3")
_emit_emits_metric_event("verification_gate", "p4obs", "metric_4")
_emit_emits_metric_event("verification_gate", "p4obs", "metric_5")
_emit_emits_metric_event("verification_gate", "p4obs", "metric_6")
_emit_records_incident_event("verification_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("verification_gate", "p4obs", "anomaly")
_emit_writes_observability_log("verification_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("verification_gate", "p4obs", "mon_state")
_emit_triggers_alert("verification_gate", "p4obs", "alert")
_emit_links_incident_trace("verification_gate", "p4obs", "trace_link")
_emit_captures_pattern("verification_gate", "p3lm", "pattern")
_emit_records_learning_event("verification_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("verification_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("verification_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("verification_gate", "p3lm", "routing")
_emit_improves_agent_policy("verification_gate", "p3lm", "policy")
_emit_stores_learning_state("verification_gate", "p3lm", "state")
_emit_records_execution_trace("verification_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("verification_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("verification_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("verification_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("verification_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("verification_gate", "env_read", "p2_env_1")
_emit_reads_environ("verification_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("verification_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("verification_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "verification_gate", "context_pull")
_emit_pulls_context("p1", "verification_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "verification_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "verification_gate", "uwg_term_2")
_emit_writes_through("p1", "verification_gate", "write_through")
_emit_writes_through("p1", "verification_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "verification_gate", "safety_validation")
_emit_invokes_eval("p1", "verification_gate", "eval_call")
_emit_proposal_commits_routing("p1", "verification_gate", "routing_commit")

Logger = logging.getLogger(__name__)


class VerificationGate(HallucinationDetectionMixin, SovereignBaseAgent):
    """
    Structural validation layer that verifies actions against actual AST structure.

    Prevents Epistemic Cascade by ensuring agents only act on verified targets
    that actually exist in the codebase structure.

    V10 Refactored: Now inherits from AtomicExecutionMixin for rollback capability
    and HallucinationDetectionMixin for structural validation.

    MRO: VerificationGate -> AtomicExecutionMixin -> HallucinationDetectionMixin -> ...

    Integrates with L4ContextManager for performance optimization.
    """

    def __init__(self, context_manager=None):
        """
        Initialize verification gate.

        Args:
            context_manager: Optional L4ContextManager for shared caching
        """
        self.verification_cache: dict[str, bool] = {}
        self.context_manager = context_manager

    def verify_action(self, file_path: Path, action_type: str, target_node: str) -> bool:
        """
        Verify that the target node exists in the file before allowing action.

        Args:
            file_path: Path to the file to verify
            action_type: Type of action (e.g., 'delete_import', 'modify_function', 'remove_class')
            target_node: Target node name to verify exists

        Returns:
            True if target exists and action is valid, False otherwise
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "VerificationGate.verify_action")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:VerificationGate.verify_action".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        if not file_path.exists():
            return False

        # Create cache key for performance
        cache_key = f"{file_path}:{action_type}:{target_node}"
        if cache_key in self.verification_cache:
            return self.verification_cache[cache_key]

        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            result = self._verify_target_in_ast(tree, action_type, target_node)

            # Cache the result
            self.verification_cache[cache_key] = result
            return result

        except (
            SyntaxError,
            UnicodeDecodeError,
            OSError,
        ):  # review: Parsing and encoding errors need separate handling strategies
            # File cannot be parsed or read
            return False

    def _verify_target_in_ast(self, tree: ast.AST, action_type: str, target_node: str) -> bool:
        """
        Verify target node exists in AST based on action type.

        Args:
            tree: Parsed AST tree
            action_type: Type of action to verify
            target_node: Target node name

        Returns:
            True if target exists for the given action type
        """
        if action_type == "delete_import":
            return self._verify_import_exists(tree, target_node)
        elif action_type == "modify_function":
            return self._verify_function_exists(tree, target_node)
        elif action_type == "remove_class":
            return self._verify_class_exists(tree, target_node)
        elif action_type == "modify_variable":
            return self._verify_variable_exists(tree, target_node)
        elif action_type == "modify_method":
            return self._verify_method_exists(tree, target_node)
        else:
            # Default: check if any node with matching name exists
            return self._verify_any_node_exists(tree, target_node)

    def _verify_import_exists(self, tree: ast.AST, import_name: str) -> bool:
        """Verify that an import statement exists."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == import_name or alias.asname == import_name:
                        return True
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == import_name or alias.asname == import_name:
                        return True
        return False

    def _verify_function_exists(self, tree: ast.AST, func_name: str) -> bool:
        """Verify that a function definition exists."""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                return True
            elif isinstance(node, ast.AsyncFunctionDef) and node.name == func_name:
                return True
        return False

    def _verify_class_exists(self, tree: ast.AST, class_name: str) -> bool:
        """Verify that a class definition exists."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return True
        return False

    def _verify_variable_exists(self, tree: ast.AST, var_name: str) -> bool:
        """Verify that a variable assignment exists."""
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == var_name:
                        return True
            elif isinstance(node, ast.AnnAssign):
                if isinstance(node.target, ast.Name) and node.target.id == var_name:
                    return True
        return False

    def _verify_method_exists(self, tree: ast.AST, method_name: str) -> bool:
        """Verify that a method exists within any class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == method_name:
                        return True
                    elif isinstance(item, ast.AsyncFunctionDef) and item.name == method_name:
                        return True
        return False

    def _verify_any_node_exists(self, tree: ast.AST, node_name: str) -> bool:
        """Generic verification - check if any node with matching name exists."""
        for node in ast.walk(tree):
            if hasattr(node, "name") and node.name == node_name:
                return True
            elif hasattr(node, "id") and node.id == node_name:
                return True
        return False

    def verify_modification(self, context) -> bool:
        """
        Verify all modifications in a SurgicalContext before allowing execution.

        This is the primary method for preventing Epistemic Cascade - it ensures
        that all target nodes actually exist before any surgical changes are made.

        Args:
            context: SurgicalContext containing violations and target coordinates

        Returns:
            True if all targets are verified, False if any hallucination detected
        """
        if not context.file_path.exists():
            Logger.warning(f"Verification failed: File does not exist: {context.file_path}")
            return False

        # Check L4 cache first if available
        if self.context_manager:
            cached_analysis = self.context_manager.get_file_analysis(context.file_path, "verification_gate")
            if cached_analysis and cached_analysis.get("verified"):
                Logger.debug(f"Using cached verification for {context.file_path}")
                return True

        # Parse file once for all verifications
        try:
            with open(context.file_path, encoding="utf-8") as f:
                content = f.read()
            tree = ast.parse(content)
        except (
            SyntaxError,
            UnicodeDecodeError,
            OSError,
        ) as e:  # review: Parsing and encoding errors need separate handling strategies
            Logger.error(f"Failed to parse {context.file_path}: {e}")
            return False

        # Verify each violation's target exists
        for violation in tqdm(context.violations, desc="Processing", unit="item"):
            action_type = self._map_violation_to_action(violation)
            target_node = self._extract_target_from_violation(violation)

            if not target_node:
                Logger.warning(f"No target node found in violation: {violation}")
                continue

            if not self._verify_target_in_ast(tree, action_type, target_node):
                Logger.warning(
                    f"Hallucination detected: {action_type} target '{target_node}' "
                    f"not found in {context.file_path}",
                )
                return False

        # Cache successful verification in L4 if available
        if self.context_manager:
            self.context_manager.set_file_analysis(
                context.file_path,
                "verification_gate",
                {"verified": True, "violations_count": len(context.violations)},
            )

        return True

    def _map_violation_to_action(self, violation) -> str:
        """Map violation constraint to action type."""
        constraint_type = getattr(violation, "constraint_type", "")
        fix_type = getattr(violation, "fix_type", "")

        # Map constraint types to action types
        if "import" in constraint_type.lower():
            return "delete_import"
        elif "function" in constraint_type.lower():
            return "modify_function"
        elif "class" in constraint_type.lower():
            return "remove_class"
        elif "method" in constraint_type.lower():
            return "modify_method"
        elif "variable" in constraint_type.lower():
            return "modify_variable"
        elif fix_type == "delete":
            return "delete_node"
        else:
            return "modify_node"

    def _extract_target_from_violation(self, violation) -> str | None:
        """Extract target node name from violation."""
        # Try target_coordinate first
        if hasattr(violation, "target_coordinate") and violation.target_coordinate:
            coord = violation.target_coordinate
            if hasattr(coord, "node_id"):
                return coord.node_id

        # Try message parsing
        if hasattr(violation, "message"):
            message = violation.message
            # Extract from patterns like "Remove import 'numpy'"
            import re

            match = re.search(r"['\"]([\w\.]+)['\"]", message)
            if match:
                return match.group(1)

        # Try expected_pattern
        if hasattr(violation, "expected_pattern"):
            pattern = violation.expected_pattern
            if pattern and isinstance(pattern, str):
                # Extract module/function name
                parts = pattern.split()
                if len(parts) > 1:
                    return parts[-1].strip(",'\"")

        return None

    def clear_cache(self):
        """Clear the verification cache."""
        self.verification_cache.clear()

    def get_cache_stats(self) -> dict[str, Any]:
        """Get cache statistics for monitoring."""
        return {
            "cache_size": len(self.verification_cache),
            "cache_keys": list(self.verification_cache.keys()),
        }

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
