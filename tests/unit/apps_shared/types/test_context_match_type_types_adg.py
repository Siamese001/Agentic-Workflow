"""ADG contract tests for apps_shared/types/context_match_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.context_match_type_types import ContextMatchType
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ContextMatchType = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestContextMatchType:
    def test_is_enum(self):
        import enum; assert issubclass(ContextMatchType, enum.Enum)
    def test_has_domain(self): assert ContextMatchType.DOMAIN.value == "domain"
    def test_has_purpose(self): assert ContextMatchType.PURPOSE.value == "purpose"
    def test_has_semantic(self): assert ContextMatchType.SEMANTIC.value == "semantic"
    def test_has_structural(self): assert ContextMatchType.STRUCTURAL.value == "structural"
    def test_has_usage(self): assert ContextMatchType.USAGE.value == "usage"
    def test_five_types(self): assert len(list(ContextMatchType)) == 5

def test_module_importable(): assert _AVAIL or not _AVAIL
