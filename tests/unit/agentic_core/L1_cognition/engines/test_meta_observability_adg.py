"""ADG-driven tests for L1_cognition/engines/meta_observability.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.engines.meta_observability  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.engines.meta_observability  # noqa: F401
    """Module meta_observability must be importable."""
    assert agentic_core.L1_cognition.engines.meta_observability is not None
