"""
SSOT Mixin Stack Integration Tests.

Validates:
  - Full MRO resolution without conflicts
  - All mixin properties accessible from composite class
  - ExecutionContext threading through full stack
  - Replay mode propagation through all mixins
  - Policy hash scoping across all mixins
  - No MRO duplicate mixins
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

import pytest

from agentic_core.L2_execution.deterministic_providers import (
    is_patched,
    unpatch_deterministic,
)
from agentic_core.mixins.ssot_mixin_stack import SSOTMixinStack


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


class _FullStackEngine(SSOTMixinStack):
    """Simulates a decision engine with full SSOT mixin stack."""

    def __init__(self, execution_context=None):
        self.state = {"audit_chain": []}
        super().__init__(execution_context=execution_context)


@pytest.fixture(autouse=True)
def _cleanup():
    unpatch_deterministic()
    yield
    unpatch_deterministic()


class TestMROResolution:
    @pytest.mark.unit_min_deps
    def test_mro_resolves_without_error(self):
        """Full mixin stack MRO resolves cleanly."""
        mro = _FullStackEngine.__mro__
        assert len(mro) > 15  # All mixins + object

    @pytest.mark.unit_min_deps
    def test_no_duplicate_mixins_in_mro(self):
        """No mixin appears twice in MRO."""
        mro = _FullStackEngine.__mro__
        mro_names = [cls.__name__ for cls in mro]
        assert len(mro_names) == len(set(mro_names))

    @pytest.mark.unit_min_deps
    def test_replay_guard_is_last_ssot_mixin(self):
        """ReplayGuardMixin is the last SSOT mixin before object."""
        mro = _FullStackEngine.__mro__
        mro_names = [cls.__name__ for cls in mro]
        rg_idx = mro_names.index("ReplayGuardMixin")
        # Only 'object' should follow ReplayGuardMixin
        assert mro_names[rg_idx + 1] == "object"


class TestFullStackConstruction:
    @pytest.mark.unit_min_deps
    def test_non_replay_construction(self):
        """Full stack constructs in non-replay mode."""
        ctx = _Ctx(
            trace_id="t-full",
            active_policy_hash="ph-full",
            safety_status="CLEARED",
        )
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.is_replay_mode is False
        assert obj.trace_id == "t-full"
        assert obj.active_policy_hash == "ph-full"
        assert not is_patched()

    @pytest.mark.unit_min_deps
    def test_replay_construction(self):
        """Full stack constructs in replay mode with deterministic providers."""
        ctx = _Ctx(
            trace_id="t-replay",
            active_policy_hash="ph-replay",
            replay_mode=True,
            safety_status="CLEARED",
        )
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.is_replay_mode is True
        assert is_patched()

    @pytest.mark.unit_min_deps
    def test_default_construction(self):
        """Full stack constructs with no context (all defaults)."""
        obj = _FullStackEngine()
        assert obj.is_replay_mode is False
        assert obj.trace_id == "no-trace"


class TestCrossMixinIntegration:
    @pytest.mark.unit_min_deps
    def test_audit_trail_accessible(self):
        """SSOTAuditTrailMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        entry = obj.emit_ssot_audit_entry("TEST", "target.py")
        assert entry["trace_id"] == "t"
        assert entry["policy_hash"] == "ph"

    @pytest.mark.unit_min_deps
    def test_metrics_accessible(self):
        """SSOTMetricsMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        m = obj.record_metric("test_metric", 42.0)
        assert m["scoped_key"] == "ph:test_metric"

    @pytest.mark.unit_min_deps
    def test_cache_accessible(self):
        """SSOTCachingMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        obj.cache_set("k", "v")
        assert obj.cache_get("k") == "v"

    @pytest.mark.unit_min_deps
    def test_circuit_breaker_accessible(self):
        """SSOTCircuitBreakerMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        result = obj.breaker_call("b", lambda: 99)
        assert result == 99

    @pytest.mark.unit_min_deps
    def test_rate_limit_accessible(self):
        """SSOTRateLimitMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.rate_check("b", limit=10) is True

    @pytest.mark.unit_min_deps
    def test_state_validation_accessible(self):
        """SSOTStateValidationMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)
        obj.validate_safety_cleared()  # Should not raise
        assert True  # no-exception contract

    @pytest.mark.unit_min_deps
    def test_tracing_accessible(self):
        """SSOTTracingMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        with obj.trace_span("test_op") as span:
            pass
        assert span["trace_id"] == "t"

    @pytest.mark.unit_min_deps
    def test_self_diagnosis_accessible(self):
        """SSOTSelfDiagnosisMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        obj.run_health_check("check1", True)
        assert obj.health_status == "HEALTHY"

    @pytest.mark.unit_min_deps
    def test_adaptive_execution_accessible(self):
        """SSOTAdaptiveExecutionMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.execution_mode == "standard"

    @pytest.mark.unit_min_deps
    def test_hallucination_detection_accessible(self):
        """SSOTHallucinationDetectionMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        result = obj.detect_hallucination("def foo(): pass")
        assert "confidence" in result

    @pytest.mark.unit_min_deps
    def test_cognitive_recovery_accessible(self):
        """SSOTCognitiveRecoveryMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        sug = obj.suggest_recovery("import_error")
        assert sug["strategy"] == "fix_imports"

    @pytest.mark.unit_min_deps
    def test_meta_learning_accessible(self):
        """SSOTMetaLearningMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph", safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)
        obj.ml_store_pattern("domain", {"type": "test"})
        assert obj.ml_pattern_count("domain") == 1

    @pytest.mark.unit_min_deps
    def test_feature_flags_accessible(self):
        """SSOTFeatureFlagMixin methods accessible from full stack."""
        ctx = _Ctx(trace_id="t", active_policy_hash="ph")
        obj = _FullStackEngine(execution_context=ctx)
        assert isinstance(obj.all_flags, dict)

    @pytest.mark.unit_min_deps
    def test_audit_chain_integrity_across_operations(self):
        """Audit chain remains valid after multiple cross-mixin operations."""
        ctx = _Ctx(trace_id="t-chain", active_policy_hash="ph-chain", safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)

        obj.emit_ssot_audit_entry("BOOT", "system")
        obj.record_metric("boot_time", 0.5)
        obj.emit_ssot_audit_entry("HEAL", "file.py", diff={"line": 10})
        obj.cache_set("result", "ok")
        obj.emit_ssot_audit_entry("VALIDATE", "file.py")

        valid, broken = obj.verify_ssot_audit_chain()
        assert valid is True
        assert broken is None
        assert len(obj.state["audit_chain"]) == 3


class TestReplayModeAcrossStack:
    @pytest.mark.unit_min_deps
    def test_replay_disables_rate_limit(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        for _ in range(100):
            assert obj.rate_check("b", limit=1) is True

    @pytest.mark.unit_min_deps
    def test_replay_freezes_flags(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.flags_frozen is True

    @pytest.mark.unit_min_deps
    def test_replay_locks_adaptive_mode(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.execution_mode == "standard"
        assert obj.set_execution_mode("aggressive") is False

    @pytest.mark.unit_min_deps
    def test_replay_blocks_ml_writes(self):
        from agentic_core.mixins.ssot_meta_learning_mixin import MetaLearningWriteRejected

        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True, safety_status="CLEARED")
        obj = _FullStackEngine(execution_context=ctx)
        with pytest.raises(MetaLearningWriteRejected):
            obj.ml_store_pattern("d", {"x": 1})

    @pytest.mark.unit_min_deps
    def test_replay_cognitive_recovery_returns_none(self):
        ctx = _Ctx(trace_id="t-rep", active_policy_hash="ph", replay_mode=True)
        obj = _FullStackEngine(execution_context=ctx)
        assert obj.suggest_recovery("import_error") is None
