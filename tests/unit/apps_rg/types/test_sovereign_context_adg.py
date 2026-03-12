"""ADG-driven tests for apps_rg/types/SovereignContext.py — fan_in=3.

Contract tests: SovereignContext airlock, commit, rollback, get.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_rg.types.SovereignContext import SimpleBuffer, SimpleTrace, SovereignContext


class TestSovereignContextImport:
    def test_class_importable(self):
        assert callable(SovereignContext)

    def test_simple_buffer_importable(self):
        assert callable(SimpleBuffer)

    def test_simple_trace_importable(self):
        assert callable(SimpleTrace)


class TestSovereignContextAirlock:
    def test_write_to_airlock(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("key", "value")
        # Not visible until committed
        assert ctx.get("key") is None

    def test_commit_airlock_requires_signature(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("k", "v")
        with pytest.raises(ValueError, match="signature"):
            ctx.commit_airlock("")

    def test_commit_airlock_makes_visible(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("x", 42)
        ctx.commit_airlock("valid_sig_abc123")
        assert ctx.get("x") == 42

    def test_commit_clears_airlock(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("y", "data")
        ctx.commit_airlock("sig")
        # Writing again to same key in airlock should work (airlock is cleared)
        ctx.write_to_airlock("y", "new_data")
        assert ctx.get("y") == "data"  # committed state still old

    def test_rollback_discards_airlock(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("z", "staged")
        ctx.rollback_airlock()
        # After rollback, commit has nothing to promote
        ctx.commit_airlock("sig")
        assert ctx.get("z") is None


class TestSovereignContextGet:
    def test_get_default_none(self):
        ctx = SovereignContext()
        assert ctx.get("missing") is None

    def test_get_with_default(self):
        ctx = SovereignContext()
        assert ctx.get("missing", "fallback") == "fallback"

    def test_get_committed_value(self):
        ctx = SovereignContext()
        ctx.write_to_airlock("k", 99)
        ctx.commit_airlock("sig")
        assert ctx.get("k") == 99


class TestSimpleBuffer:
    def test_write_and_read(self):
        buf = SimpleBuffer()
        buf.write("k", "v")
        assert buf.read("k") == "v"

    def test_read_missing_returns_default(self):
        buf = SimpleBuffer()
        assert buf.read("x") is None
        assert buf.read("x", "default") == "default"


class TestSimpleTrace:
    def test_add_trace_and_summary(self):
        trace = SimpleTrace()
        trace.add_trace("START", {"step": 1})
        summary = trace.get_summary()
        assert summary["total_spans"] == 1

    def test_error_counted_in_failures(self):
        trace = SimpleTrace()
        trace.add_trace("ERROR_OCCURRED", {"detail": "x"})
        summary = trace.get_summary()
        assert summary["failures"] == 1

    def test_no_errors_zero_failures(self):
        trace = SimpleTrace()
        trace.add_trace("SUCCESS")
        summary = trace.get_summary()
        assert summary["failures"] == 0
