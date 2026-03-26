"""ADG contract tests for L3_orchestration/types/route_type_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.types.route_type_types  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.types.route_type_types  # noqa: F401
    """Module route_type_types must be importable."""
    assert agentic_core.L3_orchestration.types.route_type_types is not None
