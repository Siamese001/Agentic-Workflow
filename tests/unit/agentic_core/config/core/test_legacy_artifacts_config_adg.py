"""ADG-driven tests for agentic_core/config/core/legacy_artifacts_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.config.core.legacy_artifacts_config  # noqa: F401


def test_module_importable():
    """Module legacy_artifacts_config must be importable."""
    assert agentic_core.config.core.legacy_artifacts_config is not None
