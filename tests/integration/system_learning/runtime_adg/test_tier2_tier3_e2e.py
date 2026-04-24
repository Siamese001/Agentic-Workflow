"""End-to-end integration: Tier 2 harden + Tier 3 seal_step adoption.

Exercises the full pipeline:

    AutoPersistenceTracingAdapter.trace_orchestrator()  (Tier 2)
        -> emit_trace_root + emit_exit_disposition auto-fire
        -> trace_id unified with OTel after super() yields
        -> contextvar adapter installed for nested code
    HOPPipelineExecutor._process                        (Tier 3)
        -> seal_step wraps handler dispatch
        -> L2.step.seal appears in _completed_spans
    drain -> materialize -> validate_tier1_corpus_coverage
        -> 3 of 5 Tier 1 categories satisfied from a single run
"""

from __future__ import annotations

from typing import Any

import pytest

from system_learning.runtime_adg.runtime_span_emitter import (
    SPAN_EXIT_DISPOSITION,
    SPAN_STEP_SEAL,
    SPAN_TRACE_ROOT,
    get_current_adapter,
    seal_step,
    set_current_adapter,
)


class _FakeAdapter:
    """Minimal adapter stand-in — only needs the `_completed_spans` seam."""

    def __init__(self) -> None:
        self._completed_spans: list[dict[str, Any]] = []


class TestContextVarAdapter:
    def test_get_returns_none_when_no_adapter_active(self) -> None:
        assert get_current_adapter() is None

    def test_set_then_reset_restores_prior_value(self) -> None:
        a1 = _FakeAdapter()
        a2 = _FakeAdapter()
        t1 = set_current_adapter(a1)
        assert get_current_adapter() is a1
        t2 = set_current_adapter(a2)
        assert get_current_adapter() is a2
        from system_learning.runtime_adg.runtime_span_emitter import reset_current_adapter
        reset_current_adapter(t2)
        assert get_current_adapter() is a1
        reset_current_adapter(t1)
        assert get_current_adapter() is None

    def test_seal_step_uses_current_adapter_via_contextvar(self) -> None:
        """Tier 3 invariant: nested code can seal a step without holding the adapter."""
        adapter = _FakeAdapter()
        token = set_current_adapter(adapter)
        try:
            a = get_current_adapter()
            with seal_step(a, step_id="s1", trace_id="t1") as bag:
                bag["output"] = "work-done"
        finally:
            from system_learning.runtime_adg.runtime_span_emitter import reset_current_adapter
            reset_current_adapter(token)
        assert len(adapter._completed_spans) == 1
        assert adapter._completed_spans[0]["name"] == SPAN_STEP_SEAL
        assert adapter._completed_spans[0]["attributes"]["step_id"] == "s1"


class TestBackPatchTraceId:
    def test_patches_matching_spans_only(self) -> None:
        from system_learning.runtime_adg.runtime_span_emitter import (
            back_patch_trace_id,
            emit_trace_root,
        )

        adapter = _FakeAdapter()
        staging = emit_trace_root(adapter, mission="m", trace_id="staging-abc")
        # Also add an unrelated span with a different trace_id.
        adapter._completed_spans.append(
            {"trace_id": "other", "attributes": {"trace_id": "other"}, "name": "x"}
        )
        patched = back_patch_trace_id(adapter, staging, "real-otel-xyz")
        assert patched == 1
        assert adapter._completed_spans[0]["trace_id"] == "real-otel-xyz"
        assert adapter._completed_spans[0]["attributes"]["trace_id"] == "real-otel-xyz"
        # Unrelated span untouched.
        assert adapter._completed_spans[1]["trace_id"] == "other"

    def test_fail_open_on_bad_adapter(self) -> None:
        from system_learning.runtime_adg.runtime_span_emitter import back_patch_trace_id
        assert back_patch_trace_id(None, "a", "b") == 0

        class Bad:
            pass

        assert back_patch_trace_id(Bad(), "a", "b") == 0

    def test_fail_open_on_empty_old_id(self) -> None:
        from system_learning.runtime_adg.runtime_span_emitter import back_patch_trace_id
        adapter = _FakeAdapter()
        adapter._completed_spans.append({"trace_id": "", "name": "x"})
        assert back_patch_trace_id(adapter, "", "real") == 0


class TestTraceOrchestratorTier2PlusTier3:
    """Full adapter wiring: trace_root + exit + seal all appear + trace_ids unified."""

    @pytest.fixture
    def adapter(self, monkeypatch, tmp_path):
        from system_learning.stores import version_store as vs_mod

        class _NullBridge:
            def persist_active_version(self, *_a, **_k) -> None:
                return None

        monkeypatch.setattr(vs_mod, "get_sl_memory_bridge", lambda: _NullBridge())

        from system_learning.runtime_adg.auto_persistence import (
            AutoPersistenceTracingAdapter,
        )
        from system_learning.runtime_adg.store import FileBackedRuntimeADGStore

        monkeypatch.setattr(
            FileBackedRuntimeADGStore,
            "_validate_l4_compliance",
            lambda self: None,
        )

        adapter = AutoPersistenceTracingAdapter(
            service_name="test-tier2-tier3",
            enable_auto_persistence=False,
            l4_store_path=str(tmp_path / "runtime_adg"),
            l6_base_dir=str(tmp_path / "l6"),
        )
        return adapter

    def test_trace_root_and_exit_emitted_per_run(self, adapter) -> None:
        with adapter.trace_orchestrator(mission="harden-test"):
            pass
        names = [s["name"] for s in adapter._completed_spans]
        assert SPAN_TRACE_ROOT in names
        assert SPAN_EXIT_DISPOSITION in names

    def test_trace_id_unified_across_root_exit_and_children(self, adapter) -> None:
        """Tier 2 harden: trace_root / orchestrator.execute / exit.disposition MUST share trace_id."""
        with adapter.trace_orchestrator(mission="unify-test"):
            pass
        spans = adapter._completed_spans
        by_name = {s["name"]: s for s in spans}
        root_tid = by_name[SPAN_TRACE_ROOT]["trace_id"]
        exec_tid = by_name["orchestrator.execute"]["trace_id"]
        exit_tid = by_name[SPAN_EXIT_DISPOSITION]["trace_id"]
        assert root_tid == exec_tid == exit_tid
        assert root_tid  # non-empty

    def test_contextvar_adapter_resolves_inside_orchestrator(self, adapter) -> None:
        resolved = []
        with adapter.trace_orchestrator(mission="ctxvar-test"):
            resolved.append(get_current_adapter())
        # Adapter visible inside; None after finally.
        assert resolved == [adapter]
        assert get_current_adapter() is None

    def test_contextvar_reset_after_exception(self, adapter) -> None:
        with pytest.raises(ValueError, match="boom"):
            with adapter.trace_orchestrator(mission="exc-test"):
                raise ValueError("boom")
        assert get_current_adapter() is None
        # Exception path MUST flip disposition to 'deny'.
        exit_span = [s for s in adapter._completed_spans if s["name"] == SPAN_EXIT_DISPOSITION][-1]
        assert exit_span["attributes"]["exit_disposition"] == "deny"

    def test_sequential_orchestrators_do_not_leak_adapter(self, adapter) -> None:
        """Concurrency guard: two sequential orchestrator blocks each install/reset cleanly."""
        with adapter.trace_orchestrator(mission="run-1"):
            assert get_current_adapter() is adapter
        assert get_current_adapter() is None
        with adapter.trace_orchestrator(mission="run-2"):
            assert get_current_adapter() is adapter
        assert get_current_adapter() is None


class TestTier3SealStepFromNestedAgent:
    """Tier 3 payoff: a nested helper can seal a step purely via the contextvar."""

    @pytest.fixture
    def adapter(self, monkeypatch, tmp_path):
        from system_learning.stores import version_store as vs_mod

        class _NullBridge:
            def persist_active_version(self, *_a, **_k) -> None:
                return None

        monkeypatch.setattr(vs_mod, "get_sl_memory_bridge", lambda: _NullBridge())

        from system_learning.runtime_adg.auto_persistence import (
            AutoPersistenceTracingAdapter,
        )
        from system_learning.runtime_adg.store import FileBackedRuntimeADGStore

        monkeypatch.setattr(
            FileBackedRuntimeADGStore,
            "_validate_l4_compliance",
            lambda self: None,
        )

        return AutoPersistenceTracingAdapter(
            service_name="test-tier3",
            enable_auto_persistence=False,
            l4_store_path=str(tmp_path / "runtime_adg"),
            l6_base_dir=str(tmp_path / "l6"),
        )

    def test_nested_seal_without_adapter_plumbing(self, adapter) -> None:
        def leaf_agent(step_id: str, payload: str) -> str:
            """Represents any nested worker — knows NOTHING about the adapter."""
            a = get_current_adapter()
            with seal_step(a, step_id=step_id, trace_id="") as bag:
                bag["output"] = f"processed:{payload}"
                return bag["output"]

        with adapter.trace_orchestrator(mission="nested-test"):
            out_a = leaf_agent("step-a", "alpha")
            out_b = leaf_agent("step-b", "beta")

        assert out_a == "processed:alpha"
        assert out_b == "processed:beta"

        seal_spans = [s for s in adapter._completed_spans if s["name"] == SPAN_STEP_SEAL]
        assert len(seal_spans) == 2
        assert {s["attributes"]["step_id"] for s in seal_spans} == {"step-a", "step-b"}
        # Every seal has a non-empty output_hash.
        for s in seal_spans:
            assert s["attributes"]["output_hash"]

    def test_full_tier1_coverage_from_single_run(self, adapter) -> None:
        """With trace_root + exit (auto) + seal_step (nested), 3/5 categories satisfy."""
        from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
        from system_learning.runtime_adg.span_contracts import (
            validate_tier1_corpus_coverage,
        )

        def leaf_step(step_id: str) -> None:
            a = get_current_adapter()
            with seal_step(a, step_id=step_id, trace_id="") as bag:
                bag["output"] = step_id

        with adapter.trace_orchestrator(mission="coverage-test"):
            leaf_step("step-1")

        spans = adapter.drain_completed_spans()
        snap = RuntimeADGMaterializer().materialize(spans, mission="coverage-test")
        report = validate_tier1_corpus_coverage([snap])

        assert report.category_status["runtime.trace_root"] == "satisfied"
        assert report.category_status["L2.step.seal"] == "satisfied"
        assert report.category_status["Exit.disposition"] == "satisfied"
        # route + invoke not exercised in this synthetic run.
        assert report.satisfied_count() == 3
