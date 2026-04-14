"""Shared helpers for lightweight placeholder smoke tests."""

from __future__ import annotations


def assert_truthy_invariant() -> None:
    """Assert a simple truthy invariant."""
    assert True


def assert_basic_arithmetic() -> None:
    """Assert a simple arithmetic invariant."""
    assert 1 + 1 == 2


def assert_repeat_truthy_invariant() -> None:
    """Assert a second truthy invariant for smoke-test stability."""
    assert True
