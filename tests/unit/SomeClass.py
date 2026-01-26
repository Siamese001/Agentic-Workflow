"""
Type Hint Violation Test Fixture

This file contains functions with missing type hints that the
CodeStandardsEnforcerAgent should detect.

DO NOT FIX - Used for testing type hint enforcement.
"""


# VIOLATION: Missing return type hint
def function_no_return_hint(x: int):
    """Function missing return type hint."""
    return x * 2


# VIOLATION: Missing parameter type hint
def function_no_param_hint(x) -> int:
    """Function missing parameter type hint."""
    return x * 2


# VIOLATION: Missing both return and parameter type hints
def function_no_hints(x, y):
    """Function missing all type hints."""
    return x + y


# VIOLATION: Missing some parameter type hints
def function_partial_hints(a: int, b, c: str):
    """Function with partial type hints."""
    return f"{a} {b} {c}"


# VIOLATION: Public function with no hints at all
def public_function_no_hints(data, options):
    """Public function with no type hints at all."""
    return data


# This is OK - private function (starts with _)
def _private_function(x, y):
    """Private function - type hints not required."""
    return x + y


# This is OK - dunder method
class SomeClass:
    def __init__(self, value):
        """Init method - 'self' doesn't need type hint."""
        self.value = value

    # VIOLATION: Public method missing hints
    def public_method(self, x):
        """Public method missing type hints."""
        return self.value + x

    # This is OK - private method
    def _private_method(self, x):
        """Private method - type hints not required."""
        return self.value * x


# Summary of violations in this file:
# - Missing return type: 4 (lines 13, 25, 31, 37)
# - Missing parameter type: 6 (lines 19, 25x2, 31, 37x2, 54)
