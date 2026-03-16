"""ADG-driven tests for agentic_core/mixins — fan_in=2 mixins batch.

Covers: context_management_mixin, cost_mixin, metrics_mixin, tracing_mixin.
"""
from __future__ import annotations

import pytest

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
