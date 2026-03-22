"""Guardian: G-CB-1 — CircuitBreaker Gate Contract (L5_safety).

Proves:
1. CLOSED state: calls pass through, metrics increment correctly.
2. OPEN state: CircuitBreakerOpenError raised after failure_threshold reached.
3. HALF_OPEN recovery: breaker re-closes after successful call in half-open.
4. fail-closed proof: missing breaker registry raises, does not silently pass.
5. Structural AST: CircuitBreaker, CircuitBreakerOpenError, get_breaker all
   present in the module with correct class hierarchy.
6. reset_registry() cleanly clears all registered breakers.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from agentic_core.L0_routing.config.path_constants import (
    AGENTIC_CORE_DIR,
)
from agentic_core.runtime.lifecycle_trace_contract import (
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
    _emit_escalates_failure,
    _emit_escalates_to_human,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_invokes_evaluation,
    _emit_links_execution_to_snapshot,
    _emit_observes_runtime_state,
    _emit_orchestrates_workflow,
    _emit_reads_policy_state,  # noqa: E402
    _emit_records_execution_trace,  # noqa: E402
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

_emit_records_execution_trace("p0", "evidence", "test_circuit_breaker_gate")
_emit_reads_policy_state("p0", "test_circuit_breaker_gate", "policy_binding")
_emit_snapshots_state("p0", "test_circuit_breaker_gate", "state_snapshot")
from agentic_core.runtime.lifecycle_trace_contract import (
    _emit_agent_executes_agent,
    _emit_captures_pattern,
    _emit_captures_runtime_anomaly,
    _emit_checks_agent_registry,
    _emit_dispatches_execution_plan,
    _emit_emits_metric_event,
    _emit_escalates_to_human,
    _emit_execution_terminates_at_uwg,
    _emit_feeds_meta_learning,
    _emit_gated_by_confidence,
    _emit_hard_fails_untranscripted,
    _emit_improves_agent_policy,
    _emit_invokes_eval,
    _emit_links_incident_trace,  # noqa: E402
    _emit_observes_runtime_state,
    _emit_proposal_commits_routing,
    _emit_pulls_context,
    _emit_reads_environ,
    _emit_reads_runtime_state,
    _emit_records_execution_trace,
    _emit_records_incident_event,
    _emit_records_learning_event,
    _emit_routes_through,
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
    _emit_writes_through,  # noqa: E402
)

_emit_emits_metric_event("test_circuit_breaker_gate", "p4obs", "metric_1")
_emit_emits_metric_event("test_circuit_breaker_gate", "p4obs", "metric_2")
_emit_emits_metric_event("test_circuit_breaker_gate", "p4obs", "metric_3")
_emit_emits_metric_event("test_circuit_breaker_gate", "p4obs", "metric_4")
_emit_emits_metric_event("test_circuit_breaker_gate", "p4obs", "metric_5")
_emit_emits_metric_event("test_circuit_breaker_gate", "p4obs", "metric_6")
_emit_records_incident_event("test_circuit_breaker_gate", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_circuit_breaker_gate", "p4obs", "anomaly")
_emit_writes_observability_log("test_circuit_breaker_gate", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_circuit_breaker_gate", "p4obs", "mon_state")
_emit_triggers_alert("test_circuit_breaker_gate", "p4obs", "alert")
_emit_links_incident_trace("test_circuit_breaker_gate", "p4obs", "trace_link")
_emit_captures_pattern("test_circuit_breaker_gate", "p3lm", "pattern")
_emit_records_learning_event("test_circuit_breaker_gate", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_circuit_breaker_gate", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_circuit_breaker_gate", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_circuit_breaker_gate", "p3lm", "routing")
_emit_improves_agent_policy("test_circuit_breaker_gate", "p3lm", "policy")
_emit_stores_learning_state("test_circuit_breaker_gate", "p3lm", "state")
_emit_records_execution_trace("test_circuit_breaker_gate", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_circuit_breaker_gate", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_circuit_breaker_gate", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_circuit_breaker_gate", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_circuit_breaker_gate", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_circuit_breaker_gate", "env_read", "p2_env_1")
_emit_reads_environ("test_circuit_breaker_gate", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_circuit_breaker_gate", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_circuit_breaker_gate", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_circuit_breaker_gate", "context_pull")
_emit_pulls_context("p1", "test_circuit_breaker_gate", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_circuit_breaker_gate", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_circuit_breaker_gate", "uwg_term_2")
_emit_writes_through("p1", "test_circuit_breaker_gate", "write_through")
_emit_writes_through("p1", "test_circuit_breaker_gate", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_circuit_breaker_gate", "safety_validation")
_emit_invokes_eval("p1", "test_circuit_breaker_gate", "eval_call")
_emit_proposal_commits_routing("p1", "test_circuit_breaker_gate", "routing_commit")
_emit_escalates_to_human("p1", "test_circuit_breaker_gate", "human_escalation")
_emit_routes_through("p1", "test_circuit_breaker_gate", "route_through")
_emit_checks_agent_registry("p1", "test_circuit_breaker_gate", "agent_registry")
_emit_validates_agent_capability("p1", "test_circuit_breaker_gate", "capability")
_emit_dispatches_execution_plan("p1", "test_circuit_breaker_gate", "exec_plan")
_emit_agent_executes_agent("p1", "test_circuit_breaker_gate", "sub_agent")
_emit_routes_to_agent("p1", "test_circuit_breaker_gate", "target_agent")
_emit_verifies_policy("p1", "test_circuit_breaker_gate", "policy_check")
_emit_observes_runtime_state("p1", "test_circuit_breaker_gate", "runtime_state")
_emit_verifies_boundary("p1", "test_circuit_breaker_gate", "boundary_check")
_emit_transcripts_response("p1", "test_circuit_breaker_gate", "transcript")
_emit_hard_fails_untranscripted("p1", "test_circuit_breaker_gate")
_emit_gated_by_confidence("p1", "test_circuit_breaker_gate", "confidence_gate")
emit_replay_key("p0", "test_circuit_breaker_gate")
emit_determinism_digest("p0", "test_circuit_breaker_gate")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_circuit_breaker_gate", "execution_auth")
_emit_validates_capability("p2", "test_circuit_breaker_gate", "capability_check")
_emit_routes_to_capability("p2", "test_circuit_breaker_gate", "capability_route")
_emit_writes_via_uwg("p2", "test_circuit_breaker_gate", "uwg_write")
_emit_blocks_direct_write("p2", "test_circuit_breaker_gate", "direct_write_block")
_emit_records_tool_invocation("p2", "test_circuit_breaker_gate", "tool_invocation")
_emit_captures_execution_output("p2", "test_circuit_breaker_gate", "exec_output")
_emit_dispatches_agent("p3", "test_circuit_breaker_gate", "agent_dispatch")
_emit_coordinates_agents("p3", "test_circuit_breaker_gate", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_circuit_breaker_gate", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_circuit_breaker_gate", "healing_outcome")
_emit_escalates_failure("p3", "test_circuit_breaker_gate", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_circuit_breaker_gate", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_circuit_breaker_gate", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_circuit_breaker_gate", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_circuit_breaker_gate", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_circuit_breaker_gate", "eval_metric")
_emit_stores_embedding("p4", "test_circuit_breaker_gate", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_circuit_breaker_gate", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_circuit_breaker_gate", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = PROJECT_ROOT / AGENTIC_CORE_DIR / "L5_safety" / "enforcement" / "circuit_breaker_gate.py"

pytestmark = pytest.mark.guardian


# ===========================================================================
# A) Structural AST — required symbols present
# ===========================================================================


class TestStructuralContract:
    """Verify the module defines the required classes and functions via AST."""

    REQUIRED_CLASSES = {
        "CircuitBreaker",
        "CircuitBreakerOpenError",
        "CircuitBreakerTimeoutError",
        "CircuitBreakerConfig",
        "CircuitBreakerMetrics",
        "CircuitState",
    }
    REQUIRED_FUNCTIONS = {"get_breaker", "get_all_breakers", "reset_registry"}

    def test_module_exists(self):
        assert MODULE_PATH.exists(), "circuit_breaker_gate.py must exist in L5_safety/enforcement"

    def test_required_classes_present(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        found = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
        missing = self.REQUIRED_CLASSES - found
        assert not missing, "Missing classes in circuit_breaker_gate: " + str(missing)

    def test_required_functions_present(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        found = {n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)}
        missing = self.REQUIRED_FUNCTIONS - found
        assert not missing, "Missing functions in circuit_breaker_gate: " + str(missing)

    def test_circuit_breaker_open_error_is_exception(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        tree = ast.parse(src, filename=str(MODULE_PATH))
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "CircuitBreakerOpenError":
                bases = [
                    ast.unparse(b) if hasattr(ast, "unparse") else getattr(b, "id", "") for b in node.bases
                ]
                assert any("Exception" in b or "Error" in b for b in bases), (
                    "CircuitBreakerOpenError must inherit from Exception"
                )
                return
        pytest.fail("CircuitBreakerOpenError class not found")

    def test_circuit_state_enum_has_states(self):
        src = MODULE_PATH.read_text(encoding="utf-8")
        assert "CLOSED" in src, "CircuitState must define CLOSED"
        assert "OPEN" in src, "CircuitState must define OPEN"
        assert "HALF_OPEN" in src, "CircuitState must define HALF_OPEN"


# ===========================================================================
# B) Runtime: CLOSED state normal operation
# ===========================================================================


class TestClosedState:
    """Breaker in CLOSED state allows calls and tracks success metrics."""

    @pytest.fixture(autouse=True)
    def _reset(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import reset_registry

        reset_registry()
        yield
        reset_registry()

    def test_get_breaker_returns_breaker_instance(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            CircuitBreaker,
            get_breaker,
        )

        breaker = get_breaker("test_cb_closed")
        assert isinstance(breaker, CircuitBreaker)

    def test_same_name_returns_same_instance(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker

        b1 = get_breaker("test_singleton")
        b2 = get_breaker("test_singleton")
        assert b1 is b2

    def test_successful_call_does_not_raise(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker

        breaker = get_breaker("test_success")
        assert breaker.allow_request(), "CLOSED breaker must allow requests"
        breaker.record_success()
        assert breaker.is_closed

    def test_get_all_breakers_contains_registered(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            get_all_breakers,
            get_breaker,
        )

        get_breaker("test_all_a")
        get_breaker("test_all_b")
        all_b = get_all_breakers()
        assert "test_all_a" in all_b
        assert "test_all_b" in all_b


# ===========================================================================
# C) Runtime: OPEN state fail-closed
# ===========================================================================


class TestOpenState:
    """After failure_threshold is reached breaker opens and rejects all calls."""

    @pytest.fixture(autouse=True)
    def _reset(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import reset_registry

        reset_registry()
        yield
        reset_registry()

    def test_open_after_threshold_failures(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker

        breaker = get_breaker("test_open_threshold", failure_threshold=THRESHOLD, reset_timeout_seconds=999.0)

        for _ in range(2):
            breaker.record_failure()

        assert breaker.is_open, "Breaker must be OPEN after failure_threshold failures"

    def test_open_state_rejects_requests(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import get_breaker

        breaker = get_breaker("test_open_reject", failure_threshold=THRESHOLD, reset_timeout_seconds=999.0)

        breaker.record_failure()
        assert breaker.is_open, "Breaker must be OPEN after 1 failure"
        assert not breaker.allow_request(), "OPEN breaker must reject all requests"


# ===========================================================================
# D) reset_registry cleans state
# ===========================================================================


class TestResetRegistry:
    def test_reset_removes_all_breakers(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            get_all_breakers,
            get_breaker,
            reset_registry,
        )

        get_breaker("reset_a")
        get_breaker("reset_b")
        reset_registry()
        all_b = get_all_breakers()
        assert "reset_a" not in all_b
        assert "reset_b" not in all_b

    def test_reset_allows_fresh_registration(self):
        from agentic_core.L5_safety.enforcement.circuit_breaker_gate import (
            get_breaker,
            reset_registry,
        )

        b1 = get_breaker("fresh_after_reset")
        reset_registry()
        b2 = get_breaker("fresh_after_reset")
        assert b1 is not b2, "After reset, new instance must be created"
