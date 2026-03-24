"""End-to-end pipeline tests: tracer → drain → materialize → persist.

Validates the complete runtime ADG pipeline:
1. OpenTelemetryTracingAdapter buffers spans during execution
2. drain_completed_spans() returns deterministic ordered records
3. RuntimeADGMaterializer converts records → RuntimeADGSnapshot
4. InMemoryRuntimeADGStore persists snapshot idempotently
5. Snapshot is content-addressed and retrievable by trace_id
"""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


try:
    from apps_shared.utils.open_telemetry_tracing_adapter_util import (
        OpenTelemetryTracingAdapter,
    )

    _TRACER_AVAILABLE = True
except ImportError:
    _TRACER_AVAILABLE = False

from system_learning.runtime_adg.materializer import RuntimeADGMaterializer
from system_learning.runtime_adg.snapshot import RuntimeADGSnapshot
from system_learning.runtime_adg.store import InMemoryRuntimeADGStore


class _FakeSpanContext:
    def __init__(self, trace_id: int, span_id: int):
        self.trace_id = trace_id
        self.span_id = span_id


class _FakeSpan:
    def __init__(self, trace_id: int, span_id: int):
        self._context = _FakeSpanContext(trace_id, span_id)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def get_span_context(self):
        return self._context

    def set_attribute(self, key, value):
        return None

    def add_event(self, name, attributes=None):
        return None

    def set_status(self, status):
        return None

    def record_exception(self, exc):
        return None


class _SequentialFakeTracer:
    def __init__(self, spans: list[tuple[int, int]]) -> None:
        self._spans = list(spans)
        self._idx = 0

    def start_as_current_span(self, name: str):
        if self._idx < len(self._spans):
            t_id, s_id = self._spans[self._idx]
            self._idx += 1
        else:
            t_id, s_id = 0xABCDEF, self._idx
        return _FakeSpan(t_id, s_id)


def _build_adapter_with_spans(span_ids: list[tuple[int, int]]) -> OpenTelemetryTracingAdapter:
    import apps_shared.utils.open_telemetry_tracing_adapter_util as m

    class _StatusCode:
        OK = "OK"
        ERROR = "ERROR"

    class _Status:
        def __init__(self, code, description=None):
            pass

    m.Status = _Status
    m.StatusCode = _StatusCode

    adapter = OpenTelemetryTracingAdapter(enable_logging=False)
    adapter._enabled = True
    adapter.tracer = _SequentialFakeTracer(span_ids)
    return adapter


@pytest.mark.skipif(not _TRACER_AVAILABLE, reason="OTel tracer deps unavailable")
class TestEndToEndPipeline:
    def test_full_pipeline_produces_valid_snapshot(self):
        adapter = _build_adapter_with_spans([(0xABCD, 0x1), (0xABCD, 0x2)])
        with adapter.trace_orchestrator("pipeline-test", metadata={"path": "A"}):
            with adapter.trace_tool("search", parameters={"query": "runtime-adg"}):
                pass

        spans = adapter.drain_completed_spans()
        assert len(spans) == 2

        snap = RuntimeADGMaterializer().materialize(spans, mission="pipeline-test")
        assert isinstance(snap, RuntimeADGSnapshot)
        assert snap.node_count() == 2
        assert len(snap.snapshot_id) == 64

    def test_pipeline_spans_cleared_after_drain(self):
        adapter = _build_adapter_with_spans([(0xABCD, 0x1)])
        with adapter.trace_orchestrator("test"):
            pass
        adapter.drain_completed_spans()
        assert adapter.drain_completed_spans() == []

    def test_snapshot_persists_and_retrieves_by_trace(self):
        adapter = _build_adapter_with_spans([(0xABCD, 0x1), (0xABCD, 0x2)])
        with adapter.trace_orchestrator("persist-test"):
            with adapter.trace_cognitive("plan-step"):
                pass

        spans = adapter.drain_completed_spans()
        snap = RuntimeADGMaterializer().materialize(spans, mission="persist-test")

        store = InMemoryRuntimeADGStore()
        vid = store.persist(snap)

        assert vid == store.get_version_id_for_trace(snap.trace_id)
        payload = store.get_by_version(vid)
        assert payload == snap.canonical_bytes()

    def test_snapshot_idempotent_across_two_persists(self):
        adapter = _build_adapter_with_spans([(0xABCD, 0x1)])
        with adapter.trace_orchestrator("idempotent-test"):
            pass
        spans = adapter.drain_completed_spans()
        snap = RuntimeADGMaterializer().materialize(spans, mission="m", trace_id="trace-idem")

        store = InMemoryRuntimeADGStore()
        vid_a = store.persist(snap)
        vid_b = store.persist(snap)
        assert vid_a == vid_b

    def test_snapshot_nodes_match_span_hierarchy(self):
        adapter = _build_adapter_with_spans([(0xABCD, 0x10), (0xABCD, 0x20)])
        with adapter.trace_orchestrator("hierarchy-test", metadata={"path": "B"}):
            with adapter.trace_tool("lookup", parameters={"key": "x"}):
                pass

        spans = adapter.drain_completed_spans()
        snap = RuntimeADGMaterializer().materialize(spans)
        node_names = {n.name for n in snap.nodes}
        assert "orchestrator.execute" in node_names
        assert "tool.lookup" in node_names

    def test_snapshot_edges_include_parent_child(self):
        adapter = _build_adapter_with_spans([(0xABCD, 0x1), (0xABCD, 0x2)])
        with adapter.trace_orchestrator("edge-test"):
            with adapter.trace_tool("tool", parameters={}):
                pass

        spans = adapter.drain_completed_spans()
        snap = RuntimeADGMaterializer().materialize(spans)
        pc_edges = [e for e in snap.edges if e.relation == "parent_child"]
        assert len(pc_edges) >= 2

    def test_snapshot_canonical_bytes_stable(self):
        adapter = _build_adapter_with_spans([(0xABCD, 0x1)])
        with adapter.trace_orchestrator("stable-test"):
            pass

        spans = adapter.drain_completed_spans()
        snap = RuntimeADGMaterializer().materialize(spans, mission="stable", trace_id="stable-trace")
        assert snap.canonical_bytes() == snap.canonical_bytes()
        import hashlib

        h = hashlib.sha256(snap.canonical_bytes()).hexdigest()
        assert h == snap.snapshot_hash


class TestRuntimeADGModulePublicSurface:
    def test_all_public_symbols_importable(self):
        from system_learning.runtime_adg import (  # noqa: F401
            FileBackedRuntimeADGStore,
            InMemoryRuntimeADGStore,
            RuntimeADGEdge,
            RuntimeADGMaterializer,
            RuntimeADGNode,
            RuntimeADGSnapshot,
            attributes_to_json,
            create_runtime_adg_snapshot,
        )

    def test_materializer_is_class(self):
        from system_learning.runtime_adg import RuntimeADGMaterializer

        assert callable(RuntimeADGMaterializer)
        assert hasattr(RuntimeADGMaterializer, "materialize")

    def test_in_memory_store_has_expected_api(self):
        from system_learning.runtime_adg import InMemoryRuntimeADGStore

        store = InMemoryRuntimeADGStore()
        assert callable(store.persist)
        assert callable(store.get_by_version)
        assert callable(store.get_version_id_for_trace)
        assert callable(store.list_snapshots)

    def test_file_backed_store_has_expected_api(self):
        from system_learning.runtime_adg import FileBackedRuntimeADGStore

        assert hasattr(FileBackedRuntimeADGStore, "persist")
        assert hasattr(FileBackedRuntimeADGStore, "get_by_version")
        assert hasattr(FileBackedRuntimeADGStore, "get_version_id_for_trace")
        assert hasattr(FileBackedRuntimeADGStore, "list_snapshots")
        assert hasattr(FileBackedRuntimeADGStore, "load_snapshot")
