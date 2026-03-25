"""ADG contract tests for apps_shared/types/execution_orchestrator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.execution_orchestrator_types  # noqa: F401


def test_module_importable():
    """Module execution_orchestrator_types must be importable."""
    assert apps_shared.types.execution_orchestrator_types is not None
