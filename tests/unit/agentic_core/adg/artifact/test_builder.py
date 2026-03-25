"""Foundational behavioral tests for agentic_core/adg/artifact/builder.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.artifact.builder_types  # noqa: F401


def test_module_importable():
    """Module builder_types must be importable."""
    assert agentic_core.adg.artifact.builder_types is not None
