"""Foundational behavioral tests for agentic_core/L4_state/config/versioned_configs.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.config.versioned_configs  # noqa: F401


def test_module_importable():
    """Module versioned_configs must be importable."""
    assert agentic_core.L4_state.config.versioned_configs is not None
