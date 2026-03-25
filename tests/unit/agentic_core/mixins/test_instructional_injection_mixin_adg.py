"""ADG-driven tests for agentic_core/mixins/instructional_injection_mixin.py — fan_in=3.

Contract tests: InstructionalInjectionMixin interface and injection layer methods.
"""
from __future__ import annotations

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

# REMOVED: _emit_records_execution_trace("p0", "evidence", "test_instructional_injection_mixin_adg")
# REMOVED: _emit_applies_guardrail("p0", "test_instructional_injection_mixin_adg", "p0_governance")
# REMOVED: _emit_reads_policy_state("p0", "test_instructional_injection_mixin_adg", "policy_binding")
# REMOVED: _emit_snapshots_state("p0", "test_instructional_injection_mixin_adg", "state_snapshot")
# REMOVED: emit_replay_key("p0", "test_instructional_injection_mixin_adg")
# REMOVED: emit_determinism_digest("p0", "test_instructional_injection_mixin_adg")
# REMOVED: _emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
# REMOVED: _emit_authorize_and_execute("p2", "test_instructional_injection_mixin_adg", "execution_auth")
# REMOVED: _emit_validates_capability("p2", "test_instructional_injection_mixin_adg", "capability_check")
# REMOVED: _emit_routes_to_capability("p2", "test_instructional_injection_mixin_adg", "capability_route")
# REMOVED: _emit_writes_via_uwg("p2", "test_instructional_injection_mixin_adg", "uwg_write")
# REMOVED: _emit_blocks_direct_write("p2", "test_instructional_injection_mixin_adg", "direct_write_block")
# REMOVED: _emit_records_tool_invocation("p2", "test_instructional_injection_mixin_adg", "tool_invocation")
# REMOVED: _emit_captures_execution_output("p2", "test_instructional_injection_mixin_adg", "exec_output")
# REMOVED: _emit_dispatches_agent("p3", "test_instructional_injection_mixin_adg", "agent_dispatch")
# REMOVED: _emit_coordinates_agents("p3", "test_instructional_injection_mixin_adg", "agent_coordination")
# REMOVED: _emit_records_workflow_lineage("p3", "test_instructional_injection_mixin_adg", "workflow_lineage")
# REMOVED: _emit_records_healing_outcome("p3", "test_instructional_injection_mixin_adg", "healing_outcome")
# REMOVED: _emit_escalates_failure("p3", "test_instructional_injection_mixin_adg", "failure_escalation")
# REMOVED: _emit_orchestrates_workflow("p3", "test_instructional_injection_mixin_adg", "workflow_orchestration")
# REMOVED: _emit_dispatches_healing_run("p3", "test_instructional_injection_mixin_adg", "healing_dispatch")
# REMOVED: _emit_invokes_evaluation("p3", "test_instructional_injection_mixin_adg", "evaluation_signal")
# REMOVED: _emit_records_telemetry_event("p4", "test_instructional_injection_mixin_adg", "telemetry_event")
# REMOVED: _emit_captures_evaluation_metric("p4", "test_instructional_injection_mixin_adg", "eval_metric")
# REMOVED: _emit_stores_embedding("p4", "test_instructional_injection_mixin_adg", "embedding_store")
# REMOVED: _emit_updates_meta_learning_state("p4", "test_instructional_injection_mixin_adg", "meta_learning")
# REMOVED: _emit_links_execution_to_snapshot("p4", "test_instructional_injection_mixin_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit

from agentic_core.mixins.instructional_injection_mixin import (
    InstructionalInjectionMixin,
    get_instructional_injection_mixin,
    instructional_injection_mixin,
)
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

# REMOVED: _emit_emits_metric_event("test_instructional_injection_mixin_adg", "p4obs", "metric_1")
# REMOVED: _emit_emits_metric_event("test_instructional_injection_mixin_adg", "p4obs", "metric_2")
# REMOVED: _emit_emits_metric_event("test_instructional_injection_mixin_adg", "p4obs", "metric_3")
# REMOVED: _emit_emits_metric_event("test_instructional_injection_mixin_adg", "p4obs", "metric_4")
# REMOVED: _emit_emits_metric_event("test_instructional_injection_mixin_adg", "p4obs", "metric_5")
# REMOVED: _emit_emits_metric_event("test_instructional_injection_mixin_adg", "p4obs", "metric_6")
# REMOVED: _emit_records_incident_event("test_instructional_injection_mixin_adg", "p4obs", "incident")
# REMOVED: _emit_captures_runtime_anomaly("test_instructional_injection_mixin_adg", "p4obs", "anomaly")
# REMOVED: _emit_writes_observability_log("test_instructional_injection_mixin_adg", "p4obs", "obs_log")
# REMOVED: _emit_updates_monitoring_state("test_instructional_injection_mixin_adg", "p4obs", "mon_state")
# REMOVED: _emit_triggers_alert("test_instructional_injection_mixin_adg", "p4obs", "alert")
# REMOVED: _emit_links_incident_trace("test_instructional_injection_mixin_adg", "p4obs", "trace_link")
# REMOVED: _emit_captures_pattern("test_instructional_injection_mixin_adg", "p3lm", "pattern")
# REMOVED: _emit_records_learning_event("test_instructional_injection_mixin_adg", "p3lm", "learning_event")
# REMOVED: _emit_writes_learning_snapshot("test_instructional_injection_mixin_adg", "p3lm", "snapshot")
# REMOVED: _emit_feeds_meta_learning("test_instructional_injection_mixin_adg", "p3lm", "meta_feed")
# REMOVED: _emit_updates_routing_strategy("test_instructional_injection_mixin_adg", "p3lm", "routing")
# REMOVED: _emit_improves_agent_policy("test_instructional_injection_mixin_adg", "p3lm", "policy")
# REMOVED: _emit_stores_learning_state("test_instructional_injection_mixin_adg", "p3lm", "state")
# REMOVED: _emit_records_execution_trace("test_instructional_injection_mixin_adg", "L0_ROUTING", "p2_trace_1")
# REMOVED: _emit_records_execution_trace("test_instructional_injection_mixin_adg", "L1_REASONING", "p2_trace_2")
# REMOVED: _emit_records_execution_trace("test_instructional_injection_mixin_adg", "L2_EXECUTION", "p2_trace_3")
# REMOVED: _emit_records_execution_trace("test_instructional_injection_mixin_adg", "L3_ORCHESTRATION", "p2_trace_4")
# REMOVED: _emit_records_execution_trace("test_instructional_injection_mixin_adg", "L4_STATE", "p2_trace_5")
# REMOVED: _emit_reads_environ("test_instructional_injection_mixin_adg", "env_read", "p2_env_1")
# REMOVED: _emit_reads_environ("test_instructional_injection_mixin_adg", "env_read", "p2_env_2")
# REMOVED: _emit_reads_runtime_state("test_instructional_injection_mixin_adg", "runtime_state", "p2_rt_1")
# REMOVED: _emit_reads_runtime_state("test_instructional_injection_mixin_adg", "runtime_state", "p2_rt_2")
# REMOVED: _emit_pulls_context("p1", "test_instructional_injection_mixin_adg", "context_pull")
# REMOVED: _emit_pulls_context("p1", "test_instructional_injection_mixin_adg", "context_pull_2")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_instructional_injection_mixin_adg", "uwg_term")
# REMOVED: _emit_execution_terminates_at_uwg("p1", "test_instructional_injection_mixin_adg", "uwg_term_2")
# REMOVED: _emit_writes_through("p1", "test_instructional_injection_mixin_adg", "write_through")
# REMOVED: _emit_writes_through("p1", "test_instructional_injection_mixin_adg", "write_through_2")
# REMOVED: _emit_validated_by_safety_plane("p1", "test_instructional_injection_mixin_adg", "safety_validation")
# REMOVED: _emit_invokes_eval("p1", "test_instructional_injection_mixin_adg", "eval_call")
# REMOVED: _emit_proposal_commits_routing("p1", "test_instructional_injection_mixin_adg", "routing_commit")
# REMOVED: _emit_escalates_to_human("p1", "test_instructional_injection_mixin_adg", "human_escalation")
# REMOVED: _emit_routes_through("p1", "test_instructional_injection_mixin_adg", "route_through")
# REMOVED: _emit_checks_agent_registry("p1", "test_instructional_injection_mixin_adg", "agent_registry")
# REMOVED: _emit_validates_agent_capability("p1", "test_instructional_injection_mixin_adg", "capability")
# REMOVED: _emit_dispatches_execution_plan("p1", "test_instructional_injection_mixin_adg", "exec_plan")
# REMOVED: _emit_agent_executes_agent("p1", "test_instructional_injection_mixin_adg", "sub_agent")
# REMOVED: _emit_routes_to_agent("p1", "test_instructional_injection_mixin_adg", "target_agent")
# REMOVED: _emit_verifies_policy("p1", "test_instructional_injection_mixin_adg", "policy_check")
# REMOVED: _emit_observes_runtime_state("p1", "test_instructional_injection_mixin_adg", "runtime_state")
# REMOVED: _emit_verifies_boundary("p1", "test_instructional_injection_mixin_adg", "boundary_check")
# REMOVED: _emit_transcripts_response("p1", "test_instructional_injection_mixin_adg", "transcript")
# REMOVED: _emit_hard_fails_untranscripted("p1", "test_instructional_injection_mixin_adg")
# REMOVED: _emit_gated_by_confidence("p1", "test_instructional_injection_mixin_adg", "confidence_gate")


class ConcreteAgent(InstructionalInjectionMixin):
    pass


class TestInstructionalInjectionMixinImport:
    def test_class_importable(self):
        assert callable(InstructionalInjectionMixin)

    def test_alias_same_as_class(self):
        assert instructional_injection_mixin is InstructionalInjectionMixin

    def test_factory_function_callable(self):
        assert callable(get_instructional_injection_mixin)

    def test_factory_returns_instance(self):
        obj = get_instructional_injection_mixin()
        assert isinstance(obj, InstructionalInjectionMixin)


class TestGetPattern:
    def test_returns_pattern_for_valid_id(self):
        agent = ConcreteAgent()
        pattern = agent.get_pattern(1)
        assert pattern is not None

    def test_returns_none_for_invalid_id(self):
        agent = ConcreteAgent()
        assert agent.get_pattern(999) is None

    def test_pattern_has_expected_attributes(self):
        agent = ConcreteAgent()
        pattern = agent.get_pattern(1)
        if pattern is not None:
            assert hasattr(pattern, "layer")
            assert hasattr(pattern, "enabled")
            assert hasattr(pattern, "template")


class TestGetPatternsByLayer:
    def test_returns_list(self):
        from agentic_core.config.core.injection_layer_config import InjectionLayer
        agent = ConcreteAgent()
        result = agent.get_patterns_by_layer(InjectionLayer.SAFETY)
        assert isinstance(result, list)

    def test_safety_layer_has_patterns(self):
        from agentic_core.config.core.injection_layer_config import InjectionLayer
        agent = ConcreteAgent()
        patterns = agent.get_patterns_by_layer(InjectionLayer.SAFETY)
        assert len(patterns) > 0


class TestInjectPattern:
    def test_inject_unchanged_on_disabled(self):
        agent = ConcreteAgent()
        # Pattern 999 doesn't exist → should return prompt unchanged
        result = agent.inject_pattern("my prompt", 999)
        assert result == "my prompt"

    def test_inject_safety_layer_returns_string(self):
        agent = ConcreteAgent()
        result = agent.inject_safety_layer("base prompt")
        assert isinstance(result, str)

    def test_inject_safety_layer_contains_original(self):
        agent = ConcreteAgent()
        result = agent.inject_safety_layer("original content")
        assert "original content" in result


class TestGetInjectionSummary:
    def test_returns_dict(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert isinstance(summary, dict)

    def test_has_total_patterns(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert "total_patterns" in summary
        assert summary["total_patterns"] >= 30

    def test_has_enabled_count(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert "enabled_count" in summary
        assert summary["enabled_count"] >= 0

    def test_has_layers_key(self):
        agent = ConcreteAgent()
        summary = agent.get_injection_summary()
        assert "layers" in summary
        assert isinstance(summary["layers"], dict)
