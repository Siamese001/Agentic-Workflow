"""ADG-driven tests for agentic_core/L5_safety/governance/lazy_seam_classifier.py — fan_in=0."""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit

#  # MOVED: import agentic_core.L5_safety.governance.lazy_seam_classifier  # noqa: F401


def test_module_importable():
    import agentic_core.L5_safety.governance.lazy_seam_classifier  # noqa: F401
    """Module lazy_seam_classifier must be importable."""
    assert agentic_core.L5_safety.governance.lazy_seam_classifier is not None
