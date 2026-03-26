"""ADG contract tests for apps_shared/types/reasoning_output.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module reasoning_output must be importable."""
    import apps_shared.types.reasoning_output  # noqa: F401

    assert apps_shared.types.reasoning_output is not None
