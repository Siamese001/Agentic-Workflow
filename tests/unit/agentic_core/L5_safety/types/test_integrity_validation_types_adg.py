"""ADG contract tests for L5_safety/types/integrity_validation_types.py."""
from __future__ import annotations
import pytest
pytestmark = pytest.mark.unit
from agentic_core.L5_safety.types.integrity_validation_types import IntegrityViolation, IntegrityResult

class TestIntegrityViolation:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(IntegrityViolation)
    def test_creates(self):
        v = IntegrityViolation(rule="r1", severity="error", description="bad")
        assert v.rule == "r1"; assert v.severity == "error"

class TestIntegrityResult:
    def test_is_dataclass(self):
        import dataclasses; assert dataclasses.is_dataclass(IntegrityResult)
    def test_valid_by_default(self):
        r = IntegrityResult(valid=True)
        assert r.valid is True; assert r.violations == []
