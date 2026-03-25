"""ADG contract tests for apps_shared/types/AgentRole.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

import apps_shared.types.AgentRole  # noqa: F401


def test_module_importable():
    """Module AgentRole must be importable."""
    assert apps_shared.types.AgentRole is not None
