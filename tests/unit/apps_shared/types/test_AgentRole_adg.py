"""ADG contract tests for apps_shared/types/AgentRole.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit



def test_module_importable():
    """Module AgentRole must be importable."""
    import apps_shared.types.AgentRole  # noqa: F401

    assert apps_shared.types.AgentRole is not None