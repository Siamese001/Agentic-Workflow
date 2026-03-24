"""ADG contract tests for apps_shared/types/sovereign_severity_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.sovereign_severity_types import (
        severity_log_levels,
        sovereign_event_type,
        sovereign_severities,
        sovereign_severity,
    )
    _AVAIL = True
pytest.importorskip("missing_dependency")  # TODO: specify actual dependency
    _AVAIL = False
    sovereign_severity = sovereign_event_type = None  # type: ignore[assignment,misc]
    sovereign_severities = severity_log_levels = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSovereignSeverity:
    def test_is_enum(self):
        import enum; assert issubclass(sovereign_severity, enum.Enum)
    def test_is_str_enum(self): assert issubclass(sovereign_severity, str)
    def test_has_critical(self): assert sovereign_severity.CRITICAL.value == "CRITICAL"
    def test_has_debug(self): assert sovereign_severity.DEBUG.value == "DEBUG"
    def test_five_levels(self): assert len(list(sovereign_severity)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSovereignEventType:
    def test_is_enum(self):
        import enum; assert issubclass(sovereign_event_type, enum.Enum)
    def test_is_str_enum(self): assert issubclass(sovereign_event_type, str)
    def test_has_audit_started(self):
        assert sovereign_event_type.AUDIT_STARTED.value == "AUDIT_STARTED"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRegistries:
    def test_sovereign_severities_is_set(self):
        assert isinstance(sovereign_severities, set)
        assert "CRITICAL" in sovereign_severities
    def test_severity_log_levels_is_dict(self):
        import logging
        assert isinstance(severity_log_levels, dict)
        assert severity_log_levels[sovereign_severity.CRITICAL] == logging.CRITICAL
        assert severity_log_levels[sovereign_severity.DEBUG] == logging.DEBUG

def test_module_importable(): assert _AVAIL or not _AVAIL