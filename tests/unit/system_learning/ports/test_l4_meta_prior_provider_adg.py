"""ADG-driven tests for system_learning/ports/l4_meta_prior_provider.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.ports.l4_meta_prior_provider  # noqa: F401


def test_module_importable():
    """Module l4_meta_prior_provider must be importable."""
    assert system_learning.ports.l4_meta_prior_provider is not None
