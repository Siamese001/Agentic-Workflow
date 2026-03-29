"""ADG-driven tests for apps_shared/utils/agent_interface_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module agent_interface_util must be importable."""
    import apps_shared.utils.agent_interface_util  # noqa: F401

    assert apps_shared.utils.agent_interface_util is not None