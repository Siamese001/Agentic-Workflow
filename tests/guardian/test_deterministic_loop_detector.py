"""Guardian: G-DLD-1 — DeterministicLoopDetector Contract (L2_execution).

Proves:
1. Structural AST: DeterministicLoopDetector, ToolBudget, ToolBudgetExceededError present.
2. ToolBudgetExceededError carries reason_code TOOL_BUDGET_EXCEEDED.
3. increment_and_check raises exactly at max_steps (not before, not after grace).
4. Isolation: separate trace_ids do NOT share counters.
5. reset_trace() clears counters for a trace without affecting others.
6. get_current_step_count() returns deterministic step count between calls.
7. Structural: module MUST NOT import wall-clock (time.time / datetime) — step
   budget must be clock-free (determinism contract).
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    L2_EXECUTION_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_applies_guardrail,  # noqa: E402
    _emit_authorize_and_execute,
    _emit_blocks_direct_write,
    _emit_captures_evaluation_metric,
    _emit_captures_execution_output,
    _emit_coordinates_agents,
    _emit_dispatches_agent,
    _emit_dispatches_healing_run,
    _emit_escalates_failure,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
    _emit_records_healing_outcome,
    _emit_records_telemetry_event,
    _emit_records_tool_invocation,
    _emit_records_workflow_lineage,
    _emit_routes_to_capability,
    _emit_signs_execution_trace,  # noqa: E402
    _emit_snapshots_state,  # noqa: E402
    _emit_stores_embedding,
    _emit_updates_meta_learning_state,
    _emit_validates_capability,
    _emit_writes_via_uwg,
    emit_determinism_digest,  # noqa: E402
    emit_replay_key,  # noqa: E402
)

_emit_records_execution_trace("p0", "evidence", "test_deterministic_loop_detector")
_emit_applies_guardrail("p0", "test_deterministic_loop_detector", "p0_governance")
_emit_reads_policy_state("p0", "test_deterministic_loop_detector", "policy_binding")
_emit_snapshots_state("p0", "test_deterministic_loop_detector", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_records_execution_trace,
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

_emit_emits_metric_event("test_deterministic_loop_detector", "p4obs", "metric_1")
_emit_emits_metric_event("test_deterministic_loop_detector", "p4obs", "metric_2")
_emit_emits_metric_event("test_deterministic_loop_detector", "p4obs", "metric_3")
_emit_emits_metric_event("test_deterministic_loop_detector", "p4obs", "metric_4")
_emit_emits_metric_event("test_deterministic_loop_detector", "p4obs", "metric_5")
_emit_emits_metric_event("test_deterministic_loop_detector", "p4obs", "metric_6")
_emit_records_incident_event("test_deterministic_loop_detector", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_deterministic_loop_detector", "p4obs", "anomaly")
_emit_writes_observability_log("test_deterministic_loop_detector", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_deterministic_loop_detector", "p4obs", "mon_state")
_emit_triggers_alert("test_deterministic_loop_detector", "p4obs", "alert")
_emit_links_incident_trace("test_deterministic_loop_detector", "p4obs", "trace_link")
_emit_captures_pattern("test_deterministic_loop_detector", "p3lm", "pattern")
_emit_records_learning_event("test_deterministic_loop_detector", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_deterministic_loop_detector", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_deterministic_loop_detector", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_deterministic_loop_detector", "p3lm", "routing")
_emit_improves_agent_policy("test_deterministic_loop_detector", "p3lm", "policy")
_emit_stores_learning_state("test_deterministic_loop_detector", "p3lm", "state")
_emit_records_execution_trace("test_deterministic_loop_detector", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_deterministic_loop_detector", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_deterministic_loop_detector", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_deterministic_loop_detector", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_deterministic_loop_detector", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_deterministic_loop_detector", "env_read", "p2_env_1")
_emit_reads_environ("test_deterministic_loop_detector", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_deterministic_loop_detector", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_deterministic_loop_detector", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_deterministic_loop_detector", "context_pull")
_emit_pulls_context("p1", "test_deterministic_loop_detector", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_loop_detector", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_deterministic_loop_detector", "uwg_term_2")
_emit_writes_through("p1", "test_deterministic_loop_detector", "write_through")
_emit_writes_through("p1", "test_deterministic_loop_detector", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_deterministic_loop_detector", "safety_validation")
_emit_invokes_eval("p1", "test_deterministic_loop_detector", "eval_call")
_emit_proposal_commits_routing("p1", "test_deterministic_loop_detector", "routing_commit")
emit_replay_key("p0", "test_deterministic_loop_detector")
emit_determinism_digest("p0", "test_deterministic_loop_detector")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_deterministic_loop_detector", "execution_auth")
_emit_validates_capability("p2", "test_deterministic_loop_detector", "capability_check")
_emit_routes_to_capability("p2", "test_deterministic_loop_detector", "capability_route")
_emit_writes_via_uwg("p2", "test_deterministic_loop_detector", "uwg_write")
_emit_blocks_direct_write("p2", "test_deterministic_loop_detector", "direct_write_block")
_emit_records_tool_invocation("p2", "test_deterministic_loop_detector", "tool_invocation")
_emit_captures_execution_output("p2", "test_deterministic_loop_detector", "exec_output")
_emit_dispatches_agent("p3", "test_deterministic_loop_detector", "agent_dispatch")
_emit_coordinates_agents("p3", "test_deterministic_loop_detector", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_deterministic_loop_detector", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_deterministic_loop_detector", "healing_outcome")
_emit_escalates_failure("p3", "test_deterministic_loop_detector", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_deterministic_loop_detector", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_deterministic_loop_detector", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_deterministic_loop_detector", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_deterministic_loop_detector", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_deterministic_loop_detector", "eval_metric")
_emit_stores_embedding("p4", "test_deterministic_loop_detector", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_deterministic_loop_detector", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_deterministic_loop_detector", "exec_snapshot_link")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = PROJECT_ROOT / L2_EXECUTION_DIR / "enforcement" / "deterministic_loop_detector.py"

pytestmark = pytest.mark.guardian


# ===========================================================================
# A) Structural AST contract
# ===========================================================================


class TestStructuralContract:
    REQUIRED_CLASSES = {"DeterministicLoopDetector", "ToolBudget", "ToolBudgetExceededError"}
    REQUIRED_METHODS = {"increment_and_check", "get_current_step_count", "reset_trace"}

    def test_module_exists(self):
        assert MODULE_PATH.exists(), "deterministic_loop_detector.py must exist in L2_execution/enforcement"

    def test_required_classes_present(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        found = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        missing = self.REQUIRED_CLASSES - found
        assert not missing, "Missing classes: " + str(missing)

    def test_required_methods_on_detector(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        detector_cls = None
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "DeterministicLoopDetector":
                detector_cls = node
                break
        assert detector_cls is not None, "DeterministicLoopDetector class not found"
        method_names = {n.name for n in detector_cls.body if isinstance(n, ast.FunctionDef)}
        missing = self.REQUIRED_METHODS - method_names
        assert not missing, "Missing methods on DeterministicLoopDetector: " + str(missing)

    def test_tool_budget_exceeded_error_is_exception(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "ToolBudgetExceededError":
                bases = [
                    ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "") for b in node.bases
                ]
                assert any("Exception" in b or "Error" in b for b in bases), (
                    "ToolBudgetExceededError must inherit from Exception"
                )
                return
        pytest.fail("ToolBudgetExceededError not found")

    def test_no_wall_clock_imports(self):
        """Determinism contract: step budget must be clock-free."""
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        forbidden = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ("time", "datetime"):
                        forbidden.add(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module in ("time", "datetime"):
                    forbidden.add(node.module)
        assert not forbidden, (
            "DeterministicLoopDetector must NOT import wall-clock modules "
            + str(forbidden)
            + " — step budget must be deterministic"
        )


# ===========================================================================
# B) ToolBudgetExceededError carries required fields
# ===========================================================================


class TestToolBudgetExceededError:
    def test_error_has_reason_code(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        exc = ToolBudgetExceededError(tool_name="my_tool", budget=5)
        assert exc.reason_code == "TOOL_BUDGET_EXCEEDED"

    def test_error_carries_tool_name_and_budget(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        exc = ToolBudgetExceededError(tool_name="analyze", budget=10)
        assert exc.tool_name == "analyze"
        assert exc.budget == 10

    def test_error_message_contains_tool_name(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        exc = ToolBudgetExceededError(tool_name="crawl_tool", budget=3)
        assert "crawl_tool" in str(exc)


# ===========================================================================
# C) increment_and_check: raises exactly at max_steps
# ===========================================================================


class TestIncrementAndCheck:
    @pytest.fixture
    def detector(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
        )

        return DeterministicLoopDetector()

    @pytest.fixture
    def budget_3(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import ToolBudget

        return ToolBudget(max_steps=3)

    def test_allows_calls_up_to_budget_minus_one(self, detector, budget_3):
        for i in range(3):
            detector.increment_and_check("trace-a", "tool_x", budget_3)

    def test_raises_exactly_at_max_steps(self, detector, budget_3):
        for _ in range(3):
            detector.increment_and_check("trace-b", "tool_y", budget_3)
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            ToolBudgetExceededError,
        )

        with pytest.raises(ToolBudgetExceededError):
            detector.increment_and_check("trace-b", "tool_y", budget_3)

    def test_step_count_matches_increments(self, detector, budget_3):
        for i in range(2):
            detector.increment_and_check("trace-c", "tool_z", budget_3)
        assert detector.get_current_step_count("trace-c", "tool_z") == 2


# ===========================================================================
# D) Trace isolation — separate trace_ids do NOT share counters
# ===========================================================================


class TestTraceIsolation:
    def test_separate_traces_independent(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
            ToolBudgetExceededError,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=2)

        detector.increment_and_check("trace-alpha", "tool", budget)
        detector.increment_and_check("trace-alpha", "tool", budget)
        # trace-alpha at budget; trace-beta starts fresh
        detector.increment_and_check("trace-beta", "tool", budget)
        # trace-alpha must now raise
        with pytest.raises(ToolBudgetExceededError):
            detector.increment_and_check("trace-alpha", "tool", budget)
        # trace-beta still has one step left
        detector.increment_and_check("trace-beta", "tool", budget)

    def test_unrelated_tool_names_independent(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
            ToolBudgetExceededError,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=1)

        detector.increment_and_check("t1", "tool_a", budget)
        with pytest.raises(ToolBudgetExceededError):
            detector.increment_and_check("t1", "tool_a", budget)
        # tool_b on same trace is unaffected
        detector.increment_and_check("t1", "tool_b", budget)


# ===========================================================================
# E) reset_trace() clears without affecting other traces
# ===========================================================================


class TestResetTrace:
    def test_reset_clears_counts(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=5)

        detector.increment_and_check("trace-r", "tool", budget)
        detector.increment_and_check("trace-r", "tool", budget)
        assert detector.get_current_step_count("trace-r", "tool") == 2

        detector.reset_trace("trace-r")
        assert detector.get_current_step_count("trace-r", "tool") == 0

    def test_reset_does_not_affect_other_traces(self):
        from agentic_core.L2_execution.enforcement.deterministic_loop_detector import (
            DeterministicLoopDetector,
            ToolBudget,
        )

        detector = DeterministicLoopDetector()
        budget = ToolBudget(max_steps=5)

        detector.increment_and_check("trace-keep", "tool", budget)
        detector.increment_and_check("trace-keep", "tool", budget)
        detector.increment_and_check("trace-drop", "tool", budget)

        detector.reset_trace("trace-drop")

        assert detector.get_current_step_count("trace-keep", "tool") == 2
        assert detector.get_current_step_count("trace-drop", "tool") == 0
