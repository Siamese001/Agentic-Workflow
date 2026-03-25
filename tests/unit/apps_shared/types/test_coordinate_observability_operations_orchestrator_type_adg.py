"""ADG contract tests for apps_shared/types/coordinate_observability_operations_orchestrator_type.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.coordinate_observability_operations_orchestrator_type  # noqa: F401


def test_module_importable():
    """Module coordinate_observability_operations_orchestrator_type must be importable."""
    assert apps_shared.types.coordinate_observability_operations_orchestrator_type is not None
