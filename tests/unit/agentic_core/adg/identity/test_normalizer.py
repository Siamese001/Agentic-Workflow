"""Foundational behavioral tests for agentic_core/adg/identity/normalizer.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.identity.normalizer  # noqa: F401


def test_module_importable():
    """Module normalizer must be importable."""
    assert agentic_core.adg.identity.normalizer is not None
