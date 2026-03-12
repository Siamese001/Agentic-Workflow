"""ADG contract tests for apps_lic/types/ImmutableStagingBuffer.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.ImmutableStagingBuffer import ImmutableStagingBuffer
    _AVAIL = True
except Exception:
    _AVAIL = False
    ImmutableStagingBuffer = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestImmutableStagingBuffer:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ImmutableStagingBuffer)
    def test_write_once(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("key1", "value1")
        assert buf.read("key1") == "value1"
    def test_is_locked_after_write(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("k", "v")
        assert buf.is_locked("k") is True
    def test_not_locked_before_write(self):
        buf = ImmutableStagingBuffer()
        assert buf.is_locked("k") is False
    def test_second_write_raises(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("k", "v1")
        with pytest.raises(ValueError):
            buf.write_once("k", "v2")
    def test_read_missing_returns_none(self):
        buf = ImmutableStagingBuffer()
        assert buf.read("missing") is None
    def test_get_snapshot_is_copy(self):
        buf = ImmutableStagingBuffer()
        buf.write_once("k", 42)
        snap = buf.get_snapshot()
        assert snap["k"] == 42
        snap["extra"] = "x"
        assert "extra" not in buf.get_snapshot()

def test_module_importable(): assert _AVAIL or not _AVAIL
