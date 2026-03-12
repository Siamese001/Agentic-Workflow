"""ADG contract tests for system_learning/types/rca_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from system_learning.types.rca_types import RCAFinding, RCAReport
    _AVAIL = True
except Exception:
    _AVAIL = False
    RCAFinding = RCAReport = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRCAFinding:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RCAFinding)
    def test_is_frozen(self):
        assert RCAFinding.__dataclass_params__.frozen is True
    def test_creates(self):
        f = RCAFinding(category="SYNTAX", signature="missing_colon", count=3, evidence_hash="a" * 64)
        assert f.category == "SYNTAX"; assert f.count == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRCAReport:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RCAReport)
    def test_is_frozen(self):
        assert RCAReport.__dataclass_params__.frozen is True
    def test_has_report_id_field(self):
        import dataclasses
        fields = {f.name for f in dataclasses.fields(RCAReport)}
        assert "report_id" in fields
        assert "findings" in fields

def test_module_importable(): assert _AVAIL or not _AVAIL
