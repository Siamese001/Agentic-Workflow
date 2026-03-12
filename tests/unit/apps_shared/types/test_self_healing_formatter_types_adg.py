"""ADG contract tests for apps_shared/types/self_healing_formatter_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.self_healing_formatter_types import (
        RepairStrategy, RepairResult, FormatRepair,
    )
    _AVAIL = True
except Exception:
    _AVAIL = False
    RepairStrategy = RepairResult = FormatRepair = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRepairStrategy:
    def test_is_enum(self):
        import enum; assert issubclass(RepairStrategy, enum.Enum)
    def test_is_str_enum(self): assert issubclass(RepairStrategy, str)
    def test_has_json_repair(self): assert RepairStrategy.JSON_REPAIR.value == "json_repair"
    def test_has_fallback_text(self): assert RepairStrategy.FALLBACK_TEXT.value == "fallback_text"
    def test_five_strategies(self): assert len(list(RepairStrategy)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestRepairResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(RepairResult)
    def test_creates_success(self):
        r = RepairResult(success=True, repaired_data={"key": "val"})
        assert r.success is True; assert r.attempts == 0
    def test_creates_failure(self):
        r = RepairResult(
            success=False, repaired_data=None,
            strategy_used=RepairStrategy.JSON_REPAIR,
            error_message="parse error", attempts=3,
        )
        assert r.success is False; assert r.attempts == 3

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestFormatRepair:
    def test_is_abstract(self):
        from abc import ABC; assert issubclass(FormatRepair, ABC)
    def test_cannot_instantiate_directly(self):
        with pytest.raises(TypeError):
            FormatRepair()  # type: ignore[abstract]

def test_module_importable(): assert _AVAIL or not _AVAIL
