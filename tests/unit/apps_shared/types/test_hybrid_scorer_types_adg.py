"""ADG contract tests for apps_shared/types/hybrid_scorer_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.hybrid_scorer_types  # noqa: F401


def test_module_importable():
    """Module hybrid_scorer_types must be importable."""
    assert apps_shared.types.hybrid_scorer_types is not None
