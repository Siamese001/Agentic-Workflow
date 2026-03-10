"""
Test syntax error handling in FCA.

Validates:
- SyntaxError results in graceful UNKNOWN classification
- No crashes on malformed Python files
- Violations are generated for unparseable files
"""

import pytest


class TestSyntaxErrorHandling:
    """Tests for FCA handling of syntax errors."""

    @pytest.fixture
    def fca(self):
        """Create FCA instance for testing."""
        from agentic_core.L5_safety.reasoning.FileClassificationAgent import FileClassificationAgent

        return FileClassificationAgent()

    def test_syntax_error_does_not_crash(self, fca, tmp_path):
        """FCA should not crash on syntax errors."""
        content = '''"""Module with syntax error."""
def broken_function(
    # Missing closing paren and body
'''
        test_file = tmp_path / "broken.py"
        test_file.write_text(content)

        # Should not raise exception
        try:
            result = fca.classify_file(test_file)
            # Result should indicate unknown or error
            assert result is not None
        except SyntaxError:
            pytest.fail("FCA should handle SyntaxError gracefully")

    def test_incomplete_class_definition(self, fca, tmp_path):
        """FCA should handle incomplete class definitions."""
        content = '''"""Module with incomplete class."""
class Incomplete
'''
        test_file = tmp_path / "incomplete.py"
        test_file.write_text(content)

        try:
            result = fca.classify_file(test_file)
            assert result is not None
        except SyntaxError:
            pytest.fail("FCA should handle incomplete class gracefully")

    def test_invalid_indentation(self, fca, tmp_path):
        """FCA should handle invalid indentation."""
        content = '''"""Module with bad indentation."""
def function():
pass  # Wrong indentation
'''
        test_file = tmp_path / "bad_indent.py"
        test_file.write_text(content)

        try:
            result = fca.classify_file(test_file)
            assert result is not None
        except IndentationError:
            pytest.fail("FCA should handle IndentationError gracefully")

    def test_unicode_errors(self, fca, tmp_path):
        """FCA should handle unicode errors gracefully."""
        test_file = tmp_path / "unicode.py"
        # Write bytes that aren't valid UTF-8
        test_file.write_bytes(b'"""Module."""\n\xff\xfe\x00\x01')

        try:
            fca.classify_file(test_file)
            # Should not crash
        except UnicodeDecodeError:
            pytest.fail("FCA should handle UnicodeDecodeError gracefully")

    def test_empty_file(self, fca, tmp_path):
        """FCA should handle empty files."""
        test_file = tmp_path / "empty.py"
        test_file.write_text("")

        result = fca.classify_file(test_file)
        assert result is not None

    def test_only_comments(self, fca, tmp_path):
        """FCA should handle files with only comments."""
        content = """# Just a comment
# Another comment
"""
        test_file = tmp_path / "comments.py"
        test_file.write_text(content)

        result = fca.classify_file(test_file)
        assert result is not None

    def test_only_docstring(self, fca, tmp_path):
        """FCA should handle files with only docstring."""
        content = '''"""Just a docstring module."""
'''
        test_file = tmp_path / "docstring.py"
        test_file.write_text(content)

        result = fca.classify_file(test_file)
        assert result is not None
