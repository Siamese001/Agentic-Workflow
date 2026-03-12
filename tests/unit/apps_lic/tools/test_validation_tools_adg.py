"""ADG-driven tests for apps_lic/tools/validation_tools.py — fan_in=1."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

from apps_lic.tools.validation_tools import ValidationResult, validate_schema_policy


class TestValidationResult:
    def test_creates_with_defaults(self):
        result = ValidationResult()
        assert result.is_valid is True
        assert result.errors == []
        assert result.warnings == []

    def test_add_error_marks_invalid(self):
        result = ValidationResult()
        result.add_error("field missing")
        assert result.is_valid is False
        assert "field missing" in result.errors

    def test_add_warning_does_not_invalidate(self):
        result = ValidationResult()
        result.add_warning("minor issue")
        assert result.is_valid is True
        assert "minor issue" in result.warnings

    def test_merge_propagates_errors(self):
        r1 = ValidationResult()
        r2 = ValidationResult()
        r2.add_error("err")
        r1.merge(r2)
        assert r1.is_valid is False
        assert "err" in r1.errors


class TestValidateSchemaPolicy:
    def test_returns_validation_result(self):
        result = validate_schema_policy({"key": "value"})
        assert isinstance(result, ValidationResult)

    def test_empty_data(self):
        result = validate_schema_policy({})
        assert isinstance(result, ValidationResult)
