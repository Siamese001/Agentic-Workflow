"""Foundational behavioral tests for agentic_core/adg/applications/execute_ssot_integration.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.adg.applications.execute_ssot_integration  # noqa: F401


def test_module_importable():
    """Module execute_ssot_integration must be importable."""
    assert agentic_core.adg.applications.execute_ssot_integration is not None
