"""ADG-driven tests for agentic_core/L1_cognition/engines/pitch_engine.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.engines.pitch_engine  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.engines.pitch_engine  # noqa: F401
    """Module pitch_engine must be importable."""
    assert agentic_core.L1_cognition.engines.pitch_engine is not None
