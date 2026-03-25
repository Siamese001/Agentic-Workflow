"""ADG-driven tests for agentic_core/utils/workflow_engines/completeness_scorer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.completeness_scorer  # noqa: F401


def test_module_importable():
    """Module completeness_scorer must be importable."""
    assert agentic_core.utils.workflow_engines.completeness_scorer is not None
