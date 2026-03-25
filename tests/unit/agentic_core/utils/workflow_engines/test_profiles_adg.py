"""ADG-driven tests for agentic_core/utils/workflow_engines/profiles.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.utils.workflow_engines.profiles  # noqa: F401


def test_module_importable():
    """Module profiles must be importable."""
    assert agentic_core.utils.workflow_engines.profiles is not None
