"""Foundational behavioral tests for agentic_core/mixins/subatomic_testing_mixin.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.mixins.subatomic_testing_mixin  # noqa: F401


def test_module_importable():
    import agentic_core.mixins.subatomic_testing_mixin  # noqa: F401
    """Module subatomic_testing_mixin must be importable."""
    assert agentic_core.mixins.subatomic_testing_mixin is not None
