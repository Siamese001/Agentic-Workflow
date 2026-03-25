"""ADG-driven tests for agentic_core/utils/workflow_engines/answer_correctness.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.answer_correctness  # noqa: F401


def test_module_importable():
    """Module answer_correctness must be importable."""
    assert agentic_core.utils.workflow_engines.answer_correctness is not None
