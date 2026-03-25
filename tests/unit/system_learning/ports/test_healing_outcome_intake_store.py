"""Foundational behavioral tests for system_learning/ports/healing_outcome_intake_store.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.ports.healing_outcome_intake_store  # noqa: F401


def test_module_importable():
    """Module healing_outcome_intake_store must be importable."""
    assert system_learning.ports.healing_outcome_intake_store is not None
