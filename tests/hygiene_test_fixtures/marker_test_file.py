"""
Marker Test File - For Technical Debt Marker Detection

This file contains various technical debt markers (TODO, FIXME, HACK, XXX, BUG)
to verify that the UnifiedHygieneValidatorAgent correctly scans and reports them.

DO NOT FIX THESE MARKERS - Used for testing marker detection.
"""
from __future__ import annotations


# TODO: This is a TODO marker on line 12
def function_with_todo() -> str:
    """A function with a TODO comment."""
    return "needs work"


# FIXME: This is a FIXME marker on line 19
def function_with_fixme() -> int:
    """A function with a FIXME comment."""
    return 42  # FIXME: Return value should be calculated


# HACK: This is a HACK marker on line 26
def function_with_hack() -> bool:
    """A function with a HACK comment."""
    # HACK: Temporary workaround for issue #123
    return True


# XXX: This is a XXX marker on line 33
def function_with_xxx() -> None:
    """A function with a XXX comment."""
    pass  # XXX: Needs implementation


# BUG: This is a BUG marker on line 39
def function_with_bug() -> float:
    """A function with a BUG comment."""
    # BUG: Division by zero possible here
    return 1.0 / 1.0


class MarkerTestClass:
    """A class with multiple markers."""
    
    def __init__(self):
        # TODO: Initialize properly
        self.value = 0
    
    def method_with_markers(self) -> None:
        # FIXME: This method is broken
        # HACK: Using workaround
        # XXX: Review this logic
        pass


# Summary of markers in this file:
# - TODO: 2 occurrences (lines 12, 48)
# - FIXME: 2 occurrences (lines 19, 22, 52)
# - HACK: 2 occurrences (lines 26, 28, 53)
# - XXX: 2 occurrences (lines 33, 35, 54)
# - BUG: 1 occurrence (lines 39, 41)
