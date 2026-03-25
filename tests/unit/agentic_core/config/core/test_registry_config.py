"""Foundational behavioral tests for agentic_core/config/core/registry_config.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.config.core.registry_config  # noqa: F401


def test_module_importable():
    """Module registry_config must be importable."""
    assert agentic_core.config.core.registry_config is not None
