"""ADG contract tests for apps_shared/types/adaptive_recovery_loop_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module adaptive_recovery_loop_types must be importable."""
    import apps_shared.types.adaptive_recovery_loop_types  # noqa: F401

    assert apps_shared.types.adaptive_recovery_loop_types is not None
