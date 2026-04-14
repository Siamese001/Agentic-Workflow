"""Test quality improvement framework for strengthening assertions and coverage.

Provides tools and utilities to enhance test quality, add behavioral validation,
and improve test coverage across the codebase.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from tqdm import tqdm

logger = logging.getLogger(__name__)


class AssertionStrength(Enum):
    """Strength levels for test assertions."""

    WEAK = "weak"  # Basic property checks (assert obj.attr == value)
    MEDIUM = "medium"  # Behavioral validation (assert obj.method() returns expected)
    STRONG = "strong"  # State validation and edge cases (assert obj.state transitions correctly)
    COMPREHENSIVE = "comprehensive"  # Full behavioral + error handling + integration


@dataclass
class TestQualityIssue:
    """Represents a test quality issue found during analysis."""

    test_name: str
    file_path: str
    issue_type: str
    description: str
    line_number: int | None = None
    current_strength: AssertionStrength = AssertionStrength.WEAK
    suggested_improvement: str | None = None


class TestQualityAnalyzer:
    """Analyzes test files for quality issues and suggests improvements."""

    def __init__(self):
        """Initialize the test quality analyzer."""
        self.weak_assertion_patterns = [
            "assert obj is not None",
            "assert obj is None",
            "assert len(obj) == 0",
            "assert len(obj) > 0",
            "assert isinstance(obj,",
            "assert hasattr(obj,",
            "assert obj.attr == value",  # Without behavioral context
        ]

        self.strong_assertion_patterns = [
            "assert obj.method()",
            "assert obj.state ==",
            "assert obj.raises(",
            "assert obj.contains(",
            "assert obj.validate()",
            r"\.assert_called\w*\\(",
            r"pytest\.raises\\(",
        ]

    def analyze_test_file(self, file_path: str) -> list[TestQualityIssue]:
        """Analyze a test file for quality issues."""
        issues = []

        with open(file_path, encoding="utf-8") as f:
            content = f.read()
            lines = content.split("\n")

        # Track when we're inside a test function
        current_test_start = -1
        current_test_name = None

        for i, line in tqdm(enumerate(lines, 1), desc="Processing", unit="item"):
            # Check for weak assertions using proper context detection
            for pattern in tqdm(self.weak_assertion_patterns, desc="Processing", unit="item"):
                if pattern in line and self._is_within_test_method(lines, i):
                    issues.append(
                        TestQualityIssue(
                            test_name=self._extract_test_name(lines[:i]),
                            file_path=file_path,
                            issue_type="weak_assertion",
                            description=f"Weak assertion pattern detected: {pattern}",
                            line_number=i,
                            current_strength=AssertionStrength.WEAK,
                            suggested_improvement=self._suggest_improvement(pattern),
                        ),
                    )

            # Track test function boundaries
            if "def test_" in line:
                current_test_start = i
                current_test_name = self._extract_test_name(lines[:i])
                continue

            # Reset when we hit next function/class
            if line.strip().startswith(("def ", "class ", "async def ")) and current_test_start > 0:
                current_test_start = -1
                current_test_name = None
                continue

            # Check for try/with blocks within test functions
            if current_test_start > 0 and ("try:" in line or "with" in line):
                # Look for asserts in the rest of the test function
                has_assert = False
                for j in range(i, min(len(lines), current_test_start + 50)):  # Search within reasonable scope
                    line_content = lines[j].strip()
                    # Only count actual assert statements, not 'pass' or comments containing 'assert'
                    if line_content.startswith("assert") or " assert " in line_content:
                        has_assert = True
                        break
                    # Stop at next function/class
                    if line_content.startswith(("def ", "class ", "async def ")):
                        break

                if not has_assert:
                    issues.append(
                        TestQualityIssue(
                            test_name=current_test_name,
                            file_path=file_path,
                            issue_type="missing_exception_testing",
                            description="Missing exception testing in try/with block",
                            line_number=i,
                            current_strength=AssertionStrength.WEAK,
                            suggested_improvement="Add pytest.raises() or specific exception validation",
                        ),
                    )

            # Check for behavioral validation opportunities
            if "def test_" in line and ("create" in line or "build" in line):
                if not any("method()" in l or "result." in l for l in lines[i : i + 15]):
                    issues.append(
                        TestQualityIssue(
                            test_name=self._extract_test_name(lines[:i]),
                            file_path=file_path,
                            issue_type="missing_behavioral_validation",
                            description="Test creates objects but doesn't validate behavior",
                            line_number=i,
                            current_strength=AssertionStrength.MEDIUM,
                            suggested_improvement="Add behavioral validation (method calls, state changes)",
                        ),
                    )

        return issues

    def _extract_test_name(self, lines_before: list[str]) -> str:
        """Extract test name from preceding lines."""
        for line in reversed(lines_before):
            if "def test_" in line:
                return line.strip().split("def test_")[1].split("(")[0]
        return "unknown"

    def _is_within_test_method(self, lines: list[str], line_index: int) -> bool:
        """Check if a line is within a test method using proper indentation analysis."""
        # Look backwards to find method definition
        indent_level = None
        for i in range(line_index - 1, max(-1, line_index - 50), -1):
            line = lines[i]
            if line.strip().startswith("def test_"):
                # Found test method - check if current line is indented under it
                method_indent = len(line) - len(line.lstrip())
                current_indent = len(lines[line_index - 1]) - len(lines[line_index - 1].lstrip())
                return current_indent > method_indent
            elif line.strip() and not line.startswith(" ") and not line.startswith("\t"):
                # Found dedentation - outside any method
                break
        return False

    def _suggest_improvement(self, pattern: str) -> str:
        """Suggest improvement for weak assertion pattern."""
        suggestions = {
            "assert True": "Add specific condition validation",
            "assert False": "Add specific failure condition",
            "assert is not None": "Validate specific properties or behavior",
            "assert ==": "Add range or type validation",
            "assert !=": "Add specific inequality validation",
        }
        return suggestions.get(pattern, "Add specific validation with meaningful assertion")


class TestAssertionEnhancer:
    """Enhances test assertions with stronger validation patterns."""

    @staticmethod
    def strengthen_property_assertion(test_code: str, assertion_line: str) -> str:
        """Strengthen a basic property assertion with behavioral validation."""
        if "assert obj.attr == value" in assertion_line:
            # Extract object and attribute
            parts = assertion_line.strip().replace("assert ", "").split(" == ")
            obj_attr = parts[0].strip()
            value = parts[1].strip()

            # Suggest stronger validation
            enhanced = f"""# Enhanced assertion with behavioral validation
        assert {obj_attr} == {value}
        # Add behavioral validation
        assert hasattr({obj_attr.split(".")[0]}, 'validate') or hasattr({obj_attr.split(".")[0]}, 'is_valid')
        # Consider: assert {obj_attr.split(".")[0]}.validate() is True"""

            return enhanced

        return test_code

    @staticmethod
    def add_exception_validation(test_code: str, try_block: str) -> str:
        """Add proper exception validation to try blocks."""
        enhanced = f"""{try_block}
        # Add exception validation
        with pytest.raises(ExpectedExceptionType) as exc_info:
            # Code that should raise exception
            pass
        assert str(exc_info.value) == "Expected error message"
        assert exc_info.value.error_code == expected_code"""

        return enhanced

    @staticmethod
    def add_state_validation(test_code: str, object_creation: str) -> str:
        """Add state validation after object creation."""
        enhanced = f"""{object_creation}
        # Add state validation
        assert obj.state == expected_state
        assert obj.is_valid() is True
        assert obj.get_status() == expected_status"""

        return enhanced


class TestCoverageAnalyzer:
    """Analyzes test coverage and identifies gaps."""

    def __init__(self):
        """Initialize the coverage analyzer."""
        self.coverage_patterns = {
            "error_paths": ["except", "raise", "error", "fail"],
            "edge_cases": ["empty", "none", "zero", "negative", "maximum"],
            "integration": ["multiple", "combined", "workflow", "pipeline"],
            "performance": ["time", "memory", "speed", "benchmark"],
        }

    def analyze_coverage_gaps(self, source_file: str, test_file: str) -> list[str]:
        """Analyze coverage gaps between source and test files."""
        gaps = []

        try:
            # Read source file
            with open(source_file, encoding="utf-8") as f:
                source_content = f.read()

            # Read test file
            with open(test_file, encoding="utf-8") as f:
                test_content = f.read()

            # Check for missing error path testing
            if any(pattern in source_content for pattern in self.coverage_patterns["error_paths"]):
                if not any(
                    "pytest.raises" in test_content
                    or "assert" in test_content
                    and "error" in test_content.lower(),
                ):
                    gaps.append("Missing error path testing")

            # Check for missing edge case testing
            if any(pattern in source_content.lower() for pattern in self.coverage_patterns["edge_cases"]):
                if not any(
                    pattern in test_content.lower() for pattern in self.coverage_patterns["edge_cases"]
                ):
                    gaps.append("Missing edge case testing")

            # Check for missing integration testing
            if "class" in source_content and "def" in source_content:
                if not any("multiple" in test_content.lower() or "combined" in test_content.lower()):
                    gaps.append("Missing integration testing")

        except Exception as e:
            logger.error(f"Failed to analyze coverage gaps: {e}")

        return gaps


# Utility functions for test improvement
def create_behavioral_test_template(class_name: str, methods: list[str]) -> str:
    """Create a template for behavioral testing of a class."""
    template = f"""
class Test{class_name}Behavioral:
    \"\"\"Behavioral tests for {class_name}.\"\"\"

    def test_initial_state_is_valid(self, {class_name.lower()}_instance):
        \"\"\"Test that initial state is valid.\"\"\"
        assert {class_name.lower()}_instance.is_valid() is True
        assert {class_name.lower()}_instance.state == "initialized"

    def test_method_behavioral_validation(self, {class_name.lower()}_instance):
        \"\"\"Test method behavior with state validation.\"\"\"
        # Test each method with behavioral validation
        {chr(10).join([f"        # Test {method}" for method in methods])}

    def test_error_handling(self, {class_name.lower()}_instance):
        \"\"\"Test error handling with proper validation.\"\"\"
        with pytest.raises(ExpectedException):
            {class_name.lower()}_instance.method_that_should_fail()

    def test_state_transitions(self, {class_name.lower()}_instance):
        \"\"\"Test state transitions are valid.\"\"\"
        initial_state = {class_name.lower()}_instance.state
        # Perform operation
        {class_name.lower()}_instance.some_operation()
        # Validate state transition
        assert {class_name.lower()}_instance.state != initial_state
        assert {class_name.lower()}_instance.state in expected_states
"""
    return template


def strengthen_existing_assertions(test_file_path: str) -> str:
    """Strengthen assertions in an existing test file."""
    analyzer = TestQualityAnalyzer()
    enhancer = TestAssertionEnhancer()

    issues = analyzer.analyze_test_file(test_file_path)

    with open(test_file_path, encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    for issue in issues:
        if issue.issue_type == "weak_assertion" and issue.line_number:
            line_idx = issue.line_number - 1
            if line_idx < len(lines):
                original_line = lines[line_idx]
                enhanced_line = enhancer.strengthen_property_assertion(original_line, original_line)
                lines[line_idx] = enhanced_line

    return "\n".join(lines)


# Global analyzer instance
test_quality_analyzer = TestQualityAnalyzer()
test_coverage_analyzer = TestCoverageAnalyzer()
