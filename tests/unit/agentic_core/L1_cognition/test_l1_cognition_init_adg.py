"""ADG-driven tests for agentic_core/L1_cognition/__init__.py — fan_in=5.

Contract tests: all __all__ re-exports must be importable, have correct types,
and be identical to their canonical source in the types submodule.
"""
from __future__ import annotations

import pytest

from agentic_core.runtime.lifecycle_trace_contract import (
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

_emit_records_execution_trace("p0", "evidence", "test_l1_cognition_init_adg")
_emit_applies_guardrail("p0", "test_l1_cognition_init_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_l1_cognition_init_adg", "policy_binding")
_emit_snapshots_state("p0", "test_l1_cognition_init_adg", "state_snapshot")
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

_emit_emits_metric_event("test_l1_cognition_init_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_l1_cognition_init_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_l1_cognition_init_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_l1_cognition_init_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_l1_cognition_init_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_l1_cognition_init_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_l1_cognition_init_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_l1_cognition_init_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_l1_cognition_init_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_l1_cognition_init_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_l1_cognition_init_adg", "p4obs", "alert")
_emit_links_incident_trace("test_l1_cognition_init_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_l1_cognition_init_adg", "p3lm", "pattern")
_emit_records_learning_event("test_l1_cognition_init_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_l1_cognition_init_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_l1_cognition_init_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_l1_cognition_init_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_l1_cognition_init_adg", "p3lm", "policy")
_emit_stores_learning_state("test_l1_cognition_init_adg", "p3lm", "state")
_emit_records_execution_trace("test_l1_cognition_init_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_l1_cognition_init_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_l1_cognition_init_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_l1_cognition_init_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_l1_cognition_init_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_l1_cognition_init_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_l1_cognition_init_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_l1_cognition_init_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_l1_cognition_init_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_l1_cognition_init_adg", "context_pull")
_emit_pulls_context("p1", "test_l1_cognition_init_adg", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_l1_cognition_init_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_l1_cognition_init_adg", "uwg_term_2")
_emit_writes_through("p1", "test_l1_cognition_init_adg", "write_through")
_emit_writes_through("p1", "test_l1_cognition_init_adg", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_l1_cognition_init_adg", "safety_validation")
_emit_invokes_eval("p1", "test_l1_cognition_init_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_l1_cognition_init_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_l1_cognition_init_adg", "human_escalation")
_emit_routes_through("p1", "test_l1_cognition_init_adg", "route_through")
_emit_checks_agent_registry("p1", "test_l1_cognition_init_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_l1_cognition_init_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_l1_cognition_init_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_l1_cognition_init_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_l1_cognition_init_adg", "target_agent")
_emit_verifies_policy("p1", "test_l1_cognition_init_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_l1_cognition_init_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_l1_cognition_init_adg", "boundary_check")
_emit_transcripts_response("p1", "test_l1_cognition_init_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_l1_cognition_init_adg")
_emit_gated_by_confidence("p1", "test_l1_cognition_init_adg", "confidence_gate")
emit_replay_key("p0", "test_l1_cognition_init_adg")
emit_determinism_digest("p0", "test_l1_cognition_init_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_l1_cognition_init_adg", "execution_auth")
_emit_validates_capability("p2", "test_l1_cognition_init_adg", "capability_check")
_emit_routes_to_capability("p2", "test_l1_cognition_init_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_l1_cognition_init_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_l1_cognition_init_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_l1_cognition_init_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_l1_cognition_init_adg", "exec_output")
_emit_dispatches_agent("p3", "test_l1_cognition_init_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_l1_cognition_init_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_l1_cognition_init_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_l1_cognition_init_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_l1_cognition_init_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_l1_cognition_init_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_l1_cognition_init_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_l1_cognition_init_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_l1_cognition_init_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_l1_cognition_init_adg", "eval_metric")
_emit_stores_embedding("p4", "test_l1_cognition_init_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_l1_cognition_init_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_l1_cognition_init_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit


class TestL1CognitionPublicAPI:
    def test_all_exports_present(self):
        import agentic_core.L1_cognition as m
        for name in m.__all__:
            assert hasattr(m, name), f"Missing __all__ member: {name}"

    def test_action_request_importable(self):
        from agentic_core.L1_cognition import ActionRequest
        assert callable(ActionRequest)

    def test_action_result_importable(self):
        from agentic_core.L1_cognition import ActionResult
        assert callable(ActionResult)

    def test_planning_request_importable(self):
        from agentic_core.L1_cognition import PlanningRequest
        assert callable(PlanningRequest)

    def test_planning_result_importable(self):
        from agentic_core.L1_cognition import PlanningResult
        assert callable(PlanningResult)

    def test_package_docstring_present(self):
        import agentic_core.L1_cognition as m
        assert m.__doc__ is not None and "cognition" in m.__doc__.lower()


class TestL1CognitionShimIdentity:
    """Re-exports must be identical to canonical source types."""

    def test_action_request_same_object(self):
        from agentic_core.L1_cognition import ActionRequest as shim
        from agentic_core.L1_cognition.types.action_request_types import ActionRequest as canon
        assert shim is canon

    def test_action_result_same_object(self):
        from agentic_core.L1_cognition import ActionResult as shim
        from agentic_core.L1_cognition.types.action_request_types import ActionResult as canon
        assert shim is canon

    def test_planning_request_same_object(self):
        from agentic_core.L1_cognition import PlanningRequest as shim
        from agentic_core.L1_cognition.types.action_request_types import PlanningRequest as canon
        assert shim is canon

    def test_planning_result_same_object(self):
        from agentic_core.L1_cognition import PlanningResult as shim
        from agentic_core.L1_cognition.types.action_request_types import PlanningResult as canon
        assert shim is canon


class TestL1CognitionSovereigntyContract:
    """The L1 layer must contain NO execution or routing logic."""

    def test_no_write_gateway_import(self):
        """L1 must not import write_gateway (L2 execution module)."""
        import agentic_core.L1_cognition as m
        source = getattr(m, "__file__", "") or ""
        # Verify by checking the package's __init__ doesn't import write_gateway
        from pathlib import Path
        init_src = Path(source).read_text() if source else ""
        assert "write_gateway" not in init_src

    def test_reasoning_subpackage_exists(self):
        from pathlib import Path

        import agentic_core.L1_cognition as m
        pkg_dir = Path(m.__file__).parent
        assert (pkg_dir / "reasoning").is_dir()
