"""
Unit tests for spine adapter wiring — verifies D0EngineAdapter, RiskGateAdapter,
VigilanceDispatcherAdapter, and MetaLearningBus are properly wired in both
LicSpineAdapter and RgSpineAdapter (G1-a/b/c/d).

Also covers BaseSpineAdapter error paths (G14).
"""

from __future__ import annotations

import pytest

from agentic_core.L0_routing.meta_control.meta_learning_bus import MetaLearningBus
from apps_lic.engines.lic_spine_adapter import LicSpineAdapter
from apps_rg.engines.rg_spine_adapter import RgSpineAdapter
from apps_shared.spine.d0_engine_adapter import D0EngineAdapter
from apps_shared.spine.risk_gate_adapter import RiskGateAdapter, RiskResult
from apps_shared.spine.vigilance_dispatcher_adapter import VigilanceDispatcherAdapter

# ---------------------------------------------------------------------------
# D0EngineAdapter contract tests
# ---------------------------------------------------------------------------


class TestD0EngineAdapter:
    def test_instantiates_without_error(self):
        adapter = D0EngineAdapter()
        assert adapter is not None

    def test_render_d0_empty_string_returns_empty(self):
        adapter = D0EngineAdapter()
        result = adapter.render_d0("")
        assert result == ""

    def test_render_d0_passthrough_when_no_real_engine(self):
        """If real engine unavailable, returns input unchanged."""
        adapter = D0EngineAdapter()
        if not adapter.is_real:
            result = adapter.render_d0("some:fence text")
            assert result == "some:fence text"

    def test_render_d0_with_real_engine_produces_xml_wrapper(self):
        adapter = D0EngineAdapter()
        if adapter.is_real:
            result = adapter.render_d0("role_a:Allow all reads|role_b:Deny writes")
            assert "<D0>" in result
            assert "</D0>" in result

    def test_render_d0_with_real_engine_deterministic(self):
        adapter = D0EngineAdapter()
        r1 = adapter.render_d0("role_b:text_b|role_a:text_a")
        r2 = adapter.render_d0("role_b:text_b|role_a:text_a")
        assert r1 == r2

    def test_render_d0_with_real_engine_sorted_fences(self):
        """Fences must be sorted by fence_id for deterministic output."""
        adapter = D0EngineAdapter()
        if adapter.is_real:
            result = adapter.render_d0("z_fence:last|a_fence:first")
            lines = result.strip().splitlines()
            content_lines = [l for l in lines if l.startswith("[")]
            assert content_lines[0].startswith("[a_fence]")
            assert content_lines[1].startswith("[z_fence]")

    def test_render_d0_malformed_segment_skipped(self):
        """Segments without ':' are skipped gracefully."""
        adapter = D0EngineAdapter()
        if adapter.is_real:
            # segment "nocolon" has no ':', should be skipped
            result = adapter.render_d0("valid_id:valid text|nocolon")
            assert "<D0>" in result
            # Only valid segment rendered
            assert "[valid_id]" in result

    def test_render_d0_single_fence(self):
        adapter = D0EngineAdapter()
        if adapter.is_real:
            result = adapter.render_d0("single_fence:some important text")
            assert "[single_fence]" in result

    def test_is_real_attribute_present(self):
        adapter = D0EngineAdapter()
        assert isinstance(adapter.is_real, bool)


# ---------------------------------------------------------------------------
# RiskGateAdapter contract tests
# ---------------------------------------------------------------------------


class TestRiskGateAdapter:
    def test_instantiates_without_error(self):
        adapter = RiskGateAdapter()
        assert adapter is not None

    def test_evaluate_returns_risk_result(self):
        adapter = RiskGateAdapter()

        class _Payload:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_Payload(), d0_injections="")
        assert isinstance(result, RiskResult)

    def test_evaluate_allows_clean_payload(self):
        adapter = RiskGateAdapter()

        class _CleanPayload:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_CleanPayload(), d0_injections="")
        assert result.allow is True

    def test_evaluate_blocks_on_deny_execution_in_d0(self):
        adapter = RiskGateAdapter()
        if not adapter.is_real:
            pytest.fail("Real gate not available")

        class _Payload:
            sanitized = False
            check_ids = ()

        result = adapter.evaluate(payload_like=_Payload(), d0_injections="DENY_EXECUTION")
        assert result.allow is False
        assert result.level == "HIGH"
        assert "D0_DENY_EXECUTION" in result.reasons

    def test_evaluate_medium_risk_on_sanitized_input(self):
        adapter = RiskGateAdapter()
        if not adapter.is_real:
            pytest.fail("Real gate not available")

        class _SanitizedPayload:
            sanitized = True
            check_ids = ()

        result = adapter.evaluate(payload_like=_SanitizedPayload(), d0_injections="")
        assert result.level == "MEDIUM"
        assert "SANITIZED_INPUT" in result.reasons

    def test_evaluate_medium_risk_on_many_check_ids(self):
        adapter = RiskGateAdapter()
        if not adapter.is_real:
            pytest.fail("Real gate not available")

        class _HeavyPayload:
            sanitized = False
            check_ids = ("c1", "c2", "c3", "c4", "c5")

        result = adapter.evaluate(payload_like=_HeavyPayload(), d0_injections="")
        assert result.level == "MEDIUM"
        assert "MANY_CHECK_IDS" in result.reasons

    def test_evaluate_deterministic(self):
        adapter = RiskGateAdapter()

        class _P:
            sanitized = False
            check_ids = ()

        r1 = adapter.evaluate(payload_like=_P(), d0_injections="neutral")
        r2 = adapter.evaluate(payload_like=_P(), d0_injections="neutral")
        assert r1.allow == r2.allow
        assert r1.level == r2.level
        assert r1.reasons == r2.reasons

    def test_null_fallback_returns_allow_true(self):
        """When real gate unavailable, adapter returns allow=True."""
        adapter = RiskGateAdapter()
        if adapter.is_real:
            pytest.fail("Real gate available, null fallback test not applicable")

        class _P:
            pass

        result = adapter.evaluate(payload_like=_P(), d0_injections="DENY_EXECUTION")
        assert result.allow is True


# ---------------------------------------------------------------------------
# VigilanceDispatcherAdapter contract tests
# ---------------------------------------------------------------------------


class TestVigilanceDispatcherAdapter:
    def test_instantiates_without_error(self):
        adapter = VigilanceDispatcherAdapter()
        assert adapter is not None

    def test_dispatch_does_not_raise(self):
        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch(trace_id="t1", signals=("sig_a",), summary="test dispatch")
        assert True  # no-exception contract

    def test_dispatch_with_no_kwargs_does_not_raise(self):
        adapter = VigilanceDispatcherAdapter()
        adapter.dispatch()
        assert True  # no-exception contract

    def test_dispatch_enqueues_event_when_real(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import _drain_event_queue

        _drain_event_queue()  # clear
        adapter = VigilanceDispatcherAdapter()
        if adapter.is_real:
            adapter.dispatch(trace_id="test_trace", signals=("signal_1",), summary="test")
            events = _drain_event_queue()
            assert len(events) == 1
            assert events[0].trace_id == "test_trace"

    def test_dispatch_exception_does_not_propagate(self):
        """Any internal dispatch error must be swallowed silently."""
        adapter = VigilanceDispatcherAdapter()
        # Pass None as trace_id to trigger potential conversion errors
        # Must not raise
        adapter.dispatch(trace_id=None, signals=None, summary=None)
        assert True  # no-exception contract

    def test_event_queue_bounded(self):
        from apps_shared.spine.vigilance_dispatcher_adapter import _EVENT_QUEUE, _drain_event_queue

        _drain_event_queue()
        adapter = VigilanceDispatcherAdapter()
        if adapter.is_real:
            for i in range(300):
                adapter.dispatch(trace_id=f"t{i}", signals=(f"s{i}",), summary=f"ev{i}")
            assert len(_EVENT_QUEUE) <= 256
            _drain_event_queue()


# ---------------------------------------------------------------------------
# MetaLearningBus integration with spine (G1-d)
# ---------------------------------------------------------------------------


class TestMetaLearningBusInSpine:
    def test_lic_spine_has_meta_learning_bus(self):
        adapter = LicSpineAdapter()
        # Access internal orchestrator's meta_bus
        orch = adapter._orchestrator
        assert isinstance(orch.meta_bus, MetaLearningBus)

    def test_rg_spine_has_meta_learning_bus(self):
        adapter = RgSpineAdapter()
        orch = adapter._orchestrator
        assert isinstance(orch.meta_bus, MetaLearningBus)

    def test_meta_bus_enqueue_and_dequeue(self):
        from agentic_core.L0_routing.meta_control.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningChangePackage,
        )

        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create(trace_id="trace_001", kind="threshold", payload={"key": "val"})
        bus.enqueue(pkg)
        assert bus.size() == 1
        result = bus.dequeue()
        assert result is not None
        assert result.trace_id == "trace_001"
        assert bus.size() == 0

    def test_meta_bus_dequeue_empty_returns_none(self):
        bus = MetaLearningBus()
        assert bus.dequeue() is None

    def test_meta_bus_apply_next_calls_apply_fn(self):
        from agentic_core.L0_routing.meta_control.meta_learning_bus import (
            MetaLearningBus,
            MetaLearningChangePackage,
        )

        bus = MetaLearningBus()
        pkg = MetaLearningChangePackage.create("t1", "kind_x", {"a": 1})
        bus.enqueue(pkg)
        applied = []
        bus.apply_next(apply_fn=applied.append)
        assert len(applied) == 1
        assert applied[0].trace_id == "t1"


# ---------------------------------------------------------------------------
# LicSpineAdapter / RgSpineAdapter: real adapter wiring end-to-end
# ---------------------------------------------------------------------------


class TestSpineAdapterRealWiring:
    def test_lic_spine_d0_engine_is_adapter(self):
        spine = LicSpineAdapter()
        orch = spine._orchestrator
        assert isinstance(orch.d0_engine, D0EngineAdapter)

    def test_lic_spine_risk_gate_is_adapter(self):
        spine = LicSpineAdapter()
        orch = spine._orchestrator
        assert isinstance(orch.risk_gate, RiskGateAdapter)

    def test_lic_spine_vigilance_is_adapter(self):
        spine = LicSpineAdapter()
        orch = spine._orchestrator
        assert isinstance(orch.vigilance_dispatcher, VigilanceDispatcherAdapter)

    def test_rg_spine_d0_engine_is_adapter(self):
        spine = RgSpineAdapter()
        orch = spine._orchestrator
        assert isinstance(orch.d0_engine, D0EngineAdapter)

    def test_rg_spine_risk_gate_is_adapter(self):
        spine = RgSpineAdapter()
        orch = spine._orchestrator
        assert isinstance(orch.risk_gate, RiskGateAdapter)

    def test_rg_spine_vigilance_is_adapter(self):
        spine = RgSpineAdapter()
        orch = spine._orchestrator
        assert isinstance(orch.vigilance_dispatcher, VigilanceDispatcherAdapter)

    def test_lic_execute_returns_result_with_cid(self):
        spine = LicSpineAdapter()
        result = spine.execute({"u0_user_prompt": "hello world"})
        assert "cid" in result
        assert result["cid"].startswith("lic-")

    def test_rg_execute_returns_result_with_cid(self):
        spine = RgSpineAdapter()
        result = spine.execute({"u0_user_prompt": "hello rg"})
        assert "cid" in result
        assert result["cid"].startswith("rg-")

    def test_lic_execute_deterministic_cid(self):
        """Same input → same CID (deterministic hash derivation)."""
        s1 = LicSpineAdapter()
        s2 = LicSpineAdapter()
        r1 = s1.execute({"u0_user_prompt": "determinism test"})
        r2 = s2.execute({"u0_user_prompt": "determinism test"})
        assert r1["cid"] == r2["cid"]

    def test_rg_execute_deterministic_cid(self):
        s1 = RgSpineAdapter()
        s2 = RgSpineAdapter()
        r1 = s1.execute({"u0_user_prompt": "determinism rg"})
        r2 = s2.execute({"u0_user_prompt": "determinism rg"})
        assert r1["cid"] == r2["cid"]

    def test_different_inputs_produce_different_cids(self):
        spine = LicSpineAdapter()
        r1 = spine.execute({"u0_user_prompt": "input_alpha"})
        r2 = spine.execute({"u0_user_prompt": "input_beta"})
        assert r1["cid"] != r2["cid"]


# ---------------------------------------------------------------------------
# BaseSpineAdapter error paths (G14)
# ---------------------------------------------------------------------------


class TestBaseSpineAdapterErrorPaths:
    def test_invalid_prefix_no_dash_raises(self):
        from agentic_core.interfaces.execution import CIDRegistry
        from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

        class _MinAdapter(BaseSpineAdapter):
            pass

        with pytest.raises(ValueError, match="must end with '-'"):
            _MinAdapter(
                cid_registry=CIDRegistry(),
                orchestrator=object(),
                prefix="nodash",
            )

    def test_invalid_prefix_uppercase_raises(self):
        from agentic_core.interfaces.execution import CIDRegistry
        from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

        class _MinAdapter(BaseSpineAdapter):
            pass

        with pytest.raises(ValueError, match="lowercase"):
            _MinAdapter(
                cid_registry=CIDRegistry(),
                orchestrator=object(),
                prefix="Upper-",
            )

    def test_invalid_prefix_too_short_raises(self):
        from agentic_core.interfaces.execution import CIDRegistry
        from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

        class _MinAdapter(BaseSpineAdapter):
            pass

        with pytest.raises(ValueError, match="too short"):
            _MinAdapter(
                cid_registry=CIDRegistry(),
                orchestrator=object(),
                prefix="-",
            )

    def test_valid_prefix_accepted(self):
        from agentic_core.interfaces.execution import CIDRegistry
        from apps_shared.spine.base_spine_adapter import BaseSpineAdapter

        class _MinAdapter(BaseSpineAdapter):
            pass

        adapter = _MinAdapter(
            cid_registry=CIDRegistry(),
            orchestrator=object(),
            prefix="valid-",
        )
        assert adapter.prefix == "valid-"
