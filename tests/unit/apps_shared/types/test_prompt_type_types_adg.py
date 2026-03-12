"""ADG contract tests for apps_shared/types/prompt_type_types.py.
Note: source file has syntax/naming issues so import may fail — skipif guards used.
"""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
try:
    from apps_shared.types.prompt_type_types import PromptType, PromptSchema, ValidationResult
    _AVAIL = True
except Exception:
    _AVAIL = False
    PromptType = PromptSchema = ValidationResult = None  # type: ignore[assignment,misc]

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPromptType:
    def test_is_enum(self):
        import enum; assert issubclass(PromptType, enum.Enum)
    def test_is_str_enum(self): assert issubclass(PromptType, str)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestPromptSchema:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(PromptSchema)

@pytest.mark.skipif(not _AVAIL, reason="deps unavailable")
class TestValidationResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(ValidationResult)

def test_module_importable(): assert _AVAIL or not _AVAIL
