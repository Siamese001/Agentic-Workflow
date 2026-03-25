"""Foundational behavioral tests for system_learning/engines/hitl_decision_logger.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import system_learning.engines.hitl_decision_logger  # noqa: F401


def test_module_importable():
    """Module hitl_decision_logger must be importable."""
    assert system_learning.engines.hitl_decision_logger is not None
