"""ADG-driven tests for agentic_core/L4_state/utils/get_existing_files_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L4_state.utils.get_existing_files_util  # noqa: F401


def test_module_importable():
    """Module get_existing_files_util must be importable."""
    assert agentic_core.L4_state.utils.get_existing_files_util is not None
