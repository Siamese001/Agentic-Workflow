"""Tests for metrics_emission - metrics emission."""
import pytest
from unittest.mock import Mock
from agentic_core.L4_state.enforcement.metrics_emission import MetricsEmitter


class TestMetricsEmitter:
    def test_init(self):
        m = MetricsEmitter()
        assert m is not None

    def test_emit_counter(self):
        m = MetricsEmitter()
        m.emit_counter("requests", 1)
        snap = m.snapshot()
        assert snap.get("requests", 0) >= 1

    def test_emit_gauge(self):
        m = MetricsEmitter()
        m.emit_gauge("memory_mb", 256)
        snap = m.snapshot()
        assert snap.get("memory_mb") == 256

    def test_emit_histogram(self):
        m = MetricsEmitter()
        m.emit_histogram("latency_ms", 42.0)
        snap = m.snapshot()
        assert "latency_ms" in snap

    def test_attach_backend(self):
        m = MetricsEmitter()
        backend = Mock()
        m.attach_backend(backend)
        m.emit_counter("x", 1)
        backend.write.assert_called()

    def test_reset(self):
        m = MetricsEmitter()
        m.emit_counter("x", 5)
        m.reset()
        snap = m.snapshot()
        assert snap.get("x", 0) == 0
