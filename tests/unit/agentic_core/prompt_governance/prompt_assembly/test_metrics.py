"""Unit tests for PA metrics registry."""

from __future__ import annotations

import pytest

from agentic_core.prompt_governance.prompt_assembly.metrics import (
    METRIC_NAMES,
    PA_METRICS,
    MetricType,
    PAMetricRegistry,
)


def test_at_least_22_metrics_defined():
    assert len(PA_METRICS) >= 22


def test_metric_names_unique():
    names = [m.name for m in PA_METRICS]
    assert len(names) == len(set(names))


def test_all_metrics_have_pa_prefix():
    for m in PA_METRICS:
        assert m.name.startswith("pa_"), m.name


def test_registry_inc_counter():
    reg = PAMetricRegistry()
    reg.inc("pa_assembly_started_total")
    reg.inc("pa_assembly_started_total", 4)
    assert reg.counters["pa_assembly_started_total"] == 5


def test_registry_observe_histogram():
    reg = PAMetricRegistry()
    reg.observe("pa_budget_input_tokens", 1500.0)
    reg.observe("pa_budget_input_tokens", 2500.0)
    assert reg.histograms["pa_budget_input_tokens"] == [1500.0, 2500.0]


def test_registry_unknown_metric_raises():
    reg = PAMetricRegistry()
    with pytest.raises(ValueError):
        reg.inc("pa_nonexistent_total")


def test_registry_wrong_type_raises():
    reg = PAMetricRegistry()
    with pytest.raises(ValueError):
        reg.observe("pa_assembly_started_total", 1.0)  # counter, not histogram


def test_snapshot_contains_all_buckets():
    reg = PAMetricRegistry()
    reg.inc("pa_assembly_started_total")
    reg.observe("pa_budget_input_tokens", 100.0)
    snap = reg.snapshot()
    assert "counters" in snap
    assert "histograms" in snap
    assert "gauges" in snap
    assert snap["counters"]["pa_assembly_started_total"] == 1
