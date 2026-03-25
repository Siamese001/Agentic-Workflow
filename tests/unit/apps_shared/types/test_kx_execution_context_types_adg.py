"""ADG contract tests for apps_shared/types/kx_execution_context_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.kx_execution_context_types  # noqa: F401


def test_module_importable():
    """Module kx_execution_context_types must be importable."""
    assert apps_shared.types.kx_execution_context_types is not None
