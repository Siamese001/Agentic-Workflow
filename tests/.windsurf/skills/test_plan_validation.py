"""Tests for plan-validation/main.py skill.

Happy path: valid plan content passes all validators
Failure path: missing wave table, bad token estimates, empty criteria
Edge case: minimal valid plan, boundary token values
"""

import sys
from pathlib import Path

import pytest

# Import the module under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / ".windsurf" / "skills" / "plan-validation"))
from main import (
    validate_plan_format,
    validate_plan_location,
    validate_success_criteria,
    validate_token_estimates,
    validate_wave_table,
)


class TestValidateWaveTable:
    """Test wave table validation."""

    def test_happy_path_valid_table(self):
        """Happy path: valid wave table passes."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1        | Test  | 5,000       | None        | Ready  | Tests pass       |
"""
        is_valid, issues = validate_wave_table(content)
        assert is_valid is True
        assert issues == []

    def test_failure_path_missing_table(self):
        """Failure path: no wave table detected."""
        content = "# Plan\n\nSome content without table."
        is_valid, issues = validate_wave_table(content)
        assert is_valid is False
        assert "Missing wave summary table" in issues[0]

    def test_edge_case_empty_rows(self):
        """Edge case: table has no data rows."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
"""
        is_valid, issues = validate_wave_table(content)
        assert is_valid is False
        assert "no data rows" in issues[0]


class TestValidateTokenEstimates:
    """Test token estimate validation."""

    def test_happy_path_valid_tokens(self):
        """Happy path: reasonable token estimates pass."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1        | Test  | 5,000       | None        | Ready  | Tests pass       |
"""
        is_valid, issues = validate_token_estimates(content)
        assert is_valid is True
        assert issues == []

    def test_failure_path_excessive_tokens(self):
        """Failure path: token estimate exceeds RED threshold."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1        | Test  | 250,000     | None        | Ready  | Tests pass       |
"""
        is_valid, issues = validate_token_estimates(content)
        assert is_valid is False
        assert "exceeds RED threshold" in issues[0]

    def test_failure_path_no_tokens(self):
        """Failure path: no token estimates found."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1        | Test  |             | None        | Ready  | Tests pass       |
"""
        is_valid, issues = validate_token_estimates(content)
        assert is_valid is False
        assert "No token estimates found" in issues[0]


class TestValidateSuccessCriteria:
    """Test success criteria validation."""

    def test_happy_path_valid_criteria(self):
        """Happy path: measurable success criteria pass."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1        | Test  | 5,000       | None        | Ready  | 6 modules tested |
"""
        is_valid, issues = validate_success_criteria(content)
        assert is_valid is True
        assert issues == []

    def test_failure_path_empty_criteria(self):
        """Failure path: empty success criteria detected."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1        | Test  | 5,000       | None        | Ready  |                  |
"""
        is_valid, issues = validate_success_criteria(content)
        assert is_valid is False
        assert "Empty or placeholder success criteria" in issues[0]

    def test_failure_path_todo_criteria(self):
        """Failure path: TODO placeholder in criteria."""
        content = """# Plan

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | P1        | Test  | 5,000       | None        | Ready  | TODO             |
"""
        is_valid, issues = validate_success_criteria(content)
        assert is_valid is False
        assert "Empty or placeholder success criteria" in issues[0]

    def test_edge_case_no_criteria_column(self):
        """Edge case: no success criteria column - passes (optional)."""
        content = """# Plan

| Wave | Focus | Status |
|------|-------|--------|
| W1   | Test  | Ready  |
"""
        is_valid, issues = validate_success_criteria(content)
        assert is_valid is True
        assert issues == []


class TestValidatePlanLocation:
    """Test plan location validation."""

    def test_happy_path_correct_location(self):
        """Happy path: plan in .windsurf/plans/ passes."""
        is_valid, issues = validate_plan_location(".windsurf/plans/test_plan.md")
        assert is_valid is True
        assert issues == []

    def test_failure_path_wrong_location(self):
        """Failure path: plan in docs/reports/plans/ fails."""
        is_valid, issues = validate_plan_location("docs/reports/plans/bad_plan.md")
        assert is_valid is False
        assert "not in SSOT location" in issues[0]

    def test_failure_path_user_home(self):
        """Failure path: plan in user home directory fails."""
        is_valid, issues = validate_plan_location("C:/Users/someone/.windsurf/plans/plan.md")
        assert is_valid is False
        assert "user home directory" in issues[0]

    def test_edge_case_windows_backslashes(self):
        """Edge case: Windows backslash paths handled."""
        is_valid, issues = validate_plan_location(".windsurf\\plans\\test_plan.md")
        assert is_valid is True


class TestValidatePlanFormat:
    """Test full plan format validation."""

    def test_happy_path_full_valid_plan(self):
        """Happy path: complete valid plan passes all checks."""
        content = """# End-to-End Testing Plan

Unified plan for testing.

## Wave Summary Table

| Wave | Phase IDs | Focus | Est. Tokens | Assumptions | Status | Success Criteria |
|------|-----------|-------|-------------|-------------|--------|------------------|
| W1   | W1.1-W1.4 | Core  | 5,000       | None        | Ready  | 6 modules covered |

## Gap Register

GAP-1: Something
"""
        result = validate_plan_format(content, ".windsurf/plans/test.md")
        assert result["valid"] is True
        assert result["issues"] == []

    def test_failure_path_multiple_issues(self):
        """Failure path: plan with multiple validation failures."""
        content = """# Bad Plan

No wave table here.
"""
        result = validate_plan_format(content, "docs/reports/plans/bad.md")
        assert result["valid"] is False
        assert len(result["issues"]) > 0
        # Should catch both location and wave table issues
        issue_text = " ".join(result["issues"])
        assert "not in SSOT location" in issue_text or "Missing wave" in issue_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
