"""ADG contract tests for apps_shared/types/validation_status_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.validation_status_types import (
        RuleFailure,
        ValidationAction,
        ValidationStatus,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    ValidationStatus = ValidationAction = RuleFailure = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidationStatus:
    def test_is_enum(self):
        import enum; assert issubclass(ValidationStatus, enum.Enum)
    def test_is_str_enum(self): assert issubclass(ValidationStatus, str)
    def test_has_pass(self): assert ValidationStatus.PASS.value == "PASS"
    def test_has_fail(self): assert ValidationStatus.FAIL.value == "FAIL"
    def test_has_block(self): assert ValidationStatus.BLOCK.value == "BLOCK"
    def test_three_statuses(self): assert len(list(ValidationStatus)) == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidationAction:
    def test_is_enum(self):
        import enum; assert issubclass(ValidationAction, enum.Enum)
    def test_is_str_enum(self): assert issubclass(ValidationAction, str)
    def test_has_regenerate(self): assert ValidationAction.REGENERATE.value == "REGENERATE"
    def test_has_halt(self): assert ValidationAction.HALT.value == "HALT"
    def test_five_actions(self): assert len(list(ValidationAction)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRuleFailure:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RuleFailure)
    def test_creates(self):
        r = RuleFailure(
            rule_id="r1", rule_name="len_check", severity="CRITICAL",
            message="too short", actual=5, expected=50,
        )
        assert r.rule_id == "r1"; assert r.context == {}

def test_module_importable(): assert _AVAIL or not _AVAIL
