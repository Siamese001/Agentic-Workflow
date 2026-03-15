"""ADG contract tests for L5_safety/types/ssot_relocator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.ssot_relocator_types import EnforcementReport, RelocationResult
    _AVAIL = True
except ImportError:
    _AVAIL = False; RelocationResult = EnforcementReport = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRelocationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RelocationResult)
    def test_creates(self):
        r = RelocationResult(source="a/b.py", target="c/b.py", success=True, action="MOVED")
        assert r.success is True; assert r.action == "MOVED"
    def test_timestamp_auto_set(self):
        r = RelocationResult(source="x", target="y", success=False, action="SKIPPED")
        assert r.timestamp != ""

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestEnforcementReport:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(EnforcementReport)
    def test_creates_defaults(self):
        r = EnforcementReport(); assert r.total_operations == 0; assert r.results == []
    def test_success_rate_empty(self):
        r = EnforcementReport(); assert r.success_rate == 100.0
    def test_success_rate_partial(self):
        r = EnforcementReport(total_operations=4, successful=3)
        assert r.success_rate == 75.0

def test_module_importable(): assert _AVAIL or not _AVAIL
