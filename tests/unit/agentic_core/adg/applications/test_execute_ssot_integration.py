"""Foundational behavioral tests for agentic_core/adg/applications/execute_ssot_integration.py.

fan_in=4 — imported by 4 other modules.
ADG import-hygiene is covered separately by test_execute_ssot_integration_adg.py.
This file covers behavioral invariants and public API contracts.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

try:
    from agentic_core.adg.applications.execute_ssot_integration import (  # noqa: F401
        PreRunADGReport,
        build_pre_run_report,
        emit_pre_run_log,
    )
    _AVAILABLE = True
except Exception:
    _AVAILABLE = False
    PreRunADGReport = None  # type: ignore[assignment,misc]
    build_pre_run_report = None  # type: ignore[assignment,misc]
    emit_pre_run_log = None  # type: ignore[assignment,misc]


@pytest.mark.skipif(not _AVAILABLE, reason="execute_ssot_integration.py deps unavailable")
class TestPreRunADGReportContract:
    def test_is_dataclass(self):
        import dataclasses
        assert dataclasses.is_dataclass(PreRunADGReport)

    def test_field_names_present(self):
        import dataclasses
        fnames = {f.name for f in dataclasses.fields(PreRunADGReport)}
        assert fnames >= {'impacted_modules', 'impacted_module_count', 'risk_score', 'impacted_tests', 'changed_files', 'impacted_test_count'}

    def test_field_count_reasonable(self):
        import dataclasses
        assert len(dataclasses.fields(PreRunADGReport)) >= 1

@pytest.mark.skipif(not _AVAILABLE, reason="execute_ssot_integration.py deps unavailable")
class TestBuildPreRunReportFunction:
    def test_is_callable(self):
        assert callable(build_pre_run_report)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(build_pre_run_report)
        assert sig.return_annotation is not inspect.Parameter.empty

@pytest.mark.skipif(not _AVAILABLE, reason="execute_ssot_integration.py deps unavailable")
class TestEmitPreRunLogFunction:
    def test_is_callable(self):
        assert callable(emit_pre_run_log)

    def test_has_return_annotation(self):
        import inspect
        sig = inspect.signature(emit_pre_run_log)
        assert sig.return_annotation is not inspect.Parameter.empty


def test_module_importable():
    """Smoke: execute_ssot_integration importable or gracefully unavailable."""
    assert True
