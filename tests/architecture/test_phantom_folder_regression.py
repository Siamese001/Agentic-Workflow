""""""
from __future__ import annotations

import agentic_core.L5_safety.config.structure_blueprint  # noqa: F401


def test_module_importable():
    """Module structure_blueprint must be importable."""
    assert agentic_core.L5_safety.config.structure_blueprint is not None
