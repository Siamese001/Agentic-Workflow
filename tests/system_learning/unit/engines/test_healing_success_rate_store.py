"""Foundational behavioral tests for system_learning/engines/healing_success_rate_store.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module healing_success_rate_store must be importable."""
    import agentic_core.L6_system_learning.healing_success_rate_store

    assert system_learning.engines.healing_success_rate_store is not None
