"""
Text Processing Utilities - Phase 4 Optimization
Native Python implementations for common text operations.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from re import Pattern


@dataclass
class TextMatch:
    """Result of a text matching operation."""

    matched: bool
    matches: list[str]
    groups: list[tuple]
    positions: list[tuple]


class TextProcessor:
    """Native Python text processing utilities."""

    @staticmethod
    def extract_patterns(text: str, pattern: str | Pattern, flags: int = 0) -> TextMatch:
        """
        Extract all matches of a pattern from text.

        Args:
            text: Text to search
            pattern: Regex pattern (string or compiled)
            flags: Regex flags (e.g., re.IGNORECASE)

        Returns:
            TextMatch with all matches and positions
        """
        if isinstance(pattern, str):
            compiled_pattern = re.compile(pattern, flags)
        else:
            compiled_pattern = pattern

        matches = compiled_pattern.finditer(text)
        match_list = []
        group_list = []
        position_list = []

        for match in matches:
            match_list.append(match.group(0))
            group_list.append(match.groups())
            position_list.append((match.start(), match.end()))

        return TextMatch(
            matched=len(match_list) > 0,
            matches=match_list,
            groups=group_list,
            positions=position_list,
        )

    @staticmethod
    def validate_pattern(text: str, pattern: str | Pattern, flags: int = 0) -> bool:
        """
        Check if text matches a pattern.

        Args:
            text: Text to validate
            pattern: Regex pattern
            flags: Regex flags

        Returns:
            True if pattern matches, False otherwise
        """
        if isinstance(pattern, str):
            compiled_pattern = re.compile(pattern, flags)
        else:
            compiled_pattern = pattern

        return compiled_pattern.search(text) is not None

    @staticmethod
    def replace_pattern(
        text: str, pattern: str | Pattern, replacement: str, count: int = 0, flags: int = 0,
    ) -> str:
        """
        Replace pattern matches in text.

        Args:
            text: Text to process
            pattern: Regex pattern
            replacement: Replacement string
            count: Maximum replacements (0 = all)
            flags: Regex flags

        Returns:
            Text with replacements applied
        """
        if isinstance(pattern, str):
            compiled_pattern = re.compile(pattern, flags)
        else:
            compiled_pattern = pattern

        return compiled_pattern.sub(replacement, text, count=count)

    @staticmethod
    def clean_whitespace(text: str, preserve_newlines: bool = False) -> str:
        """
        Clean excessive whitespace from text.

        Args:
            text: Text to clean
            preserve_newlines: Whether to preserve newline characters

        Returns:
            Cleaned text
        """
        if preserve_newlines:
            # Clean spaces/tabs but preserve newlines
            lines = text.split("\n")
            cleaned_lines = [re.sub(r"[ \t]+", " ", line.strip()) for line in lines]
            return "\n".join(cleaned_lines)
        else:
            # Replace all whitespace with single space
            return re.sub(r"\s+", " ", text).strip()

    @staticmethod
    def extract_emails(text: str) -> list[str]:
        """
        Extract email addresses from text.

        Args:
            text: Text to search

        Returns:
            List of email addresses found
        """
        pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        return re.findall(pattern, text)

    @staticmethod
    def extract_urls(text: str) -> list[str]:
        """
        Extract URLs from text.

        Args:
            text: Text to search

        Returns:
            List of URLs found
        """
        pattern = r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)"
        return re.findall(pattern, text)

    @staticmethod
    def extract_numbers(text: str, include_decimals: bool = True) -> list[float]:
        """
        Extract numbers from text.

        Args:
            text: Text to search
            include_decimals: Whether to include decimal numbers

        Returns:
            List of numbers found
        """
        if include_decimals:
            pattern = r"-?\d+\.?\d*"
        else:
            pattern = r"-?\d+"

        matches = re.findall(pattern, text)
        return [float(m) for m in matches if m and m != "-"]

    @staticmethod
    def tokenize(text: str, delimiter: str | None = None) -> list[str]:
        """
        Tokenize text into words or custom delimited parts.

        Args:
            text: Text to tokenize
            delimiter: Optional delimiter (None = whitespace)

        Returns:
            List of tokens
        """
        if delimiter:
            return [t.strip() for t in text.split(delimiter) if t.strip()]
        else:
            return text.split()

    @staticmethod
    def truncate(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length.

        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated

        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text

        return text[: max_length - len(suffix)] + suffix

    @staticmethod
    def count_words(text: str) -> int:
        """
        Count words in text.

        Args:
            text: Text to count

        Returns:
            Number of words
        """
        return len(text.split())

    @staticmethod
    def count_sentences(text: str) -> int:
        """
        Count sentences in text.

        Args:
            text: Text to count

        Returns:
            Number of sentences
        """
        # Simple sentence detection
        sentences = re.split(r"[.!?]+", text)
        return len([s for s in sentences if s.strip()])
