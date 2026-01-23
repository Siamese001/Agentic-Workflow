"""
Unit tests for V2 Architecture Patterns.
Verifies immutability, tracing, and persistence logic.
"""

import pytest

from apps_lic.shared.v2_patterns.immutable_buffer import ImmutableStagingBuffer
from apps_lic.shared.v2_patterns.manifest_manager import ManifestManager
from apps_lic.shared.v2_patterns.trace_registry import TraceRegistry

# Mocking Mixins if not available in test env,
# but assuming they import correctly based on previous phases.


class TestImmutableStagingBuffer:
    def test_write_once_enforcement(self):
        """Verify that writing to the same key twice raises ValueError."""
        buf = ImmutableStagingBuffer()
        buf.write_once("key1", "value1")

        assert buf.read("key1") == "value1"
        assert buf.is_locked("key1") is True

        with pytest.raises(ValueError) as exc:
            buf.write_once("key1", "value2")
        assert "immutable" in str(exc.value)

    def test_independent_keys(self):
        """Verify multiple keys function independently."""
        buf = ImmutableStagingBuffer()
        buf.write_once("a", 1)
        buf.write_once("b", 2)

        assert buf.read("a") == 1
        assert buf.read("b") == 2

    def test_snapshot_is_copy(self):
        """Verify get_snapshot returns a copy, not reference."""
        buf = ImmutableStagingBuffer()
        buf.write_once("x", 100)
        snap = buf.get_snapshot()
        snap["x"] = 200  # Mutate copy

        assert buf.read("x") == 100  # Original should be unchanged


class TestTraceRegistry:
    def test_add_and_retrieve_traces(self):
        """Verify traces are added in order with timestamps."""
        registry = TraceRegistry()
        registry.add_trace("START", {"user": "test"})
        registry.add_trace("END", {"status": "ok"})

        traces = registry.get_traces()
        assert len(traces) == 2
        assert traces[0]["type"] == "START"
        assert "timestamp" in traces[0]
        assert traces[1]["type"] == "END"

    def test_clear(self):
        """Verify clearing the registry."""
        registry = TraceRegistry()
        registry.add_trace("A", {})
        registry.clear()
        assert len(registry.get_traces()) == 0


class TestManifestManager:
    def test_save_and_load(self, tmp_path):
        """Verify filesystem persistence."""
        manager = ManifestManager(base_path=tmp_path)
        data = {"workflow_id": "123", "status": "active"}

        # Save
        path = manager.save_manifest("run_1", data)
        assert path.exists()

        # Load
        loaded = manager.load_manifest("run_1")
        assert loaded == data

    def test_load_nonexistent(self, tmp_path):
        """Verify error handling for missing files."""
        manager = ManifestManager(base_path=tmp_path)
        with pytest.raises(FileNotFoundError):
            manager.load_manifest("ghost_file")
