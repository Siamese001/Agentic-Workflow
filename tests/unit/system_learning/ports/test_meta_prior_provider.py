"""Foundational behavioral tests for system_learning/ports/meta_prior_provider.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.ports.meta_prior_provider  # noqa: F401


def test_module_importable():
    """Module meta_prior_provider must be importable."""
    assert system_learning.ports.meta_prior_provider is not None
