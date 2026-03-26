"""Foundational behavioral tests for agentic_core/utils/meta_learning_types_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.utils.meta_learning_types_util as _mod  # noqa: F401


def test_module_importable():
        import agentic_core.utils.meta_learning_types_util as _mod  # noqa: F401
        """Module meta_learning_types_util must be importable."""
        assert _mod is not None

    assert _mod is not None
