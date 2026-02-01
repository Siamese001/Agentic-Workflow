"""
Phase 2 Optimization Tests - Validation Mixin
Tests for shared validation workflow patterns.
"""

import pytest
from apps_shared.mixins.validation_mixin import ValidationMixin, ValidationResult


class MockAgent(ValidationMixin):
    """Mock agent for testing ValidationMixin."""

    def __init__(self):
        self.signals = set()
        self.records = []

    def record_pass(self, message, data=None):
        self.records.append({"type": "pass", "message": message, "data": data})

    def record_fail(self, message, data=None):
        self.records.append({"type": "fail", "message": message, "data": data})

    def add_signal(self, signal):
        self.signals.add(signal)

    def remove_signal(self, signal):
        self.signals.discard(signal)


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test creating ValidationResult."""
        result = ValidationResult(
            passed=True, issues=[], suggestions=["suggestion1"], metadata={"key": "value"}
        )

        assert result.passed is True
        assert result.issues == []
        assert result.suggestions == ["suggestion1"]
        assert result.metadata == {"key": "value"}

    def test_validation_result_with_issues(self):
        """Test ValidationResult with issues."""
        result = ValidationResult(
            passed=False, issues=["error1", "error2"], suggestions=[], metadata={}
        )

        assert result.passed is False
        assert len(result.issues) == 2
        assert result.issues[0] == "error1"


class TestValidationMixin:
    """Test ValidationMixin functionality."""

    def test_validate_with_result_success(self):
        """Test successful validation."""
        agent = MockAgent()

        def validator(data, context):
            return {"issues": [], "suggestions": ["good job"]}

        result = agent.validate_with_result("test_data", validator)

        assert result.passed is True
        assert len(result.issues) == 0
        assert "good job" in result.suggestions

    def test_validate_with_result_failure(self):
        """Test failed validation."""
        agent = MockAgent()

        def validator(data, context):
            return {"issues": ["error1", "error2"], "suggestions": []}

        result = agent.validate_with_result("test_data", validator)

        assert result.passed is False
        assert len(result.issues) == 2

    def test_validate_with_result_exception(self):
        """Test validation with exception."""
        agent = MockAgent()

        def validator(data, context):
            raise ValueError("Validation failed")

        result = agent.validate_with_result("test_data", validator)

        assert result.passed is False
        assert len(result.issues) == 1
        assert "Validation error" in result.issues[0]

    def test_record_validation_result_pass(self):
        """Test recording passed validation."""
        agent = MockAgent()
        result = ValidationResult(passed=True, issues=[], suggestions=[], metadata={})

        agent.record_validation_result(result, "TEST_SIGNAL")

        assert len(agent.records) == 1
        assert agent.records[0]["type"] == "pass"
        assert "TEST_SIGNAL" not in agent.signals

    def test_record_validation_result_fail(self):
        """Test recording failed validation."""
        agent = MockAgent()
        result = ValidationResult(passed=False, issues=["error"], suggestions=[], metadata={})

        agent.record_validation_result(result, "TEST_SIGNAL")

        assert len(agent.records) == 1
        assert agent.records[0]["type"] == "fail"
        assert "TEST_SIGNAL" in agent.signals

    def test_batch_validate_all_pass(self):
        """Test batch validation with all passing."""
        agent = MockAgent()

        def validator1(data, context):
            return {"issues": []}

        def validator2(data, context):
            return {"issues": []}

        validators = [("val1", validator1, "data1"), ("val2", validator2, "data2")]

        results = agent.batch_validate(validators)

        assert len(results) == 2
        assert results["val1"].passed is True
        assert results["val2"].passed is True

    def test_batch_validate_stop_on_failure(self):
        """Test batch validation stopping on first failure."""
        agent = MockAgent()

        def validator1(data, context):
            return {"issues": ["error"]}

        def validator2(data, context):
            return {"issues": []}

        validators = [("val1", validator1, "data1"), ("val2", validator2, "data2")]

        results = agent.batch_validate(validators, stop_on_first_failure=True)

        assert len(results) == 1  # Should stop after first failure
        assert results["val1"].passed is False

    def test_validate_required_fields_success(self):
        """Test required fields validation success."""
        agent = MockAgent()
        data = {"field1": "value1", "field2": "value2"}

        result = agent.validate_required_fields(data, ["field1", "field2"])

        assert result.passed is True
        assert len(result.issues) == 0

    def test_validate_required_fields_missing(self):
        """Test required fields validation with missing field."""
        agent = MockAgent()
        data = {"field1": "value1"}

        result = agent.validate_required_fields(data, ["field1", "field2"])

        assert result.passed is False
        assert len(result.issues) == 1
        assert "field2" in result.issues[0]

    def test_validate_required_fields_none_value(self):
        """Test required fields validation with None value."""
        agent = MockAgent()
        data = {"field1": "value1", "field2": None}

        result = agent.validate_required_fields(data, ["field1", "field2"])

        assert result.passed is False
        assert any("None" in issue for issue in result.issues)

    def test_validate_required_fields_empty_string(self):
        """Test required fields validation with empty string."""
        agent = MockAgent()
        data = {"field1": "value1", "field2": "   "}

        result = agent.validate_required_fields(data, ["field1", "field2"])

        assert result.passed is False
        assert any("empty" in issue for issue in result.issues)

    def test_validate_field_types_success(self):
        """Test field type validation success."""
        agent = MockAgent()
        data = {"name": "test", "age": 25, "active": True}

        result = agent.validate_field_types(data, {"name": str, "age": int, "active": bool})

        assert result.passed is True
        assert len(result.issues) == 0

    def test_validate_field_types_wrong_type(self):
        """Test field type validation with wrong type."""
        agent = MockAgent()
        data = {"name": "test", "age": "25"}  # age should be int

        result = agent.validate_field_types(data, {"name": str, "age": int})

        assert result.passed is False
        assert len(result.issues) == 1
        assert "age" in result.issues[0]
        assert "str" in result.issues[0]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
