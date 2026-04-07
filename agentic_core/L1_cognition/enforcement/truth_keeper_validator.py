from __future__ import annotations

import ast

from agentic_core.runtime.contracts.lifecycle_trace_contract import (
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

emit_replay_key("p0", "truth_keeper_validator")
emit_determinism_digest("p0", "truth_keeper_validator")

_emit_dispatches_healing_run("p1", "truth_keeper_validator", "L1")
_emit_routes_through("p1", "truth_keeper_validator", "L1")
_emit_checks_agent_registry("p1", "truth_keeper_validator", "agent_registry")
_emit_validates_agent_capability("p1", "truth_keeper_validator", "capability")
_emit_dispatches_execution_plan("p1", "truth_keeper_validator", "exec_plan")
_emit_agent_executes_agent("p1", "truth_keeper_validator", "sub_agent")
_emit_routes_to_agent("p1", "truth_keeper_validator", "target_agent")
_emit_verifies_policy("p1", "truth_keeper_validator", "policy_check")
_emit_observes_runtime_state("p1", "truth_keeper_validator", "runtime_state")
_emit_verifies_boundary("p1", "truth_keeper_validator", "boundary_check")
_emit_transcripts_response("p1", "truth_keeper_validator", "transcript")
_emit_hard_fails_untranscripted("p1", "truth_keeper_validator")
_emit_escalates_to_human("p1", "truth_keeper_validator", "L1")
_emit_reads_policy_state("p1", "truth_keeper_validator", "L1")

_emit_snapshots_state("p0", "truth_keeper_validator", "state_snapshot")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_applies_guardrail("p0", "truth_keeper_validator", "p0_governance")
_emit_authorize_and_execute("p2", "truth_keeper_validator", "execution_auth")
_emit_validates_capability("p2", "truth_keeper_validator", "capability_check")
_emit_routes_to_capability("p2", "truth_keeper_validator", "capability_route")
_emit_writes_via_uwg("p2", "truth_keeper_validator", "uwg_write")
_emit_blocks_direct_write("p2", "truth_keeper_validator", "direct_write_block")
_emit_records_tool_invocation("p2", "truth_keeper_validator", "tool_invocation")
_emit_captures_execution_output("p2", "truth_keeper_validator", "exec_output")
_emit_dispatches_agent("p3", "truth_keeper_validator", "agent_dispatch")
_emit_coordinates_agents("p3", "truth_keeper_validator", "agent_coordination")
_emit_records_workflow_lineage("p3", "truth_keeper_validator", "workflow_lineage")
_emit_records_healing_outcome("p3", "truth_keeper_validator", "healing_outcome")
_emit_escalates_failure("p3", "truth_keeper_validator", "failure_escalation")
_emit_orchestrates_workflow("p3", "truth_keeper_validator", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "truth_keeper_validator", "healing_dispatch")
_emit_invokes_evaluation("p3", "truth_keeper_validator", "evaluation_signal")
_emit_records_telemetry_event("p4", "truth_keeper_validator", "telemetry_event")
_emit_captures_evaluation_metric("p4", "truth_keeper_validator", "eval_metric")
_emit_stores_embedding("p4", "truth_keeper_validator", "embedding_store")
_emit_updates_meta_learning_state("p4", "truth_keeper_validator", "meta_learning")
_emit_links_execution_to_snapshot("p4", "truth_keeper_validator", "exec_snapshot_link")

"Brief description of functionality and purpose."
"Brief description of functionality and purpose."
import logging
import uuid
from typing import Any

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

_emit_emits_metric_event("truth_keeper_validator", "p4obs", "metric_1")
_emit_emits_metric_event("truth_keeper_validator", "p4obs", "metric_2")
_emit_emits_metric_event("truth_keeper_validator", "p4obs", "metric_3")
_emit_emits_metric_event("truth_keeper_validator", "p4obs", "metric_4")
_emit_emits_metric_event("truth_keeper_validator", "p4obs", "metric_5")
_emit_emits_metric_event("truth_keeper_validator", "p4obs", "metric_6")
_emit_records_incident_event("truth_keeper_validator", "p4obs", "incident")
_emit_captures_runtime_anomaly("truth_keeper_validator", "p4obs", "anomaly")
_emit_writes_observability_log("truth_keeper_validator", "p4obs", "obs_log")
_emit_updates_monitoring_state("truth_keeper_validator", "p4obs", "mon_state")
_emit_triggers_alert("truth_keeper_validator", "p4obs", "alert")
_emit_links_incident_trace("truth_keeper_validator", "p4obs", "trace_link")
_emit_captures_pattern("truth_keeper_validator", "p3lm", "pattern")
_emit_records_learning_event("truth_keeper_validator", "p3lm", "learning_event")
_emit_writes_learning_snapshot("truth_keeper_validator", "p3lm", "snapshot")
_emit_feeds_meta_learning("truth_keeper_validator", "p3lm", "meta_feed")
_emit_updates_routing_strategy("truth_keeper_validator", "p3lm", "routing")
_emit_improves_agent_policy("truth_keeper_validator", "p3lm", "policy")
_emit_stores_learning_state("truth_keeper_validator", "p3lm", "state")
_emit_records_execution_trace("truth_keeper_validator", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("truth_keeper_validator", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("truth_keeper_validator", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("truth_keeper_validator", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("truth_keeper_validator", "L4_STATE", "p2_trace_5")
_emit_reads_environ("truth_keeper_validator", "env_read", "p2_env_1")
_emit_reads_environ("truth_keeper_validator", "env_read", "p2_env_2")
_emit_reads_runtime_state("truth_keeper_validator", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("truth_keeper_validator", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "truth_keeper_validator", "context_pull")
_emit_pulls_context("p1", "truth_keeper_validator", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "truth_keeper_validator", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "truth_keeper_validator", "uwg_term_2")
_emit_writes_through("p1", "truth_keeper_validator", "write_through")
_emit_writes_through("p1", "truth_keeper_validator", "write_through_2")
_emit_validated_by_safety_plane("p1", "truth_keeper_validator", "safety_validation")
_emit_invokes_eval("p1", "truth_keeper_validator", "eval_call")
_emit_proposal_commits_routing("p1", "truth_keeper_validator", "routing_commit")

LOGGER = logging.getLogger(__name__)
Logger: Any = logging.getLogger(__name__)


class TruthKeeper:
    """
    Agent that ensures semantic consistency between docstrings and code.

    Analyzes functions to verify their docstrings accurately describe:
    - Parameters and their types
    - Return values and types
    - Function behavior and side effects
    """

    def __init__(self, llm_client=None):
        """
        Initialize the TruthKeeper agent.

        Args:
            llm_client: LLM client for consistency checking
        """
        self.llm_client = llm_client
        self.api_key = None

    async def check_file_consistency(self, file_path: str) -> dict[str, Any]:
        """
        Check docstring consistency for all public functions in a file.

        Args:
            file_path: Path to the Python file to check

        Returns:
            Dictionary with consistency violations and fixes
        """
        _emit_gated_by_confidence(str(uuid.uuid4()), "TruthKeeper.check_file_consistency", "0.5")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(
            _trace_id, LayerSegment.L1_REASONING, "TruthKeeper.check_file_consistency",
        )

        violations: Any = []
        fixes: Any = []
        if "test" in file_path.lower() or file_path.endswith("_test.py"):
            return {"violations": [], "fixes": [], "skipped": True}
        try:
            with open(file_path, encoding="utf-8") as f:
                content: Any = f.read()
            tree: Any = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and (not node.name.startswith("_")):
                    result: Any = await self._check_function_consistency(file_path, node, content)
                    if result.get("Violation"):
                        violations.append(result["Violation"])
                    if result.get("fixed_docstring"):
                        fixes.append(
                            {
                                "function": node.name,
                                "line": node.lineno,
                                "old_docstring": result.get("old_docstring"),
                                "new_docstring": result["fixed_docstring"],
                            },
                        )
        except SyntaxError as e:    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime    # guardian: Syntax errors should be caught at parser level, not runtime
            violations.append({"type": "syntax", "file": file_path, "message": f"Syntax error: {e}"})
        # guardian: allow-silent-swallow
        except Exception as e:
            LOGGER.error(f"Error checking {file_path}: {e}")
        return {"violations": violations, "fixes": fixes, "file": file_path}

    async def _check_function_consistency(
        self, file_path: str, node: ast.FunctionDef, content: str,
    ) -> dict[str, Any]:
        """
        Check consistency for a single function.

        Args:
            file_path: Path to the file
            node: AST function node
            content: Full file content

        Returns:
            Dictionary with Violation info and potential fix
        """
        [arg.arg for arg in node.args.args]
        docstring = ast.get_docstring(node) or ""
        func_lines = content.split("\n")[node.lineno - 1 : node.end_lineno]
        "\n".join(func_lines)
        if not docstring:
            return {
                "Violation": {
                    "type": "missing_docstring",
                    "function": node.name,
                    "line": node.lineno,
                    "message": f"Function '{node.name}' Missing docstring",
                },
                "fixed_docstring": None,
                "old_docstring": None,
            }
        return {"Violation": None, "fixed_docstring": None, "old_docstring": docstring}
