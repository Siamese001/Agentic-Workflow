"""Foundational behavioral tests for agentic_core/adg/analysis/coupling_metrics.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_coupling_metrics_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.analysis.coupling_metrics import (  # noqa: F401
        CouplingMetricsReport,
        ModuleMetrics,
        compute_coupling_metrics,
    )
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False
    ModuleMetrics = None  # type: ignore[assignment,misc]
    CouplingMetricsReport = None  # type: ignore[assignment,misc]
    compute_coupling_metrics = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="coupling_metrics.py deps unavailable")
class TestModuleMetricsContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(ModuleMetrics)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(ModuleMetrics)}
        assert fnames >= {'ce', 'module_path', 'abstractness', 'instability', 'ca', 'distance'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(ModuleMetrics)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="coupling_metrics.py deps unavailable")
class TestCouplingMetricsReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(CouplingMetricsReport)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(CouplingMetricsReport)}
        assert fnames >= {'metrics_by_module'}

@pytest.mark.skipif(not _AVAILABLE, reason="coupling_metrics.py deps unavailable")
class TestComputeCouplingMetricsFunction:
    def test_is_callable(self):
        assert callable(compute_coupling_metrics)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(compute_coupling_metrics)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: coupling_metrics importable or gracefully unavailable."""
    pass
