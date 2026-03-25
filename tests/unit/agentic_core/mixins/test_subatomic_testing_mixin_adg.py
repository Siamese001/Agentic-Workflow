"""ADG importability contract for agentic_core/mixins/subatomic_testing_mixin.py."""
from __future__ import annotations

import agentic_core.mixins.subatomic_testing_mixin  # noqa: F401


def test_module_importable():
    """Module subatomic_testing_mixin must be importable."""
    assert agentic_core.mixins.subatomic_testing_mixin is not None
