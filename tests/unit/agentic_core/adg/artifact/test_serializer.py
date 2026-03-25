"""Foundational behavioral tests for agentic_core/adg/artifact/serializer.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.artifact.serializer_util  # noqa: F401


def test_module_importable():
    """Module serializer_util must be importable."""
    assert agentic_core.adg.artifact.serializer_util is not None
