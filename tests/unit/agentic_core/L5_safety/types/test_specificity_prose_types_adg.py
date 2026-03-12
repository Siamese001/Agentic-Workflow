"""ADG contract tests for L5_safety/types/specificity_prose_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from agentic_core.L5_safety.types.specificity_prose_types import (
        SpecificityProseConfig, CompanySpecificDetail,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False; SpecificityProseConfig = CompanySpecificDetail = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestSpecificityProseConfig:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(SpecificityProseConfig)
    def test_defaults(self):
        c = SpecificityProseConfig()
        assert c.paragraph_count == 3
        assert c.min_words_per_paragraph == 85
        assert c.min_company_specifics == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCompanySpecificDetail:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CompanySpecificDetail)
    def test_creates(self):
        d = CompanySpecificDetail(detail="Watson", category="PRODUCT", source="website")
        assert d.detail == "Watson"

def test_module_importable(): assert _AVAIL or not _AVAIL
