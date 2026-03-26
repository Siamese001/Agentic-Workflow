"""ADG importability contract for agentic_core/L6_observability/utils/system_telemetry_util.py."""
from __future__ import annotations

#  # MOVED: import agentic_core.L6_observability.utils.system_telemetry_util  # noqa: F401


def test_module_importable():
    import agentic_core.L6_observability.utils.system_telemetry_util  # noqa: F401
    """Module system_telemetry_util must be importable."""
    assert agentic_core.L6_observability.utils.system_telemetry_util is not None
