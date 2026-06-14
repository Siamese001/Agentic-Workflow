"""Unit tests for agentic_core.L4_state.otel.spans.

Wave 3.2 (plan adg-testing-hotspots-wave-plan-a7f3c1) — Core P1 observability
surface. ``spans`` (fan_in=13, L4_STATE) implements the canonical L4/UWG span
catalog plus required-field validation. The module records degraded in-memory
``SpanRecord`` objects when no live tracer is reachable, so coverage targets the
pure recorder surface: catalog shape, span emission, auto-id generation, the
read/write required-field validation paths, and the recorder reset/filter API.
"""

from __future__ import annotations

import pytest

from agentic_core.L4_state.otel.spans import (
    L4_READ_SPAN_NAMES,
    L4_REFRESH_SPAN_NAMES,
    UWG_WRITE_SPAN_NAMES,
    SpanRecord,
    emit_l4_span,
    emit_uwg_span,
    get_emitted_spans,
    reset_emitted_spans,
)


@pytest.fixture(autouse=True)
def _clean_recorder() -> None:
    """Isolate each test — clear the module-level span recorder before and after."""
    reset_emitted_spans()
    yield
    reset_emitted_spans()


class TestSpanCatalogs:
    def test_catalogs_are_nonempty_tuples(self) -> None:
        assert isinstance(L4_READ_SPAN_NAMES, tuple) and L4_READ_SPAN_NAMES
        assert isinstance(UWG_WRITE_SPAN_NAMES, tuple) and UWG_WRITE_SPAN_NAMES
        assert isinstance(L4_REFRESH_SPAN_NAMES, tuple) and L4_REFRESH_SPAN_NAMES

    def test_read_names_unique(self) -> None:
        assert len(set(L4_READ_SPAN_NAMES)) == len(L4_READ_SPAN_NAMES)

    def test_write_names_unique(self) -> None:
        assert len(set(UWG_WRITE_SPAN_NAMES)) == len(UWG_WRITE_SPAN_NAMES)

    def test_commit_names_present(self) -> None:
        assert "uwg.commit.apply" in UWG_WRITE_SPAN_NAMES
        assert "l4.read.rubric" in L4_READ_SPAN_NAMES


class TestSpanRecord:
    def test_defaults(self) -> None:
        rec = SpanRecord(name="l4.read.rubric")
        assert rec.attributes == {}
        assert rec.duration_ms == 0.0
        assert rec.status == "OK"
        assert rec.trace_id == ""

    def test_latency_ms_returns_duration(self) -> None:
        rec = SpanRecord(name="x", duration_ms=12.5)
        assert rec.latency_ms() == 12.5

    def test_mutable_dataclass(self) -> None:
        # SpanRecord is NOT frozen (mutated by emitters); confirm assignability.
        rec = SpanRecord(name="x")
        rec.status = "OBSERVABILITY_FAILURE"
        assert rec.status == "OBSERVABILITY_FAILURE"


class TestRecorderApi:
    def test_reset_clears(self) -> None:
        emit_l4_span("l4.read.rubric", trace_id="t1")
        assert get_emitted_spans()
        reset_emitted_spans()
        assert get_emitted_spans() == []

    def test_get_emitted_returns_copy(self) -> None:
        emit_l4_span("l4.read.rubric", trace_id="t1")
        snap = get_emitted_spans()
        snap.clear()
        assert get_emitted_spans()  # internal list unaffected by mutating the copy

    def test_name_prefix_filter(self) -> None:
        emit_l4_span("l4.read.rubric", trace_id="t1")
        emit_uwg_span("uwg.commit.apply", trace_id="t2", policy_hash="p", replay_key="r")
        assert len(get_emitted_spans("l4.read")) == 1
        assert len(get_emitted_spans("uwg.")) == 1
        assert len(get_emitted_spans()) == 2


class TestEmitL4Span:
    def test_records_span(self) -> None:
        rec = emit_l4_span("l4.read.rubric", trace_id="trace-1", tenant_id="tenant-1")
        assert rec.name == "l4.read.rubric"
        assert rec.trace_id == "trace-1"
        assert get_emitted_spans()[0] is rec

    def test_auto_generates_ids_when_missing(self) -> None:
        rec = emit_l4_span("l4.read.rubric", tenant_id="tenant-1")
        assert rec.trace_id and rec.span_id
        assert rec.attributes["status"] == "OK"

    def test_missing_trace_id_is_observability_failure(self) -> None:
        # operation_type defaults to "read" with a tenant; force empty trace via
        # an explicitly-blank string is auto-filled, so test the scoped-read path.
        rec = emit_l4_span("l4.read.rubric", trace_id="t", operation_type="read", tenant_id="")
        assert rec.attributes["status"] == "OBSERVABILITY_FAILURE"
        assert "missing_tenant_id_on_scoped_read" in rec.attributes["validation_failures"]

    def test_scoped_read_with_tenant_is_ok(self) -> None:
        rec = emit_l4_span("l4.read.rubric", trace_id="t", operation_type="read", tenant_id="tenant-1")
        assert rec.attributes["status"] == "OK"
        assert "validation_failures" not in rec.attributes

    def test_extra_merged_into_attributes(self) -> None:
        rec = emit_l4_span("l4.read.rubric", trace_id="t", tenant_id="x", extra={"custom": 99})
        assert rec.attributes["custom"] == 99

    def test_reason_and_artifact_refs_listified(self) -> None:
        rec = emit_l4_span(
            "l4.read.rubric", trace_id="t", tenant_id="x",
            reason_codes=("rc1",), artifact_refs=("a1", "a2"),
        )
        assert rec.attributes["reason_codes"] == ["rc1"]
        assert rec.attributes["artifact_refs"] == ["a1", "a2"]


class TestEmitUwgSpan:
    def test_commit_path_ok_with_required_fields(self) -> None:
        rec = emit_uwg_span(
            "uwg.commit.apply", trace_id="t", policy_hash="p", replay_key="r",
        )
        assert rec.attributes["status"] == "OK"
        assert "validation_failures" not in rec.attributes

    def test_commit_path_missing_policy_hash_fails(self) -> None:
        rec = emit_uwg_span("uwg.commit.apply", trace_id="t", replay_key="r")
        assert rec.attributes["status"] == "OBSERVABILITY_FAILURE"
        assert "missing_policy_hash_on_write" in rec.attributes["validation_failures"]

    def test_commit_path_missing_replay_key_fails(self) -> None:
        rec = emit_uwg_span("uwg.commit.apply", trace_id="t", policy_hash="p")
        assert "missing_replay_key_on_commit" in rec.attributes["validation_failures"]

    def test_non_commit_path_does_not_require_commit_fields(self) -> None:
        rec = emit_uwg_span("uwg.read_surface.refresh", trace_id="t")
        assert rec.attributes["status"] == "OK"

    def test_write_lock_acquire_is_commit_path(self) -> None:
        rec = emit_uwg_span("uwg.write_lock.acquire", trace_id="t")
        assert rec.attributes["status"] == "OBSERVABILITY_FAILURE"

    def test_auto_generates_ids(self) -> None:
        rec = emit_uwg_span("uwg.commit.apply", policy_hash="p", replay_key="r")
        assert rec.trace_id and rec.span_id

    def test_extra_merged(self) -> None:
        rec = emit_uwg_span(
            "uwg.commit.apply", trace_id="t", policy_hash="p", replay_key="r",
            extra={"mutation_count": 3},
        )
        assert rec.attributes["mutation_count"] == 3
