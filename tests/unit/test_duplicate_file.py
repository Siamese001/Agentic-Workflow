"""
Test Duplicate File A - For GAP-4 Verification

This file is intentionally identical to test_duplicate_file.py in duplicate_b/
to verify that the HygieneValidatorAgent correctly detects duplicates
via MD5 hash comparison.

DO NOT MODIFY - Used for testing duplicate detection.
"""

from __future__ import annotations


def calculate_sum(a: int, b: int) -> int:
    """Calculate the sum of two numbers."""
    return a + b


def calculate_product(a: int, b: int) -> int:
    """Calculate the product of two numbers."""
    return a * b


class DuplicateTestClass:
    """A test class that exists in both duplicate files."""

    def __init__(self, value: int):
        self.value = value

    def double(self) -> int:
        """Return double the value."""
        return self.value * 2

    def triple(self) -> int:
        """Return triple the value."""
        return self.value * 3


# This content is identical in both files
MAGIC_CONSTANT = 42
ANOTHER_CONSTANT = "duplicate_test"
