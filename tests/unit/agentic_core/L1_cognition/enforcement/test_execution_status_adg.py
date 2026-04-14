"""Smoke tests for the execution status surface."""

from __future__ import annotations

import pytest

from L1_cognition.test_support import assert_module_surface


@pytest.mark.unit
def test_execution_status_surface():
    assert_module_surface(
        "agentic_core.execution_status_adg",
        "ExecutionStatusAdg",
        "validate_execution_status_adg",
    )
