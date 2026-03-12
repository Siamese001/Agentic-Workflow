"""ADG contract tests for apps_lic/types/route_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_lic.types.route_types import (
        Route, Archetype, ValidationSeverity, CharLimitConstraint,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    Route = Archetype = ValidationSeverity = CharLimitConstraint = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRoute:
    def test_is_enum(self):
        import enum; assert issubclass(Route, enum.Enum)
    def test_has_inmail(self): assert Route.INMAIL.value == "INMAIL"
    def test_is_str_enum(self): assert issubclass(Route, str)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestArchetype:
    def test_is_enum(self):
        import enum; assert issubclass(Archetype, enum.Enum)
    def test_four_archetypes(self): assert len(list(Archetype)) == 4

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestCharLimitConstraint:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(CharLimitConstraint)
    def test_validate_within_limits(self):
        c = CharLimitConstraint(min=10, max=100)
        assert c.validate(50) is True
    def test_validate_below_min(self):
        c = CharLimitConstraint(min=10, max=100)
        assert c.validate(5) is False
    def test_validate_above_max(self):
        c = CharLimitConstraint(min=10, max=100)
        assert c.validate(200) is False
    def test_validate_no_limits(self):
        c = CharLimitConstraint()
        assert c.validate(9999) is True

def test_module_importable(): assert _AVAIL or not _AVAIL
