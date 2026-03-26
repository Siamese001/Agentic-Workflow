"""ADG-driven tests for agentic_core/L6_observability/enforcement/rag_telemetry_collector.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L6_observability.enforcement.rag_telemetry_collector  # noqa: F401


def test_module_importable():
    import agentic_core.L6_observability.enforcement.rag_telemetry_collector  # noqa: F401
    """Module rag_telemetry_collector must be importable."""
    assert agentic_core.L6_observability.enforcement.rag_telemetry_collector is not None
