"""ADG-driven tests for agentic_core/knowledge/healing/wiki_healer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.knowledge.healing.wiki_healer  # noqa: F401


def test_module_importable():
    """Module wiki_healer must be importable."""
    assert agentic_core.knowledge.healing.wiki_healer is not None
