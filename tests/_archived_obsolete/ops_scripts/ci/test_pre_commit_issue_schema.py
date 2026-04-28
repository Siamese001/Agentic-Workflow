"""Tests for pre_commit_issue_schema module."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from ops_scripts.ci.pre_commit_issue_schema import (
    IssueCollection,
    PreCommitIssue,
    SeverityLevel,
    colorize_severity,
    get_severity_icon,
)


class TestSeverityLevel:
    """Test SeverityLevel enum."""

    def test_severity_values(self) -> None:
        """All severity levels have correct string values (lowercase per SSOT)."""
        assert SeverityLevel.CRITICAL.value == "critical"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.INFO.value == "info"


class TestPreCommitIssue:
    """Test PreCommitIssue dataclass."""

    def test_happy_path_full_issue(self) -> None:
        """Create issue with all fields."""
        issue = PreCommitIssue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity=SeverityLevel.HIGH,
            message="Test message",
            explanation="Test explanation",
            file_path="path/to/file.py",
            line_number=42,
            issue_type="test_type",
            suggestion="Fix it",
        )
        assert issue.hook_id == "test-hook"
        assert issue.severity == SeverityLevel.HIGH
        assert issue.line_number == 42

    def test_happy_path_minimal_issue(self) -> None:
        """Create issue with only required fields."""
        issue = PreCommitIssue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity=SeverityLevel.MEDIUM,
            message="Test message",
            explanation="Test explanation",
        )
        assert issue.file_path is None
        assert issue.line_number is None
        assert issue.issue_type == "general"

    def test_to_json_roundtrip(self) -> None:
        """Serialize to JSON and back (lowercase per SSOT)."""
        issue = PreCommitIssue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity=SeverityLevel.CRITICAL,
            message="Test message",
            explanation="Test explanation",
            file_path="path/to/file.py",
            line_number=10,
        )
        json_str = issue.to_json()
        data = json.loads(json_str)
        assert data["severity"] == "critical"
        assert data["hook_id"] == "test-hook"

    def test_from_json_roundtrip(self) -> None:
        """Deserialize from JSON correctly."""
        issue = PreCommitIssue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity=SeverityLevel.HIGH,
            message="Test message",
            explanation="Test explanation",
        )
        json_str = issue.to_json()
        restored = PreCommitIssue.from_json(json_str)
        assert restored.hook_id == issue.hook_id
        assert restored.severity == issue.severity
        assert restored.message == issue.message

    def test_from_json_invalid_severity(self) -> None:
        """Fail on invalid severity in JSON."""
        data = {
            "hook_id": "test",
            "hook_name": "Test",
            "severity": "INVALID",
            "message": "msg",
            "explanation": "expl",
        }
        with pytest.raises(ValueError):
            PreCommitIssue.from_json(json.dumps(data))

    def test_passed_factory(self) -> None:
        """Create passed status issue."""
        issue = PreCommitIssue.passed("test-hook", "Test Hook")
        assert issue.severity == SeverityLevel.INFO
        assert issue.issue_type == "passed"
        assert "No issues" in issue.message

    def test_skipped_factory(self) -> None:
        """Create skipped status issue."""
        issue = PreCommitIssue.skipped("test-hook", "Test Hook", "no files")
        assert issue.severity == SeverityLevel.INFO
        assert issue.issue_type == "skipped"
        assert "no files" in issue.message


class TestIssueCollection:
    """Test IssueCollection dataclass."""

    def test_happy_path_add_and_save(self, tmp_path: Path) -> None:
        """Add issues and save to file."""
        collection = IssueCollection(
            hook_id="test-hook",
            hook_name="Test Hook",
            timestamp="2024-01-01T00:00:00",
        )
        issue1 = PreCommitIssue.passed("test-hook", "Test Hook")
        issue2 = PreCommitIssue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity=SeverityLevel.HIGH,
            message="Issue 2",
            explanation="Explanation 2",
        )
        collection.add(issue1)
        collection.add(issue2)

        save_path = tmp_path / "issues.jsonl"
        collection.save_to_file(save_path)

        assert save_path.exists()
        lines = save_path.read_text().strip().split("\n")
        assert len(lines) == 2

    def test_load_from_file_happy_path(self, tmp_path: Path) -> None:
        """Load issues from valid JSONL file."""
        issue = PreCommitIssue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity=SeverityLevel.MEDIUM,
            message="Test",
            explanation="Test explanation",
        )
        save_path = tmp_path / "issues.jsonl"
        save_path.write_text(issue.to_json() + "\n")

        loaded = IssueCollection.load_from_file("test-hook", "Test Hook", save_path)
        assert len(loaded.issues) == 1
        assert loaded.issues[0].message == "Test"

    def test_load_from_file_missing_file(self, tmp_path: Path) -> None:
        """Return empty collection for missing file."""
        missing_path = tmp_path / "nonexistent.jsonl"
        loaded = IssueCollection.load_from_file("test-hook", "Test Hook", missing_path)
        assert len(loaded.issues) == 0

    def test_load_from_file_malformed_json(self, tmp_path: Path, capsys) -> None:
        """Skip malformed lines and report count."""
        save_path = tmp_path / "issues.jsonl"
        issue = PreCommitIssue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity=SeverityLevel.LOW,
            message="Valid",
            explanation="Valid explanation",
        )
        save_path.write_text(issue.to_json() + "\ninvalid json\n")

        loaded = IssueCollection.load_from_file("test-hook", "Test Hook", save_path)
        assert len(loaded.issues) == 1
        # Check warning was printed
        captured = capsys.readouterr()
        assert "malformed" in captured.err


class TestSeverityHelpers:
    """Test severity helper functions."""

    def test_colorize_with_color(self) -> None:
        """Apply color codes when enabled."""
        result = colorize_severity(SeverityLevel.CRITICAL, "text", use_color=True)
        assert "\033[" in result
        assert "text" in result

    def test_colorize_without_color(self) -> None:
        """Return plain text when disabled."""
        result = colorize_severity(SeverityLevel.CRITICAL, "text", use_color=False)
        assert result == "text"

    def test_get_severity_icon(self) -> None:
        """Return correct icons."""
        assert get_severity_icon(SeverityLevel.CRITICAL) == "⛔"
        assert get_severity_icon(SeverityLevel.HIGH) == "⚠️"
        assert get_severity_icon(SeverityLevel.MEDIUM) == "🔹"
        assert get_severity_icon(SeverityLevel.LOW) == "ℹ️"
        assert get_severity_icon(SeverityLevel.INFO) == "✓"
