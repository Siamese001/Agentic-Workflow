"""Foundational behavioral tests for system_learning/engines/hitl_decision_logger.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

def test_module_importable():
    """Module hitl_decision_logger must be importable."""
    import system_learning.engines.hitl_decision_logger
    assert system_learning.engines.hitl_decision_logger is not None
