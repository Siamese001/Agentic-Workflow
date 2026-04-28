"""Tier-1 emit-site coverage for OpenTelemetryTracingAdapter.trace_orchestrator.

Plan: closes the historical gap surfaced by `tools/debug/_runtime_adg_coverage_audit.py`
where 3 of 5 Tier-1 categories (`runtime.trace_root`, `L2.step.seal`,
`Exit.disposition`) reported `emit_site_gap` because production code paths
went through the parent adapter, which did not emit them.

These tests verify that EVERY adapter inheriting from
`OpenTelemetryTracingAdapter` now produces:

  1. `runtime.trace_root` at run start (with `trace_id`, `run_id`,
     `input_envelope_hash` attributes).
  2. `Exit.disposition` at run end (with `exit_disposition` attribute set
     to `allow` on success or `deny` on a raised exception).
  3. The adapter installed as the ambient context-var so nested code can
     call `seal_step()` to emit `L2.step.seal` without explicit plumbing.
"""

from __future__ import annotations

import pytest

from apps_shared.utils.open_telemetry_tracing_adapter_util import (
    OpenTelemetryTracingAdapter,
)
from system_learning.runtime_adg.runtime_span_emitter import (
    SPAN_EXIT_DISPOSITION,
    SPAN_STEP_SEAL,
    SPAN_TRACE_ROOT,
    get_current_adapter,
    seal_step,
)


def _spans_by_name(adapter: OpenTelemetryTracingAdapter, name: str) -> list[dict]:
    return [s for s in getattr(adapter, "_completed_spans", []) if s.get("name") == name]


class TestTier1EmitSitesOnSuccess:
    def test_emits_trace_root(self) -> None:
        adapter = OpenTelemetryTracingAdapter(
            service_name="t1-svc", enable_console_export=False, enable_logging=False
        )
        with adapter.trace_orchestrator(mission="m1"):
            pass
        roots = _spans_by_name(adapter, SPAN_TRACE_ROOT)
        assert len(roots) == 1, f"expected exactly one trace_root span, got {len(roots)}"
        attrs = roots[0]["attributes"]
        assert attrs.get("trace_id"), "trace_root must carry trace_id"
        assert attrs.get("run_id"), "trace_root must carry run_id"
        assert "input_envelope_hash" in attrs, "trace_root must carry input_envelope_hash"
        assert attrs.get("mission") == "m1"

    def test_emits_exit_disposition_allow(self) -> None:
        adapter = OpenTelemetryTracingAdapter(
            service_name="t1-svc", enable_console_export=False, enable_logging=False
        )
        with adapter.trace_orchestrator(mission="m2"):
            pass
        exits = _spans_by_name(adapter, SPAN_EXIT_DISPOSITION)
        assert len(exits) == 1
        attrs = exits[0]["attributes"]
        assert attrs.get("exit_disposition") == "allow"

    def test_installs_ambient_adapter(self) -> None:
        adapter = OpenTelemetryTracingAdapter(
            service_name="t1-svc", enable_console_export=False, enable_logging=False
        )
        observed: list[object] = []
        with adapter.trace_orchestrator(mission="m3"):
            observed.append(get_current_adapter())
        assert observed == [adapter], "trace_orchestrator must install adapter as ambient context-var"
        # And restored after exit
        assert get_current_adapter() is None

    def test_seal_step_emits_via_ambient_adapter(self) -> None:
        adapter = OpenTelemetryTracingAdapter(
            service_name="t1-svc", enable_console_export=False, enable_logging=False
        )
        with adapter.trace_orchestrator(mission="m4"):
            ambient = get_current_adapter()
            assert ambient is adapter
            with seal_step(ambient, step_id="s1", trace_id="abc") as bag:
                bag["output"] = {"ok": True}
        seals = _spans_by_name(adapter, SPAN_STEP_SEAL)
        assert len(seals) == 1
        assert seals[0]["attributes"]["step_id"] == "s1"


class TestTier1EmitSitesOnFailure:
    def test_exit_disposition_deny_on_inner_exception(self) -> None:
        adapter = OpenTelemetryTracingAdapter(
            service_name="t1-svc", enable_console_export=False, enable_logging=False
        )
        with pytest.raises(RuntimeError, match="boom"):
            with adapter.trace_orchestrator(mission="m5"):
                raise RuntimeError("boom")
        exits = _spans_by_name(adapter, SPAN_EXIT_DISPOSITION)
        assert len(exits) == 1
        assert exits[0]["attributes"]["exit_disposition"] == "deny"

    def test_trace_root_still_emitted_on_failure(self) -> None:
        adapter = OpenTelemetryTracingAdapter(
            service_name="t1-svc", enable_console_export=False, enable_logging=False
        )
        with pytest.raises(ValueError):
            with adapter.trace_orchestrator(mission="m6"):
                raise ValueError("nope")
        roots = _spans_by_name(adapter, SPAN_TRACE_ROOT)
        assert len(roots) == 1


class TestNoCircularImport:
    def test_module_imports_clean(self) -> None:
        """The lazy import of runtime_span_emitter must not introduce a cycle.

        Re-importing the adapter module after touching the emitter module
        must succeed under any import order.
        """
        import importlib

        import apps_shared.utils.open_telemetry_tracing_adapter_util as m1
        import system_learning.runtime_adg.runtime_span_emitter as m2

        importlib.reload(m2)
        importlib.reload(m1)
        assert hasattr(m1, "OpenTelemetryTracingAdapter")
