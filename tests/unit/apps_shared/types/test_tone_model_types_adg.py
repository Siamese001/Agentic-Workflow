"""ADG contract tests for apps_shared/types/tone_model_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module tone_model_types must be importable."""
    import apps_shared.types.tone_model_types  # noqa: F401

    assert apps_shared.types.tone_model_types is not None