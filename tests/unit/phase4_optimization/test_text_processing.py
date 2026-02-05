"""
Phase 4 Optimization Tests - Text Processing
Tests for native Python text processing utilities.
"""

import pytest
from apps_shared.utils.text_processing_validator import TextProcessor, TextMatch


class TestTextMatch:
    """Test TextMatch dataclass."""

    def test_text_match_creation(self):
        """Test creating TextMatch."""
        match = TextMatch(matched=True, matches=["test"], groups=[()], positions=[(0, 4)])

        assert match.matched is True
        assert match.matches == ["test"]
        assert match.groups == [()]
        assert match.positions == [(0, 4)]


class TestTextProcessor:
    """Test TextProcessor functionality."""

    def test_extract_patterns_simple(self):
        """Test extracting simple pattern."""
        text = "The numbers are 123 and 456"
        result = TextProcessor.extract_patterns(text, r"\d+")

        assert result.matched is True
        assert result.matches == ["123", "456"]
        assert len(result.positions) == 2

    def test_extract_patterns_with_groups(self):
        """Test extracting pattern with groups."""
        text = "Email: user@example.com"
        result = TextProcessor.extract_patterns(text, r"(\w+)@(\w+\.\w+)")

        assert result.matched is True
        assert len(result.groups) == 1
        assert result.groups[0] == ("user", "example.com")

    def test_extract_patterns_no_match(self):
        """Test extracting pattern with no matches."""
        text = "No numbers here"
        result = TextProcessor.extract_patterns(text, r"\d+")

        assert result.matched is False
        assert result.matches == []

    def test_validate_pattern_match(self):
        """Test pattern validation with match."""
        text = "test@example.com"
        result = TextProcessor.validate_pattern(text, r"\w+@\w+\.\w+")

        assert result is True

    def test_validate_pattern_no_match(self):
        """Test pattern validation without match."""
        text = "not an email"
        result = TextProcessor.validate_pattern(text, r"\w+@\w+\.\w+")

        assert result is False

    def test_replace_pattern_simple(self):
        """Test simple pattern replacement."""
        text = "The price is $100"
        result = TextProcessor.replace_pattern(text, r"\$\d+", "$200")

        assert result == "The price is $200"

    def test_replace_pattern_multiple(self):
        """Test replacing multiple occurrences."""
        text = "foo bar foo baz"
        result = TextProcessor.replace_pattern(text, r"foo", "qux")

        assert result == "qux bar qux baz"

    def test_replace_pattern_count_limit(self):
        """Test replacement with count limit."""
        text = "foo foo foo"
        result = TextProcessor.replace_pattern(text, r"foo", "bar", count=2)

        assert result == "bar bar foo"

    def test_clean_whitespace_default(self):
        """Test cleaning whitespace without preserving newlines."""
        text = "  Hello   \n  World  \t  "
        result = TextProcessor.clean_whitespace(text)

        assert result == "Hello World"

    def test_clean_whitespace_preserve_newlines(self):
        """Test cleaning whitespace while preserving newlines."""
        text = "  Hello   \n  World  "
        result = TextProcessor.clean_whitespace(text, preserve_newlines=True)

        assert result == "Hello\nWorld"

    def test_extract_emails_single(self):
        """Test extracting single email."""
        text = "Contact me at user@example.com for details"
        result = TextProcessor.extract_emails(text)

        assert result == ["user@example.com"]

    def test_extract_emails_multiple(self):
        """Test extracting multiple emails."""
        text = "Email: user1@test.com or user2@example.org"
        result = TextProcessor.extract_emails(text)

        assert len(result) == 2
        assert "user1@test.com" in result
        assert "user2@example.org" in result

    def test_extract_urls_http(self):
        """Test extracting HTTP URLs."""
        text = "Visit http://example.com for more info"
        result = TextProcessor.extract_urls(text)

        assert result == ["http://example.com"]

    def test_extract_urls_https(self):
        """Test extracting HTTPS URLs."""
        text = "Check https://www.example.com/page?param=value"
        result = TextProcessor.extract_urls(text)

        assert len(result) == 1
        assert "https://www.example.com/page?param=value" in result[0]

    def test_extract_numbers_integers(self):
        """Test extracting integer numbers."""
        text = "The values are 10, 20, and 30"
        result = TextProcessor.extract_numbers(text)

        assert result == [10.0, 20.0, 30.0]

    def test_extract_numbers_decimals(self):
        """Test extracting decimal numbers."""
        text = "Prices: 10.99, 20.50, 30.00"
        result = TextProcessor.extract_numbers(text)

        assert result == [10.99, 20.50, 30.00]

    def test_extract_numbers_negative(self):
        """Test extracting negative numbers."""
        text = "Temperature: -5.5 degrees"
        result = TextProcessor.extract_numbers(text)

        assert result == [-5.5]

    def test_tokenize_default(self):
        """Test tokenizing with default whitespace."""
        text = "Hello world from Python"
        result = TextProcessor.tokenize(text)

        assert result == ["Hello", "world", "from", "Python"]

    def test_tokenize_custom_delimiter(self):
        """Test tokenizing with custom delimiter."""
        text = "apple,banana,cherry"
        result = TextProcessor.tokenize(text, delimiter=",")

        assert result == ["apple", "banana", "cherry"]

    def test_truncate_short_text(self):
        """Test truncating text shorter than max length."""
        text = "Short"
        result = TextProcessor.truncate(text, 10)

        assert result == "Short"

    def test_truncate_long_text(self):
        """Test truncating long text."""
        text = "This is a very long text that needs truncation"
        result = TextProcessor.truncate(text, 20)

        assert len(result) == 20
        assert result.endswith("...")

    def test_truncate_custom_suffix(self):
        """Test truncating with custom suffix."""
        text = "Long text here"
        result = TextProcessor.truncate(text, 10, suffix=">>")

        assert result.endswith(">>")
        assert len(result) == 10

    def test_count_words_simple(self):
        """Test counting words."""
        text = "Hello world from Python"
        result = TextProcessor.count_words(text)

        assert result == 4

    def test_count_words_extra_spaces(self):
        """Test counting words with extra spaces."""
        text = "Hello   world  from   Python"
        result = TextProcessor.count_words(text)

        assert result == 4

    def test_count_sentences_simple(self):
        """Test counting sentences."""
        text = "First sentence. Second sentence! Third sentence?"
        result = TextProcessor.count_sentences(text)

        assert result == 3

    def test_count_sentences_multiple_punctuation(self):
        """Test counting sentences with multiple punctuation."""
        text = "Hello!!! How are you?? I'm fine."
        result = TextProcessor.count_sentences(text)

        assert result == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
