"""ADG-driven tests for agentic_core/L6_observability/golden_evaluation/__init__.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L6_observability.golden_evaluation.__init__ as _mod  # noqa: F401


def test_module_importable():
        import agentic_core.L6_observability.golden_evaluation.__init__ as _mod  # noqa: F401
        """Module golden_evaluation must be importable."""
        assert _mod is not None

    assert _mod is not None
