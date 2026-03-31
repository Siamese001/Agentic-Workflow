"""ADG contract tests for apps_shared/types/orchestrate_observability_planning_orchestrator_type.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module orchestrate_observability_planning_orchestrator_type must be importable."""
    import apps_shared.types.orchestrate_observability_planning_orchestrator_type  # noqa: F401

    assert apps_shared.types.orchestrate_observability_planning_orchestrator_type is not None
