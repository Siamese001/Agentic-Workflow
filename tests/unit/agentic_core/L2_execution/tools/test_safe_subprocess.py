"""Foundational behavioral tests for agentic_core/L2_execution/tools/safe_subprocess.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.tools.safe_subprocess  # noqa: F401


def test_module_importable():
    """Module safe_subprocess must be importable."""
    assert agentic_core.L2_execution.tools.safe_subprocess is not None
