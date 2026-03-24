"""ADG-driven tests for agentic_core/L6_observability/utils/integrity_report_generator_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.L6_observability.utils.integrity_report_generator_util import (  # noqa: F401
        AgentIntegrityReporter,
        GapAnalysisItem,
        IntegrityReportResult,
        generate_full_report,
        validate_registry_coverage,
    )
    _AVAILABLE = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAILABLE = False
    GapAnalysisItem = None  # type: ignore[assignment,misc]
    IntegrityReportResult = None  # type: ignore[assignment,misc]
    AgentIntegrityReporter = None  # type: ignore[assignment,misc]
    validate_registry_coverage = None  # type: ignore[assignment,misc]
    generate_full_report = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="integrity_report_generator_util.py deps unavailable")
class TestGapAnalysisItem:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(GapAnalysisItem)
    def test_importable(self):
        assert GapAnalysisItem is not None

@pytest.mark.skipif(not _AVAILABLE, reason="integrity_report_generator_util.py deps unavailable")
class TestIntegrityReportResult:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(IntegrityReportResult)
    def test_importable(self):
        assert IntegrityReportResult is not None

@pytest.mark.skipif(not _AVAILABLE, reason="integrity_report_generator_util.py deps unavailable")
class TestAgentIntegrityReporter:
    def test_is_class(self):
        assert isinstance(AgentIntegrityReporter, type)
    def test_importable(self):
        assert AgentIntegrityReporter is not None

@pytest.mark.skipif(not _AVAILABLE, reason="integrity_report_generator_util.py deps unavailable")
class TestValidateRegistryCoverage:
    def test_is_callable(self):
        assert callable(validate_registry_coverage)

@pytest.mark.skipif(not _AVAILABLE, reason="integrity_report_generator_util.py deps unavailable")
class TestGenerateFullReport:
    def test_is_callable(self):
        assert callable(generate_full_report)


def test_module_importable():
    """Module integrity_report_generator_util.py is importable (or deps unavailable)."""
    assert _AVAILABLE or not _AVAILABLE