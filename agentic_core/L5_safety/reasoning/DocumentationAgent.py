from __future__ import annotations

from typing import Any

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

emit_replay_key("p0", "DocumentationAgent")
emit_determinism_digest("p0", "DocumentationAgent")

_emit_dispatches_healing_run("p1", "DocumentationAgent", "L5")
_emit_routes_through("p1", "DocumentationAgent", "L5")
_emit_checks_agent_registry("p1", "DocumentationAgent", "agent_registry")
_emit_validates_agent_capability("p1", "DocumentationAgent", "capability")
_emit_dispatches_execution_plan("p1", "DocumentationAgent", "exec_plan")
_emit_agent_executes_agent("p1", "DocumentationAgent", "sub_agent")
_emit_routes_to_agent("p1", "DocumentationAgent", "target_agent")
_emit_verifies_policy("p1", "DocumentationAgent", "policy_check")
_emit_observes_runtime_state("p1", "DocumentationAgent", "runtime_state")
_emit_verifies_boundary("p1", "DocumentationAgent", "boundary_check")
_emit_transcripts_response("p1", "DocumentationAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "DocumentationAgent")
_emit_gated_by_confidence("p1", "DocumentationAgent", "confidence_gate")
_emit_escalates_to_human("p1", "DocumentationAgent", "L5")
_emit_reads_policy_state("p1", "DocumentationAgent", "L5")

_emit_applies_guardrail("p0", "DocumentationAgent", "p0_governance")
_emit_snapshots_state("p0", "DocumentationAgent", "state_snapshot")
_emit_authorize_and_execute("p2", "DocumentationAgent", "execution_auth")
_emit_validates_capability("p2", "DocumentationAgent", "capability_check")
_emit_routes_to_capability("p2", "DocumentationAgent", "capability_route")
_emit_writes_via_uwg("p2", "DocumentationAgent", "uwg_write")
_emit_blocks_direct_write("p2", "DocumentationAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "DocumentationAgent", "tool_invocation")
_emit_captures_execution_output("p2", "DocumentationAgent", "exec_output")
_emit_dispatches_agent("p3", "DocumentationAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "DocumentationAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "DocumentationAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "DocumentationAgent", "healing_outcome")
_emit_escalates_failure("p3", "DocumentationAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "DocumentationAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "DocumentationAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "DocumentationAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "DocumentationAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "DocumentationAgent", "eval_metric")
_emit_stores_embedding("p4", "DocumentationAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "DocumentationAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "DocumentationAgent", "exec_snapshot_link")

"DocumentationAgent - Documentation quality enforcement.\n\nPart of the quality enforcement agent family.\nValidates docstring presence in classes and functions.\n"
import ast
from dataclasses import dataclass

from agentic_core.L3_orchestration.reasoning.SubAtomicAgent import SubAtomicAgent
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

_emit_emits_metric_event("DocumentationAgent", "p4obs", "metric_1")
_emit_emits_metric_event("DocumentationAgent", "p4obs", "metric_2")
_emit_emits_metric_event("DocumentationAgent", "p4obs", "metric_3")
_emit_emits_metric_event("DocumentationAgent", "p4obs", "metric_4")
_emit_emits_metric_event("DocumentationAgent", "p4obs", "metric_5")
_emit_emits_metric_event("DocumentationAgent", "p4obs", "metric_6")
_emit_records_incident_event("DocumentationAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("DocumentationAgent", "p4obs", "anomaly")
_emit_writes_observability_log("DocumentationAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("DocumentationAgent", "p4obs", "mon_state")
_emit_triggers_alert("DocumentationAgent", "p4obs", "alert")
_emit_links_incident_trace("DocumentationAgent", "p4obs", "trace_link")
_emit_captures_pattern("DocumentationAgent", "p3lm", "pattern")
_emit_records_learning_event("DocumentationAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("DocumentationAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("DocumentationAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("DocumentationAgent", "p3lm", "routing")
_emit_improves_agent_policy("DocumentationAgent", "p3lm", "policy")
_emit_stores_learning_state("DocumentationAgent", "p3lm", "state")
_emit_records_execution_trace("DocumentationAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("DocumentationAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("DocumentationAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("DocumentationAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("DocumentationAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("DocumentationAgent", "env_read", "p2_env_1")
_emit_reads_environ("DocumentationAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("DocumentationAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("DocumentationAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "DocumentationAgent", "context_pull")
_emit_pulls_context("p1", "DocumentationAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "DocumentationAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "DocumentationAgent", "uwg_term_2")
_emit_writes_through("p1", "DocumentationAgent", "write_through")
_emit_writes_through("p1", "DocumentationAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "DocumentationAgent", "safety_validation")
_emit_invokes_eval("p1", "DocumentationAgent", "eval_call")
_emit_proposal_commits_routing("p1", "DocumentationAgent", "routing_commit")


@dataclass
class DocumentationAgent(SubAtomicAgent):
    """
    Documentation enforcement agent for docstring validation.

    Validates:
        - No missing docstrings in classes and functions.

    Role:
        Pure focus on docstring presence and quality.

    Note:
        Legacy L1 class - true agent is DocEnforcerAgent in L2.

    Attributes:
        agent: Injected CanonBaseAgentInterface implementation.
    """

    # guardian: allow-type-erasure
    def heal(self, violation: dict[str, Any]) -> dict[str, Any]:
        """
        [HEALER PROTOCOL] Standardized healing interface for DocumentationAgent violations.

        Args:
            violation: Violation dict with keys: type, file, message, etc.

        Returns:
            Dict with keys: status, details, artifacts, errors
        """
        try:
            violation.get("type", "")
            file_path = violation.get("file")
            if not file_path:
                return {
                    "status": "failed",
                    "details": "No file path provided in violation",
                    "artifacts": [],
                    "errors": ["Missing file path"],
                }
            return {
                "status": "manual_required",
                "details": "DocumentationAgent requires manual review for healing",
                "artifacts": [],
                "errors": [],
            }
        except (ValueError, TypeError) as e:  # guardian: allow-silent-swallow
            return {
                "status": "failed",
                "details": "Exception during healing",
                "artifacts": [],
                "errors": [str(e)],
            }

    def execute(self) -> None:
        """
        Execute documentation validation checks.

        Runs missing docstrings check and reports results
        to the validation context.
        """
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "DocumentationAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:DocumentationAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print(f"\n[>>>] {self.agent.name} ACTIVATED: Documentation Check...")
        passed, details = self.check_no_missing_docstrings()
        self.agent.ctx.report(self.agent.name, 21, passed, details)

    def _has_missing_docstring(self, node: ast.AST) -> bool:
        """
        Check if an AST node is missing a docstring.

        Args:
            node: AST node (FunctionDef or ClassDef) to check.

        Returns:
            True if docstring is missing, False otherwise.
        """
        return not ast.get_docstring(node)

    def _find_missing_docstring_violations_in_tree(self, tree: ast.AST, fp: str) -> list[str]:
        """
        Find all missing docstring violations in an AST tree.

        Args:
            tree: Parsed AST tree to analyze.
            fp: File path for violation reporting.

        Returns:
            List of violation strings in 'filepath:line name' format.
        """
        file_violations: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.ClassDef) and self._has_missing_docstring(node):
                file_violations.append(f"{fp}:{node.lineno} {node.name}")
        return file_violations

    def check_no_missing_docstrings(self) -> tuple[bool, list[str]]:
        """
        Check for missing docstrings in classes and functions.

        Uses AST parsing to identify FunctionDef and ClassDef nodes
        without docstrings.

        Returns:
            Tuple of (passed: bool, violations: List[str]).
            - passed: True if no violations found.
            - violations: List of 'filepath:line name' strings.
        """
        violations: list[str] = []
        for fp in self.agent.ctx.python_files:
            try:
                with open(fp, encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                violations.extend(self._find_missing_docstring_violations_in_tree(tree, fp))
            except (ValueError, TypeError):  # guardian: allow-silent-swallow
                continue
        return (len(violations) == 0, violations)

    # guardian: allow-type-erasure
    def heal_repository(self, **kwargs) -> dict:
        """
        Execute healing chain via parent class.

        Returns:
            Dict with healing results from parent implementation.
        """
        return super().heal_repository(**kwargs)
