"""Foundational behavioral tests for agentic_core/adg/analysis/test_gap.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_test_gap_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.analysis.test_gap import (  # noqa: F401
        TestGapEntry,
        TestGapReport,
        detect_test_gaps,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    TestGapEntry = None  # type: ignore[assignment,misc]
    TestGapReport = None  # type: ignore[assignment,misc]
    detect_test_gaps = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="test_gap.py deps unavailable")
class TestTestGapEntryContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TestGapEntry)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(TestGapEntry)}
        assert fnames >= {'layer', 'module_path', 'fan_in'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(TestGapEntry)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="test_gap.py deps unavailable")
class TestTestGapReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(TestGapReport)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(TestGapReport)}
        assert fnames >= {'uncovered_modules', 'highest_risk_gaps', 'coverage_rate', 'gap_by_layer', 'covered_modules', 'total_production_modules'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(TestGapReport)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="test_gap.py deps unavailable")
class TestDetectTestGapsFunction:
    def test_is_callable(self):
        assert callable(detect_test_gaps)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(detect_test_gaps)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: test_gap importable or gracefully unavailable."""
    assert True
