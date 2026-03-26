"""ADG-driven tests for agentic_core/L1_cognition/engines/codebase_mapper.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L1_cognition.engines.codebase_mapper  # noqa: F401


def test_module_importable():
    import agentic_core.L1_cognition.engines.codebase_mapper  # noqa: F401
    """Module codebase_mapper must be importable."""
    assert agentic_core.L1_cognition.engines.codebase_mapper is not None
