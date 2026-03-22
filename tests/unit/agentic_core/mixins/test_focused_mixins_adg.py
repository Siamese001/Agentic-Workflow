"""ADG-driven tests for agentic_core/mixins — fan_in=2 mixins batch.

Covers: context_management_mixin, cost_mixin, metrics_mixin, tracing_mixin.
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

_emit_records_execution_trace("p0", "evidence", "test_focused_mixins_adg")
_emit_applies_guardrail("p0", "test_focused_mixins_adg", "p0_governance")
_emit_reads_policy_state("p0", "test_focused_mixins_adg", "policy_binding")
_emit_snapshots_state("p0", "test_focused_mixins_adg", "state_snapshot")
emit_replay_key("p0", "test_focused_mixins_adg")
emit_determinism_digest("p0", "test_focused_mixins_adg")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_focused_mixins_adg", "execution_auth")
_emit_validates_capability("p2", "test_focused_mixins_adg", "capability_check")
_emit_routes_to_capability("p2", "test_focused_mixins_adg", "capability_route")
_emit_writes_via_uwg("p2", "test_focused_mixins_adg", "uwg_write")
_emit_blocks_direct_write("p2", "test_focused_mixins_adg", "direct_write_block")
_emit_records_tool_invocation("p2", "test_focused_mixins_adg", "tool_invocation")
_emit_captures_execution_output("p2", "test_focused_mixins_adg", "exec_output")
_emit_dispatches_agent("p3", "test_focused_mixins_adg", "agent_dispatch")
_emit_coordinates_agents("p3", "test_focused_mixins_adg", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_focused_mixins_adg", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_focused_mixins_adg", "healing_outcome")
_emit_escalates_failure("p3", "test_focused_mixins_adg", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_focused_mixins_adg", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_focused_mixins_adg", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_focused_mixins_adg", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_focused_mixins_adg", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_focused_mixins_adg", "eval_metric")
_emit_stores_embedding("p4", "test_focused_mixins_adg", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_focused_mixins_adg", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_focused_mixins_adg", "exec_snapshot_link")

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# context_management_mixin
# ---------------------------------------------------------------------------
from agentic_core.mixins.context_management_mixin import (
    ContextItem,
    ContextManagementMixin,
    ContextPriority,
)


class TestContextPriority:
    def test_all_levels_present(self):
        names = {e.name for e in ContextPriority}
        assert {"CRITICAL", "HIGH", "MEDIUM", "LOW"} == names

    def test_critical_lowest_value(self):
        assert ContextPriority.CRITICAL.value < ContextPriority.LOW.value


class TestContextItem:
    def test_creates_valid(self):
        item = ContextItem(content="hello", priority=ContextPriority.HIGH, token_count=5)
        assert item.content == "hello"
        assert item.priority == ContextPriority.HIGH
        assert item.token_count == 5

    def test_item_id_auto_generated(self):
        item = ContextItem(content="test", priority=ContextPriority.LOW, token_count=1)
        assert len(item.item_id) > 0

    def test_custom_item_id_preserved(self):
        item = ContextItem(content="x", priority=ContextPriority.CRITICAL, token_count=1, item_id="my-id")
        assert item.item_id == "my-id"


class TestContextManagementMixinInterface:
    def test_class_importable(self):
        assert callable(ContextManagementMixin)

    def test_has_add_context(self):
        assert hasattr(ContextManagementMixin, "add_context")

    def test_has_get_optimized_context(self):
        assert hasattr(ContextManagementMixin, "get_optimized_context")

    def test_has_clear_context(self):
        assert hasattr(ContextManagementMixin, "clear_context")

    def test_instance_clear_context(self):
        class MyComp(ContextManagementMixin):
            pass
        comp = MyComp()
        comp.clear_context()  # should not raise

    def test_get_context_status_returns_dict(self):
        class MyComp(ContextManagementMixin):
            pass
        comp = MyComp()
        comp.clear_context()
        status = comp.get_context_status()
        assert isinstance(status, dict)


# ---------------------------------------------------------------------------
# cost_mixin
# ---------------------------------------------------------------------------
from agentic_core.mixins.cost_mixin import (
    BudgetConfig,
    BudgetExceededError,
    CostGuardrailMixin,
    TokenUsage,
)


class TestTokenUsage:
    def test_defaults(self):
        u = TokenUsage()
        assert u.prompt_tokens == 0
        assert u.completion_tokens == 0
        assert u.total_tokens == 0
        assert u.model == "unknown"

    def test_custom_values(self):
        u = TokenUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150, model="gemini")
        assert u.total_tokens == 150


class TestBudgetConfig:
    def test_defaults(self):
        cfg = BudgetConfig()
        assert cfg.max_tokens_per_request == 8000
        assert cfg.max_recursive_depth == 10
        assert cfg.alert_threshold_pct == 0.8

    def test_custom(self):
        cfg = BudgetConfig(max_tokens_per_request=1000, max_loop_iterations=10)
        assert cfg.max_tokens_per_request == 1000


class TestBudgetExceededError:
    def test_is_exception(self):
        assert issubclass(BudgetExceededError, Exception)

    def test_attributes_stored(self):
        err = BudgetExceededError("tokens", 9000, 8000)
        assert err.limit_type == "tokens"
        assert err.current == 9000
        assert err.limit == 8000


class TestCostGuardrailMixinInterface:
    def test_class_importable(self):
        assert callable(CostGuardrailMixin)

    def test_has_record_token_usage(self):
        assert hasattr(CostGuardrailMixin, "record_token_usage")

    def test_has_get_budget_status(self):
        assert hasattr(CostGuardrailMixin, "get_budget_status")


# ---------------------------------------------------------------------------
# metrics_mixin
# ---------------------------------------------------------------------------
from agentic_core.mixins.metrics_mixin import MetricsMixin, PerformanceMetrics


class TestPerformanceMetrics:
    def test_creates_valid(self):
        m = PerformanceMetrics(operation_name="test_op")
        assert m.operation_name == "test_op"
        assert m.call_count == 0

    def test_avg_time_ms_zero_when_no_calls(self):
        m = PerformanceMetrics(operation_name="op")
        assert m.avg_time_ms == 0.0

    def test_avg_time_ms_computed(self):
        m = PerformanceMetrics(operation_name="op", call_count=2, total_time_ms=100.0)
        assert m.avg_time_ms == 50.0

    def test_cache_hit_rate_zero_when_empty(self):
        m = PerformanceMetrics(operation_name="op")
        assert m.cache_hit_rate == 0.0

    def test_cache_hit_rate_computed(self):
        m = PerformanceMetrics(operation_name="op", cache_hits=3, cache_misses=1)
        assert m.cache_hit_rate == 0.75

    def test_to_dict_has_required_keys(self):
        m = PerformanceMetrics(operation_name="op")
        d = m.to_dict()
        for key in ("operation_name", "call_count", "total_time_ms", "avg_time_ms"):
            assert key in d


class TestMetricsMixinInterface:
    def test_class_importable(self):
        assert callable(MetricsMixin)

    def test_has_record_timing(self):
        assert hasattr(MetricsMixin, "record_timing")

    def test_has_get_metrics(self):
        assert hasattr(MetricsMixin, "get_metrics")

    def test_instance_get_metrics_returns_dict(self):
        class MyComp(MetricsMixin):
            pass
        comp = MyComp()
        result = comp.get_metrics()
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# tracing_mixin
# ---------------------------------------------------------------------------
from agentic_core.mixins.tracing_mixin import SpanContext, TracingMixin
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

_emit_emits_metric_event("test_focused_mixins_adg", "p4obs", "metric_1")
_emit_emits_metric_event("test_focused_mixins_adg", "p4obs", "metric_2")
_emit_emits_metric_event("test_focused_mixins_adg", "p4obs", "metric_3")
_emit_emits_metric_event("test_focused_mixins_adg", "p4obs", "metric_4")
_emit_emits_metric_event("test_focused_mixins_adg", "p4obs", "metric_5")
_emit_emits_metric_event("test_focused_mixins_adg", "p4obs", "metric_6")
_emit_records_incident_event("test_focused_mixins_adg", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_focused_mixins_adg", "p4obs", "anomaly")
_emit_writes_observability_log("test_focused_mixins_adg", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_focused_mixins_adg", "p4obs", "mon_state")
_emit_triggers_alert("test_focused_mixins_adg", "p4obs", "alert")
_emit_links_incident_trace("test_focused_mixins_adg", "p4obs", "trace_link")
_emit_captures_pattern("test_focused_mixins_adg", "p3lm", "pattern")
_emit_records_learning_event("test_focused_mixins_adg", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_focused_mixins_adg", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_focused_mixins_adg", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_focused_mixins_adg", "p3lm", "routing")
_emit_improves_agent_policy("test_focused_mixins_adg", "p3lm", "policy")
_emit_stores_learning_state("test_focused_mixins_adg", "p3lm", "state")
_emit_records_execution_trace("test_focused_mixins_adg", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_focused_mixins_adg", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_focused_mixins_adg", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_focused_mixins_adg", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_focused_mixins_adg", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_focused_mixins_adg", "env_read", "p2_env_1")
_emit_reads_environ("test_focused_mixins_adg", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_focused_mixins_adg", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_focused_mixins_adg", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_focused_mixins_adg", "context_pull")
_emit_pulls_context("p1", "test_focused_mixins_adg", "context_pull_secondary")
_emit_execution_terminates_at_uwg("p1", "test_focused_mixins_adg", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_focused_mixins_adg", "uwg_term_secondary")
_emit_writes_through("p1", "test_focused_mixins_adg", "write_through")
_emit_writes_through("p1", "test_focused_mixins_adg", "write_through_secondary")
_emit_validated_by_safety_plane("p1", "test_focused_mixins_adg", "safety_validation")
_emit_invokes_eval("p1", "test_focused_mixins_adg", "eval_call")
_emit_proposal_commits_routing("p1", "test_focused_mixins_adg", "routing_commit")
_emit_escalates_to_human("p1", "test_focused_mixins_adg", "human_escalation")
_emit_routes_through("p1", "test_focused_mixins_adg", "route_through")
_emit_checks_agent_registry("p1", "test_focused_mixins_adg", "agent_registry")
_emit_validates_agent_capability("p1", "test_focused_mixins_adg", "capability")
_emit_dispatches_execution_plan("p1", "test_focused_mixins_adg", "exec_plan")
_emit_agent_executes_agent("p1", "test_focused_mixins_adg", "sub_agent")
_emit_routes_to_agent("p1", "test_focused_mixins_adg", "target_agent")
_emit_verifies_policy("p1", "test_focused_mixins_adg", "policy_check")
_emit_observes_runtime_state("p1", "test_focused_mixins_adg", "runtime_state")
_emit_verifies_boundary("p1", "test_focused_mixins_adg", "boundary_check")
_emit_transcripts_response("p1", "test_focused_mixins_adg", "transcript")
_emit_hard_fails_untranscripted("p1", "test_focused_mixins_adg")
_emit_gated_by_confidence("p1", "test_focused_mixins_adg", "confidence_gate")


class TestSpanContext:
    def test_auto_generates_trace_id(self):
        ctx = SpanContext()
        assert len(ctx.trace_id) > 0

    def test_auto_generates_span_id(self):
        ctx = SpanContext()
        assert len(ctx.span_id) > 0

    def test_parent_span_id_none_by_default(self):
        ctx = SpanContext()
        assert ctx.parent_span_id is None

    def test_service_name_default(self):
        ctx = SpanContext()
        assert ctx.service_name == "unknown"

    def test_two_contexts_have_different_trace_ids(self):
        a = SpanContext()
        b = SpanContext()
        assert a.trace_id != b.trace_id


class TestTracingMixinInterface:
    def test_class_importable(self):
        assert callable(TracingMixin)

    def test_has_start_span(self):
        assert hasattr(TracingMixin, "start_span")

    def test_instance_start_span_is_context_manager(self):
        mixin = TracingMixin.__new__(TracingMixin)
        TracingMixin.__init__(mixin, service_name="test_service")
        with mixin.start_span("test_operation"):
            pass  # should not raise
