"""ADG-driven tests for agentic_core/L6_observability/utils/integrity_report_generator_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import agentic_core.L6_observability.utils.integrity_report_generator_util  # noqa: F401


def test_module_importable():
    """Module integrity_report_generator_util must be importable."""
    assert agentic_core.L6_observability.utils.integrity_report_generator_util is not None
