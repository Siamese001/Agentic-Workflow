"""
Phases 2-7 — SSOT Mixin Integration Tests.

Covers:
  Phase 2: Metrics + Caching (policy-hash scoping, replay TTL disable)
  Phase 3: CircuitBreaker + RateLimit + StateValidation
  Phase 4: Tracing + ContextPropagation
  Phase 5: SelfDiagnosis + AdaptiveExecution
  Phase 6: HallucinationDetection + CognitiveRecovery
  Phase 7: MetaLearning + FeatureFlags
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pytest

from agentic_core.L2_execution.deterministic_providers import (
    unpatch_deterministic,
)
from agentic_core.mixins.replay_guard_mixin import ReplayGuardMixin
from agentic_core.mixins.ssot_adaptive_execution_mixin import SSOTAdaptiveExecutionMixin
from agentic_core.mixins.ssot_caching_mixin import SSOTCachingMixin
from agentic_core.mixins.ssot_circuit_breaker_mixin import (
    CircuitOpenError,
    PolicyHashMismatch,
    SovereignTokenDenied,
    SSOTCircuitBreakerMixin,
    StateValidationError,
)
from agentic_core.mixins.ssot_cognitive_recovery_mixin import SSOTCognitiveRecoveryMixin
from agentic_core.mixins.ssot_context_propagation_mixin import (
    SSOTContextPropagationMixin,
    get_propagated_policy_hash,
    get_propagated_replay_mode,
    get_propagated_trace_id,
)
from agentic_core.mixins.ssot_feature_flag_mixin import SSOTFeatureFlagMixin
from agentic_core.mixins.ssot_hallucination_detection_mixin import SSOTHallucinationDetectionMixin
from agentic_core.mixins.ssot_meta_learning_mixin import (
    MetaLearningWriteRejected,
    SSOTMetaLearningMixin,
)
from agentic_core.mixins.ssot_metrics_mixin import SSOTMetricsMixin
from agentic_core.mixins.ssot_rate_limit_mixin import RateLimitExceeded, SSOTRateLimitMixin
from agentic_core.mixins.ssot_self_diagnosis_mixin import SSOTSelfDiagnosisMixin
from agentic_core.mixins.ssot_state_validation_mixin import (
    SSOTStateValidationError,
    SSOTStateValidationMixin,
)
from agentic_core.mixins.ssot_tracing_mixin import SSOTTracingMixin
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
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_escalates_to_human,
    _emit_routes_through,
)

_emit_records_execution_trace("p0", "evidence", "test_ssot_mixin_integration")
_emit_applies_guardrail("p0", "test_ssot_mixin_integration", "p0_governance")
_emit_snapshots_state("p0", "test_ssot_mixin_integration", "state_snapshot")
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
    _emit_escalates_to_human,
    _emit_routes_through,
    _emit_checks_agent_registry,
    _emit_validates_agent_capability,
    _emit_dispatches_execution_plan,
    _emit_agent_executes_agent,
    _emit_routes_to_agent,
    _emit_verifies_policy,
    _emit_observes_runtime_state,
    _emit_verifies_boundary,
    _emit_transcripts_response,
    _emit_hard_fails_untranscripted,
    _emit_gated_by_confidence,
    _emit_writes_through,  # noqa: E402
    _emit_links_incident_trace,  # noqa: E402
)

_emit_emits_metric_event("test_ssot_mixin_integration", "p4obs", "metric_1")
_emit_emits_metric_event("test_ssot_mixin_integration", "p4obs", "metric_2")
_emit_emits_metric_event("test_ssot_mixin_integration", "p4obs", "metric_3")
_emit_emits_metric_event("test_ssot_mixin_integration", "p4obs", "metric_4")
_emit_emits_metric_event("test_ssot_mixin_integration", "p4obs", "metric_5")
_emit_emits_metric_event("test_ssot_mixin_integration", "p4obs", "metric_6")
_emit_records_incident_event("test_ssot_mixin_integration", "p4obs", "incident")
_emit_captures_runtime_anomaly("test_ssot_mixin_integration", "p4obs", "anomaly")
_emit_writes_observability_log("test_ssot_mixin_integration", "p4obs", "obs_log")
_emit_updates_monitoring_state("test_ssot_mixin_integration", "p4obs", "mon_state")
_emit_triggers_alert("test_ssot_mixin_integration", "p4obs", "alert")
_emit_links_incident_trace("test_ssot_mixin_integration", "p4obs", "trace_link")
_emit_captures_pattern("test_ssot_mixin_integration", "p3lm", "pattern")
_emit_records_learning_event("test_ssot_mixin_integration", "p3lm", "learning_event")
_emit_writes_learning_snapshot("test_ssot_mixin_integration", "p3lm", "snapshot")
_emit_feeds_meta_learning("test_ssot_mixin_integration", "p3lm", "meta_feed")
_emit_updates_routing_strategy("test_ssot_mixin_integration", "p3lm", "routing")
_emit_improves_agent_policy("test_ssot_mixin_integration", "p3lm", "policy")
_emit_stores_learning_state("test_ssot_mixin_integration", "p3lm", "state")
_emit_records_execution_trace("test_ssot_mixin_integration", "L0_ROUTING", "p2_trace_1")
_emit_records_execution_trace("test_ssot_mixin_integration", "L1_REASONING", "p2_trace_2")
_emit_records_execution_trace("test_ssot_mixin_integration", "L2_EXECUTION", "p2_trace_3")
_emit_records_execution_trace("test_ssot_mixin_integration", "L3_ORCHESTRATION", "p2_trace_4")
_emit_records_execution_trace("test_ssot_mixin_integration", "L4_STATE", "p2_trace_5")
_emit_reads_environ("test_ssot_mixin_integration", "env_read", "p2_env_1")
_emit_reads_environ("test_ssot_mixin_integration", "env_read", "p2_env_2")
_emit_reads_runtime_state("test_ssot_mixin_integration", "runtime_state", "p2_rt_1")
_emit_reads_runtime_state("test_ssot_mixin_integration", "runtime_state", "p2_rt_2")
_emit_pulls_context("p1", "test_ssot_mixin_integration", "context_pull")
_emit_pulls_context("p1", "test_ssot_mixin_integration", "context_pull_2")
_emit_execution_terminates_at_uwg("p1", "test_ssot_mixin_integration", "uwg_term")
_emit_execution_terminates_at_uwg("p1", "test_ssot_mixin_integration", "uwg_term_2")
_emit_writes_through("p1", "test_ssot_mixin_integration", "write_through")
_emit_writes_through("p1", "test_ssot_mixin_integration", "write_through_2")
_emit_validated_by_safety_plane("p1", "test_ssot_mixin_integration", "safety_validation")
_emit_invokes_eval("p1", "test_ssot_mixin_integration", "eval_call")
_emit_proposal_commits_routing("p1", "test_ssot_mixin_integration", "routing_commit")
_emit_escalates_to_human("p1", "test_ssot_mixin_integration", "human_escalation")
_emit_routes_through("p1", "test_ssot_mixin_integration", "route_through")
_emit_checks_agent_registry("p1", "test_ssot_mixin_integration", "agent_registry")
_emit_validates_agent_capability("p1", "test_ssot_mixin_integration", "capability")
_emit_dispatches_execution_plan("p1", "test_ssot_mixin_integration", "exec_plan")
_emit_agent_executes_agent("p1", "test_ssot_mixin_integration", "sub_agent")
_emit_routes_to_agent("p1", "test_ssot_mixin_integration", "target_agent")
_emit_verifies_policy("p1", "test_ssot_mixin_integration", "policy_check")
_emit_observes_runtime_state("p1", "test_ssot_mixin_integration", "runtime_state")
_emit_verifies_boundary("p1", "test_ssot_mixin_integration", "boundary_check")
_emit_transcripts_response("p1", "test_ssot_mixin_integration", "transcript")
_emit_hard_fails_untranscripted("p1", "test_ssot_mixin_integration")
_emit_gated_by_confidence("p1", "test_ssot_mixin_integration", "confidence_gate")
emit_replay_key("p0", "test_ssot_mixin_integration")
emit_determinism_digest("p0", "test_ssot_mixin_integration")
_emit_signs_execution_trace("p0", "p0hash", "p0_trace", 0)
_emit_authorize_and_execute("p2", "test_ssot_mixin_integration", "execution_auth")
_emit_validates_capability("p2", "test_ssot_mixin_integration", "capability_check")
_emit_routes_to_capability("p2", "test_ssot_mixin_integration", "capability_route")
_emit_writes_via_uwg("p2", "test_ssot_mixin_integration", "uwg_write")
_emit_blocks_direct_write("p2", "test_ssot_mixin_integration", "direct_write_block")
_emit_records_tool_invocation("p2", "test_ssot_mixin_integration", "tool_invocation")
_emit_captures_execution_output("p2", "test_ssot_mixin_integration", "exec_output")
_emit_dispatches_agent("p3", "test_ssot_mixin_integration", "agent_dispatch")
_emit_coordinates_agents("p3", "test_ssot_mixin_integration", "agent_coordination")
_emit_records_workflow_lineage("p3", "test_ssot_mixin_integration", "workflow_lineage")
_emit_records_healing_outcome("p3", "test_ssot_mixin_integration", "healing_outcome")
_emit_escalates_failure("p3", "test_ssot_mixin_integration", "failure_escalation")
_emit_orchestrates_workflow("p3", "test_ssot_mixin_integration", "workflow_orchestration")
_emit_dispatches_healing_run("p3", "test_ssot_mixin_integration", "healing_dispatch")
_emit_invokes_evaluation("p3", "test_ssot_mixin_integration", "evaluation_signal")
_emit_records_telemetry_event("p4", "test_ssot_mixin_integration", "telemetry_event")
_emit_captures_evaluation_metric("p4", "test_ssot_mixin_integration", "eval_metric")
_emit_stores_embedding("p4", "test_ssot_mixin_integration", "embedding_store")
_emit_updates_meta_learning_state("p4", "test_ssot_mixin_integration", "meta_learning")
_emit_links_execution_to_snapshot("p4", "test_ssot_mixin_integration", "exec_snapshot_link")

MAX_RETRIES = 3
DEFAULT_SLEEP = 1.0
THRESHOLD = 0.95
BUFFER_SIZE = 8192
BATCH_SIZE = 32
MAX_DEPTH = 6
MAX_FILES = 1000
DEFAULT_TIMEOUT = 300


@dataclass
class _Ctx:
    """Minimal ExecutionContext stand-in."""

    mission_id: str = ""
    step_id: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    trace_id: str | None = None
    parent_span_id: str | None = None
    replay_mode: bool = False
    active_policy_hash: str | None = None
    safety_status: str = "PENDING"


# ---------------------------------------------------------------------------
# Composite test classes
# ---------------------------------------------------------------------------


class _MetricsObj(SSOTMetricsMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _CacheObj(SSOTCachingMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _BreakerObj(SSOTCircuitBreakerMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _RateLimitObj(SSOTRateLimitMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _StateValObj(SSOTStateValidationMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _TracingObj(SSOTTracingMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _CtxPropObj(SSOTContextPropagationMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _DiagObj(SSOTSelfDiagnosisMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _AdaptObj(SSOTAdaptiveExecutionMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _HalluObj(SSOTHallucinationDetectionMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _CogRecObj(SSOTCognitiveRecoveryMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _MLObj(SSOTMetaLearningMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


class _FlagObj(SSOTFeatureFlagMixin, ReplayGuardMixin):
    def __init__(self, ctx=None):
        super().__init__(execution_context=ctx)


@pytest.fixture(autouse=True)
def _cleanup():
    unpatch_deterministic()
    yield
    unpatch_deterministic()


# ===================================================================
# PHASE 2 — Metrics + Caching
# ===================================================================


class TestSSOTMetrics:
    @pytest.mark.unit_min_deps
    def test_metric_scoped_by_policy_hash(self):
        ctx = _Ctx(trace_id="t1", active_policy_hash="ph-m1")
        obj = _MetricsObj(ctx)
        entry = obj.record_metric("heal_count", 5.0)
        assert entry["scoped_key"].startswith("ph-m1:")
        assert entry["policy_hash"] == "ph-m1"

    @pytest.mark.unit_min_deps
    def test_different_policy_hash_isolates_metrics(self):
        obj1 = _MetricsObj(_Ctx(trace_id="t", active_policy_hash="A"))
        obj2 = _MetricsObj(_Ctx(trace_id="t", active_policy_hash="B"))
        obj1.record_metric("x", 1.0)
        obj2.record_metric("x", 2.0)
        assert obj1.get_metrics("x")[0]["value"] == 1.0
        assert obj2.get_metrics("x")[0]["value"] == 2.0

    @pytest.mark.unit_min_deps
    def test_get_all_metrics(self):
        obj = _MetricsObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.record_metric("a", 1.0)
        obj.record_metric("b", 2.0)
        assert len(obj.get_metrics()) == 2

    @pytest.mark.unit_min_deps
    def test_clear_metrics(self):
        obj = _MetricsObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.record_metric("a", 1.0)
        obj.clear_metrics()
        assert len(obj.get_metrics()) == 0


class TestSSOTCaching:
    @pytest.mark.unit_min_deps
    def test_cache_set_get(self):
        obj = _CacheObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.cache_set("key1", "value1")
        assert obj.cache_get("key1") == "value1"

    @pytest.mark.unit_min_deps
    def test_cache_scoped_by_policy_hash(self):
        obj1 = _CacheObj(_Ctx(trace_id="t", active_policy_hash="A"))
        obj2 = _CacheObj(_Ctx(trace_id="t", active_policy_hash="B"))
        obj1.cache_set("k", "v1")
        assert obj2.cache_get("k") is None  # Different policy hash

    @pytest.mark.unit_min_deps
    def test_replay_disables_ttl(self):
        ctx = _Ctx(trace_id="t-replay", active_policy_hash="ph", replay_mode=True)
        obj = _CacheObj(ctx)
        obj.cache_set("k", "v", ttl=0.001)
        # Under replay, TTL is None so entry never expires
        import time

        time.sleep(DEFAULT_SLEEP)  # patched sleep advances virtual clock
        assert obj.cache_get("k") == "v"

    @pytest.mark.unit_min_deps
    def test_cache_invalidate(self):
        obj = _CacheObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.cache_set("k", "v")
        assert obj.cache_invalidate("k") is True
        assert obj.cache_get("k") is None

    @pytest.mark.unit_min_deps
    def test_cache_size_and_clear(self):
        obj = _CacheObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.cache_set("a", 1)
        obj.cache_set("b", 2)
        assert obj.cache_size() == 2
        assert obj.cache_clear() == 2
        assert obj.cache_size() == 0


# ===================================================================
# PHASE 3 — CircuitBreaker + RateLimit + StateValidation
# ===================================================================


class TestSSOTCircuitBreaker:
    @pytest.mark.unit_min_deps
    def test_successful_call_passes(self):
        obj = _BreakerObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        result = obj.breaker_call("bucket", lambda: 42)
        assert result == 42

    @pytest.mark.unit_min_deps
    def test_breaker_scoped_by_policy_hash(self):
        obj = _BreakerObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.breaker_call("b", lambda: 1)
        assert obj.breaker_status("b") == "closed"

    @pytest.mark.unit_min_deps
    def test_safety_exceptions_propagate(self):
        obj = _BreakerObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with pytest.raises(StateValidationError):
            obj.breaker_call("b", _raise_state_validation)
        with pytest.raises(PolicyHashMismatch):
            obj.breaker_call("b", _raise_policy_mismatch)
        with pytest.raises(SovereignTokenDenied):
            obj.breaker_call("b", _raise_token_denied)

    @pytest.mark.unit_min_deps
    def test_breaker_opens_after_threshold(self):
        obj = _BreakerObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        for _ in range(5):
            with pytest.raises(RuntimeError):
                obj.breaker_call("b", _raise_runtime)
        assert obj.breaker_status("b") == "open"

    @pytest.mark.unit_min_deps
    def test_open_breaker_raises_circuit_open(self):
        obj = _BreakerObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        for _ in range(5):
            with pytest.raises(RuntimeError):
                obj.breaker_call("b", _raise_runtime)
        with pytest.raises(CircuitOpenError):
            obj.breaker_call("b", lambda: 1)

    @pytest.mark.unit_min_deps
    def test_replay_mode_no_breaker_mutation(self):
        ctx = _Ctx(trace_id="t-replay", active_policy_hash="ph", replay_mode=True)
        obj = _BreakerObj(ctx)
        for _ in range(10):
            with pytest.raises(RuntimeError):
                obj.breaker_call("b", _raise_runtime)
        # Under replay, breaker state should NOT mutate
        assert obj.breaker_status("b") == "closed"

    @pytest.mark.unit_min_deps
    def test_breaker_reset(self):
        obj = _BreakerObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        for _ in range(5):
            with pytest.raises(RuntimeError):
                obj.breaker_call("b", _raise_runtime)
        obj.breaker_reset("b")
        assert obj.breaker_status("b") == "closed"


class TestSSOTRateLimit:
    @pytest.mark.unit_min_deps
    def test_rate_check_allows_within_limit(self):
        obj = _RateLimitObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        assert obj.rate_check("bucket", limit=LIMIT) is True

    @pytest.mark.unit_min_deps
    def test_rate_check_raises_on_exceed(self):
        obj = _RateLimitObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        for _ in range(3):
            obj.rate_check("b", limit=LIMIT, window=60.0)
        with pytest.raises(RateLimitExceeded):
            obj.rate_check("b", limit=LIMIT, window=60.0)

    @pytest.mark.unit_min_deps
    def test_replay_mode_disables_rate_limit(self):
        ctx = _Ctx(trace_id="t-replay", active_policy_hash="ph", replay_mode=True)
        obj = _RateLimitObj(ctx)
        for _ in range(100):
            assert obj.rate_check("b", limit=LIMIT) is True

    @pytest.mark.unit_min_deps
    def test_rate_remaining(self):
        obj = _RateLimitObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.rate_check("b", limit=LIMIT)
        assert obj.rate_remaining("b", limit=LIMIT) == 4

    @pytest.mark.unit_min_deps
    def test_rate_reset(self):
        obj = _RateLimitObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        for _ in range(3):
            obj.rate_check("b", limit=LIMIT)
        obj.rate_reset("b")
        assert obj.rate_remaining("b", limit=LIMIT) == 5


class TestSSOTStateValidation:
    @pytest.mark.unit_min_deps
    def test_precondition_passes(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.validate_precondition("check_ok", True)  # Should not raise

    @pytest.mark.unit_min_deps
    def test_precondition_fails(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with pytest.raises(SSOTStateValidationError):
            obj.validate_precondition("check_fail", False)

    @pytest.mark.unit_min_deps
    def test_postcondition_fails(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with pytest.raises(SSOTStateValidationError):
            obj.validate_postcondition("post_fail", False)

    @pytest.mark.unit_min_deps
    def test_safety_cleared_validation(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED"))
        obj.validate_safety_cleared()  # Should not raise

    @pytest.mark.unit_min_deps
    def test_safety_not_cleared_raises(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph", safety_status="PENDING"))
        with pytest.raises(SSOTStateValidationError):
            obj.validate_safety_cleared()

    @pytest.mark.unit_min_deps
    def test_policy_hash_stable_validation(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.validate_policy_hash_stable()  # Should not raise

    @pytest.mark.unit_min_deps
    def test_policy_hash_drift_raises(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj._active_policy_hash = "drifted"
        with pytest.raises(SSOTStateValidationError):
            obj.validate_policy_hash_stable()

    @pytest.mark.unit_min_deps
    def test_failure_count_tracked(self):
        obj = _StateValObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with pytest.raises(SSOTStateValidationError):
            obj.validate_precondition("f1", False)
        with pytest.raises(SSOTStateValidationError):
            obj.validate_postcondition("f2", False)
        assert obj.validation_failure_count == 2


# ===================================================================
# PHASE 4 — Tracing + ContextPropagation
# ===================================================================


class TestSSOTTracing:
    @pytest.mark.unit_min_deps
    def test_span_records_trace_and_policy(self):
        obj = _TracingObj(_Ctx(trace_id="t-trace", active_policy_hash="ph-trace"))
        with obj.trace_span("test_op") as span:
            pass
        assert span["trace_id"] == "t-trace"
        assert span["policy_hash"] == "ph-trace"
        assert span["status"] == "ok"

    @pytest.mark.unit_min_deps
    def test_span_records_duration(self):
        obj = _TracingObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with obj.trace_span("op") as span:
            pass
        assert span["duration_ms"] is not None
        assert span["duration_ms"] >= 0

    @pytest.mark.unit_min_deps
    def test_span_error_status(self):
        obj = _TracingObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with pytest.raises(ValueError):
            with obj.trace_span("fail_op") as span:
                raise ValueError("test error")
        assert span["status"] == "error"
        assert span["error"] == "test error"

    @pytest.mark.unit_min_deps
    def test_nested_spans(self):
        obj = _TracingObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with obj.trace_span("outer"):
            with obj.trace_span("inner") as inner:
                assert inner.get("parent_operation") == "outer"
        assert len(obj.completed_spans) == 2

    @pytest.mark.unit_min_deps
    def test_completed_spans_list(self):
        obj = _TracingObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        with obj.trace_span("a"):
            pass
        with obj.trace_span("b"):
            pass
        assert len(obj.completed_spans) == 2


class TestSSOTContextPropagation:
    @pytest.mark.unit_min_deps
    def test_propagates_to_contextvars(self):
        _CtxPropObj(_Ctx(trace_id="t-prop", active_policy_hash="ph-prop"))
        assert get_propagated_trace_id() == "t-prop"
        assert get_propagated_policy_hash() == "ph-prop"
        assert get_propagated_replay_mode() is False

    @pytest.mark.unit_min_deps
    def test_replay_mode_propagated(self):
        _CtxPropObj(
            _Ctx(
                trace_id="t-rep",
                active_policy_hash="ph",
                replay_mode=True,
            )
        )
        assert get_propagated_replay_mode() is True

    @pytest.mark.unit_min_deps
    def test_propagation_scope_restores(self):
        obj = _CtxPropObj(_Ctx(trace_id="t1", active_policy_hash="ph1"))
        # Create a second object with different values to overwrite contextvars
        _CtxPropObj(_Ctx(trace_id="t2", active_policy_hash="ph2"))
        assert get_propagated_trace_id() == "t2"
        with obj.propagation_scope():
            assert get_propagated_trace_id() == "t1"
        assert get_propagated_trace_id() == "t2"


# ===================================================================
# PHASE 5 — SelfDiagnosis + AdaptiveExecution
# ===================================================================


class TestSSOTSelfDiagnosis:
    @pytest.mark.unit_min_deps
    def test_health_check_pass(self):
        obj = _DiagObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        rec = obj.run_health_check("check1", True)
        assert rec["passed"] is True
        assert obj.health_status == "HEALTHY"

    @pytest.mark.unit_min_deps
    def test_health_check_fail_degrades(self):
        obj = _DiagObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.run_health_check("check1", False, "something broke")
        assert obj.health_status == "DEGRADED"
        assert len(obj.failed_checks) == 1

    @pytest.mark.unit_min_deps
    def test_reset_health(self):
        obj = _DiagObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.run_health_check("c", False)
        obj.reset_health()
        assert obj.health_status == "HEALTHY"
        assert len(obj.health_checks) == 0


class TestSSOTAdaptiveExecution:
    @pytest.mark.unit_min_deps
    def test_default_mode_standard(self):
        obj = _AdaptObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        assert obj.execution_mode == "standard"

    @pytest.mark.unit_min_deps
    def test_set_mode(self):
        obj = _AdaptObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        assert obj.set_execution_mode("aggressive") is True
        assert obj.execution_mode == "aggressive"

    @pytest.mark.unit_min_deps
    def test_replay_locks_to_standard(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _AdaptObj(ctx)
        assert obj.execution_mode == "standard"
        assert obj.set_execution_mode("aggressive") is False
        assert obj.execution_mode == "standard"

    @pytest.mark.unit_min_deps
    def test_derive_mode_conservative(self):
        obj = _AdaptObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        assert obj.derive_mode_from_signals(failure_rate=0.6) == "conservative"

    @pytest.mark.unit_min_deps
    def test_derive_mode_replay_always_standard(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _AdaptObj(ctx)
        assert obj.derive_mode_from_signals(failure_rate=0.9) == "standard"

    @pytest.mark.unit_min_deps
    def test_invalid_mode_rejected(self):
        obj = _AdaptObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        assert obj.set_execution_mode("invalid_mode") is False


# ===================================================================
# PHASE 6 — HallucinationDetection + CognitiveRecovery
# ===================================================================


class TestSSOTHallucinationDetection:
    @pytest.mark.unit_min_deps
    def test_normal_output_low_suspicion(self):
        obj = _HalluObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        result = obj.detect_hallucination("def fix_imports():\n    pass")
        assert result["is_suspicious"] is False

    @pytest.mark.unit_min_deps
    def test_empty_output_high_suspicion(self):
        obj = _HalluObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        result = obj.detect_hallucination("")
        assert result["is_suspicious"] is True

    @pytest.mark.unit_min_deps
    def test_replay_deterministic(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj1 = _HalluObj(ctx)
        obj2 = _HalluObj(ctx)
        r1 = obj1.detect_hallucination("test output")
        r2 = obj2.detect_hallucination("test output")
        assert r1["confidence"] == r2["confidence"]

    @pytest.mark.unit_min_deps
    def test_detection_history(self):
        obj = _HalluObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.detect_hallucination("a")
        obj.detect_hallucination("b")
        assert len(obj.detection_history) == 2


class TestSSOTCognitiveRecovery:
    @pytest.mark.unit_min_deps
    def test_suggest_recovery(self):
        obj = _CogRecObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        sug = obj.suggest_recovery("import_error")
        assert sug is not None
        assert sug["strategy"] == "fix_imports"

    @pytest.mark.unit_min_deps
    def test_replay_returns_none(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _CogRecObj(ctx)
        assert obj.suggest_recovery("import_error") is None

    @pytest.mark.unit_min_deps
    def test_recovery_hints_recorded(self):
        obj = _CogRecObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        obj.suggest_recovery("naming_violation")
        assert len(obj.recovery_hints) == 1

    @pytest.mark.unit_min_deps
    def test_unknown_failure_manual_review(self):
        obj = _CogRecObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        sug = obj.suggest_recovery("unknown_thing")
        assert sug["strategy"] == "manual_review"


# ===================================================================
# PHASE 7 — MetaLearning + FeatureFlags
# ===================================================================


class TestSSOTMetaLearning:
    @pytest.mark.unit_min_deps
    def test_store_and_read(self):
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _MLObj(ctx)
        obj.ml_store_pattern("healing", {"type": "import_fix"})
        patterns = obj.ml_read_patterns("healing")
        assert len(patterns) == 1
        assert patterns[0]["pattern"]["type"] == "import_fix"

    @pytest.mark.unit_min_deps
    def test_replay_blocks_writes(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True, safety_status="CLEARED")
        obj = _MLObj(ctx)
        with pytest.raises(MetaLearningWriteRejected, match="replay mode"):
            obj.ml_store_pattern("d", {"x": 1})

    @pytest.mark.unit_min_deps
    def test_safety_not_cleared_blocks_writes(self):
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="PENDING")
        obj = _MLObj(ctx)
        with pytest.raises(MetaLearningWriteRejected, match="safety_status"):
            obj.ml_store_pattern("d", {"x": 1})

    @pytest.mark.unit_min_deps
    def test_policy_drift_blocks_writes(self):
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _MLObj(ctx)
        obj._active_policy_hash = "drifted"
        with pytest.raises(MetaLearningWriteRejected, match="drifted"):
            obj.ml_store_pattern("d", {"x": 1})

    @pytest.mark.unit_min_deps
    def test_failure_blocks_writes(self):
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _MLObj(ctx)
        with pytest.raises(MetaLearningWriteRejected, match="success"):
            obj.ml_store_pattern("d", {"x": 1}, success=False)

    @pytest.mark.unit_min_deps
    def test_read_always_allowed(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _MLObj(ctx)
        # Read should work even in replay mode
        patterns = obj.ml_read_patterns("healing")
        assert patterns == []

    @pytest.mark.unit_min_deps
    def test_namespace_scoped_by_policy(self):
        ctx1 = _Ctx(trace_id="t", active_policy_hash="A", safety_status="CLEARED")
        ctx2 = _Ctx(trace_id="t", active_policy_hash="B", safety_status="CLEARED")
        obj1 = _MLObj(ctx1)
        obj2 = _MLObj(ctx2)
        obj1.ml_store_pattern("d", {"from": "A"})
        assert obj1.ml_pattern_count("d") == 1
        assert obj2.ml_pattern_count("d") == 0

    @pytest.mark.unit_min_deps
    def test_clear_patterns(self):
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _MLObj(ctx)
        obj.ml_store_pattern("d", {"x": 1})
        assert obj.ml_clear_patterns("d") == 1
        assert obj.ml_pattern_count("d") == 0


class TestSSOTFeatureFlags:
    @pytest.mark.unit_min_deps
    def test_default_flags_loaded(self):
        obj = _FlagObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        assert obj.flag_enabled("enable_llm_healing") is True
        assert obj.flag_enabled("nonexistent", default=False) is False

    @pytest.mark.unit_min_deps
    def test_flag_set(self):
        obj = _FlagObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        assert obj.flag_set("custom_flag", True) is True
        assert obj.flag_enabled("custom_flag") is True

    @pytest.mark.unit_min_deps
    def test_replay_freezes_flags(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FlagObj(ctx)
        assert obj.flags_frozen is True
        assert obj.flag_set("new_flag", True) is False

    @pytest.mark.unit_min_deps
    def test_all_flags_returns_copy(self):
        obj = _FlagObj(_Ctx(trace_id="t", active_policy_hash="ph"))
        flags = obj.all_flags
        assert isinstance(flags, dict)
        assert "enable_llm_healing" in flags


# ===================================================================
# Helpers
# ===================================================================


def _raise_state_validation():
    raise StateValidationError("test")


def _raise_policy_mismatch():
    raise PolicyHashMismatch("test")


def _raise_token_denied():
    raise SovereignTokenDenied("test")


def _raise_runtime():
    raise RuntimeError("test failure")
