#!/usr/bin/env python3
"""
Test file to verify pre-commit hooks auto-stage formatting changes.
This tests the RCA fix for uncommitted changes issue.
"""


def test_function():
    """Test function with intentionally poor formatting to trigger ruff-format."""
    x = 1 + 2
    y = [1, 2, 3, 4, 5]
    if x > 0:
        print("x is positive")
    return x, y


class TestClass:
    """Test class with formatting issues."""

    def __init__(self, value):
        self.value = value

    def get_value(self):
        return self.value


# This should be reformatted by ruff-format and auto-staged
