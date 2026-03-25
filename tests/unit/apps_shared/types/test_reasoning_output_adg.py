"""ADG contract tests for apps_shared/types/reasoning_output.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.reasoning_output  # noqa: F401


def test_module_importable():
    """Module reasoning_output must be importable."""
    assert apps_shared.types.reasoning_output is not None
