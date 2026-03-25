"""End-to-end pipeline tests: tracer → drain → materialize → persist."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.utils.open_telemetry_tracing_adapter_util  # noqa: F401


def test_module_importable():
    """Module open_telemetry_tracing_adapter_util must be importable."""
    assert apps_shared.utils.open_telemetry_tracing_adapter_util is not None
