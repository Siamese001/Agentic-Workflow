"""Tests for phase-hardened L6ObservabilityBase behaviors."""

import importlib

import pytest
from unittest.mock import patch

from agentic_core.base_agents.L6ObservabilityBase import L6ObservabilityBase


@pytest.mark.unit
class TestL6ObservabilityBaseHardening:
    """Behavioral coverage for phase-hardened L6ObservabilityBase."""

    def test_collect_metrics_returns_expected_structure(self):
        """Happy: collect_metrics returns dict with metrics and timestamp keys."""
        agent = L6ObservabilityBase()
        result = agent.collect_metrics()
        assert isinstance(result, dict)
        assert "metrics" in result
        assert "timestamp" in result

    def test_record_execution_trace_removed_from_module(self):
        """Failure: record_execution_trace is no longer a module-level name (import-time side effect removed)."""
        mod = importlib.import_module("agentic_core.base_agents.L6ObservabilityBase")
        assert not hasattr(mod, "record_execution_trace")

    def test_collect_metrics_degrades_gracefully_when_adg_unavailable(self):
        """Edge: collect_metrics returns valid dict when behavioral_index import fails."""
        agent = L6ObservabilityBase()
        with patch.dict("sys.modules", {"agentic_core.adg.runtime.behavioral_index": None}):
            result = agent.collect_metrics()
        assert isinstance(result, dict)
        assert "metrics" in result
