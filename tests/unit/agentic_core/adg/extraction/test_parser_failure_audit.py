"""
Wave 2: Parser Failure Audit Test
Verifies that SyntaxError and OSError during AST parsing are logged at ERROR level.
"""

import logging

from agentic_core.adg.extraction.static_scanner import _scan_file


class TestParserFailureLogging:
    """Ensure parser failures are escalated to ERROR level, not silently dropped."""

    def test_syntax_error_logged_at_error_level(self, tmp_path, caplog):
        """Force a SyntaxError and verify logger.error is called with line number."""
        # Create a file with deliberate syntax error
        bad_file = tmp_path / "bad_syntax.py"
        bad_file.write_text("def foo(\n  pass", encoding="utf-8")  # Missing closing paren

        with caplog.at_level(logging.ERROR):
            edges, parse_failed, _, _ = _scan_file(
                bad_file,
                repo_root=tmp_path,
                layer="L2",
                scan_mode="full"
            )

        # Verify parse was marked as failed
        assert parse_failed is True, "Parse failure should be flagged"
        assert edges == [], "Should return empty edges on parse failure"

        # Verify ERROR level logging occurred
        assert caplog.records, "Expected ERROR logs but none found"

        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert error_records, f"Expected at least one ERROR record, found: {[r.levelname for r in caplog.records]}"

        # Verify the error message contains specific context
        syntax_error_found = any(
            "SyntaxError" in r.message or "line" in r.message.lower()
            for r in error_records
        )
        assert syntax_error_found, (
            f"ERROR log should mention 'SyntaxError' and line info. Got: {[r.message for r in error_records]}"
        )

    def test_os_error_logged_at_error_level(self, tmp_path, caplog):
        """Force an OSError and verify logger.error is called with exc_info."""
        # Create a file path that doesn't exist
        nonexistent = tmp_path / "does_not_exist.py"

        with caplog.at_level(logging.ERROR):
            edges, parse_failed, _, _ = _scan_file(
                nonexistent,
                repo_root=tmp_path,
                layer="L2",
                scan_mode="full"
            )

        # Verify parse was marked as failed
        assert parse_failed is True, "File read failure should be flagged"

        # Verify ERROR level logging
        error_records = [r for r in caplog.records if r.levelno >= logging.ERROR]
        assert error_records, "Expected ERROR log for OSError"

        os_error_found = any(
            "OSError" in r.message or "Permission" in r.message or "reading" in r.message.lower()
            for r in error_records
        )
        assert os_error_found, (
            f"ERROR log should mention file access error. Got: {[r.message for r in error_records]}"
        )

    def test_no_debug_level_for_parse_failures(self, tmp_path, caplog):
        """Ensure parse failures are NEVER logged at DEBUG level (must be ERROR)."""
        bad_file = tmp_path / "bad_indent.py"
        bad_file.write_text("def foo():\n    pass\n   bad_indent = 1", encoding="utf-8")

        with caplog.at_level(logging.DEBUG):
            _scan_file(bad_file, repo_root=tmp_path, layer="L2", scan_mode="full")

        # Check for any DEBUG-level syntax error logs (these are the old bad pattern)
        debug_syntax_logs = [
            r for r in caplog.records
            if r.levelno == logging.DEBUG and ("syntax" in r.message.lower() or "parse" in r.message.lower())
        ]

        assert not debug_syntax_logs, (
            f"Found DEBUG-level parse error logs - these must be ERROR level:\n"
            f"{[r.message for r in debug_syntax_logs]}"
        )


class TestParseFailureVisibility:
    """Ensure parse failures are visible to operators and CI."""

    def test_parse_failure_includes_file_path(self, tmp_path, caplog):
        """ERROR log must include the problematic file path for debugging."""
        nested_dir = tmp_path / "nested" / "deep"
        nested_dir.mkdir(parents=True)
        bad_file = nested_dir / "corrupt.py"
        bad_file.write_text("class Class:\n  def method(:", encoding="utf-8")

        with caplog.at_level(logging.ERROR):
            _scan_file(bad_file, repo_root=tmp_path, layer="L2", scan_mode="full")

        # Verify the error log contains the full file path
        error_messages = " ".join([r.message for r in caplog.records if r.levelno >= logging.ERROR])
        assert str(bad_file) in error_messages or "corrupt.py" in error_messages, (
            f"ERROR log must include the file path. Got: {error_messages[:200]}"
        )

    def test_parse_failure_includes_line_number(self, tmp_path, caplog):
        """ERROR log should include the line number where syntax error occurred."""
        bad_file = tmp_path / "line_two_error.py"
        bad_file.write_text("line_one = 1\ndef bad(\n  pass", encoding="utf-8")  # Error on line 2-3

        with caplog.at_level(logging.ERROR):
            _scan_file(bad_file, repo_root=tmp_path, layer="L2", scan_mode="full")

        error_messages = " ".join([r.message for r in caplog.records if r.levelno >= logging.ERROR])
        # Should mention a line number (2 or 3 in this case)
        import re
        has_line_number = bool(re.search(r'line\s+\d+', error_messages, re.IGNORECASE))
        assert has_line_number, (
            f"ERROR log should include line number. Got: {error_messages[:200]}"
        )
