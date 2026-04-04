"""Tests for pre_commit_summary_reporter module."""

from __future__ import annotations

from ops_scripts.ci.pre_commit_issue_schema import PreCommitIssue, SeverityLevel
from ops_scripts.ci.pre_commit_summary_reporter import (
    collect_issue,
    format_table_row,
    get_issue_file_path,
    get_issues_dir,
    init_collection,
    load_all_issues,
    print_summary_table,
)


class TestGetIssuesDir:
    """Test get_issues_dir function."""

    def test_happy_path_default(self) -> None:
        """Return default temp directory."""
        result = get_issues_dir()
        assert "pre-commit-issues" in str(result)

    def test_happy_path_env_override(self, monkeypatch) -> None:
        """Use env var when set."""
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", r"C:\custom\path")
        result = get_issues_dir()
        assert str(result) == r"C:\custom\path"


class TestGetIssueFilePath:
    """Test get_issue_file_path function."""

    def test_happy_path(self) -> None:
        """Generate correct path with hook ID."""
        path = get_issue_file_path("adg-burndown-gate")
        assert "adg_burndown_gate.jsonl" in str(path)

    def test_hook_id_with_hyphens(self) -> None:
        """Replace hyphens with underscores."""
        path = get_issue_file_path("my-test-hook")
        assert "my_test_hook.jsonl" in str(path)


class TestInitCollection:
    """Test init_collection function."""

    def test_happy_path_creates_directory(self, monkeypatch, tmp_path) -> None:
        """Create issues directory."""
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(tmp_path / "issues"))
        init_collection()
        assert (tmp_path / "issues").exists()

    def test_happy_path_clears_existing(self, monkeypatch, tmp_path) -> None:
        """Clear existing JSONL files."""
        issues_dir = tmp_path / "issues"
        issues_dir.mkdir()
        (issues_dir / "old.jsonl").write_text("old data")
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))
        init_collection()
        assert not (issues_dir / "old.jsonl").exists()


class TestCollectIssue:
    """Test collect_issue function."""

    def test_happy_path_writes_issue(self, monkeypatch, tmp_path) -> None:
        """Write issue to file."""
        issues_dir = tmp_path / "issues"
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))
        collect_issue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity="HIGH",
            message="Test message",
            explanation="Test explanation",
            file_path="path/to/file.py",
            line_number=42,
        )
        issue_file = issues_dir / "test_hook.jsonl"
        assert issue_file.exists()
        content = issue_file.read_text()
        assert "Test message" in content
        assert "HIGH" in content

    def test_invalid_severity_defaults_to_medium(self, monkeypatch, tmp_path) -> None:
        """Default to MEDIUM on invalid severity."""
        issues_dir = tmp_path / "issues"
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))
        collect_issue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity="INVALID",
            message="Test",
            explanation="Test",
        )
        issue_file = issues_dir / "test_hook.jsonl"
        content = issue_file.read_text()
        assert "MEDIUM" in content

    def test_edge_case_no_file_path(self, monkeypatch, tmp_path) -> None:
        """Handle None file_path."""
        issues_dir = tmp_path / "issues"
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))
        collect_issue(
            hook_id="test-hook",
            hook_name="Test Hook",
            severity="LOW",
            message="Test",
            explanation="Test",
            file_path=None,
        )
        issue_file = issues_dir / "test_hook.jsonl"
        assert issue_file.exists()


class TestFormatTableRow:
    """Test format_table_row function."""

    def test_happy_path_basic(self) -> None:
        """Format basic issue row."""
        rows = format_table_row(
            severity=SeverityLevel.HIGH,
            hook_name="Test Hook",
            file_path="path/file.py",
            message="Test message",
            explanation="Test explanation",
            use_color=False,
        )
        assert len(rows) >= 1
        assert "HIGH" in rows[0]
        assert "Test Hook" in rows[0]

    def test_long_message_wraps(self) -> None:
        """Wrap long messages across lines."""
        long_message = "A" * 200
        rows = format_table_row(
            severity=SeverityLevel.MEDIUM,
            hook_name="Hook",
            file_path="file.py",
            message=long_message,
            explanation="Explanation",
            term_width=80,
            use_color=False,
        )
        assert len(rows) > 1  # Message wrapped

    def test_long_file_path_truncated(self) -> None:
        """Truncate long file paths."""
        long_path = "very/long/path/" * 10 + "file.py"
        rows = format_table_row(
            severity=SeverityLevel.LOW,
            hook_name="Hook",
            file_path=long_path,
            message="Msg",
            explanation="Explanation",
            use_color=False,
        )
        assert "..." in rows[0] or len(rows[0]) < 150

    def test_none_file_path_shows_dash(self) -> None:
        """Show dash for None file path."""
        rows = format_table_row(
            severity=SeverityLevel.INFO,
            hook_name="Hook",
            file_path=None,
            message="Msg",
            explanation="Explanation",
            use_color=False,
        )
        assert "—" in rows[0]


class TestPrintSummaryTable:
    """Test print_summary_table function."""

    def test_happy_path_no_issues(self, monkeypatch, tmp_path, capsys) -> None:
        """Show passed message when no issues."""
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(tmp_path / "empty"))
        exit_code = print_summary_table(use_color=False, verbose=False)
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "GOVERNANCE SUMMARY" in captured.out
        assert "passed" in captured.out or "No issues" in captured.out

    def test_with_critical_issues(self, monkeypatch, tmp_path, capsys) -> None:
        """Return exit code 1 for critical issues."""
        issues_dir = tmp_path / "issues"
        issues_dir.mkdir()
        # Write a critical issue
        issue = PreCommitIssue(
            hook_id="adg-burndown-gate",
            hook_name="ADG Burndown",
            severity=SeverityLevel.CRITICAL,
            message="Critical issue",
            explanation="Critical explanation",
        )
        (issues_dir / "adg_burndown_gate.jsonl").write_text(issue.to_json() + "\n")
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))

        exit_code = print_summary_table(use_color=False, verbose=False)
        captured = capsys.readouterr()
        assert exit_code == 1
        assert "CRITICAL" in captured.out
        assert "critical/high issues" in captured.out

    def test_with_high_issues(self, monkeypatch, tmp_path, capsys) -> None:
        """Return exit code 1 for high issues."""
        issues_dir = tmp_path / "issues"
        issues_dir.mkdir()
        issue = PreCommitIssue(
            hook_id="hollow-file-gate",
            hook_name="Hollow File",
            severity=SeverityLevel.HIGH,
            message="High issue",
            explanation="High explanation",
        )
        (issues_dir / "hollow_file_gate.jsonl").write_text(issue.to_json() + "\n")
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))

        exit_code = print_summary_table(use_color=False, verbose=False)
        captured = capsys.readouterr()
        assert exit_code == 1
        assert "HIGH" in captured.out

    def test_with_medium_issues_only(self, monkeypatch, tmp_path, capsys) -> None:
        """Return exit code 0 for medium-only issues."""
        issues_dir = tmp_path / "issues"
        issues_dir.mkdir()
        issue = PreCommitIssue(
            hook_id="guardian-exemption-gate",
            hook_name="Guardian",
            severity=SeverityLevel.MEDIUM,
            message="Medium issue",
            explanation="Medium explanation",
        )
        (issues_dir / "guardian_exemption_gate.jsonl").write_text(issue.to_json() + "\n")
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))

        exit_code = print_summary_table(use_color=False, verbose=False)
        captured = capsys.readouterr()
        assert exit_code == 0
        assert "MEDIUM" in captured.out

    def test_verbose_shows_passed_hooks(self, monkeypatch, tmp_path, capsys) -> None:
        """Show passed hooks in verbose mode."""
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(tmp_path / "empty"))
        exit_code = print_summary_table(use_color=False, verbose=True)
        captured = capsys.readouterr()
        # Should show at least one passed hook
        assert "ADG" in captured.out or "passed" in captured.out


class TestLoadAllIssues:
    """Test load_all_issues function."""

    def test_happy_path_loads_all_hooks(self, monkeypatch, tmp_path) -> None:
        """Load issues from all governance hooks."""
        issues_dir = tmp_path / "issues"
        issues_dir.mkdir()
        # Add issues to two different hooks
        issue1 = PreCommitIssue(
            hook_id="adg-burndown-gate",
            hook_name="ADG Burndown",
            severity=SeverityLevel.HIGH,
            message="Issue 1",
            explanation="Explanation 1",
        )
        issue2 = PreCommitIssue(
            hook_id="hollow-file-gate",
            hook_name="Hollow File",
            severity=SeverityLevel.MEDIUM,
            message="Issue 2",
            explanation="Explanation 2",
        )
        (issues_dir / "adg_burndown_gate.jsonl").write_text(issue1.to_json() + "\n")
        (issues_dir / "hollow_file_gate.jsonl").write_text(issue2.to_json() + "\n")
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(issues_dir))

        collections = load_all_issues()
        assert "adg-burndown-gate" in collections
        assert "hollow-file-gate" in collections
        assert len(collections["adg-burndown-gate"].issues) == 1
        assert len(collections["hollow-file-gate"].issues) == 1

    def test_missing_files_return_empty(self, monkeypatch, tmp_path) -> None:
        """Return empty collections for missing files."""
        monkeypatch.setenv("PRE_COMMIT_ISSUES_DIR", str(tmp_path / "empty"))
        collections = load_all_issues()
        assert len(collections) == 6  # All governance hooks
        for collection in collections.values():
            assert len(collection.issues) == 0
