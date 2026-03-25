"""
Seam contract tests — verifies all 11 L0 routing seam modules load cleanly
and expose their expected callable interfaces.

G16: Covers all seam files under agentic_core/L0_routing/seams/.
"""

from __future__ import annotations

import importlib
import inspect

import pytest

from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_l0_seam_contracts")
# REMOVED: _emit_applies_guardrail("p0", "test_l0_seam_contracts", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_l0_seam_contracts", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_l0_seam_contracts", "state_snapshot")
from agentic_core.L_CONTRACTS.lifecycle_trace_contract import (
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

# REMOVED: _emit_emits_metric_event("test_l0_seam_contracts", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_l0_seam_contracts", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_l0_seam_contracts", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_l0_seam_contracts", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_l0_seam_contracts", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_l0_seam_contracts", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_l0_seam_contracts", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_l0_seam_contracts", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_l0_seam_contracts", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_l0_seam_contracts", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_l0_seam_contracts", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_l0_seam_contracts", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_l0_seam_contracts", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_l0_seam_contracts", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_l0_seam_contracts", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_l0_seam_contracts", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_l0_seam_contracts", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_l0_seam_contracts", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_l0_seam_contracts", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_l0_seam_contracts", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_l0_seam_contracts", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_l0_seam_contracts", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_l0_seam_contracts", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_l0_seam_contracts", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_l0_seam_contracts", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_l0_seam_contracts", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_l0_seam_contracts", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_l0_seam_contracts", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_l0_seam_contracts", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_l0_seam_contracts", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l0_seam_contracts", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_l0_seam_contracts", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_l0_seam_contracts", "write_through")
# REMOVED: _emit_writes_through("p1", "test_l0_seam_contracts", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_l0_seam_contracts", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_l0_seam_contracts", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_l0_seam_contracts", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_l0_seam_contracts", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_l0_seam_contracts", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_l0_seam_contracts", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_l0_seam_contracts", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_l0_seam_contracts", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_l0_seam_contracts", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_l0_seam_contracts", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_l0_seam_contracts", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_l0_seam_contracts", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_l0_seam_contracts", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_l0_seam_contracts", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_l0_seam_contracts")
# REMOVED: _emit_gated_by_confidence("p1", "test_l0_seam_contracts", "confidence_gate")
# REMOVED: emit_replay_key("p0", "test_l0_seam_contracts")
# REMOVED: emit_determinism_digest("p0", "test_l0_seam_contracts")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_l0_seam_contracts", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_l0_seam_contracts", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_l0_seam_contracts", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_l0_seam_contracts", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_l0_seam_contracts", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_l0_seam_contracts", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_l0_seam_contracts", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_l0_seam_contracts", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_l0_seam_contracts", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_l0_seam_contracts", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_l0_seam_contracts", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_l0_seam_contracts", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_l0_seam_contracts", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_l0_seam_contracts", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_l0_seam_contracts", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_l0_seam_contracts", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_l0_seam_contracts", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_l0_seam_contracts", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_l0_seam_contracts", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_l0_seam_contracts", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300  # 5 minutes
# Configuration constants

# ---------------------------------------------------------------------------
# Seam registry: (module_stem, expected_callable_name, callable_type)
# callable_type: "function" or "class"
# ---------------------------------------------------------------------------
SEAM_REGISTRY = [
    ("observability_seam", "load_meta_learning_agent", "function"),
    ("elevator_shaft_seam", "load_context_jit", "function"),
    ("learning_seam", None, None),
    ("safety_enforcement_seam", None, None),
    ("canonical_truth_seam", None, None),
    ("layer_emission_seam", None, None),
    ("redis_decision_cache", None, None),
    ("safety_kernel_seam", None, None),
    ("safety_reasoning_seam", None, None),
    ("safety_validators_seam", None, None),
    ("vigilance_seam", None, None),
]

SEAM_MODULE_PREFIX = "agentic_core.L0_routing.seams."


@pytest.mark.parametrize("stem,_callable,_type", SEAM_REGISTRY)
def test_seam_imports_without_error(stem, _callable, _type):
    """Each seam module must be importable with no ImportError."""
    mod = importlib.import_module(SEAM_MODULE_PREFIX + stem)
    assert mod is not None


@pytest.mark.parametrize(
    "stem,callable_name,callable_type", [(s, c, t) for s, c, t in SEAM_REGISTRY if c is not None]
)
def test_seam_exports_expected_callable(stem, callable_name, callable_type):
    """Each seam with a declared callable must export it."""
    mod = importlib.import_module(SEAM_MODULE_PREFIX + stem)
    assert hasattr(mod, callable_name), f"Seam {stem} missing expected export '{callable_name}'"
    obj = getattr(mod, callable_name)
    if callable_type == "function":
        assert callable(obj), f"{callable_name} must be callable"


# ---------------------------------------------------------------------------
# observability_seam specific contracts
# ---------------------------------------------------------------------------


class TestObservabilitySeam:
    def test_load_meta_learning_agent_returns_class_or_none(self):
        from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent

        result = load_meta_learning_agent()
        # Must be a class or None (fail-open)
        assert result is None or (inspect.isclass(result)), f"Expected class or None, got {type(result)}"

    def test_load_meta_learning_agent_returns_meta_learning_client(self):
        from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent

        cls = load_meta_learning_agent()
        if cls is not None:
            assert cls.__name__ == "MetaLearningClient"

    def test_load_meta_learning_agent_no_exception_on_repeat_calls(self):
        from agentic_core.L0_routing.seams.observability_seam import load_meta_learning_agent

        r1 = load_meta_learning_agent()
        r2 = load_meta_learning_agent()
        assert r1 is r2 or (r1 is None and r2 is None)


# ---------------------------------------------------------------------------
# elevator_shaft_seam specific contracts
# ---------------------------------------------------------------------------


class TestElevatorShaftSeam:
    def test_load_context_jit_returns_dict(self):
        from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit

        result = load_context_jit("intent_001")
        assert isinstance(result, dict)

    def test_load_context_jit_returns_empty_dict(self):
        """Seam is a pure stub — always returns empty dict (no control flow allowed)."""
        from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit

        result = load_context_jit("any_intent")
        assert result == {}

    def test_load_context_jit_intent_id_accepted(self):
        """intent_id parameter is accepted without error."""
        from agentic_core.L0_routing.seams.elevator_shaft_seam import load_context_jit

        r1 = load_context_jit("intent_a")
        r2 = load_context_jit("intent_b")
        assert r1 == r2 == {}

    def test_load_context_jit_no_control_flow_in_seam(self):
        """Seam must have no If/Try/For/While (enforced by existing invariant test)."""
        import ast

        seam_file = "agentic_core/L0_routing/seams/elevator_shaft_seam.py"
        with open(seam_file, encoding="utf-8") as f:
            content = f.read()
        tree = ast.parse(content)
        forbidden = (ast.If, ast.For, ast.While, ast.Try)
        found = [type(n).__name__ for n in ast.walk(tree) if isinstance(n, forbidden)]
        assert not found, f"Control flow found in seam: {found}"
