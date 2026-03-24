"""Tests for system_learning/runtime_adg/store.py.

Covers:
- InMemoryRuntimeADGStore: persist, get_by_version, list_snapshots, idempotency
- FileBackedRuntimeADGStore: persist, trace index, list, idempotency
- persist returns same version_id for identical snapshots (content-addressed)
- get_version_id_for_trace maps trace_id → version_id
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    attributes_to_json,
    create_runtime_adg_snapshot,
)
from system_learning.runtime_adg.store import (
    FileBackedRuntimeADGStore,
    InMemoryRuntimeADGStore,
)


def _make_snapshot(trace_id: str = "tr-001", mission: str = "test"):
    node = RuntimeADGNode(
        node_id="span-1",
        name="orchestrator.execute",
        kind="orchestrator",
        layer="L3_ORCHESTRATION",
        component="NervousSystem",
        started_at_utc=1000,
        duration_ms=50.0,
        status="ok",
        attributes_json=attributes_to_json({"mission": mission}),
    )
    edge = RuntimeADGEdge(src_id="__root__", dst_id="span-1", relation="parent_child")
    return create_runtime_adg_snapshot(
        trace_id=trace_id,
        mission=mission,
        started_at_utc=1000,
        ended_at_utc=1050,
        nodes=(node,),
        edges=(edge,),
    )


class TestInMemoryRuntimeADGStore:
    def test_persist_returns_version_id(self):
        store = InMemoryRuntimeADGStore()
        snap = _make_snapshot()
        vid = store.persist(snap)
        assert vid.startswith("v_")

    def test_persist_idempotent(self):
        store = InMemoryRuntimeADGStore()
        snap = _make_snapshot()
        vid_a = store.persist(snap)
        vid_b = store.persist(snap)
        assert vid_a == vid_b

    def test_get_by_version_returns_bytes(self):
        store = InMemoryRuntimeADGStore()
        snap = _make_snapshot()
        vid = store.persist(snap)
        payload = store.get_by_version(vid)
        assert payload is not None
        assert len(payload) > 0

    def test_get_by_version_returns_canonical_bytes(self):
        store = InMemoryRuntimeADGStore()
        snap = _make_snapshot()
        vid = store.persist(snap)
        payload = store.get_by_version(vid)
        assert payload == snap.canonical_bytes()

    def test_get_version_id_for_trace(self):
        store = InMemoryRuntimeADGStore()
        snap = _make_snapshot(trace_id="my-trace")
        vid = store.persist(snap)
        assert store.get_version_id_for_trace("my-trace") == vid

    def test_get_version_id_for_unknown_trace_returns_none(self):
        store = InMemoryRuntimeADGStore()
        assert store.get_version_id_for_trace("not-a-trace") is None

    def test_list_snapshots_empty_initially(self):
        store = InMemoryRuntimeADGStore()
        assert store.list_snapshots() == []

    def test_list_snapshots_includes_persisted(self):
        store = InMemoryRuntimeADGStore()
        snap = _make_snapshot()
        vid = store.persist(snap)
        assert vid in store.list_snapshots()

    def test_different_traces_get_different_version_ids(self):
        store = InMemoryRuntimeADGStore()
        snap_a = _make_snapshot(trace_id="trace-A", mission="m-A")
        snap_b = _make_snapshot(trace_id="trace-B", mission="m-B")
        vid_a = store.persist(snap_a)
        vid_b = store.persist(snap_b)
        assert vid_a != vid_b
        assert len(store.list_snapshots()) == 2


class TestFileBackedRuntimeADGStore:
    def test_persist_returns_version_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileBackedRuntimeADGStore(Path(tmp))
            snap = _make_snapshot()
            vid = store.persist(snap)
            assert vid.startswith("v_")

    def test_persist_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileBackedRuntimeADGStore(Path(tmp))
            snap = _make_snapshot()
            vid_a = store.persist(snap)
            vid_b = store.persist(snap)
            assert vid_a == vid_b

    def test_get_by_version_returns_canonical_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileBackedRuntimeADGStore(Path(tmp))
            snap = _make_snapshot()
            vid = store.persist(snap)
            payload = store.get_by_version(vid)
            assert payload == snap.canonical_bytes()

    def test_trace_index_maps_trace_to_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileBackedRuntimeADGStore(Path(tmp))
            snap = _make_snapshot(trace_id="persisted-trace")
            vid = store.persist(snap)
            assert store.get_version_id_for_trace("persisted-trace") == vid

    def test_trace_index_survives_reload(self):
        with tempfile.TemporaryDirectory() as tmp:
            store_a = FileBackedRuntimeADGStore(Path(tmp))
            snap = _make_snapshot(trace_id="reload-trace")
            vid = store_a.persist(snap)
            store_b = FileBackedRuntimeADGStore(Path(tmp))
            assert store_b.get_version_id_for_trace("reload-trace") == vid

    def test_list_snapshots_includes_persisted(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileBackedRuntimeADGStore(Path(tmp))
            snap = _make_snapshot()
            vid = store.persist(snap)
            assert vid in store.list_snapshots()

    def test_get_by_version_unknown_returns_none(self):
        with tempfile.TemporaryDirectory() as tmp:
            store = FileBackedRuntimeADGStore(Path(tmp))
            assert store.get_by_version("v_nonexistent") is None
