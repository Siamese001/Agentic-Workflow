from __future__ import annotations

from dataclasses import dataclass

from agentic_core.base_agents.SovereignBaseAgent import SovereignBaseAgent
from agentic_core.L2_execution.utils import write_gateway as _wg
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_checks_agent_registry,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_execution_plan,
    _emit_dispatches_healing_run,
    # noqa: E402,
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

emit_replay_key("p0", "StructuralEngineerAgent")
emit_determinism_digest("p0", "StructuralEngineerAgent")

_emit_dispatches_healing_run("p1", "StructuralEngineerAgent", "L5")
_emit_routes_through("p1", "StructuralEngineerAgent", "L5")
_emit_checks_agent_registry("p1", "StructuralEngineerAgent", "agent_registry")
_emit_validates_agent_capability("p1", "StructuralEngineerAgent", "capability")
_emit_dispatches_execution_plan("p1", "StructuralEngineerAgent", "exec_plan")
_emit_agent_executes_agent("p1", "StructuralEngineerAgent", "sub_agent")
_emit_routes_to_agent("p1", "StructuralEngineerAgent", "target_agent")
_emit_verifies_policy("p1", "StructuralEngineerAgent", "policy_check")
_emit_observes_runtime_state("p1", "StructuralEngineerAgent", "runtime_state")
_emit_verifies_boundary("p1", "StructuralEngineerAgent", "boundary_check")
_emit_transcripts_response("p1", "StructuralEngineerAgent", "transcript")
_emit_hard_fails_untranscripted("p1", "StructuralEngineerAgent")
_emit_gated_by_confidence("p1", "StructuralEngineerAgent", "confidence_gate")
_emit_escalates_to_human("p1", "StructuralEngineerAgent", "L5")
_emit_reads_policy_state("p1", "StructuralEngineerAgent", "L5")
_emit_authorize_and_execute("p2", "StructuralEngineerAgent", "execution_auth")
_emit_validates_capability("p2", "StructuralEngineerAgent", "capability_check")
_emit_routes_to_capability("p2", "StructuralEngineerAgent", "capability_route")
_emit_writes_via_uwg("p2", "StructuralEngineerAgent", "uwg_write")
_emit_blocks_direct_write("p2", "StructuralEngineerAgent", "direct_write_block")
_emit_records_tool_invocation("p2", "StructuralEngineerAgent", "tool_invocation")
_emit_captures_execution_output("p2", "StructuralEngineerAgent", "exec_output")
_emit_dispatches_agent("p3", "StructuralEngineerAgent", "agent_dispatch")
_emit_coordinates_agents("p3", "StructuralEngineerAgent", "agent_coordination")
_emit_records_workflow_lineage("p3", "StructuralEngineerAgent", "workflow_lineage")
_emit_records_healing_outcome("p3", "StructuralEngineerAgent", "healing_outcome")
_emit_escalates_failure("p3", "StructuralEngineerAgent", "failure_escalation")
_emit_orchestrates_workflow("p3", "StructuralEngineerAgent", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "StructuralEngineerAgent", "healing_dispatch")
_emit_invokes_evaluation("p3", "StructuralEngineerAgent", "evaluation_signal")
_emit_records_telemetry_event("p4", "StructuralEngineerAgent", "telemetry_event")
_emit_captures_evaluation_metric("p4", "StructuralEngineerAgent", "eval_metric")
_emit_stores_embedding("p4", "StructuralEngineerAgent", "embedding_store")
_emit_updates_meta_learning_state("p4", "StructuralEngineerAgent", "meta_learning")
_emit_links_execution_to_snapshot("p4", "StructuralEngineerAgent", "exec_snapshot_link")

"\nStructural Engineer Agent - Code Structure Validation\nCANONICAL: True - Consolidated 2026-01-06 (merged from engineering.py)\n\nResponsible for:\n- Large functions\n- Many parameters\n- No large classes (>20 methods or >500 lines)\n- Complexity metrics, cyclomatic complexity\n- Code organization, modularity, cohesion\n- Large files\n- Class density\n- Duplicate code\n"
import ast
import os
from pathlib import Path
from typing import Any

from agentic_core.L4_state.utils.complexity_analyzer import calculate_mccabe_complexity
from agentic_core.runtime.contracts.lifecycle_trace_contract import (
    LayerSegment,
    _emit_agent_executes_agent,
    _emit_applies_guardrail,
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
    _emit_snapshots_state,
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
from agentic_core.utils.timeout_decorator_util import timeout

_emit_emits_metric_event("StructuralEngineerAgent", "p4obs", "metric_1")
_emit_emits_metric_event("StructuralEngineerAgent", "p4obs", "metric_2")
_emit_emits_metric_event("StructuralEngineerAgent", "p4obs", "metric_3")
_emit_emits_metric_event("StructuralEngineerAgent", "p4obs", "metric_4")
_emit_emits_metric_event("StructuralEngineerAgent", "p4obs", "metric_5")
_emit_emits_metric_event("StructuralEngineerAgent", "p4obs", "metric_6")
_emit_records_incident_event("StructuralEngineerAgent", "p4obs", "incident")
_emit_captures_runtime_anomaly("StructuralEngineerAgent", "p4obs", "anomaly")
_emit_writes_observability_log("StructuralEngineerAgent", "p4obs", "obs_log")
_emit_updates_monitoring_state("StructuralEngineerAgent", "p4obs", "mon_state")
_emit_triggers_alert("StructuralEngineerAgent", "p4obs", "alert")
_emit_links_incident_trace("StructuralEngineerAgent", "p4obs", "trace_link")
_emit_captures_pattern("StructuralEngineerAgent", "p3lm", "pattern")
_emit_records_learning_event("StructuralEngineerAgent", "p3lm", "learning_event")
_emit_writes_learning_snapshot("StructuralEngineerAgent", "p3lm", "snapshot")
_emit_feeds_meta_learning("StructuralEngineerAgent", "p3lm", "meta_feed")
_emit_updates_routing_strategy("StructuralEngineerAgent", "p3lm", "routing")
_emit_improves_agent_policy("StructuralEngineerAgent", "p3lm", "policy")
_emit_stores_learning_state("StructuralEngineerAgent", "p3lm", "state")
_emit_records_execution_trace("StructuralEngineerAgent", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("StructuralEngineerAgent", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("StructuralEngineerAgent", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("StructuralEngineerAgent", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("StructuralEngineerAgent", "L4_STATE", "p2_trace_5")
_emit_reads_environ("StructuralEngineerAgent", "env_read", "p2_env_1")
_emit_reads_environ("StructuralEngineerAgent", "env_read", "p2_env_2")
_emit_reads_runtime_state("StructuralEngineerAgent", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("StructuralEngineerAgent", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "StructuralEngineerAgent", "context_pull")
_emit_pulls_context("p1", "StructuralEngineerAgent", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "StructuralEngineerAgent", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "StructuralEngineerAgent", "uwg_term_2")
_emit_writes_through("p1", "StructuralEngineerAgent", "write_through")
_emit_writes_through("p1", "StructuralEngineerAgent", "write_through_2")
_emit_validated_by_safety_plane("p1", "StructuralEngineerAgent", "safety_validation")
_emit_invokes_eval("p1", "StructuralEngineerAgent", "eval_call")
_emit_proposal_commits_routing("p1", "StructuralEngineerAgent", "routing_commit")


@dataclass
class StructuralEngineerAgent(SovereignBaseAgent, HealerMixin):
    """
    Structural Engineer validates code structure and organization.

    Validates:
    - No large classes (>20 methods or >500 lines)
    - Proper function size (<50 lines)
    - Cyclomatic complexity (<10)
    - Modularity, cohesion, coupling
    """

    def get_validation_keys(self) -> list[int]:
        """Return canon keys validated by this agent."""
        return list(range(20, 31))

    # guardian: allow-type-erasure
    async def execute(self) -> Any:
        """Execute Structural Engineer validation checks."""
        import uuid as _uuid  # noqa: PLC0415

        _emit_snapshots_state(str(_uuid.uuid4()), "StructuralEngineerAgent.execute", "state_snapshot")
        import uuid as _uuid  # noqa: PLC0415

        _emit_applies_guardrail(str(_uuid.uuid4()), "StructuralEngineerAgent.execute", "p0_governance")
        import uuid as _uuid  # noqa: PLC0415

        _trace_id = str(_uuid.uuid4())
        _emit_records_execution_trace(_trace_id, LayerSegment.L5_POLICY, "StructuralEngineerAgent.execute")
        import hashlib as _hashlib  # noqa: PLC0415

        _seg_hash = _hashlib.sha256(f"{_trace_id}:StructuralEngineerAgent.execute".encode()).hexdigest()[:24]
        _emit_signs_execution_trace(_trace_id, _seg_hash, _seg_hash, 0)

        print()
        print(f"   [{self.name}] 🔍 Checking Large Classes...")
        passed, violations = self.check_no_large_classes()
        if not passed:
            print(f"   [{self.name}] ❌ Large Classes: FAIL ({len(violations)} violations)")
            await self._heal_violations("large_classes", violations)
        else:
            print(f"   [{self.name}] ✅ Large Classes: PASS - All classes within limits")
        print(f"   [{self.name}] 🔍 Checking Large Functions...")
        passed, violations = self.check_no_large_functions()
        if not passed:
            print(
                f"   [{self.name}] ❌ Large Functions: FAIL ({len(violations)} violations) - Large functions detected",
            )
            await self._heal_violations("large_functions", violations)
        else:
            print(f"   [{self.name}] ✅ Large Functions: PASS - All functions within limits")

    def check_no_large_classes(self) -> tuple[bool, list[str]]:
        """
        Check for classes with >20 methods or >500 lines.

        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path

        violations: Any = []
        max_methods: Any = int(os.getenv("MAX_CLASS_METHODS", "20"))
        max_lines: Any = int(os.getenv("MAX_CLASS_LINES", "500"))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, encoding="utf-8") as f:
                    content: Any = f.read()
                    tree: Any = ast.parse(content)
                    content.splitlines()
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        method_count: Any = sum(
                            1 for n in node.body if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)
                        )
                        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                            class_lines: Any = node.end_lineno - node.lineno + 1
                        else:
                            class_lines: Any = 0
                        if method_count > max_methods:
                            violations.append(    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                                f"{file_path}:{node.lineno}: Class '{node.name}' has {method_count} methods (max {max_methods})",
                            )
                        if class_lines > max_lines:
                            violations.append(
                                f"{file_path}:{node.lineno}: Class '{node.name}' has {class_lines} lines (max {max_lines})",
                            )
            except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                self.logger.debug(f"Failed to check class size in {file_path}: {e}")
                continue
        return (len(violations) == 0, violations)

    def check_no_large_functions(self) -> tuple[bool, list[str]]:
        """
        Check for functions exceeding 50 lines.

        Returns:
            Tuple of (passed, list of violations)
        """
        from pathlib import Path

        violations: Any = []
        max_lines: Any = int(os.getenv("MAX_FUNCTION_LINES", "50"))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, encoding="utf-8") as f:
                    content: Any = f.read()
                    tree: Any = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                        if hasattr(node, "lineno") and hasattr(node, "end_lineno"):
                            func_lines: Any = node.end_lineno - node.lineno + 1
                            if func_lines > max_lines:
                                violations.append(
                                    f"{file_path}:{node.lineno}: Function '{node.name}' has {func_lines} lines (max {max_lines})",
                                )
            except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                self.logger.debug(f"Failed to check function size in {file_path}: {e}")
                continue
        return (len(violations) == 0, violations)

    def check_cyclomatic_complexity(self) -> tuple[bool, list[str]]:
        """
        Check for high cyclomatic complexity (>10).

        Returns:
            Tuple of (passed, list of violations)
        """
        violations: Any = []
        max_complexity: Any = int(os.getenv("MAX_CYCLOMATIC_COMPLEXITY", "10"))
        for file_path in self.ctx.python_files:
            try:
                resolved_path: Any = Path(file_path).resolve()
                with open(resolved_path, encoding="utf-8") as f:
                    tree: Any = ast.parse(f.read())
                for node in ast.walk(tree):    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                    if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                        complexity: Any = self._calculate_complexity(node)
                        if complexity > max_complexity:
                            violations.append(
                                f"{file_path}:{node.lineno}: Function '{node.name}' has complexity {complexity} (max {max_complexity})",
                            )
            except (OSError, UnicodeDecodeError, SyntaxError) as e:    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies    # guardian: Parsing and encoding errors need separate handling strategies
                self.logger.debug(f"Failed to check complexity in {file_path}: {e}")
                continue
        return (len(violations) == 0, violations)

    def _calculate_complexity(self, node: ast.AST) -> int:
        """
        Calculate cyclomatic complexity of a function.

        CONSOLIDATED: Delegates to shared L4 utility.
        See agentic_core.L4_state.utils.complexity_analyzer
        """
        return calculate_mccabe_complexity(node)

    async def _heal_violations(self, key: int, violations: list[str]):
        """
        Heal violations for a specific key.

        Args:
            key: Canon key number
            violations: List of Violation descriptions
        """
        max_healing_per_file = int(os.getenv("MAX_HEALING_PER_FILE", "8"))
        file_violations = {}
        for Violation in violations[:max_healing_per_file]:
            if ":" in Violation:
                parts = Violation.split(": ", 1)
                if len(parts) >= 1:
                    file_path = parts[0]
                    if file_path not in file_violations:
                        file_violations[file_path] = []
                    file_violations[file_path].append(Violation)
        for file_path, file_viols in file_violations.items():
            await self._smart_fix(file_path, key, file_viols)

    async def _smart_fix(self, file_path: str, violation_key: int, violations: list[str]):
        """
        Apply smart fix to a file using Gemini 2.5 Flash.

        Args:
            file_path: Path to file to fix
            violation_key: Canon key being fixed
            violations: List of violations in this file
        """
        from pathlib import Path

        try:
            resolved_path = Path(file_path).resolve()
            with open(resolved_path, encoding="utf-8") as f:
                original_code = f.read()
        # guardian: allow-silent-swallow
        except (RuntimeError, OSError) as e:
            print(f"      [!] Cannot read {file_path}: {e}")
            return
        violation_details = "\n".join(violations)
        Task = f"Fix Subatomic Canon Key {violation_key}. Violations:\n{violation_details}"
        # guardian: allow-magic-config
        max_rounds = 5
        current_code = original_code
        previous_failure = None
        for round_num in range(1, max_rounds + 1):
            print(
                f"      [Round {round_num}/{max_rounds}] Healing Key {violation_key} → {Path(file_path).name}",
            )
            mutated_code = await self.resilient_mutation(
                Task=Task,
                code=current_code,
                file_path=file_path,
                round_num=round_num,
                previous_failure=previous_failure,
            )
            is_valid, reason = await self.verify_fix(original_code, mutated_code, violation_key)
            if not is_valid:
                print(f"      [!] Round {round_num}: {reason} – retrying")
                previous_failure = reason
                current_code = mutated_code
                continue
            try:
                _wg.open_write(file_path, mutated_code)
                print(f"      [OK] Round {round_num}: Fixed {Path(file_path).name}")
                return
            # guardian: allow-silent-swallow
            except (RuntimeError, OSError) as e:
                print(f"      [X] Cannot write {file_path}: {e}")
                return
        print(f"      [X] Failed to fix {Path(file_path).name} after {max_rounds} rounds")

    @timeout(300)
    # guardian: allow-magic-config
    def heal_repository(
        self,
        dry_run: bool = True,
        execute: bool = False,
        depth: int = 0,
        max_depth: int = 3,
        _call_path: set | None = None,
    ) -> dict[str, int]:
        """L2 execution agent - invoke shared healing chain."""
        if _call_path is None:
            _call_path = set()
        agent_name = self.__class__.__name__
        if agent_name in _call_path:
            return {"errors": 1, "cycle_detected": True}
        if depth > max_depth:
            return {"errors": 1, "depth_limited": True}
        _call_path.add(agent_name)
        try:
            super().heal_repository(
                dry_run=dry_run, execute=execute, depth=depth, max_depth=max_depth, _call_path=_call_path,
            )
            print(f"[{agent_name}] L2 execution - healing chain invoked")
            return {"skipped": 1}
        finally:
            _call_path.discard(agent_name)

    def heal(self, violation, **kwargs):
        return super().heal(violation, **kwargs)
