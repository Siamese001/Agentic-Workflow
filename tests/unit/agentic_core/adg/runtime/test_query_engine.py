"""Foundational behavioral tests for agentic_core/adg/runtime/query_engine.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.runtime.query_engine  # noqa: F401


def test_module_importable():
    """Module query_engine must be importable."""
    assert agentic_core.adg.runtime.query_engine is not None
