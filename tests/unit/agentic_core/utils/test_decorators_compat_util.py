"""Foundational behavioral tests for agentic_core/utils/decorators_compat_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.utils.decorators_compat_util  # noqa: F401


def test_module_importable():
    import agentic_core.utils.decorators_compat_util  # noqa: F401
    """Module decorators_compat_util must be importable."""
    assert agentic_core.utils.decorators_compat_util is not None
