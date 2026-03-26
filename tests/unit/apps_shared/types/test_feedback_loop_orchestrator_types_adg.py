"""ADG contract tests for apps_shared/types/feedback_loop_orchestrator_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module feedback_loop_orchestrator_types must be importable."""
    import apps_shared.types.feedback_loop_orchestrator_types  # noqa: F401

    assert apps_shared.types.feedback_loop_orchestrator_types is not None