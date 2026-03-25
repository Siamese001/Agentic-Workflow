"""Foundational behavioral tests for agentic_core/L2_execution/types/infra_error_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L2_execution.types.infra_error_types  # noqa: F401


def test_module_importable():
    """Module infra_error_types must be importable."""
    assert agentic_core.L2_execution.types.infra_error_types is not None
