"""Foundational behavioral tests for agentic_core/adg/artifact/normalizer.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.artifact.normalizer_config  # noqa: F401


def test_module_importable():
    """Module normalizer_config must be importable."""
    assert agentic_core.adg.artifact.normalizer_config is not None
