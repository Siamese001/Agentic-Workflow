"""ADG-driven tests for agentic_core/L2_execution/engines/batch_embedding_service.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.engines.batch_embedding_service  # noqa: F401


def test_module_importable():
    """Module batch_embedding_service must be importable."""
    assert agentic_core.L2_execution.engines.batch_embedding_service is not None
