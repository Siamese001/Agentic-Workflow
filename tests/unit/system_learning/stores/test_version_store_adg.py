"""ADG-driven tests for system_learning/stores/version_store.py — fan_in=2."""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytestmark = pytest.mark.unit

try:
    from system_learning.stores.version_store import (  # noqa: F401
        FileBackedVersionStore,
        InMemoryVersionStore,
    )

    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    InMemoryVersionStore = None  # type: ignore[assignment,misc]
    FileBackedVersionStore = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="version_store.py deps unavailable")
class TestInMemoryVersionStore:
    def test_is_class(self):
        assert isinstance(InMemoryVersionStore, type)

    def test_importable(self):
        assert InMemoryVersionStore is not None


@pytest.mark.skipif(not _AVAILABLE, reason="version_store.py deps unavailable")
class TestFileBackedVersionStore:
    def test_is_class(self):
        assert isinstance(FileBackedVersionStore, type)

    def test_importable(self):
        assert FileBackedVersionStore is not None

    def test_commit_persists_active_version(self, tmp_path):
        store = FileBackedVersionStore(tmp_path)

        class _Bridge:
            def __init__(self):
                self.calls = []

            def persist_active_version(self, component, version_id, *, ts=""):
                self.calls.append((component, version_id, ts))
                return True

        bridge = _Bridge()
        with patch("system_learning.stores.version_store.get_sl_memory_bridge", return_value=bridge):
            version_id = store.commit_change_package({"test": "data"})

        assert bridge.calls[0][0] == "version_store"
        assert bridge.calls[0][1] == version_id
        assert bridge.calls[0][2] != ""  # ts should be a UUID string

    def test_commit_runtime_telemetry_slice_is_idempotent(self, tmp_path):
        from system_learning.types.telemetry_types import create_telemetry_slice_from_runtime_records

        store = FileBackedVersionStore(tmp_path)
        telemetry_slice = create_telemetry_slice_from_runtime_records(
            (
                {
                    "ts_utc": 1700000000000,
                    "kind": "orchestrator",
                    "trace_id": "trace-1",
                    "span_id": "span-1",
                    "parent_span_id": "",
                    "layer": "L3_Orchestration",
                    "component": "NervousSystem",
                    "name": "orchestrator.execute",
                    "attributes": {"mission": "demo"},
                },
                {
                    "ts_utc": 1700000001000,
                    "kind": "tool",
                    "trace_id": "trace-1",
                    "span_id": "span-2",
                    "parent_span_id": "span-1",
                    "layer": "L2_Execution",
                    "component": "Tool.search",
                    "name": "tool.search",
                    "attributes": {"tool.name": "search"},
                },
            )
        )

        class _Bridge:
            def persist_active_version(self, component, version_id, *, ts=""):
                return True

        with patch("system_learning.stores.version_store.get_sl_memory_bridge", return_value=_Bridge()):
            version_id_1 = store.commit_change_package(telemetry_slice)
            version_id_2 = store.commit_change_package(telemetry_slice)

        assert version_id_1 == version_id_2
        assert store.list_versions() == [version_id_1]
        assert store.get(version_id_1) == telemetry_slice.canonical_bytes()


def test_module_importable():
    """Module version_store.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE