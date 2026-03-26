"""Foundational behavioral tests for agentic_core/L5_safety/types/hardening_errors.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.types.hardening_errors  # noqa: F401


def test_module_importable():
        import agentic_core.L5_safety.types.hardening_errors  # noqa: F401
        """Module hardening_errors must be importable."""
        assert agentic_core.L5_safety.types.hardening_errors is not None

    assert agentic_core.L5_safety.types.hardening_errors is not None
