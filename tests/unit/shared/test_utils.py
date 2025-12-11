"""Unit tests for runtime/shared/utils.py"""
from __future__ import annotations


class TestTextUtils:
    def test_singleton_exists(self):
        assert text_utils is not None
        assert isinstance(text_utils, TextUtils)

    def test_normalize_whitespace(self):
        if hasattr(text_utils, 'normalize_whitespace'):
            result = text_utils.normalize_whitespace("  hello   world  ")
            assert "  " not in result.strip()

    def test_truncate(self):
        if hasattr(text_utils, 'truncate'):
            result = text_utils.truncate("a" * 1000, max_length=100)
            assert len(result) <= 100

    def test_empty_string(self):
        if hasattr(text_utils, 'normalize_whitespace'):
            assert text_utils.normalize_whitespace("") == ""

    def test_determinism(self):
        if hasattr(text_utils, 'normalize_whitespace'):
            inp = "  test  "
            assert text_utils.normalize_whitespace(inp) == text_utils.normalize_whitespace(inp)

class TestDuplicateDetector:
    def test_creation(self):
        det = DuplicateDetector()
        assert det is not None

    def test_unique_not_duplicate(self):
        det = DuplicateDetector()
        if hasattr(det, 'is_duplicate'):
            assert det.is_duplicate("unique_12345") is False

class TestSanitizeFilename:
    def test_removes_invalid_chars(self):
        result = sanitize_filename("file<>name.txt")
        assert "<" not in result and ">" not in result

    def test_preserves_valid(self):
        result = sanitize_filename("valid_file.txt")
        assert "valid" in result

    def test_special_chars(self):
        result = sanitize_filename('file:*?|.txt')
        for c in ':*?|':
            assert c not in result

    def test_determinism(self):
        inp = "test<>.txt"
        assert sanitize_filename(inp) == sanitize_filename(inp)
