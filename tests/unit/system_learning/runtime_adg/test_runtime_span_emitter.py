"""Unit tests for Tier 2 runtime span emitters."""

from __future__ import annotations

import pytest

from system_learning.runtime_adg.runtime_span_emitter import (
    SPAN_EXIT_DISPOSITION,
    SPAN_STEP_SEAL,
    SPAN_TRACE_ROOT,
    emit_exit_disposition,
    emit_trace_root,
    seal_step,
)


class _FakeAdapter:
    """Minimal stand-in for OpenTelemetryTracingAdapter."""

    def __init__(self) -> None:
        self._completed_spans: list[dict] = []


@pytest.fixture
def adapter() -> _FakeAdapter:
    return _FakeAdapter()


class TestEmitTraceRoot:
    def test_appends_span(self, adapter: _FakeAdapter) -> None:
        trace_id = emit_trace_root(adapter, mission="test")
        assert len(adapter._completed_spans) == 1
        s = adapter._completed_spans[0]
        assert s["name"] == SPAN_TRACE_ROOT
        assert s["trace_id"] == trace_id
        assert s["parent_span_id"] == ""
        assert s["attributes"]["run_id"].startswith("run-")
        assert s["attributes"]["trace_id"] == trace_id

    def test_returns_stable_trace_id_when_provided(self, adapter: _FakeAdapter) -> None:
        tid = emit_trace_root(adapter, mission="m", trace_id="fixed-tid")
        assert tid == "fixed-tid"
        assert adapter._completed_spans[0]["trace_id"] == "fixed-tid"

    def test_envelope_hash_stable_for_same_input(self, adapter: _FakeAdapter) -> None:
        emit_trace_root(adapter, mission="m", input_envelope={"k": "v"})
        emit_trace_root(adapter, mission="m", input_envelope={"k": "v"})
        h1 = adapter._completed_spans[0]["attributes"]["input_envelope_hash"]
        h2 = adapter._completed_spans[1]["attributes"]["input_envelope_hash"]
        assert h1 == h2
        assert h1  # non-empty

    def test_fail_open_on_bad_adapter(self) -> None:
        """Adapter without `_completed_spans` must not raise."""

        class Bad:
            pass

        tid = emit_trace_root(Bad(), mission="m")
        assert tid  # still returns a trace_id

    def test_none_adapter_does_not_crash(self) -> None:
        tid = emit_trace_root(None, mission="m")
        assert tid


class TestEmitExitDisposition:
    def test_appends_exit_span(self, adapter: _FakeAdapter) -> None:
        emit_exit_disposition(
            adapter,
            trace_id="t1",
            disposition="allow",
            policy_hash="ph",
            reason_codes=("r1", "r2"),
        )
        assert len(adapter._completed_spans) == 1
        s = adapter._completed_spans[0]
        assert s["name"] == SPAN_EXIT_DISPOSITION
        assert s["attributes"]["exit_disposition"] == "allow"
        assert s["attributes"]["policy_hash"] == "ph"
        assert s["attributes"]["reason_codes"] == ["r1", "r2"]

    def test_rejects_invalid_disposition(self, adapter: _FakeAdapter) -> None:
        with pytest.raises(ValueError, match="invalid exit_disposition"):
            emit_exit_disposition(adapter, trace_id="t", disposition="maybe")

    def test_all_valid_dispositions_accepted(self, adapter: _FakeAdapter) -> None:
        for d in ("allow", "deny", "reroute", "escalate", "commit_request"):
            emit_exit_disposition(adapter, trace_id="t", disposition=d)
        assert len(adapter._completed_spans) == 5


class TestSealStep:
    def test_seals_step_with_output(self, adapter: _FakeAdapter) -> None:
        with seal_step(adapter, step_id="s1", trace_id="t1") as bag:
            bag["output"] = {"result": 42}
            bag["evidence_ids"] = ("ev-1", "ev-2")
        assert len(adapter._completed_spans) == 1
        s = adapter._completed_spans[0]
        assert s["name"] == SPAN_STEP_SEAL
        assert s["attributes"]["step_id"] == "s1"
        assert s["attributes"]["output_hash"]  # non-empty hash
        assert s["attributes"]["evidence_ids"] == ["ev-1", "ev-2"]
        assert s["attributes"]["replay_key"]
        assert s["attributes"]["lineage_hash"]

    def test_seal_survives_exception_and_re_raises(self, adapter: _FakeAdapter) -> None:
        with pytest.raises(ValueError, match="boom"):
            with seal_step(adapter, step_id="s-err", trace_id="t") as bag:
                bag["output"] = "partial"
                raise ValueError("boom")
        # Span MUST still be appended with status=error.
        assert len(adapter._completed_spans) == 1
        assert adapter._completed_spans[0]["status"] == "error"
        assert adapter._completed_spans[0]["name"] == SPAN_STEP_SEAL

    def test_output_hash_changes_when_output_changes(self, adapter: _FakeAdapter) -> None:
        with seal_step(adapter, step_id="a", trace_id="t") as bag:
            bag["output"] = "one"
        with seal_step(adapter, step_id="b", trace_id="t") as bag:
            bag["output"] = "two"
        h1 = adapter._completed_spans[0]["attributes"]["output_hash"]
        h2 = adapter._completed_spans[1]["attributes"]["output_hash"]
        assert h1 != h2


class TestTier1ContractsInteraction:
    """End-to-end: emitted spans must register as Tier 1 satisfied."""

    def test_emitted_spans_satisfy_tier1_contracts(self, adapter: _FakeAdapter) -> None:
        from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
        from system_learning.runtime_adg.span_contracts import (
            validate_tier1_corpus_coverage,
        )

        trace_id = emit_trace_root(adapter, mission="e2e", input_envelope={"x": 1})
        with seal_step(adapter, step_id="step-1", trace_id=trace_id) as bag:
            bag["output"] = "done"
        emit_exit_disposition(
            adapter,
            trace_id=trace_id,
            disposition="allow",
            policy_hash="p",
            reason_codes=("ok",),
        )

        # Materialize spans -> snapshot -> run corpus coverage.
        m = RuntimeADGMaterializer()
        snapshot = m.materialize(adapter._completed_spans, mission="e2e")
        report = validate_tier1_corpus_coverage([snapshot])

        assert report.category_status["runtime.trace_root"] == "satisfied"
        assert report.category_status["L2.step.seal"] == "satisfied"
        assert report.category_status["Exit.disposition"] == "satisfied"
        # We emitted 3 of 5 categories; L0.route.select and L2.invoke remain
        # as emit_site_gap for this synthetic run (not in Tier 2 scope).
        assert report.satisfied_count() == 3
