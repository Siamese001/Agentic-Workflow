"""
Tests for InvalidStubDetector
"""

import ast
from pathlib import Path

import pytest

from agentic_core.L5_safety.validators.base_detector_validator import AntiPatternCategory
from agentic_core.L5_safety.validators.invalid_stub_validator import InvalidStubDetector


class TestInvalidStubDetector:
    """Test suite for InvalidStubDetector."""

    def test_category(self):
        """Test that detector returns correct category."""
        detector = InvalidStubDetector()
        assert detector.category == AntiPatternCategory.INVALID_STUB

    def test_detects_invalid_stub_single_return(self, tmp_path: Path):
        """Test detection of stub with single success return."""
        detector = InvalidStubDetector()

        # Create a test file with invalid stub
        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    def mock_find_book(book_id):
        return {"status": 200, "data": {"id": book_id}}

    result = mock_find_book("valid_id")
    assert result["status"] == 200
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 1
        assert violations[0].category == AntiPatternCategory.INVALID_STUB
        assert violations[0].message is not None
        assert "mock_find_book" in violations[0].message
        assert "only returns success" in violations[0].message

    def test_detects_invalid_stub_multiple_unconditional_returns(self, tmp_path: Path):
        """Test detection of stub with multiple unconditional returns."""
        detector = InvalidStubDetector()

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    def mock_find_book(book_id):
        if book_id == "1":
            return {"status": 200}
        return {"status": 200}

    result = mock_find_book("valid_id")
    assert result["status"] == 200
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 1
        assert violations[0].message is not None
        assert "mock_find_book" in violations[0].message
        assert "multiple unconditional returns" in violations[0].message

    def test_valid_stub_with_error_return(self, tmp_path: Path):
        """Test that stub with error return is not flagged."""
        detector = InvalidStubDetector()

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    def mock_find_book(book_id):
        if book_id == "missing":
            return {"status": 404, "error": "Not found"}
        return {"status": 200, "data": {"id": book_id}}

    result = mock_find_book("valid_id")
    assert result["status"] == 200
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 0

    def test_valid_stub_with_raise(self, tmp_path: Path):
        """Test that stub with exception raising is not flagged."""
        detector = InvalidStubDetector()

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    def mock_find_book(book_id):
        if book_id == "missing":
            raise ValueError("Not found")
        return {"status": 200, "data": {"id": book_id}}

    result = mock_find_book("valid_id")
    assert result["status"] == 200
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 0

    def test_valid_stub_with_none_return(self, tmp_path: Path):
        """Test that stub with None return (error indicator) is not flagged."""
        detector = InvalidStubDetector()

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    def mock_find_book(book_id):
        if book_id == "missing":
            return None
        return {"status": 200, "data": {"id": book_id}}

    result = mock_find_book("valid_id")
    assert result["status"] == 200
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 0

    def test_whitelist_comment(self, tmp_path: Path):
        """Test that whitelist comment prevents violation detection."""
        detector = InvalidStubDetector()

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    # guardian: allow-invalid-stub
    def mock_find_book(book_id):
        return {"status": 200, "data": {"id": book_id}}

    result = mock_find_book("valid_id")
    assert result["status"] == 200
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 0

    def test_non_stub_function_ignored(self, tmp_path: Path):
        """Test that non-stub functions are not analyzed."""
        detector = InvalidStubDetector()

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    def regular_function(book_id):
        return {"status": 200, "data": {"id": book_id}}

    result = regular_function("valid_id")
    assert result["status"] == 200
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 0

    def test_scan_file_only_tests(self, tmp_path: Path):
        """Test that scan_file only processes test files."""
        detector = InvalidStubDetector()

        # Non-test file - should be skipped
        non_test_file = tmp_path / "regular.py"
        non_test_file.write_text("""
def mock_find_book(book_id):
    return {"status": 200, "data": {"id": book_id}}
""")

        result = detector.scan_file(non_test_file)
        assert result.violations == []

        # Test file - should be processed
        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def mock_find_book(book_id):
    return {"status": 200, "data": {"id": book_id}}
""")

        result = detector.scan_file(test_file)
        assert len(result.violations) > 0

    def test_scan_file_in_tests_directory(self, tmp_path: Path):
        """Test that files in tests/ directory are processed."""
        detector = InvalidStubDetector()

        tests_dir = tmp_path / "tests"
        tests_dir.mkdir()

        test_file = tests_dir / "example.py"
        test_file.write_text("""
def mock_find_book(book_id):
    return {"status": 200, "data": {"id": book_id}}
""")

        result = detector.scan_file(test_file)
        assert len(result.violations) > 0

    def test_suggested_fix_generation(self, tmp_path: Path):
        """Test that fix suggestions are generated."""
        detector = InvalidStubDetector()

        test_file = tmp_path / "test_example.py"
        test_file.write_text("""
def test_find_book():
    def mock_find_book(book_id):
        return {"status": 200, "data": {"id": book_id}}
""")

        tree = ast.parse(test_file.read_text())
        violations = detector.detect(test_file, tree)

        assert len(violations) == 1
        assert violations[0].suggested_fix is not None
        assert "error_condition" in violations[0].suggested_fix
        assert "status: 404" in violations[0].suggested_fix or '"status": 404' in violations[0].suggested_fix
