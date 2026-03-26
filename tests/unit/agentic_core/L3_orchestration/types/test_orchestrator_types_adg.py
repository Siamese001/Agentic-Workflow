"""ADG contract tests for L3_orchestration/types/orchestrator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L3_orchestration.types.orchestrator_types  # noqa: F401


def test_module_importable():
    import agentic_core.L3_orchestration.types.orchestrator_types  # noqa: F401
    """Module orchestrator_types must be importable."""
    assert agentic_core.L3_orchestration.types.orchestrator_types is not None
