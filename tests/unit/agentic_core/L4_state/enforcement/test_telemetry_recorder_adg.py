"""ADG importability contract for agentic_core/L4_state/enforcement/telemetry_recorder.py."""
from __future__ import annotations

import agentic_core.L4_state.enforcement.telemetry_recorder  # noqa: F401


def test_module_importable():
    """Module telemetry_recorder must be importable."""
    assert agentic_core.L4_state.enforcement.telemetry_recorder is not None
