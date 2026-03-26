"""Foundational behavioral tests for agentic_core/L5_safety/config/structure_blueprint/ssot.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.config.structure_blueprint.ssot  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.config.structure_blueprint.ssot  # noqa: F401
    """Module ssot must be importable."""
    assert agentic_core.L5_safety.config.structure_blueprint.ssot is not None
