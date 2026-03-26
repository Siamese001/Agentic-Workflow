"""Foundational behavioral tests for agentic_core/L5_safety/config/structure_blueprint/_constants.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.config.structure_blueprint._constants  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.config.structure_blueprint._constants  # noqa: F401
    """Module _constants must be importable."""
    assert agentic_core.L5_safety.config.structure_blueprint._constants is not None
