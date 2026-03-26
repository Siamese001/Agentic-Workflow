"""ADG-driven tests for agentic_core/L1_cognition/engines/deterministic_context_optimizer.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.engines.deterministic_context_optimizer  # noqa: F401


def test_module_importable():
        import agentic_core.L1_cognition.engines.deterministic_context_optimizer  # noqa: F401
        """Module deterministic_context_optimizer must be importable."""
        assert agentic_core.L1_cognition.engines.deterministic_context_optimizer is not None

    assert agentic_core.L1_cognition.engines.deterministic_context_optimizer is not None
