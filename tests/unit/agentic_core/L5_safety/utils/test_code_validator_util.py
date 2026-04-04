"""
Unit Tests for code_validator_util - Micro-wave 10B

Tests the code validator utility functions including:
- Syntax validation
- Canonical pattern validation
- Async/await validation
- Print statement detection
"""

from __future__ import annotations

from pathlib import Path

import pytest

from agentic_core.L5_safety.utils.code_validator_util import (
    CodeValidator,
    RuleSet,
    ValidationReport,
    Violation,
    ViolationType,
    validate_directory,
    validate_file,
)


class TestViolationDataclass:
    """Tests for Violation dataclass."""

    def test_violation_creation(self):
        """Test Violation can be created with required fields."""
        violation = Violation(
            violation_type=ViolationType.SYNTAX,
            file_path="test.py",
            line_number=10,
            issue="Syntax error",
            severity="HIGH",
            suggested_fix="Fix it",
            auto_fixable=False,
        )

        assert violation.violation_type == ViolationType.SYNTAX
        assert violation.file_path == "test.py"
        assert violation.line_number == 10
        assert violation.severity == "HIGH"
        assert violation.auto_fixable is False

    def test_violation_to_dict(self):
        """Test Violation to_dict method."""
        violation = Violation(
            violation_type=ViolationType.CANON,
            file_path="test.py",
            line_number=5,
            issue="Canon violation",
        )

        d = violation.to_dict()
        assert d["type"] == "CANON"
        assert d["file_path"] == "test.py"
        assert d["line_number"] == 5
        assert d["issue"] == "Canon violation"


class TestRuleSetDataclass:
    """Tests for RuleSet dataclass."""

    def test_ruleset_default_values(self):
        """Test RuleSet default values."""
        ruleset = RuleSet()

        assert ruleset.check_syntax is True
        assert ruleset.check_canon is True
        assert ruleset.check_async is True
        assert ruleset.check_prints is True
        assert ruleset.print_policy == "warn"
        assert isinstance(ruleset.canon_patterns, dict)

    def test_ruleset_custom_values(self):
        """Test RuleSet with custom values."""
        ruleset = RuleSet(
            check_syntax=False,
            check_prints=False,
            print_policy="error",
        )

        assert ruleset.check_syntax is False
        assert ruleset.check_canon is True  # Default
        assert ruleset.check_prints is False
        assert ruleset.print_policy == "error"


class TestValidationReportDataclass:
    """Tests for ValidationReport dataclass."""

    def test_validation_report_defaults(self):
        """Test ValidationReport default values."""
        report = ValidationReport()

        assert report.violations == []
        assert report.total_violations == 0
        assert report.auto_fixable_count == 0
        assert report.high_severity_count == 0
        assert report.validation_timestamp is not None

    def test_validation_report_to_dict(self):
        """Test ValidationReport to_dict method."""
        violation = Violation(
            violation_type=ViolationType.SYNTAX,
            file_path="test.py",
            line_number=1,
            issue="Test",
        )
        report = ValidationReport(violations=[violation])

        d = report.to_dict()
        assert "violations" in d
        assert len(d["violations"]) == 1
        assert "validation_timestamp" in d


class TestCodeValidatorSyntax:
    """Tests for syntax validation."""

    def test_validate_syntax_valid_file(self, tmp_path):
        """Test syntax validation with valid Python file."""
        validator = CodeValidator()
        test_file = tmp_path / "valid.py"
        test_file.write_text("def hello():\n    pass\n")

        violations = validator.validate_syntax(test_file)

        assert len(violations) == 0

    def test_validate_syntax_invalid_file(self, tmp_path):
        """Test syntax validation with invalid Python file."""
        validator = CodeValidator()
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def hello(\n    pass\n")  # Syntax error

        violations = validator.validate_syntax(test_file)

        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.SYNTAX
        assert violations[0].severity == "HIGH"

    def test_validate_syntax_disabled(self, tmp_path):
        """Test syntax validation when disabled in ruleset."""
        ruleset = RuleSet(check_syntax=False)
        validator = CodeValidator(ruleset)
        test_file = tmp_path / "invalid.py"
        test_file.write_text("def hello(\n    pass\n")  # Syntax error

        violations = validator.validate_syntax(test_file)

        assert len(violations) == 0  # Should not check


class TestCodeValidatorCanon:
    """Tests for canonical pattern validation."""

    def test_validate_canon_wildcard_import(self, tmp_path):
        """Test detection of wildcard imports."""
        validator = CodeValidator()
        test_file = tmp_path / "wildcard.py"
        test_file.write_text("from module import *\n")

        violations = validator.validate_canon(test_file)

        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.CANON
        assert "Wildcard import" in violations[0].issue

    def test_validate_canon_agent_naming(self, tmp_path):
        """Test detection of agent class naming issues."""
        validator = CodeValidator()
        test_file = tmp_path / "agent.py"
        test_file.write_text("class MyAgent:\n    pass\n")  # Should end with Agent

        violations = validator.validate_canon(test_file)

        # This class already ends with Agent, so no violation
        assert len(violations) == 0

    def test_validate_canon_disabled(self, tmp_path):
        """Test canon validation when disabled."""
        ruleset = RuleSet(check_canon=False)
        validator = CodeValidator(ruleset)
        test_file = tmp_path / "wildcard.py"
        test_file.write_text("from module import *\n")

        violations = validator.validate_canon(test_file)

        assert len(violations) == 0


class TestCodeValidatorAsync:
    """Tests for async/await validation."""

    def test_validate_async_with_await(self, tmp_path):
        """Test async function with await is valid."""
        validator = CodeValidator()
        test_file = tmp_path / "async_valid.py"
        test_file.write_text("async def hello():\n    await something()\n")

        violations = validator.validate_async(test_file)

        assert len(violations) == 0

    def test_validate_async_without_await_short(self, tmp_path):
        """Test short async function without await (should pass)."""
        validator = CodeValidator()
        test_file = tmp_path / "async_short.py"
        test_file.write_text("async def hello():\n    pass\n")  # Only 2 lines, threshold is >2

        violations = validator.validate_async(test_file)

        assert len(violations) == 0  # Too short to trigger

    def test_validate_async_disabled(self, tmp_path):
        """Test async validation when disabled."""
        ruleset = RuleSet(check_async=False)
        validator = CodeValidator(ruleset)
        test_file = tmp_path / "async_no_await.py"
        test_file.write_text("async def hello():\n    x = 1\n    y = 2\n    z = 3\n")

        violations = validator.validate_async(test_file)

        assert len(violations) == 0


class TestCodeValidatorPrints:
    """Tests for print statement validation."""

    def test_validate_prints_detected(self, tmp_path):
        """Test detection of print statements."""
        validator = CodeValidator()
        test_file = tmp_path / "prints.py"
        test_file.write_text("print('hello')\n")

        violations = validator.validate_prints(test_file)

        assert len(violations) == 1
        assert violations[0].violation_type == ViolationType.PRINT
        assert "Print statement" in violations[0].issue

    def test_validate_prints_commented_ok(self, tmp_path):
        """Test that commented prints are ignored."""
        validator = CodeValidator()
        test_file = tmp_path / "commented.py"
        test_file.write_text("# print('hello')\n")

        violations = validator.validate_prints(test_file)

        assert len(violations) == 0

    def test_validate_prints_error_policy(self, tmp_path):
        """Test print policy error severity."""
        ruleset = RuleSet(print_policy="error")
        validator = CodeValidator(ruleset)
        test_file = tmp_path / "prints.py"
        test_file.write_text("print('hello')\n")

        violations = validator.validate_prints(test_file)

        assert len(violations) == 1
        assert violations[0].severity == "HIGH"  # Error policy = HIGH

    def test_validate_prints_disabled(self, tmp_path):
        """Test print validation when disabled."""
        ruleset = RuleSet(check_prints=False)
        validator = CodeValidator(ruleset)
        test_file = tmp_path / "prints.py"
        test_file.write_text("print('hello')\n")

        violations = validator.validate_prints(test_file)

        assert len(violations) == 0

    def test_validate_prints_ignore_policy(self, tmp_path):
        """Test print policy ignore."""
        ruleset = RuleSet(print_policy="ignore")
        validator = CodeValidator(ruleset)
        test_file = tmp_path / "prints.py"
        test_file.write_text("print('hello')\n")

        violations = validator.validate_prints(test_file)

        assert len(violations) == 0


class TestValidateFile:
    """Tests for validate_file function."""

    def test_validate_file_comprehensive(self, tmp_path):
        """Test comprehensive file validation."""
        validator = CodeValidator()
        test_file = tmp_path / "comprehensive.py"
        test_file.write_text("""from module import *
print('hello')

async def func():
    x = 1
    y = 2
    z = 3
""")

        violations = validator.validate_file(test_file)

        # Should find wildcard import and print
        types = [v.violation_type for v in violations]
        assert ViolationType.CANON in types  # Wildcard import
        assert ViolationType.PRINT in types  # Print statement

    def test_validate_file_convenience_function(self, tmp_path):
        """Test the convenience validate_file function."""
        test_file = tmp_path / "simple.py"
        test_file.write_text("from module import *\n")

        violations = validate_file(test_file)

        assert len(violations) >= 1
        assert violations[0].violation_type == ViolationType.CANON


class TestValidateDirectory:
    """Tests for validate_directory function."""

    def test_validate_directory(self, tmp_path):
        """Test directory validation."""
        validator = CodeValidator()

        # Create multiple files
        (tmp_path / "file1.py").write_text("print('hello')\n")
        (tmp_path / "file2.py").write_text("from module import *\n")

        report = validator.validate_directory(tmp_path)

        assert report.total_violations >= 2
        assert len(report.violations) >= 2
        assert report.validation_timestamp is not None

    def test_validate_directory_nonexistent(self):
        """Test directory validation with non-existent directory."""
        validator = CodeValidator()

        report = validator.validate_directory(Path("/nonexistent/path"))

        assert report.total_violations == 0
        assert report.violations == []

    def test_validate_directory_convenience_function(self, tmp_path):
        """Test the convenience validate_directory function."""
        (tmp_path / "file.py").write_text("print('hello')\n")

        report = validate_directory(tmp_path)

        assert isinstance(report, ValidationReport)
        assert report.total_violations >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
