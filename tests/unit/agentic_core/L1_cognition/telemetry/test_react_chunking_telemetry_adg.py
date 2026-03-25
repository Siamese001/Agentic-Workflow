"""ADG importability contract for agentic_core/L1_cognition/telemetry/react_chunking_telemetry.py."""
from __future__ import annotations

import agentic_core.L1_cognition.telemetry.react_chunking_telemetry  # noqa: F401


def test_module_importable():
    """Module react_chunking_telemetry must be importable."""
    assert agentic_core.L1_cognition.telemetry.react_chunking_telemetry is not None
