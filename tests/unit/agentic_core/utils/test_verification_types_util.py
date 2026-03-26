"""Foundational behavioral tests for agentic_core/utils/verification_types_util.py."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.utils.verification_types_util as _mod  # noqa: F401


def test_module_importable():
    import agentic_core.utils.verification_types_util as _mod  # noqa: F401
    """Module verification_types_util must be importable."""
    assert _mod is not None
