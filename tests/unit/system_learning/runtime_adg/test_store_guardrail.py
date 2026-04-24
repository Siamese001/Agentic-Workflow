"""Tests for Tier 1 persist() guardrail in FileBackedRuntimeADGStore.

Plan: `.windsurf/plans/runtime-adg-tier1-trace-binding-c9b84d.md` (W1.P1)
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from system_learning.runtime_adg.snapshot import (
    RuntimeADGEdge,
    RuntimeADGNode,
    create_runtime_adg_snapshot,
)
from system_learning.runtime_adg.store import FileBackedRuntimeADGStore


def _make_node(node_id: str = "n1", name: str = "test.span") -> RuntimeADGNode:
    return RuntimeADGNode(
        node_id=node_id,
        name=name,
        kind="tool",
        layer="L2",
        component="TestComponent",
        started_at_utc=1000,
        duration_ms=5.0,
        status="ok",
        attributes_json='{"k":"v"}',
    )


def _make_snapshot(trace_id: str = "trace-abc", with_payload: bool = True):
    nodes = (_make_node(),) if with_payload else ()
    edges = (RuntimeADGEdge(src_id="__root__", dst_id="n1", relation="parent_child"),) if with_payload else ()
    return create_runtime_adg_snapshot(
        trace_id=trace_id,
        mission="test-mission",
        started_at_utc=1000,
        ended_at_utc=1005,
        nodes=nodes,
        edges=edges,
    )


def _stub_bridge(monkeypatch: pytest.MonkeyPatch) -> None:
    """Stub the system-learning memory bridge side effect in version_store.

    `commit_change_package()` calls `get_sl_memory_bridge().persist_active_version(...)`
    which tries to import a missing `tools.implement_unified_memory` module.
    That path is unrelated to runtime ADG correctness; short-circuit it.
    """
    from system_learning.stores import version_store as vs_mod

    class _NullBridge:
        def persist_active_version(self, *_args, **_kwargs) -> None:
            return None

    monkeypatch.setattr(vs_mod, "get_sl_memory_bridge", lambda: _NullBridge())


@pytest.fixture
def store(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> FileBackedRuntimeADGStore:
    # Bypass L4-sovereignty validation for tests by pointing at a path
    # under L4_approved territory. Easiest: stub the validator.
    monkeypatch.setattr(
        FileBackedRuntimeADGStore,
        "_validate_l4_compliance",
        lambda self: None,
    )
    _stub_bridge(monkeypatch)
    return FileBackedRuntimeADGStore(base_dir=tmp_path / "runtime_adg")


class TestGuardrailEmptyTrace:
    def test_empty_trace_id_rejected_by_default(self, store: FileBackedRuntimeADGStore) -> None:
        snap = _make_snapshot(trace_id="")
        with pytest.raises(ValueError, match="empty trace_id"):
            store.persist(snap)

    def test_allow_unbound_escape_hatch(self, store: FileBackedRuntimeADGStore) -> None:
        snap = _make_snapshot(trace_id="")
        # Must not raise.
        vid = store.persist(snap, allow_unbound=True)
        assert vid  # non-empty
        # Nothing should have been written to trace_index for empty trace_id.
        assert "" not in store._trace_index

    def test_valid_trace_id_accepted(self, store: FileBackedRuntimeADGStore) -> None:
        snap = _make_snapshot(trace_id="trace-xyz")
        vid = store.persist(snap)
        assert store._trace_index["trace-xyz"] == vid


class TestGuardrailEmptyPayload:
    def test_empty_payload_rejected(self, store: FileBackedRuntimeADGStore) -> None:
        snap = _make_snapshot(trace_id="t1", with_payload=False)
        with pytest.raises(ValueError, match="empty payload"):
            store.persist(snap)

    def test_allow_empty_payload_escape_hatch(self, store: FileBackedRuntimeADGStore) -> None:
        snap = _make_snapshot(trace_id="t1", with_payload=False)
        vid = store.persist(snap, allow_empty_payload=True)
        assert vid

    def test_only_nodes_is_non_empty(self, store: FileBackedRuntimeADGStore) -> None:
        """A snapshot with only nodes and no edges should still count as non-empty."""
        snap = create_runtime_adg_snapshot(
            trace_id="t1",
            mission="m",
            started_at_utc=1,
            ended_at_utc=2,
            nodes=(_make_node(),),
            edges=(),
        )
        assert store.persist(snap)  # must not raise


class TestFirstWriteWinsBugFix:
    def test_second_write_updates_trace_index(self, store: FileBackedRuntimeADGStore) -> None:
        """The pre-Tier-1 bug was 'if trace_id not in index: write' — meaning
        a second persist with the same trace_id would silently skip the index
        update if content differed. Now updates unconditionally (idempotently
        per content hash)."""
        snap1 = _make_snapshot(trace_id="t-same")
        vid1 = store.persist(snap1)

        # New snapshot with SAME trace_id but different content -> different vid.
        snap2 = create_runtime_adg_snapshot(
            trace_id="t-same",
            mission="different-mission",
            started_at_utc=2000,
            ended_at_utc=2005,
            nodes=(_make_node(node_id="different"),),
            edges=(),
        )
        vid2 = store.persist(snap2)
        assert vid1 != vid2
        # Trace index should now point to the most recent version.
        assert store._trace_index["t-same"] == vid2

    def test_idempotent_same_content(self, store: FileBackedRuntimeADGStore) -> None:
        """Persisting the same snapshot twice must not double-write the index."""
        snap = _make_snapshot(trace_id="t1")
        vid1 = store.persist(snap)
        vid2 = store.persist(snap)
        assert vid1 == vid2
        assert store._trace_index["t1"] == vid1


class TestStaleEmptyKeyCleanup:
    def test_load_strips_empty_string_keys(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Simulates the existing production state: _trace_index.json with
        empty-string key. Loading should silently strip it."""
        monkeypatch.setattr(
            FileBackedRuntimeADGStore,
            "_validate_l4_compliance",
            lambda self: None,
        )
        base = tmp_path / "runtime_adg"
        base.mkdir()
        # Write a polluted index directly.
        (base / "_trace_index.json").write_text(
            json.dumps({"": "v_bogus", "real-trace": "v_real"}),
            encoding="utf-8",
        )
        store = FileBackedRuntimeADGStore(base_dir=base)
        # Empty key must be gone; real key preserved.
        assert "" not in store._trace_index
        assert store._trace_index.get("real-trace") == "v_real"

    def test_load_strips_empty_values(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            FileBackedRuntimeADGStore,
            "_validate_l4_compliance",
            lambda self: None,
        )
        base = tmp_path / "runtime_adg"
        base.mkdir()
        (base / "_trace_index.json").write_text(
            json.dumps({"trace-a": "", "trace-b": "v_ok"}),
            encoding="utf-8",
        )
        store = FileBackedRuntimeADGStore(base_dir=base)
        assert "trace-a" not in store._trace_index
        assert store._trace_index["trace-b"] == "v_ok"
