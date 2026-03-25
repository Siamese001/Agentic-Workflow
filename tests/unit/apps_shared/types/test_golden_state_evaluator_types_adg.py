"""ADG contract tests for apps_shared/types/golden_state_evaluator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.golden_state_evaluator_types  # noqa: F401


def test_module_importable():
    """Module golden_state_evaluator_types must be importable."""
    assert apps_shared.types.golden_state_evaluator_types is not None
