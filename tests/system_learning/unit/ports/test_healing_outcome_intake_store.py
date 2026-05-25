"""Foundational behavioral tests for system_learning/ports/healing_outcome_intake_store.py."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module healing_outcome_intake_store must be importable."""
    import agentic_core.L6_system_learning.healing_outcome_intake_store

    assert system_learning.ports.healing_outcome_intake_store is not None
