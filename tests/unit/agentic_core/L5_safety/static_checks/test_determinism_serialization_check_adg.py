"""ADG importability contract for agentic_core/L5_safety/static_checks/determinism_serialization_check.py."""
from __future__ import annotations

import agentic_core.L5_safety.static_checks.determinism_serialization_check  # noqa: F401


def test_module_importable():
    """Module determinism_serialization_check must be importable."""
    assert agentic_core.L5_safety.static_checks.determinism_serialization_check is not None
