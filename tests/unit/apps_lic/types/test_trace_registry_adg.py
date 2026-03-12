"""ADG-driven tests for apps_lic/types/TraceRegistry.py — fan_in=2.

Contract tests: TraceRegistry init, add/get/clear, persistence-free operation.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_lic.types.TraceRegistry import TraceRegistry


class TestTraceRegistryInit:
    def test_creates_without_persistence(self):
        registry = TraceRegistry()
        assert registry is not None

    def test_traces_start_empty(self):
        registry = TraceRegistry()
        assert registry._traces == []

    def test_persistence_path_default_none(self):
        registry = TraceRegistry()
        assert registry.persistence_path is None


class TestTraceRegistryAPI:
    def setup_method(self):
        self.registry = TraceRegistry()

    def test_has_add_trace(self):
        assert hasattr(self.registry, "add_trace")

    def test_has_get_traces(self):
        assert hasattr(self.registry, "get_traces")

    def test_has_clear(self):
        assert hasattr(self.registry, "clear")

    def test_add_trace_increments_count(self):
        initial = len(self.registry._traces)
        self.registry.add_trace(event_type="test_event", details={"step": "init"})
        assert len(self.registry._traces) == initial + 1

    def test_get_traces_returns_list(self):
        self.registry.add_trace(event_type="test_event", details={"step": "init"})
        traces = self.registry.get_traces()
        assert isinstance(traces, list)
        assert len(traces) >= 1

    def test_clear_empties_traces(self):
        self.registry.add_trace(event_type="test_event", details={"step": "init"})
        self.registry.clear()
        assert self.registry._traces == []
