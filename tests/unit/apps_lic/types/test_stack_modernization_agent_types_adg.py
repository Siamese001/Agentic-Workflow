"""ADG contract tests for apps_lic/types/stack_modernization_agent_types.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_module_importable():
    """Module stack_modernization_agent_types must be importable."""
    import apps_lic.types.stack_modernization_agent_types  # noqa: F401

    assert apps_lic.types.stack_modernization_agent_types is not None