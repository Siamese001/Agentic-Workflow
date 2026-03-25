"""ADG-driven tests for L2_execution/config/strategist_bio_writer_config.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.config.strategist_bio_writer_config  # noqa: F401


def test_module_importable():
    """Module strategist_bio_writer_config must be importable."""
    assert agentic_core.L2_execution.config.strategist_bio_writer_config is not None
