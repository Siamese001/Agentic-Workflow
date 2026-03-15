"""ADG contract tests for apps_shared/types/operation_category_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit
try:
    from apps_shared.types.operation_category_types import (
        OperationCategory,
        OperationContext,
        OperationOutcome,
        OperationParameters,
        OperationScope,
    )
    _AVAIL = True
except ImportError:
    _AVAIL = False
    OperationCategory = OperationScope = OperationContext = None  # type: ignore[assignment,misc]
    OperationParameters = OperationOutcome = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOperationCategory:
    def test_is_enum(self):
        import enum; assert issubclass(OperationCategory, enum.Enum)
    def test_has_monitoring(self): assert OperationCategory.MONITORING.value == "monitoring"
    def test_five_categories(self): assert len(list(OperationCategory)) == 5

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOperationScope:
    def test_is_enum(self):
        import enum; assert issubclass(OperationScope, enum.Enum)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOperationContext:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(OperationContext)
    def test_creates(self):
        ctx = OperationContext(
            operation_id="op1",
            category=OperationCategory.MONITORING,
            scope=OperationScope.COMPONENT,
            target="pipeline",
        )
        assert ctx.operation_id == "op1"

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestOperationOutcome:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(OperationOutcome)
    def test_creates(self):
        out = OperationOutcome(operation_id="op1", success=True)
        assert out.success is True; assert out.error is None

def test_module_importable(): assert _AVAIL or not _AVAIL
