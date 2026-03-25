"""ADG contract tests for apps_shared/types/tone_model_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.tone_model_types  # noqa: F401


def test_module_importable():
    """Module tone_model_types must be importable."""
    assert apps_shared.types.tone_model_types is not None
