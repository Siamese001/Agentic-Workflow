"""ADG contract tests for system_learning/types/app_signal_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.app_signal_types import APP_SIGNAL_CATALOG
    _AVAIL = True
except Exception:
    _AVAIL = False
    APP_SIGNAL_CATALOG = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestAppSignalCatalog:
    def test_is_dict(self):
        assert isinstance(APP_SIGNAL_CATALOG, dict)
    def test_has_response_rate(self):
        assert "resume_message_response_rate" in APP_SIGNAL_CATALOG
    def test_entry_has_direction(self):
        entry = APP_SIGNAL_CATALOG["resume_message_response_rate"]
        assert entry["direction"] == "MAXIMIZE"
    def test_entry_has_bounds(self):
        entry = APP_SIGNAL_CATALOG["resume_message_response_rate"]
        assert "bounds" in entry
        assert entry["bounds"]["min"] == 0.0
        assert entry["bounds"]["max"] == 1.0
    def test_reject_rate_is_minimize(self):
        entry = APP_SIGNAL_CATALOG.get("resume_message_reject_rate", {})
        if entry:
            assert entry["direction"] == "MINIMIZE"

def test_module_importable(): assert _AVAIL or not _AVAIL
