"""ADG-driven tests for agentic_core/runtime/utils/sovereign_dependency_error_util.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.runtime.utils.sovereign_dependency_error_util  # noqa: F401


def test_module_importable():
        import agentic_core.runtime.utils.sovereign_dependency_error_util  # noqa: F401
        """Module sovereign_dependency_error_util must be importable."""
        assert agentic_core.runtime.utils.sovereign_dependency_error_util is not None

    assert agentic_core.runtime.utils.sovereign_dependency_error_util is not None
