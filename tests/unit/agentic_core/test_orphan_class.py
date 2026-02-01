"""
Orphan Test File - For Dead Code Detection Verification

This file is intentionally NOT imported by any other file in the repository.
It should be detected as an "orphan" (dead code) by the HygieneValidatorAgent.

DO NOT IMPORT THIS FILE - Used for testing orphan detection.
"""


def orphan_function_one() -> str:
    """A function that is never called."""
    return "I am orphaned"


def orphan_function_two(x: int) -> int:
    """Another function that is never called."""
    return x * 2


class OrphanClass:
    """A class that is never instantiated."""

    def __init__(self):
        self.status = "orphaned"

    def do_nothing(self) -> None:
        """A method that does nothing useful."""
        pass


# This entire file is dead code
ORPHAN_CONSTANT = "nobody_uses_me"
